import pygame
import random
import math
from src.managers import ResourceManager
from src.config import *

class Button:
    def __init__(self, x, y, image_path, text, font, size=(200, 50)):
        self.image = ResourceManager().get_image(f'btn_{image_path}', image_path, size, (100, 100, 100))
        self.rect = self.image.get_rect(center=(x, y))
        self.text = text
        self.font = font

    def draw(self, screen):
        screen.blit(self.image, self.rect)
        if self.text:
            txt_surf = self.font.render(self.text, True, (0, 0, 0))
            txt_rect = txt_surf.get_rect(center=self.rect.center)
            screen.blit(txt_surf, txt_rect)

    def is_clicked(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                return True
        return False

# --- คลาสใหม่: ปุ่มแบบรูปภาพ (ใช้ทำปุ่มลำโพง) ---
class IconButton:
    def __init__(self, x, y, image_path, size=(50, 50)):
        self.image_path = image_path
        self.size = size
        self.image = ResourceManager().get_image(image_path, image_path, size, (100, 100, 100))
        self.rect = self.image.get_rect(center=(x, y))

    def draw(self, screen):
        screen.blit(self.image, self.rect)

    def is_clicked(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                return True
        return False
        
    def change_image(self, new_image_path):
        self.image_path = new_image_path
        self.image = ResourceManager().get_image(new_image_path, new_image_path, self.size, (100, 100, 100))

class ShooterMixin:
    def shoot(self, all_sprites, laser_group, x, y, angle, laser_class):
        laser = laser_class(x, y, angle)
        all_sprites.add(laser)
        laser_group.add(laser)
        ResourceManager().play_sound('laser', 'assets/sounds/laser.ogg')

class Player(pygame.sprite.Sprite, ShooterMixin):
    def __init__(self, skin_path, bonus_hp=0): 
        super().__init__()
        self.original_image = ResourceManager().get_image('player', skin_path, (60, 50), (0, 255, 0))
        self.image = self.original_image
        self.rect = self.image.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT - 60))
        self.speed = 6
        self.__hp = 3 + bonus_hp 
        self.angle = 0 

    def get_hp(self): return self.__hp
    
    def take_damage(self): 
        self.__hp -= 1
        ResourceManager().play_sound('damage', 'assets/sounds/damage.ogg') 
        
    def heal(self): 
        self.__hp += 1

    def update(self):
        keys = pygame.key.get_pressed()
        if (keys[pygame.K_LEFT] or keys[pygame.K_a]) and self.rect.left > 0: self.rect.x -= self.speed
        if (keys[pygame.K_RIGHT] or keys[pygame.K_d]) and self.rect.right < SCREEN_WIDTH: self.rect.x += self.speed
        if (keys[pygame.K_UP] or keys[pygame.K_w]) and self.rect.top > 0: self.rect.y -= self.speed
        if (keys[pygame.K_DOWN] or keys[pygame.K_s]) and self.rect.bottom < SCREEN_HEIGHT: self.rect.y += self.speed

        mouse_x, mouse_y = pygame.mouse.get_pos()
        rel_x, rel_y = mouse_x - self.rect.centerx, mouse_y - self.rect.centery
        self.angle = (180 / math.pi) * -math.atan2(rel_y, rel_x) - 90
        
        self.image = pygame.transform.rotate(self.original_image, int(self.angle))
        self.rect = self.image.get_rect(center=self.rect.center)

    def fire(self, all_sprites, lasers):
        self.shoot(all_sprites, lasers, self.rect.centerx, self.rect.centery, self.angle, PlayerLaser)

class BaseLaser(pygame.sprite.Sprite):
    def __init__(self, x, y, angle, image_path, speed):
        super().__init__()
        img = ResourceManager().get_image('base_laser', image_path, (10, 30), (255, 255, 0))
        self.image = pygame.transform.rotate(img, angle)
        self.rect = self.image.get_rect(center=(x, y))
        
        rad = math.radians(angle + 90)
        self.dx = math.cos(rad) * speed
        self.dy = -math.sin(rad) * speed

    def update(self):
        self.rect.x += self.dx
        self.rect.y += self.dy
        if not (-50 < self.rect.x < SCREEN_WIDTH+50 and -50 < self.rect.y < SCREEN_HEIGHT+50): 
            self.kill()

