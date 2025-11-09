# flappy_env.py
import math
import pygame
from random import randint
import numpy as np

# --- constants taken from your game ---
WIDTH, HEIGHT = 600, 600
TUBE_WIDTH = 50
TUBE_VELOCITY_INIT = 3
TUBE_GAP = 150
BIRD_X = 50
BIRD_WIDTH = 35
BIRD_HEIGHT = 35
GRAVITY = 0.5

class FlappyBirdEnv:
    """
    A tiny Gym-like env built from your Pygame loop.
    observation: np.array([bird_y, bird_vel, next_dx, top_gap, bottom_gap]) (normalized)
    actions: 0 = no flap, 1 = flap
    reward: +1 when passing a pipe, -1 on death, -0.01 per step to encourage progress
    done: collision with pipe or ground/sky
    """
    def __init__(self, render=False):
        self.render_mode = render
        self.screen = None
        self.clock = None
        self.font = None
        self.background = None
        self.bird_img = None
        self.tube_img = None
        self.sand_img = None
        self.reset()
        if self.render_mode:
            pygame.init()
            self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
            pygame.display.set_caption('Flappy Bird – RL')
            self.clock = pygame.time.Clock()
            self.font = pygame.font.SysFont('sans', 20)
            # If you have image files next to the script, uncomment these 4 lines:
            self.background = pygame.transform.scale(pygame.image.load("background-day.png"), (WIDTH, HEIGHT))
            self.bird_img = pygame.transform.scale(pygame.image.load("yellowbird-midflap.png"), (BIRD_WIDTH, BIRD_HEIGHT))
            self.tube_img = pygame.transform.scale(pygame.image.load("pipe-green.png"), (TUBE_WIDTH, HEIGHT))
            self.sand_img = pygame.transform.scale(pygame.image.load("base.png"), (WIDTH, HEIGHT - 550))

    # --- game mechanics (based on your loop) ---
    def _spawn_tube(self):
        return randint(100, 300)

    def reset(self):
        self.tube_x = [600, 800, 1000]
        self.tube_h = [self._spawn_tube(), self._spawn_tube(), self._spawn_tube()]
        self.tube_passed = [False, False, False]
        self.tube_velocity = TUBE_VELOCITY_INIT

        self.bird_y = 400.0
        self.bird_v = 0.0
        self.score = 0
        self.done = False
        return self._get_obs()

    def step(self, action:int):
        # action: 1 = flap
        if self.done:
            return self._get_obs(), 0.0, True, {}

        if action == 1:
            self.bird_v = -10.0
        
        # gravity
        self.bird_y += self.bird_v
        self.bird_v += GRAVITY

        # move tubes
        for i in range(3):
            self.tube_x[i] -= self.tube_velocity
            if self.tube_x[i] < -TUBE_WIDTH:
                self.tube_x[i] = 590
                self.tube_h[i] = self._spawn_tube()
                self.tube_passed[i] = False

        # ===== REWARD SHAPING =====
        reward = 0.0
        
        # 1. Small alive bonus (khuyến khích sống lâu)
        reward += 0.1
        
        # 2. Reward dựa trên khoảng cách đến center của gap
        i = self._next_tube_index()
        gap_center = self.tube_h[i] + TUBE_GAP / 2
        bird_center = self.bird_y + BIRD_HEIGHT / 2
        
        # Khoảng cách đến tâm gap
        dist_to_center = abs(bird_center - gap_center)
        
        # Thưởng khi gần center, phạt khi xa (tối đa ±1.0)
        alignment_reward = 1.0 - min(dist_to_center / 200.0, 1.0)
        reward += alignment_reward * 0.5  # scale down để không quá mạnh
        
        # 3. Bonus khi đang tiến gần đến ống (khuyến khích tiến về phía trước)
        horizontal_progress = -0.01  # small penalty mỗi frame
        reward += horizontal_progress

        # 4. Scoring (big reward khi qua ống)
        for i in range(3):
            if self.tube_x[i] + TUBE_WIDTH <= BIRD_X and not self.tube_passed[i]:
                self.tube_passed[i] = True
                self.score += 1
                reward += 10.0  # Big bonus!

        # 5. Collision (big penalty)
        if self._collides():
            self.done = True
            reward = -10.0  # Phạt nặng khi chết

        return self._get_obs(), reward, self.done, {"score": self.score}

    def _collides(self):
        # ground/sky
        if self.bird_y < 0 or self.bird_y + BIRD_HEIGHT > 550:  # 550 is top of sand
            return True
        # tubes: if x window overlapping and y not in gap
        for i in range(3):
            if (BIRD_X + BIRD_WIDTH > self.tube_x[i]) and (BIRD_X < self.tube_x[i] + TUBE_WIDTH):
                gap_top = self.tube_h[i]
                gap_bottom = self.tube_h[i] + TUBE_GAP
                bird_top = self.bird_y
                bird_bottom = self.bird_y + BIRD_HEIGHT
                if bird_top < gap_top or bird_bottom > gap_bottom:
                    return True
        return False

    def _next_tube_index(self):
        # the first tube with x + width >= BIRD_X (in front of bird)
        idx = np.argmin([x if x + TUBE_WIDTH >= BIRD_X else math.inf for x in self.tube_x])
        return int(idx)

    def _get_obs(self):
        i = self._next_tube_index()
        next_dx = (self.tube_x[i] + TUBE_WIDTH) - (BIRD_X + BIRD_WIDTH/2)
        gap_top = self.tube_h[i]
        gap_bottom = self.tube_h[i] + TUBE_GAP
        # normalize roughly to 0..1 ranges
        obs = np.array([
            self.bird_y / 600.0,
            np.clip(self.bird_v, -10, 10) / 10.0,
            np.clip(next_dx, -600, 600) / 600.0,
            gap_top / 600.0,
            gap_bottom / 600.0,
        ], dtype=np.float32)
        return obs

    def render(self):
        if not self.render_mode:
            return
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.done = True
        self.clock.tick(60)
        self.screen.fill((0, 200, 0))
        if self.background:
            self.screen.blit(self.background, (0, 0))
        # Draw simple tubes and bird if no images are loaded
        # tubes
        # tubes
        for i in range(3):
            x = self.tube_x[i]
            h = self.tube_h[i]

            if self.tube_img:  # đã load ảnh ống
                # Ống trên (giống cách bạn vẽ: đặt ảnh từ h - HEIGHT)
                self.screen.blit(self.tube_img, (x, h - HEIGHT))
                # Ống dưới
                self.screen.blit(self.tube_img, (x, h + TUBE_GAP))  # nếu bạn dùng self.TUBE_GAP thì đổi tên ở đây
            else:
                # fallback vẽ hình chữ nhật
                top_rect = pygame.Rect(x, h - HEIGHT, TUBE_WIDTH, HEIGHT)
                bot_rect = pygame.Rect(x, h + TUBE_GAP, TUBE_WIDTH, HEIGHT)
                pygame.draw.rect(self.screen, (0, 255, 0), top_rect)
                pygame.draw.rect(self.screen, (0, 255, 0), bot_rect)

        # ground
        if self.sand_img:
            self.screen.blit(self.sand_img, (0, 550))
        else:
            pygame.draw.rect(self.screen, (200, 180, 40), pygame.Rect(0, 550, WIDTH, 50))

        # bird
        if self.bird_img:
            self.screen.blit(self.bird_img, (BIRD_X, int(self.bird_y)))
        else:
            pygame.draw.rect(self.screen, (255, 0, 0), pygame.Rect(BIRD_X, int(self.bird_y), BIRD_WIDTH, BIRD_HEIGHT))

        # score
        if self.font:
            txt = self.font.render(f"Score: {self.score}", True, (0,0,0))
            self.screen.blit(txt, (5,5))
        pygame.display.flip()