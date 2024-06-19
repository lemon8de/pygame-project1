import sys
import pygame
import os
from pygame.locals import *

pygame.init()
vec = pygame.math.Vector2
HEIGHT = 700
WIDTH = 1200
ACC = 0.8
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
        position = (300,585)
        self.rect = pygame.Rect((position),size)
        self.pos = vec((position))
        self.vel = vec(0,0)
        self.accel = vec(0,0)

        self.facing_right = True
        self.facing_left = False

        #special variables to finetune animation
        self.can_jump = False
        self.falling = True

        #used by some animations that should hold its last frame
        #example a very long jump, a very long fall
        self.animation_lock = {
            'jumping' : False,
            'falling' : False,
        }
    
        #handles animation
        #---animation sprite sheets
        self.idle_left = player_idle_left
        self.idle_right = player_idle_right

        self.walk_left = player_walk_left
        self.walk_right = player_walk_right

        self.jump_left = player_jump_left
        self.jump_right = player_jump_right

        self.fall_left = player_fall_left
        self.fall_right = player_fall_right

        self.animation_index = 0
        self.image = player_idle_right[self.animation_index]

        #frame based animation rendering
        self.animation_frames = 9 
        self.current_frame = 0

    def move(self):
        self.acc = vec(0,0.3) #gravity
        pressed_keys = pygame.key.get_pressed()

        if pressed_keys[K_LEFT]:
            self.acc.x = -ACC
            self.facing_left = True
            self.facing_right = False
        if pressed_keys[K_RIGHT]:
            self.acc.x = ACC
            self.facing_right = True
            self.facing_left = False

        self.acc.x += self.vel.x * FRIC
        self.vel += self.acc
        self.pos += self.vel + 0.5 * self.acc

        if self.pos.x > WIDTH:
            self.pos.x = 0
        if self.pos.x < 0:
            self.pos.x = WIDTH

        self.rect.midbottom = self.pos

    def animation_update(self):
        #locking animations, currently jumping and falling counts as locking
        #definition of locking: to repeat the last two frames of an extended player state
        if self.animation_lock['jumping']:
            #ending the lock
            if int(self.vel.y) == 0:
                self.animation_index = 0
                self.animation_lock['jumping'] = False
                self.animation_lock['falling'] = True

            #stop the animation at this last frame
            if self.image == self.images[-1]:
                return
        #jump
        if int(self.vel.y) < 0: 
            self.images = self.jump_left if self.facing_left else self.jump_right

        #walk
        if int(self.vel.x) > 0 and not self.falling:
            self.images = self.walk_right
        elif int(self.vel.x) < 0 and not self.falling:
            self.images = self.walk_left

        #idle
        if int(self.vel.x) == 0 and self.facing_right and not self.falling:
            self.images = self.idle_right
        if int(self.vel.x) == 0 and self.facing_left and not self.falling:
            self.images = self.idle_left

        #jump
        if int(self.vel.y) < 0: 
            self.images = self.jump_left if self.facing_left else self.jump_right
        #fall
        if int(self.vel.y) > 0:
            self.images = self.fall_left if self.facing_left else self.fall_right

        self.current_frame += 1
        #currently just jumping and falling

        #non-locking animation
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

            self.falling = False
            self.can_jump = True
            self.animation_lock['falling'] = False

        #animation
        self.animation_update()

    def jump(self):
        self.can_jump = False
        self.falling = True
        self.animation_lock['jumping'] = True
        self.vel.y = -15

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
#---- player walk
player_walk_left = load_images(path='sprites/player/walk')
player_walk_right = [pygame.transform.flip(image, True, False) for image in player_walk_left] 
#---- player jump todo: this is special because there are two locking frames: the jump peak and the jump falling frame
player_jump_left = load_images(path='sprites/player/jump')
player_jump_right = [pygame.transform.flip(image, True, False) for image in player_jump_left] 
#---- player jump todo: this is special because there are two locking frames: the jump peak and the jump falling frame
player_fall_left = load_images(path='sprites/player/fall')
player_fall_right = [pygame.transform.flip(image, True, False) for image in player_fall_left] 


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
            if event.key == pygame.K_SPACE and P1.can_jump:
                #make sure to start the animation at the start
                P1.animation_index = 0
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










