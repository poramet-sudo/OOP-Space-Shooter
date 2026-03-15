import pygame
import sys
from src.config import *
from src.managers import ResourceManager, CollisionManager, GameState
from src.entities import Player, MeteorFactory, PowerUp, EnemyShip, EnemyLaser, Button

class MainMenuState(GameState):
    def __init__(self, app):
        self.app = app
        self.font_title = ResourceManager().get_font('assets/fonts/font.ttf', 50)
        self.font_btn = ResourceManager().get_font('assets/fonts/font.ttf', 24)
        # หน้าเมนูใช้พื้นหลัง bg1.png
        self.bg = ResourceManager().get_image('bg1', 'assets/images/bg1.png', (SCREEN_WIDTH, SCREEN_HEIGHT), (20, 20, 40))
        
        self.btn_play = Button(SCREEN_WIDTH//2, 250, 'assets/images/ui/button.png', "PLAY GAME", self.font_btn)
        self.btn_skin = Button(SCREEN_WIDTH//2, 330, 'assets/images/ui/button.png', "SKINS", self.font_btn)
        self.btn_level = Button(SCREEN_WIDTH//2, 410, 'assets/images/ui/button.png', "LEVELS", self.font_btn)

    def handle_events(self, events):
        for event in events:
            if self.btn_play.is_clicked(event):
                self.app.change_state(PlayState(self.app))
            elif self.btn_skin.is_clicked(event):
                self.app.change_state(SkinSelectState(self.app))
            elif self.btn_level.is_clicked(event):
                self.app.change_state(LevelSelectState(self.app))

    def update(self): pass

    def draw(self, screen):
        screen.blit(self.bg, (0, 0))
        title = self.font_title.render("SPACE SHOOTER", True, (255, 215, 0))
        screen.blit(title, title.get_rect(center=(SCREEN_WIDTH//2, 120)))
        
        self.btn_play.draw(screen)
        self.btn_skin.draw(screen)
        self.btn_level.draw(screen)

class SkinSelectState(GameState):
    def __init__(self, app):
        self.app = app
        self.font = ResourceManager().get_font('assets/fonts/font.ttf', 30)
        self.btn_font = ResourceManager().get_font('assets/fonts/font.ttf', 20)
        self.bg = ResourceManager().get_image('bg1', 'assets/images/bg1.png', (SCREEN_WIDTH, SCREEN_HEIGHT), (20, 20, 40))
        
        self.skins = ['assets/images/ships/ship1.png', 'assets/images/ships/ship2.png', 'assets/images/ships/ship3.png']
        self.buttons = []
        for i, skin in enumerate(self.skins):
            btn = Button(200 + (i*200), 300, 'assets/images/ui/button.png', f"SHIP {i+1}", self.btn_font, size=(120, 40))
            self.buttons.append((btn, skin))
            
        self.btn_back = Button(SCREEN_WIDTH//2, 500, 'assets/images/ui/button.png', "BACK", self.btn_font)

    def handle_events(self, events):
        for event in events:
            for btn, skin in self.buttons:
                if btn.is_clicked(event):
                    self.app.selected_skin = skin 
            if self.btn_back.is_clicked(event):
                self.app.change_state(MainMenuState(self.app))

    def update(self): pass

    def draw(self, screen):
        screen.blit(self.bg, (0, 0))
        title = self.font.render(f"CURRENT SKIN: SHIP {self.skins.index(self.app.selected_skin)+1}", True, (255, 215, 0))
        screen.blit(title, title.get_rect(center=(SCREEN_WIDTH//2, 100)))
        
        for btn, skin in self.buttons:
            btn.draw(screen)
            img = ResourceManager().get_image(skin, skin, (60, 50), (255,255,255))
            screen.blit(img, img.get_rect(center=(btn.rect.centerx, btn.rect.top - 40)))
            
        self.btn_back.draw(screen)

class LevelSelectState(GameState):
    def __init__(self, app):
        self.app = app
        self.font = ResourceManager().get_font('assets/fonts/font.ttf', 40)
        self.btn_font = ResourceManager().get_font('assets/fonts/font.ttf', 20)
        self.bg = ResourceManager().get_image('bg1', 'assets/images/bg1.png', (SCREEN_WIDTH, SCREEN_HEIGHT), (20, 20, 40))
        
        self.buttons = []
        for i in range(5):
            x = 150 + (i % 3) * 250
            y = 250 + (i // 3) * 120
            is_unlocked = (i + 1) <= self.app.unlocked_levels
            img_path = 'assets/images/ui/button.png' if is_unlocked else 'assets/images/ui/button_locked.png'
            text = f"LEVEL {i+1}" if is_unlocked else "LOCKED"
            btn = Button(x, y, img_path, text, self.btn_font, size=(150, 50))
            self.buttons.append((btn, i + 1, is_unlocked))
            
        self.btn_back = Button(SCREEN_WIDTH//2, 520, 'assets/images/ui/button.png', "BACK", self.btn_font)

    def handle_events(self, events):
        for event in events:
            for btn, lvl, is_unlocked in self.buttons:
                if btn.is_clicked(event) and is_unlocked:
                    self.app.current_level = lvl
                    self.app.change_state(PlayState(self.app))
            if self.btn_back.is_clicked(event):
                self.app.change_state(MainMenuState(self.app))

    def update(self): pass

    def draw(self, screen):
        screen.blit(self.bg, (0, 0))
        title = self.font.render("SELECT LEVEL", True, (255, 215, 0))
        screen.blit(title, title.get_rect(center=(SCREEN_WIDTH//2, 100)))
        for btn, _, _ in self.buttons:
            btn.draw(screen)
        self.btn_back.draw(screen)

class GameOverState(GameState):
    def __init__(self, app, score, is_victory=False):
        self.app = app
        self.score = score
        self.is_victory = is_victory
        self.font_big = ResourceManager().get_font('assets/fonts/font.ttf', 60)
        self.font_small = ResourceManager().get_font('assets/fonts/font.ttf', 30)
        self.font_btn = ResourceManager().get_font('assets/fonts/font.ttf', 20) 
        
        self.bg = ResourceManager().get_image('bg1', 'assets/images/bg1.png', (SCREEN_WIDTH, SCREEN_HEIGHT), (20, 20, 40))
        
        self.btn_next = None
        if self.is_victory and self.app.current_level < 5:
            self.btn_next = Button(SCREEN_WIDTH//2, 340, 'assets/images/ui/button.png', "NEXT LEVEL", self.font_btn, size=(220, 50))
            
        self.btn_restart = Button(SCREEN_WIDTH//2, 420, 'assets/images/ui/button.png', "REPLAY LEVEL", self.font_btn, size=(220, 50))
        self.btn_menu = Button(SCREEN_WIDTH//2, 500, 'assets/images/ui/button.png', "MAIN MENU", self.font_btn, size=(220, 50))

    def handle_events(self, events):
        for event in events:
            if self.btn_next and self.btn_next.is_clicked(event):
                self.app.current_level += 1
                self.app.change_state(PlayState(self.app))
            elif self.btn_restart.is_clicked(event):
                self.app.change_state(PlayState(self.app))
            elif self.btn_menu.is_clicked(event):
                self.app.change_state(MainMenuState(self.app))

    def update(self): pass

    def draw(self, screen):
        screen.blit(self.bg, (0, 0))
        msg = "LEVEL CLEARED!" if self.is_victory else "GAME OVER"
        color = (0, 255, 0) if self.is_victory else (255, 0, 0)
        
        title = self.font_big.render(msg, True, color)
        score_txt = self.font_small.render(f"SCORE: {self.score}", True, (255, 215, 0))
        
        screen.blit(title, title.get_rect(center=(SCREEN_WIDTH//2, 150)))
        screen.blit(score_txt, score_txt.get_rect(center=(SCREEN_WIDTH//2, 250)))
        
        if self.btn_next:
            self.btn_next.draw(screen)
        self.btn_restart.draw(screen)
        self.btn_menu.draw(screen)

class PlayState(GameState):
    def __init__(self, game_app):
        self.app = game_app
        self.all_sprites = pygame.sprite.Group()
        self.meteors = pygame.sprite.Group()
        self.lasers = pygame.sprite.Group()
        self.powerups = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.enemy_lasers = pygame.sprite.Group()
        
        self.player = Player(self.app.selected_skin)
        self.all_sprites.add(self.player)
        
        self.collision_mgr = CollisionManager(
            self.player, self.meteors, self.lasers, self.powerups, self.enemies, self.enemy_lasers
        )
        self.score = 0
        self.font = ResourceManager().get_font('assets/fonts/font.ttf', 24)
        
        bg_name = f'bg{self.app.current_level}'
        bg_path = f'assets/images/{bg_name}.png'
        self.bg_image = ResourceManager().get_image(bg_name, bg_path, (SCREEN_WIDTH, SCREEN_HEIGHT), (20, 20, 40))

        level_mult = self.app.current_level
        self.target_score = LEVEL_TARGETS[level_mult - 1]
        
        self.SPAWN_METEOR_TIMER = pygame.USEREVENT + 10
        self.SPAWN_POWERUP_TIMER = pygame.USEREVENT + 11
        self.SPAWN_ENEMY_TIMER = pygame.USEREVENT + 12
        
        pygame.time.set_timer(self.SPAWN_METEOR_TIMER, max(300, 1500 - (level_mult * 200)))
        
        # --- 💊 อัปเกรดยา: เลเวลสูง ยิ่งดรอปไวขึ้น ---
        # เลเวล 1: ดรอปทุกๆ ~10 วินาที
        # เลเวล 5: ดรอปทุกๆ ~6 วินาที
        powerup_delay = max(5000, 11000 - (level_mult * 1000))
        pygame.time.set_timer(self.SPAWN_POWERUP_TIMER, powerup_delay)
        
        pygame.time.set_timer(self.SPAWN_ENEMY_TIMER, max(800, 3000 - (level_mult * 400)))

    def handle_events(self, events):
        for event in events:
            if (event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE) or \
               (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1):
                self.player.fire(self.all_sprites, self.lasers)
            
            elif event.type == self.SPAWN_METEOR_TIMER:
                meteor = MeteorFactory.spawn(self.app.current_level) 
                self.all_sprites.add(meteor)
                self.meteors.add(meteor)
            elif event.type == self.SPAWN_POWERUP_TIMER:
                heal_item = PowerUp()
                self.all_sprites.add(heal_item)
                self.powerups.add(heal_item)
            elif event.type == self.SPAWN_ENEMY_TIMER:
                import random
                enemy = EnemyShip(random.randint(50, SCREEN_WIDTH-50), -50, self.player, self.app.current_level)
                self.all_sprites.add(enemy)
                self.enemies.add(enemy)

            elif event.type == EVENT_ENEMY_SHOOT:
                e_laser = EnemyLaser(event.x, event.y, event.angle) 
                self.all_sprites.add(e_laser)
                self.enemy_lasers.add(e_laser)

            elif event.type == EVENT_METEOR_DESTROYED:
                self.score += 10
                self.check_level_clear()
            elif event.type == EVENT_ENEMY_DESTROYED:
                self.score += 20 
                self.check_level_clear()

            elif event.type == EVENT_PLAYER_HIT:
                self.player.take_damage() 
                if self.player.get_hp() <= 0:
                    self.app.change_state(GameOverState(self.app, self.score, is_victory=False))
                    
            elif event.type == EVENT_POWERUP_COLLECTED:
                self.player.heal()

    def check_level_clear(self):
        if self.score >= self.target_score:
            if self.app.current_level == self.app.unlocked_levels and self.app.unlocked_levels < 5:
                self.app.unlocked_levels += 1
            self.app.change_state(GameOverState(self.app, self.score, is_victory=True))

    def update(self):
        self.all_sprites.update()
        self.collision_mgr.check()

    def draw(self, screen):
        screen.blit(self.bg_image, (0, 0))
        self.all_sprites.draw(screen)
        
        level_txt = self.font.render(f'LEVEL: {self.app.current_level}', True, (0, 255, 255)) 
        score_txt = self.font.render(f'SCORE: {self.score} / {self.target_score}', True, (255, 215, 0)) 
        hp_txt = self.font.render(f'HP: {self.player.get_hp()}', True, (50, 255, 50)) 
        
        screen.blit(level_txt, (10, 10))
        screen.blit(score_txt, (10, 40))
        screen.blit(hp_txt, (SCREEN_WIDTH - 150, 10))

class GameApp:
    def __init__(self):
        pygame.init()
        # --- เปลี่ยนโหมดเป็น RESIZABLE เพื่อเรียกขอบหน้าต่างและปุ่ม 3 ปุ่มกลับมา ---
        # เมื่อกดปุ่มสี่เหลี่ยม (Maximize) ระบบ SCALED จะขยายภาพให้เต็มจอโดยรักษาสัดส่วนไว้ให้เอง
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE | pygame.SCALED)
        pygame.display.set_caption("OOP Space Shooter (20 Pointers Project)")
        self.clock = pygame.time.Clock()
        self.running = True
        
        self.unlocked_levels = 1
        self.current_level = 1
        self.selected_skin = 'assets/images/ships/ship1.png'
        
        self.current_state = MainMenuState(self)

    def change_state(self, new_state):
        self.current_state = new_state

    def run(self):
        while self.running:
            events = pygame.event.get()
            for event in events:
                # ระบบจะจับการกดปุ่มกากบาท (Close) อัตโนมัติที่นี่
                if event.type == pygame.QUIT:
                    self.running = False
                
                # หากต้องการกด ESC เพื่อสลับโหมดเต็มจอ (กดซ้ำเพื่อย่อ/ขยาย) 
                # (เป็นลูกเล่นแถมให้ครับ นอกเหนือจากการกดปุ่มสี่เหลี่ยมด้วยเมาส์)
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    pygame.display.toggle_fullscreen()

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