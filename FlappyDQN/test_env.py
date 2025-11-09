# test_env.py
from flappy_env import FlappyBirdEnv
import numpy as np

env = FlappyBirdEnv(render=True)
s = env.reset()

print("Testing environment observations:")
for step in range(200):
    print(f"\nStep {step}:")
    print(f"  State: {s}")
    print(f"  Bird Y: {env.bird_y:.1f}, V: {env.bird_v:.1f}")
    
    idx = env._next_tube_index()
    print(f"  Next tube idx: {idx}")
    print(f"  Tube X: {env.tube_x[idx]:.1f}")
    print(f"  Gap: {env.tube_h[idx]:.1f} - {env.tube_h[idx] + env.tube_h[idx] + 150:.1f}")
    
    # Test random action
    a = 1 if step % 10 == 0 else 0  # Flap mỗi 10 frames
    s, r, done, info = env.step(a)
    print(f"  Action: {a}, Reward: {r:.3f}, Done: {done}")
    
    env.render()
    
    if done:
        print(f"\n💀 Died! Score: {info['score']}")
        input("Press Enter to continue...")
        s = env.reset()