import pygame
import os
from src.config import *
from abc import ABC, abstractmethod

class ResourceManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.images = {}
            cls._instance.sounds = {}
            pygame.mixer.init()
        return cls._instance

    def get_image(self, name, path, size, fallback_color):
        if name not in self.images:
            try:
                img = pygame.image.load(path).convert_alpha()
                self.images[name] = pygame.transform.scale(img, size)
            except:
                surf = pygame.Surface(size)
                surf.fill(fallback_color)
                self.images[name] = surf
        return self.images[name]

    def play_sound(self, name, path):
        if name not in self.sounds:
            try:
                self.sounds[name] = pygame.mixer.Sound(path)
            except Exception as e:
                print(f"⚠️ โหลดเสียง {name} ไม่ได้: {e}")
                self.sounds[name] = None 
        
        if self.sounds[name]:
            self.sounds[name].play()

class CollisionManager:
    def __init__(self, player, meteors, lasers, powerups):
        self.player = player
        self.meteors = meteors
        self.lasers = lasers
        self.powerups = powerups # รับกลุ่มไอเทมเข้ามาตรวจการชน

    def check(self):
        # 1. เลเซอร์ ชน อุกกาบาต (ปรับให้ลดเลือดก่อนค่อยตาย)
        hits = pygame.sprite.groupcollide(self.meteors, self.lasers, False, True)
        for meteor, laser_list in hits.items():
            meteor.hp -= len(laser_list) # โดนยิงกี่นัดก็ลดเลือดตามนั้น
            if meteor.hp <= 0:
                meteor.kill()
                pygame.event.post(pygame.event.Event(EVENT_METEOR_DESTROYED))
                ResourceManager().play_sound('explosion', 'assets/sounds/explosion.ogg')

        # 2. อุกกาบาต ชน ผู้เล่น
        if pygame.sprite.spritecollide(self.player, self.meteors, True):
            pygame.event.post(pygame.event.Event(EVENT_PLAYER_HIT))
            ResourceManager().play_sound('explosion', 'assets/sounds/explosion.ogg')

        # 3. ผู้เล่น ชน ยาเพิ่มเลือด
        if pygame.sprite.spritecollide(self.player, self.powerups, True):
            pygame.event.post(pygame.event.Event(EVENT_POWERUP_COLLECTED))
            ResourceManager().play_sound('heal', 'assets/sounds/heal.ogg')

class GameState(ABC):
    @abstractmethod
    def handle_events(self, events): pass
    @abstractmethod
    def update(self): pass
    @abstractmethod
    def draw(self, screen): pass