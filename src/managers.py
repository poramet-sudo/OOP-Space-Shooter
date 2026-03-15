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
            cls._instance.fonts = {} # เพิ่มการเก็บ Font
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

    def get_font(self, path, size):
        key = f"{path}_{size}"
        if key not in self.fonts:
            try:
                self.fonts[key] = pygame.font.Font(path, size)
            except:
                self.fonts[key] = pygame.font.Font(None, size)
        return self.fonts[key]

    def play_sound(self, name, path):
        if name not in self.sounds:
            try:
                self.sounds[name] = pygame.mixer.Sound(path)
            except:
                self.sounds[name] = None 
        if self.sounds[name]:
            self.sounds[name].play()

class CollisionManager:
    def __init__(self, player, meteors, lasers, powerups, enemies, enemy_lasers):
        self.player = player
        self.meteors = meteors
        self.lasers = lasers
        self.powerups = powerups
        self.enemies = enemies
        self.enemy_lasers = enemy_lasers

    def check(self):
        hits = pygame.sprite.groupcollide(self.meteors, self.lasers, False, True)
        for meteor, laser_list in hits.items():
            meteor.hp -= len(laser_list)
            if meteor.hp <= 0:
                meteor.kill()
                pygame.event.post(pygame.event.Event(EVENT_METEOR_DESTROYED))
                ResourceManager().play_sound('explosion', 'assets/sounds/explosion.ogg')

        enemy_hits = pygame.sprite.groupcollide(self.enemies, self.lasers, False, True)
        for enemy, laser_list in enemy_hits.items():
            enemy.hp -= len(laser_list)
            if enemy.hp <= 0:
                enemy.kill()
                pygame.event.post(pygame.event.Event(EVENT_ENEMY_DESTROYED))
                ResourceManager().play_sound('explosion', 'assets/sounds/explosion.ogg')

        if pygame.sprite.spritecollide(self.player, self.meteors, True) or \
           pygame.sprite.spritecollide(self.player, self.enemies, True) or \
           pygame.sprite.spritecollide(self.player, self.enemy_lasers, True):
            pygame.event.post(pygame.event.Event(EVENT_PLAYER_HIT))

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