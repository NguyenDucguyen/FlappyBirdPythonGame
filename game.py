import pygame

from random import randint

pygame.init()
WIDTH, HEIGHT = 600, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Flappy Bird By Nguyen Duc Nguyen')
running = True
GREEN = (0,200,0)
RED = (255,0,0)
BLUE = (0,0,255)
BLACK = (0,0,0)
YELLOW = (255,255,0)
clock = pygame.time.Clock()

TUBE_WIDTH = 50

tube1_x = 600
tube2_x = 800
tube3_x = 1000
tube1_height = randint(100,300)
tube2_height = randint(100,300)
tube3_height = randint(100,300)

TUBE_VELOCITY = 3
TUBE_GAP = 150

BIRD_X = 50
bird_y = 400
BIRD_WIDTH = 35
BIRD_HEIGHT = 35

bird_drop_velocity = 0
GRAVITY = 0.5

score = 0
font = pygame.font.SysFont('sans', 20)

tube1_pass = False
tube2_pass = False
tube3_pass = False

pausing = False
background_image = pygame.image.load("background-day.png")
background_image = pygame.transform.scale(background_image, (WIDTH, HEIGHT))
bird_image = pygame.image.load("yellowbird-midflap.png")
bird_image = pygame.transform.scale(bird_image, (BIRD_WIDTH, BIRD_HEIGHT))
tube_image = pygame.image.load("pipe-green.png")
tube_image = pygame.transform.scale(tube_image, (TUBE_WIDTH, HEIGHT))
sand_image = pygame.image.load("base.png")
sand_image = pygame.transform.scale(sand_image, (WIDTH, HEIGHT - 550))
while running:
     clock.tick(60)
     screen.fill(GREEN)
     screen.blit(background_image, (0,0))
     
     #Ve cot tren
     tube1_rect = screen.blit(tube_image, (tube1_x, tube1_height - HEIGHT))
     tube2_rect = screen.blit(tube_image, (tube2_x, tube2_height - HEIGHT))
     tube3_rect = screen.blit(tube_image, (tube3_x, tube3_height - HEIGHT))

     #Ve cot nguoc lai
     tube1_rect_inv = screen.blit(tube_image, (tube1_x, tube1_height + TUBE_GAP))
     tube2_rect_inv = screen.blit(tube_image, (tube2_x, tube2_height + TUBE_GAP))
     tube3_rect_inv = screen.blit(tube_image, (tube3_x, tube3_height + TUBE_GAP))

     tube1_x = tube1_x - TUBE_VELOCITY
     tube2_x = tube2_x - TUBE_VELOCITY
     tube3_x = tube3_x - TUBE_VELOCITY

     #ve nen cat
     sand_rect = screen.blit(sand_image, (0,550))


     #Ve chim
    #  bird_rect = pygame.draw.rect(screen,RED, (BIRD_X, bird_y,BIRD_WIDTH,BIRD_HEIGHT))
     bird_rect = screen.blit(bird_image, (BIRD_X, bird_y))
     #chim roi
     bird_y = bird_y + bird_drop_velocity
     bird_drop_velocity += GRAVITY


     # tao ong moi sau moi vong di chuyen het
     if tube1_x < -TUBE_WIDTH:
         tube1_x = 590
         tube1_height = randint(100,300)
         tube1_pass = False
     if tube2_x < -TUBE_WIDTH:
         tube2_x = 590
         tube2_height = randint(100,300)
         tube2_pass = False
     if tube3_x < -TUBE_WIDTH:
         tube3_x = 590
         tube3_height = randint(100,300)
         tube3_pass = False

     #Ve diem
     score_txt = font.render("Score: " + str(score), True, BLACK)
     screen.blit(score_txt, (5,5))

     #Cong diem
     if tube1_x + TUBE_WIDTH <= BIRD_X and tube1_pass == False:
            score += 1
            tube1_pass = True
     if tube2_x + TUBE_WIDTH <= BIRD_X and tube2_pass == False:
            score += 1
            tube2_pass = True
     if tube3_x + TUBE_WIDTH <= BIRD_X and tube3_pass == False:
            score += 1
            tube3_pass = True

    #kiem tra va cham 
     for tube in [tube1_rect, tube2_rect, tube3_rect,tube1_rect_inv, tube2_rect_inv, tube3_rect_inv,sand_rect]:
         if bird_rect.colliderect(tube):
             pausing = True
             TUBE_VELOCITY = 0
             bird_drop_velocity = 0
             game_over_txt = font.render("GAME OVER! Final Score: " + str(score), True, BLACK)
             screen.blit(game_over_txt, (200,300))
             press_space_txt = font.render("Press Space To Continue", True, BLACK)
             screen.blit(press_space_txt, (200,400))            
     
     for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
              if event.key == pygame.K_SPACE:
                #reset game
                if pausing == True:
                     bird_y = 400
                     tube1_x = 600
                     tube2_x = 800
                     tube3_x = 1000
                     score = 0
                     TUBE_VELOCITY = 3
                     pausing = False

                bird_drop_velocity = 0
                bird_drop_velocity = -10
    
     pygame.display.flip()

pygame.quit() 