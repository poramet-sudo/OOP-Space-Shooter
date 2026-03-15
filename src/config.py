import pygame

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Custom Events (Observer Pattern)
EVENT_METEOR_DESTROYED = pygame.USEREVENT + 1
EVENT_PLAYER_HIT = pygame.USEREVENT + 2
EVENT_POWERUP_COLLECTED = pygame.USEREVENT + 3 # เพิ่ม Event สำหรับเก็บยา