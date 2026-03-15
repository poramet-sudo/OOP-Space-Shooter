import pygame
import random
from src.managers import ResourceManager
from src.config import *

class ShooterMixin:
    def shoot(self, all_sprites, laser_group):
        laser = Laser(self.rect.centerx, self.rect.top)
        all_sprites.add(laser)
        laser_group.add(laser)
        ResourceManager().play_sound('laser', 'assets/sounds/laser.ogg')

class Player(pygame.sprite.Sprite, ShooterMixin):
    def __init__(self):
        super().__init__()
        self.image = ResourceManager().get_image('player', 'assets/images/ship.png', (60, 50), (0, 255, 0))
        self.rect = self.image.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT - 60))
        self.speed = 6
        self.__hp = 3

    def get_hp(self): return self.__hp
    def take_damage(self): self.__hp -= 1
    
    # เพิ่มเมธอดสำหรับฮีลเลือด (Encapsulation)
    def heal(self): 
        if self.__hp < 5: # จำกัดเลือดสูงสุดที่ 5
            self.__hp += 1

    def update(self):
        keys = pygame.key.get_pressed()
        # เคลื่อนที่ 4 ทิศทาง พร้อมจำกัดขอบหน้าจอ
        if keys[pygame.K_LEFT] and self.rect.left > 0: self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] and self.rect.right < SCREEN_WIDTH: self.rect.x += self.speed
        if keys[pygame.K_UP] and self.rect.top > 0: self.rect.y -= self.speed
        if keys[pygame.K_DOWN] and self.rect.bottom < SCREEN_HEIGHT: self.rect.y += self.speed

class Laser(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = ResourceManager().get_image('laser', 'assets/images/laser.png', (5, 20), (255, 255, 0))
        self.rect = self.image.get_rect(midbottom=(x, y))
        self.speed = -10

    def update(self):
        self.rect.y += self.speed
        if self.rect.bottom < 0: self.kill()

class Meteor(pygame.sprite.Sprite):
    def __init__(self, x, y, speed, size, hp):
        super().__init__()
        self.image = ResourceManager().get_image(f'meteor_{size[0]}', 'assets/images/meteor.png', size, (150, 75, 0))
        self.rect = self.image.get_rect(topleft=(x, y))
        self.speed = speed
        self.hp = hp # เพิ่มระบบเลือดให้อุกกาบาต

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > SCREEN_HEIGHT: self.kill()

class MeteorFactory:
    @staticmethod
    def spawn():
        x = random.randint(0, SCREEN_WIDTH - 60)
        y = random.randint(-100, -40)
        
        # อุกกาบาตใหญ่ (เลือด 3) / อุกกาบาตเล็ก (เลือด 1)
        if random.random() < 0.3:
            return Meteor(x, y, speed=random.randint(6, 9), size=(30, 30), hp=1) # ลูกเล็ก เร็ว เลือดน้อย
        else:
            return Meteor(x, y, speed=random.randint(2, 4), size=(80, 80), hp=3) # ลูกใหญ่ ช้า เลือดเยอะ

# คลาสใหม่: ไอเทมเพิ่มเลือด
class PowerUp(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = ResourceManager().get_image('heal', 'assets/images/heal.png', (25, 25), (0, 255, 0))
        self.rect = self.image.get_rect(topleft=(random.randint(0, SCREEN_WIDTH-25), -50))
        self.speed = 3

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > SCREEN_HEIGHT: self.kill()