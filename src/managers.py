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
            cls._instance.fonts = {} 
            cls._instance.explosion_frames = [] 
            
            pygame.mixer.init()
            cls._instance.bgm_playing = True 
            cls._instance.bgm_volume = 0.2 # ระดับเสียงเริ่มต้นที่ 20%
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

    def play_bgm(self, path):
        try:
            pygame.mixer.music.load(path)
            pygame.mixer.music.set_volume(self.bgm_volume) 
            pygame.mixer.music.play(-1) 
        except Exception as e:
            print(f"⚠️ โหลด BGM ไม่ได้: {e}")

    def toggle_bgm(self):
        if self.bgm_playing:
            pygame.mixer.music.pause()
            self.bgm_playing = False
        else:
            pygame.mixer.music.unpause()
            self.bgm_playing = True
        return self.bgm_playing

    # --- ฟังก์ชันใหม่: ปรับระดับเสียง ---
    def change_volume(self, amount):
        self.bgm_volume += amount
        self.bgm_volume = max(0.0, min(1.0, self.bgm_volume)) # ล็อกไว้ไม่ให้ต่ำกว่า 0 หรือเกิน 100%
        pygame.mixer.music.set_volume(self.bgm_volume)
        return self.bgm_volume

    def load_explosion_frames(self):
        if self.explosion_frames:
            return self.explosion_frames
        
        explosion_frame_files = [f'assets/images/fire0{i}.png' for i in range(10)]
        for frame_file in explosion_frame_files:
            try:
                img = pygame.image.load(frame_file).convert_alpha()
                img = pygame.transform.scale(img, (70, 70))
                self.explosion_frames.append(img)
            except Exception as e:
                print(f"⚠️ โหลดเฟรมระเบิดไม่ได้ {frame_file}: {e}")
                surf = pygame.Surface((70, 70))
                surf.fill((255, 0, 0))
                self.explosion_frames.append(surf)
        return self.explosion_frames

class CollisionManager:
    def __init__(self, player, meteors, lasers, powerups, enemies, enemy_lasers, all_sprites):
        self.player = player
        self.meteors = meteors
        self.lasers = lasers
        self.powerups = powerups
        self.enemies = enemies
        self.enemy_lasers = enemy_lasers
        self.all_sprites = all_sprites

    def check(self):
        hits = pygame.sprite.groupcollide(self.meteors, self.lasers, False, True)
        for meteor, laser_list in hits.items():
            meteor.hp -= len(laser_list)
            if meteor.hp <= 0:
                meteor.kill()
                pygame.event.post(pygame.event.Event(EVENT_METEOR_DESTROYED))
                ResourceManager().play_sound('explosion', 'assets/sounds/explosion.ogg')
                
                from src.entities import Explosion
                frames = ResourceManager().load_explosion_frames()
                self.all_sprites.add(Explosion(meteor.rect.center, frames))

        enemy_hits = pygame.sprite.groupcollide(self.enemies, self.lasers, False, True)
        for enemy, laser_list in enemy_hits.items():
            enemy.hp -= len(laser_list)
            if enemy.hp <= 0:
                enemy.kill()
                pygame.event.post(pygame.event.Event(EVENT_ENEMY_DESTROYED))
                ResourceManager().play_sound('explosion', 'assets/sounds/explosion.ogg')
                
                from src.entities import Explosion
                frames = ResourceManager().load_explosion_frames()
                self.all_sprites.add(Explosion(enemy.rect.center, frames))

        if pygame.sprite.spritecollide(self.player, self.meteors, True) or \
           pygame.sprite.spritecollide(self.player, self.enemies, True) or \
           pygame.sprite.spritecollide(self.player, self.enemy_lasers, True):
            pygame.event.post(pygame.event.Event(EVENT_PLAYER_HIT))
            
            from src.entities import Explosion
            frames = ResourceManager().load_explosion_frames()
            self.all_sprites.add(Explosion(self.player.rect.center, frames))

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