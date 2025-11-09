# quick_random_check.py
from flappy_env import FlappyBirdEnv
import random, statistics

env = FlappyBirdEnv(render=False)  # dùng bản hiện tại của bạn
L = []
for ep in range(50):
    s = env.reset()
    steps = 0
    while True:
        a = random.randint(0,1)
        s, r, done, info = env.step(a)
        steps += 1
        if done:
            L.append(steps)
            break
print("avg steps:", statistics.mean(L), "min:", min(L), "max:", max(L))
