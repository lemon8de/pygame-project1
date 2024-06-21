import sys
import pygame
import os
import random
from pygame.locals import *

pygame.init()
vec = pygame.math.Vector2
HEIGHT = 700
WIDTH = 1200
ACC = 1.0
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
        size = (160, 224)

        #initial state
        position = (250,680)
        self.rect = pygame.Rect((position),size)
        self.pos = vec((position))
        self.vel = vec(0,0)
        self.accel = vec(0,0)

        #player states
        self.facing_right = True
        self.facing_left = False
        self.can_jump = False
        self.started_falling = False #used by the falling animation to figure out if the peak height of the jump is reached
        self.falling = True #used by animations other than jump to prioritize the jumping sprite sheet
        self.backdashed_ground = False

        #used by some animations that should hold its last frame
        #example a very long jump, a very long fall
        self.animation_lock = {
            'jumping' : False,
            'falling' : False,
            'left_movement' : False,
            'right_movement' : False,
            'in_backdash' : False
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
        self.backdg_left = player_backdg_left
        self.backdg_right = player_backdg_right

        #initialize the state of the player,
        self.animation_index = 0
        self.image = player_idle_right[self.animation_index]
        self.images = self.idle_right

        self.animation_frames = 6 #speed
        self.current_frame = 0

    def move(self):
        self.acc = vec(0,0.8) #gravity
        pressed_keys = pygame.key.get_pressed()

        if pressed_keys[K_LEFT] and not self.animation_lock['left_movement']:
            self.acc.x = -ACC
            self.facing_left = True
            self.facing_right = False
        if pressed_keys[K_RIGHT] and not self.animation_lock['right_movement']:
            self.acc.x = ACC
            self.facing_right = True
            self.facing_left = False
        if pressed_keys[K_z] and not self.backdashed_ground and not self.falling:
            self.backdashed_ground = True
            self.animation_lock['right_movement'] = True
            self.animation_lock['right_movement'] = True

            self.can_jump = False
            self.falling = True
            self.vel.y = -10 #jump value
            self.acc = vec(30,0.8) if self.facing_left else vec(-30,0.8)
            self.animation_index = 0
            self.animation_lock['in_backdash'] = True

        self.acc.x += self.vel.x * FRIC
        self.vel += self.acc
        movement_delta = self.vel + 0.5 * self.acc

        #save the old position of the current frame
        old_pos = self.pos

        #move the character
        new_pos = self.pos + movement_delta
        self.pos = new_pos

        #find how much change on player position
        delta_pos = new_pos - old_pos

        #out of bounds positional reset to the other side
        '''
        if self.pos.x > WIDTH:
            self.pos.x = 0
        if self.pos.x < 0:
            self.pos.x = WIDTH
        '''

        #don't know what this is
        self.rect.midbottom = self.pos

        #well if you include delta pos x, the platform will keep falling and the character will keep falling lol
        return delta_pos 

    def animation_update(self):

        #get some velocity values to figure out what animations to run
        vel_x = int(self.vel.x)
        vel_y = int(self.vel.y)

        #walk animation
        if vel_x > 0 and not self.falling:
            self.images = self.walk_right

        elif vel_x < 0 and not self.falling:
            self.images = self.walk_left

        #idle animation
        if vel_x == 0 and self.facing_right and not self.falling:
            self.images = self.idle_right

        if vel_x == 0 and self.facing_left and not self.falling:
            self.images = self.idle_left

        #jump animation
        if vel_y < 0: 
            if self.animation_lock['jumping'] and (self.images == self.jump_left or self.images == self.jump_right):
                #stop the animation at this last frame
                if self.image == self.images[-1]:
                    return
            self.images = self.jump_left if self.facing_left else self.jump_right

        #falling animation
        #this if statement means that the jump velocity is now zero, we should play falling animations now
        if vel_y >= 0 and self.falling and not self.animation_lock['in_backdash']:
            if not self.started_falling:
                #the animation_index seems to be a continous number being appended, this is an issue if you want to run a fresh sprite sheet
                self.animation_index = 0
                self.started_falling = True
                self.animation_lock['jumping'] = False
                self.animation_lock['falling'] = True

            self.images = self.fall_left if self.facing_left else self.fall_right
            if self.animation_lock['falling'] and (self.images == self.fall_left or self.images == self.fall_right):
                #stop the animation at this last frame
                if self.image == self.images[-1]:
                    return

        if self.backdashed_ground:
            self.images = self.backdg_right if self.facing_left else self.backdg_left
            if self.animation_lock['in_backdash'] and (self.images == self.backdg_left or self.images == self.backdg_right):
                if self.image == self.images[-1]:
                    return


        #regular animation
        self.current_frame += 1
        if self.current_frame >= self.animation_frames:
            self.current_frame = 0
            self.animation_index = (self.animation_index + 1) % len(self.images)
            self.image = self.images[self.animation_index]

    def update(self):
        #landed on the ground
        hits = pygame.sprite.spritecollide(P1, platform_sprites, False)
        self.falling = True
        for collision in hits:
            if collision.below:
                self.falling = False
                self.pos.y = hits[0].rect.top + 1
                self.vel.y = 0 

                #reset player states
                self.falling = False
                self.can_jump = True
                self.animation_lock['falling'] = False
                self.started_falling = False
                self.animation_lock['right_movement'] = False
                self.animation_lock['left_movement'] = False
                self.animation_lock['in_backdash'] = False

                #remove the accel from the backdash
                self.backdashed_ground = False
                self.acc = (0,0.8)

        #animation
        self.animation_update()

    def jump(self):
        self.can_jump = False
        self.falling = True
        self.animation_lock['jumping'] = True
        self.vel.y = -20 #jump value

class platform(pygame.sprite.Sprite):
    def __init__(self, surf_xy, center_xy):
        super().__init__()
        #self.surf = pygame.Surface((WIDTH, 20))
        self.surf = pygame.Surface(surf_xy)
        self.surf.fill((255,0,0))
        self.center_pos = vec(center_xy)
        #self.rect = self.surf.get_rect(center = (WIDTH/2, HEIGHT - 10))
        self.rect = self.surf.get_rect(center = center_xy)
        self.above = False
        self.below = True

    def camera_move(self, player_movement):
        #restrict camera movement to x
        self.center_pos.x -= player_movement.x * 1.2
        self.rect = self.surf.get_rect(center = self.center_pos)


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
#---- player backdash
player_backdg_right = load_images(path='sprites/player/backdash_ground')
player_backdg_left = [pygame.transform.flip(image, True, False) for image in player_backdg_right] 


PT1 = platform(surf_xy =(WIDTH, 20), center_xy = (WIDTH/2, HEIGHT - 10))
PT2 = platform(surf_xy =(WIDTH/4, 20), center_xy = (750, 550))
PT3 = platform(surf_xy =(WIDTH/5, 20), center_xy = (950, 150))
all_entities = pygame.sprite.Group()
all_entities.add(PT1)
all_entities.add(PT2)
all_entities.add(PT3)
P1 = Player()

#TODO: this thing does not have to be grouped
player_sprite = pygame.sprite.Group()
player_sprite.add(P1)

platform_sprites = pygame.sprite.Group()
platform_sprites.add(PT1)
platform_sprites.add(PT2)
platform_sprites.add(PT3)

#im so sorry, but this is shit
platforms_spawned = 0
#platform spawning distance check
platforms_dcheck = 300

while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

        #idk why this is here
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and P1.can_jump:
                #make sure to start the animation at the start
                P1.animation_index = 0
                if P1.facing_right:
                    P1.animation_lock['left_movement'] = True
                    P1.animation_lock['right_movement'] = False
                if P1.facing_left:
                    P1.animation_lock['right_movement'] = True
                    P1.animation_lock['left_movement'] = False
                P1.jump()
        

    player_movement = P1.move()
    #print(player_movement)
    P1.update()

    #feels like this just blacks the screen for a redraw
    displaysurface.fill((0,0,0))

    #im so sorry
    #trying to spawn more platforms, emphasis on try
    should_spawn = int(P1.pos.x) > platforms_dcheck
    print(should_spawn)
    if should_spawn:
        platforms_dcheck += 300

        position = P1.pos.x + random.uniform(0.5, 1.5) * 500 #platform distance from the player

        new_platform = platform(surf_xy =(random.randint(300, 700), 20), center_xy = (position, random.randint(300, 700)))
        all_entities.add(new_platform)
        platform_sprites.add(new_platform)


    #trying to move the platforms, some type of camera movement
    for entity in all_entities:
        entity.camera_move(player_movement)

    #we have to use blit on platform_sprites because it has no image yet
    for entity in platform_sprites:
        if entity.center_pos.y < P1.pos.y:
            entity.surf.fill((0,255,0))
            entity.above = True
            entity.below = False
        else:
            entity.surf.fill((255,0,0))
            entity.above = False
            entity.below = True

        displaysurface.blit(entity.surf, entity.rect)

    #draw runs like it wants images
    player_sprite.draw(displaysurface)
    
    pygame.display.update()
    FramePerSec.tick(FPS)










