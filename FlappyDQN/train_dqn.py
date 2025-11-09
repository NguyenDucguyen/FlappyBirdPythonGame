# train_dqn.py (thêm vào đầu file)
from collections import deque
import numpy as np
import torch, os
from flappy_env import FlappyBirdEnv
from dqn_agent import DQNAgent

EPISODES = 5000
MAX_STEPS = 5000
TARGET_MA = 20          # dừng khi MA100 >= 20
PATIENCE = 1000         # dừng nếu không cải thiện best trong 1000 tập
PRINT_EVERY = 50

if __name__ == "__main__":
    # train_dqn.py
    env = FlappyBirdEnv(render=False)
    agent = DQNAgent(state_dim=5, action_dim=2, lr=5e-4, batch_size=512)

    # warmup buffer
    WARMUP = 5000
    s = env.reset()
    import random
    for _ in range(WARMUP):
        a = random.randint(0,1)
        s2, r, d, _ = env.step(a)
        agent.push(s, a, r, s2, float(d))
        s = s2 if not d else env.reset()
        scores = deque(maxlen=100)
        best = -1
        no_improve = 0

    for ep in range(1, EPISODES + 1):
        s = env.reset()
        ep_reward = 0.0
        score = 0
        for t in range(MAX_STEPS):
            a = agent.act(s)
            s2, r, done, info = env.step(a)
            agent.push(s, a, r, s2, float(done))
            agent.learn()
            s = s2
            ep_reward += r
            score = info.get("score", score)
            if done:
                break

        scores.append(score)
        ma100 = np.mean(scores) if len(scores) == 100 else np.mean(scores)
        if score > best:
            best = score
            no_improve = 0
            torch.save(agent.q.state_dict(), "flappy_dqn_best.pt")
        else:
            no_improve += 1

        if ep % PRINT_EVERY == 0:
            print(f"Ep {ep:4d} | score={score:3d} | best={best:3d} | MA100={ma100:5.2f}")

        # Điều kiện dừng
        if len(scores) == 100 and ma100 >= TARGET_MA:
            print(f"Early stop: MA100 đạt {ma100:.2f} ≥ {TARGET_MA}")
            break
        if no_improve >= PATIENCE:
            print(f"Early stop: {PATIENCE} tập không cải thiện best")
            break

    # Lưu model cuối
    torch.save(agent.q.state_dict(), "flappy_dqn.pt")
    print("Saved -> flappy_dqn.pt (cuối) ; checkpoint tốt nhất -> flappy_dqn_best.pt")
