import sys
import pygame
import os
from pygame.locals import *

pygame.init()
vec = pygame.math.Vector2
HEIGHT = 450
WIDTH = 400
ACC = 0.5
FRIC = -0.12
FPS = 60
FramePerSec = pygame.time.Clock()
displaysurface = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Game")

def load_images(path):
    print(f'loading animation set: {path}')
    images = []
    for file_name in sorted(os.listdir(path)):
        print(f'     loading-{file_name}')
        image = pygame.image.load(path + os.sep + file_name).convert()
        images.append(image)
    return images

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()

        #self.surf = pygame.Surface((30, 30))
        #self.surf.fill((128,255,40))
        #self.rect = self.surf.get_rect(center = (10, 420))
        size = (160, 224)

        #initial state
        position = (300,385)
        self.rect = pygame.Rect((position),size)
        self.pos = vec((position))
        self.vel = vec(0,0)
        self.accel = vec(0,0)
        self.facing_right = True
        self.facing_left = False
    
        #handles animation
        #---animation sprite sheets
        self.idle_right = player_idle_right
        self.idle_left = player_idle_left
        self.walk_left = player_walk_left
        self.walk_right = player_walk_right

        self.animation_index = 0
        #this is the first image to display? question mark?
        self.image = player_idle_right[self.animation_index]

        #frame based animation rendering
        self.animation_frames = 6
        self.current_frame = 0

    def move(self):
        self.acc = vec(0,2)
        pressed_keys = pygame.key.get_pressed()

        if pressed_keys[K_LEFT]:
            self.acc.x = -ACC
        if pressed_keys[K_RIGHT]:
            self.acc.x = ACC

        #self.acc.x += self.vel.x * FRIC
        #self.vel += self.acc
        #self.pos += self.vel + 0.5 * self.acc

        self.acc.x += self.vel.x * FRIC
        self.vel += self.acc
        self.pos += self.vel + 0.5 * self.acc

        if self.pos.x > WIDTH:
            self.pos.x = 0
        if self.pos.x < 0:
            self.pos.x = WIDTH

        self.rect.midbottom = self.pos

    def animation_update(self):
        #walk
        if int(self.vel.x) > 0:
            self.images = self.walk_right
            self.facing_right = True
            self.facing_left = False
        elif int(self.vel.x) < 0:
            self.images = self.walk_left
            self.facing_left = True
            self.facing_right = False

        #idle
        if int(self.vel.x) == 0 and self.facing_right:
            self.images = self.idle_right
        if int(self.vel.x) == 0 and self.facing_left:
            self.images = self.idle_left

        self.current_frame += 1
        if self.current_frame >= self.animation_frames:
            self.current_frame = 0
            self.animation_index = (self.animation_index + 1) % len(self.images)
            self.image = self.images[self.animation_index]

    def update(self):
        #platform detection
        hits = pygame.sprite.spritecollide(P1, platform_sprites, False)
        if hits:
            self.pos.y = hits[0].rect.top + 1
            self.vel.y = 0 

        #animation
        self.animation_update()

    def jump(self):
        self.vel.y = -25

class platform(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.surf = pygame.Surface((WIDTH, 20))
        self.surf.fill((255,0,0))
        self.rect = self.surf.get_rect(center = (WIDTH/2, HEIGHT - 10))

#animation set
#---- player idle
player_idle_left = load_images(path='sprites/player/idle')
player_idle_right = [pygame.transform.flip(image, True, False) for image in player_idle_left] 

player_walk_left = load_images(path='sprites/player/walk')
player_walk_right = [pygame.transform.flip(image, True, False) for image in player_walk_left] 

PT1 = platform()
P1 = Player()

#TODO: this thing does not have to be grouped
player_sprite = pygame.sprite.Group()
player_sprite.add(P1)

platform_sprites = pygame.sprite.Group()
platform_sprites.add(PT1)

while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                P1.jump()

    P1.move()
    P1.update()

    #feels like this just blacks the screen for a redraw
    displaysurface.fill((0,0,0))

    #we have to use blit on platform_sprites because it has no image yet
    for entity in platform_sprites:
        displaysurface.blit(entity.surf, entity.rect)

    #draw runs like it wants images
    player_sprite.draw(displaysurface)
    
    pygame.display.update()
    FramePerSec.tick(FPS)










