# play_trained.py
import time
import torch
from flappy_env import FlappyBirdEnv
from dqn_agent import DQNAgent
import os


if __name__ == "__main__":
    env = FlappyBirdEnv(render=True)
    state_dim, action_dim = 5, 2

    path = "flappy_dqn_best.pt" if os.path.exists("flappy_dqn_best.pt") else "flappy_dqn.pt"

    agent = DQNAgent(state_dim=state_dim, action_dim=action_dim)
    agent.q.load_state_dict(torch.load(path, map_location="cpu"))
    agent.q.eval()

    while True:
        s = env.reset()
        while True:
            env.render()
            with torch.no_grad():
                a = int(agent.q(torch.tensor(s).float().unsqueeze(0)).argmax(dim=1))
            s, r, done, info = env.step(a)
            if done:
                time.sleep(0.7)
                break
