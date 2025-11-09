# dqn_agent.py
import random
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from collections import deque

class QNet(nn.Module):
    def __init__(self, state_dim, action_dim):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(state_dim, 128), nn.ReLU(),
            nn.Linear(128, 128), nn.ReLU(),
            nn.Linear(128, action_dim)
        )
    def forward(self, x):
        return self.net(x)

class DQNAgent:
    def __init__(self, state_dim, action_dim, device=None, gamma=0.99, lr=1e-3, tau=0.005,
                 buffer_size=100_000, batch_size=256, eps_start=1.0, eps_end=0.05, eps_decay=30_000):
        self.device = device or torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.gamma = gamma
        self.tau = tau
        self.batch_size = batch_size
        self.eps_start = eps_start
        self.eps_end = eps_end
        self.eps_decay = eps_decay
        self.total_steps = 0
        self.action_dim = action_dim

        self.q = QNet(state_dim, action_dim).to(self.device)
        self.q_target = QNet(state_dim, action_dim).to(self.device)
        self.q_target.load_state_dict(self.q.state_dict())
        self.optim = optim.Adam(self.q.parameters(), lr=lr)
        self.buf = deque(maxlen=buffer_size)

    def act(self, state):
        import numpy as np, torch
        eps = self.eps_end + (self.eps_start - self.eps_end) * np.exp(-1.0 * self.total_steps / self.eps_decay)
        self.total_steps += 1
        if random.random() < eps:
            return random.randrange(self.action_dim)
        with torch.no_grad():
            s = torch.tensor(state, dtype=torch.float32, device=self.device).unsqueeze(0)
            q = self.q(s)
            return int(q.argmax(dim=1).item())

    def push(self, s, a, r, s2, d):
        self.buf.append((s, a, r, s2, d))

    def _soft_update(self):
        with torch.no_grad():
            for p, tp in zip(self.q.parameters(), self.q_target.parameters()):
                tp.data.mul_(1 - self.tau)
                tp.data.add_(self.tau * p.data)

    def learn(self):
        if len(self.buf) < self.batch_size:
            return 0.0
        batch = random.sample(self.buf, self.batch_size)
        s, a, r, s2, d = zip(*batch)
        s = torch.tensor(np.array(s), dtype=torch.float32, device=self.device)
        a = torch.tensor(a, dtype=torch.int64, device=self.device).unsqueeze(1)
        r = torch.tensor(r, dtype=torch.float32, device=self.device).unsqueeze(1)
        s2 = torch.tensor(np.array(s2), dtype=torch.float32, device=self.device)
        d = torch.tensor(d, dtype=torch.float32, device=self.device).unsqueeze(1)

        q = self.q(s).gather(1, a)
        with torch.no_grad():
            q_next = self.q_target(s2).max(dim=1, keepdim=True)[0]
            q_tar = r + (1 - d) * self.gamma * q_next
        loss = nn.functional.mse_loss(q, q_tar)

        self.optim.zero_grad()
        loss.backward()
        self.optim.step()
        self._soft_update()
        return float(loss.item())
