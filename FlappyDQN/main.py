# env_manual_demo.py
import pygame, time
from flappy_env import FlappyBirdEnv

if __name__ == "__main__":
    env = FlappyBirdEnv(render=True)  # dùng các tham số bạn đã chỉnh
    running = True
    while running:
        s = env.reset()
        done = False
        while not done:
            action = 0
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    done = True
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    action = 1  # flap 1 lần ở step này
            env.render()
            _, _, done, _ = env.step(action)
        time.sleep(0.5)
