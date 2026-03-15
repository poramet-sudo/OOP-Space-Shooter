import pygame
import sys
from src.config import *
from src.managers import ResourceManager, CollisionManager, GameState
from src.entities import Player, MeteorFactory, PowerUp

class PlayState(GameState):
    def __init__(self, game_app):
        self.app = game_app
        self.all_sprites = pygame.sprite.Group()
        self.meteors = pygame.sprite.Group()
        self.lasers = pygame.sprite.Group()
        self.powerups = pygame.sprite.Group() # Group สำหรับยาเพิ่มเลือด
        
        self.player = Player()
        self.all_sprites.add(self.player)
        
        self.collision_mgr = CollisionManager(self.player, self.meteors, self.lasers, self.powerups)
        self.score = 0
        self.font = pygame.font.Font(None, 36)

        # โหลดภาพพื้นหลัง
        self.bg_image = ResourceManager().get_image('bg', 'assets/images/bg.png', (SCREEN_WIDTH, SCREEN_HEIGHT), (20, 20, 40))

        # ตั้งเวลาปล่อยของ
        self.SPAWN_METEOR_TIMER = pygame.USEREVENT + 10
        self.SPAWN_POWERUP_TIMER = pygame.USEREVENT + 11
        pygame.time.set_timer(self.SPAWN_METEOR_TIMER, 1000)
        pygame.time.set_timer(self.SPAWN_POWERUP_TIMER, 8000) # ยาตกทุกๆ 8 วินาที

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                self.player.shoot(self.all_sprites, self.lasers)
            
            # ปล่อยอุกกาบาตและยา
            elif event.type == self.SPAWN_METEOR_TIMER:
                meteor = MeteorFactory.spawn()
                self.all_sprites.add(meteor)
                self.meteors.add(meteor)
            elif event.type == self.SPAWN_POWERUP_TIMER:
                heal_item = PowerUp()
                self.all_sprites.add(heal_item)
                self.powerups.add(heal_item)

            # รับ Event จากระบบชน
            elif event.type == EVENT_METEOR_DESTROYED:
                self.score += 10
            elif event.type == EVENT_PLAYER_HIT:
                self.player.take_damage()
                if self.player.get_hp() <= 0:
                    print(f"Game Over! Score: {self.score}")
                    self.app.running = False
            elif event.type == EVENT_POWERUP_COLLECTED:
                self.player.heal() # เรียกเมธอดฮีล

    def update(self):
        self.all_sprites.update()
        self.collision_mgr.check()

    def draw(self, screen):
        # วาดพื้นหลังอวกาศ
        screen.blit(self.bg_image, (0, 0))
        self.all_sprites.draw(screen)
        
        score_txt = self.font.render(f'Score: {self.score}', True, (255, 255, 255))
        hp_txt = self.font.render(f'HP: {self.player.get_hp()}', True, (100, 255, 100))
        screen.blit(score_txt, (10, 10))
        screen.blit(hp_txt, (SCREEN_WIDTH - 100, 10))

class GameApp:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Meteor Striker (20 Pointers)")
        self.clock = pygame.time.Clock()
        self.running = True
        
        # ปิดเสียง BGM ไว้ก่อน ถ้ามีไฟล์แล้วค่อยเอา '#' ออก
        # ResourceManager().play_sound('bgm', 'assets/sounds/bgm.mp3')
        
        self.current_state = PlayState(self)

    def run(self):
        while self.running:
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    self.running = False

            self.current_state.handle_events(events)
            self.current_state.update()
            self.current_state.draw(self.screen)

            pygame.display.flip()
            self.clock.tick(FPS)
            
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    app = GameApp()
    app.run()