class PlayerLaser(BaseLaser):
    def __init__(self, x, y, angle):
        super().__init__(x, y, angle, 'assets/images/laser.png', speed=12)

class EnemyLaser(BaseLaser):
    def __init__(self, x, y, angle):
        super().__init__(x, y, angle, 'assets/images/laserRed01.png', speed=7)

class EnemyShip(pygame.sprite.Sprite):
    def __init__(self, x, y, player, level): 
        super().__init__()
        colors = ['black', 'blue', 'green', 'red']
        chosen_color = random.choice(colors)
        img_path = f'assets/images/enemy_{chosen_color}.png'
        
        self.original_image = ResourceManager().get_image(f'enemy_{chosen_color}', img_path, (50, 50), (255, 0, 0))
        self.image = self.original_image
        self.rect = self.image.get_rect(center=(x, y))
        
        self.speed = random.randint(1 + (level // 2), 3 + (level // 2)) 
        self.hp = 1 + (level // 2)
        
        self.last_shot = pygame.time.get_ticks()
        self.shoot_delay = max(800, random.randint(1500, 3000) - (level * 200)) 
        self.player = player
        self.angle = 180

    def update(self):
        self.rect.y += self.speed 
        
        if self.player and self.player.alive():
            tracking_speed = max(1, self.speed // 2) 
            if self.rect.centerx < self.player.rect.centerx:
                self.rect.x += tracking_speed
            elif self.rect.centerx > self.player.rect.centerx:
                self.rect.x -= tracking_speed

            rel_x, rel_y = self.player.rect.centerx - self.rect.centerx, self.player.rect.centery - self.rect.centery
            self.angle = (180 / math.pi) * -math.atan2(rel_y, rel_x) - 90
            
        self.image = pygame.transform.rotate(self.original_image, int(self.angle))
        self.rect = self.image.get_rect(center=self.rect.center)
        
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shoot_delay:
            self.last_shot = now
            pygame.event.post(pygame.event.Event(EVENT_ENEMY_SHOOT, {'x': self.rect.centerx, 'y': self.rect.centery, 'angle': self.angle}))
            
        if self.rect.top > SCREEN_HEIGHT: 
            self.kill()

class Meteor(pygame.sprite.Sprite):
    def __init__(self, size, level):
        super().__init__()
        if size == 'big':
            self.image = ResourceManager().get_image('meteor_big', 'assets/images/meteor.png', (70, 70), (150, 75, 0))
            self.hp = 2 + (level // 2) 
            self.speed = random.randint(1, 2 + (level//2))
        else:
            self.image = ResourceManager().get_image('meteor_small', 'assets/images/meteor.png', (35, 35), (150, 75, 0))
            self.hp = 1
            self.speed = random.randint(3, 5 + level) 
            
        self.rect = self.image.get_rect(center=(random.randint(35, SCREEN_WIDTH-35), -50))

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()

class MeteorFactory:
    @staticmethod
    def spawn(level):
        return Meteor(random.choice(['big', 'small']), level)

class PowerUp(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = ResourceManager().get_image('powerup', 'assets/images/heal.png', (30, 30), (0, 255, 255))
        self.rect = self.image.get_rect(center=(random.randint(30, SCREEN_WIDTH-30), -50))
        self.speed = 3

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()

class Explosion(pygame.sprite.Sprite):
    def __init__(self, center, frames):
        super().__init__()
        self.frames = frames
        self.frame_index = 0
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect(center=center)
        self.last_update = pygame.time.get_ticks()
        self.frame_rate = 30 

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_rate:
            self.last_update = now
            self.frame_index += 1
            if self.frame_index >= len(self.frames):
                self.kill() 
            else:
                center = self.rect.center
                self.image = self.frames[self.frame_index]
                self.rect = self.image.get_rect(center=center)