# main.py
"""
Galaga Clone - 메인 게임 루프
"""
import pygame
import sys
import math
from typing import Optional
import settings
from assets_loader import AssetsLoader
from player import Player
from enemy import Enemy
from bullet import Bullet, TractorBeam
from wave_manager import WaveManager
from collision import *
from ui import UI
from effects import Explosion, EngineFlame, ScreenShake, FlashEffect
from powerup import PowerUp, PowerUpManager
from background import ScrollingBackground


class ComboSystem:
    """콤보 시스템 관리"""
    
    def __init__(self):
        self.combo_count = 0
        self.combo_timer = 0
        self.combo_timeout = 2000
        self.max_combo = 0
        self.total_combo_bonus = 0
    
    def add_kill(self) -> float:
        current_time = pygame.time.get_ticks()
        if current_time - self.combo_timer < self.combo_timeout:
            self.combo_count += 1
        else:
            self.combo_count = 1
        self.combo_timer = current_time
        if self.combo_count > self.max_combo:
            self.max_combo = self.combo_count
        return self.get_multiplier()
    
    def get_multiplier(self) -> float:
        if self.combo_count <= 1:
            return 1.0
        elif self.combo_count <= 5:
            return 1.5
        elif self.combo_count <= 10:
            return 2.0
        elif self.combo_count <= 20:
            return 3.0
        elif self.combo_count <= 50:
            return 4.0
        else:
            return 5.0
    
    def update(self) -> None:
        current_time = pygame.time.get_ticks()
        if self.combo_count > 0 and current_time - self.combo_timer >= self.combo_timeout:
            self.combo_count = 0
    
    def reset(self) -> None:
        self.combo_count = 0
        self.combo_timer = 0
        self.max_combo = 0
        self.total_combo_bonus = 0
    
    def is_active(self) -> bool:
        return self.combo_count >= 2


class NuclearBomb:
    """핵폭탄 이펙트"""
    
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y
        self.active = True
        self.start_time = pygame.time.get_ticks()
        self.duration = 1000
        self.max_radius = 800
    
    def update(self) -> None:
        elapsed = pygame.time.get_ticks() - self.start_time
        if elapsed >= self.duration:
            self.active = False
    
    def get_current_radius(self) -> int:
        elapsed = pygame.time.get_ticks() - self.start_time
        progress = elapsed / self.duration
        return int(self.max_radius * progress)
    
    def draw(self, surface: pygame.Surface) -> None:
        if not self.active:
            return
        radius = self.get_current_radius()
        elapsed = pygame.time.get_ticks() - self.start_time
        progress = elapsed / self.duration
        for i in range(3):
            r = radius - i * 50
            if r > 0:
                alpha = int(150 * (1 - progress))
                color = (255, 200 - i * 50, 0, alpha)
                explosion_surface = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
                pygame.draw.circle(explosion_surface, color, (r, r), r)
                rect = explosion_surface.get_rect(center=(self.x, self.y))
                surface.blit(explosion_surface, rect)


class Game:
    """메인 게임 클래스"""
    
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        self.screen = pygame.display.set_mode((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT))
        self.game_surface = pygame.Surface((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT))
        pygame.display.set_caption(settings.TITLE)
        self.clock = pygame.time.Clock()
        self.assets = AssetsLoader()
        self.ui = UI()
        self.background = ScrollingBackground()
        self.screen_shake = ScreenShake()
        self.flash_effect = FlashEffect()
        self.combo_system = ComboSystem()
        self.nuclear_bomb = None
        self.state = settings.STATE_MENU
        self.running = True
        self.selected_difficulty = 1
        self.difficulty_names = [settings.DIFFICULTY_EASY, settings.DIFFICULTY_NORMAL, settings.DIFFICULTY_HARD]
        self.score = 0
        self.high_score = self.load_high_score()
        self.high_score = self.load_high_score()
        self.ranking = self.load_ranking()
        self.show_name_input = False
        self.player_name = ""
        self.new_rank = -1
        self.all_sprites = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()
        self.tractor_beams = pygame.sprite.Group()
        self.explosions = pygame.sprite.Group()
        self.powerups = pygame.sprite.Group()
        self.player = None
        self.powerup_manager = PowerUpManager()
        self.powerup_message = ""
        self.powerup_message_time = 0
        self.powerup_message_duration = 1500
        self.combo_message = ""
        self.combo_message_time = 0
        self.combo_message_duration = 1000
        self.wave_manager = None
        self.player_being_captured = False
        self.capturing_beam = None
        self.capturing_boss = None
        self.stage_clear_time = 0
        self.stage_clear_delay = 2000
        self.bgm_playing = False
    
    def load_high_score(self):
        try:
            with open(settings.HIGHSCORE_FILE, 'r') as f:
                return int(f.read())
        except:
            return 0

    def load_ranking(self):
        """랭킹 로드"""
        try:
            with open(settings.RANKING_FILE, 'r') as f:
                ranking = []
                for line in f:
                    parts = line.strip().split(',')
                    if len(parts) == 2:
                        name = parts[0]
                        score = int(parts[1])
                        ranking.append((name, score))
                return ranking[:5]
        except:
            return []
    
    def save_ranking(self):
        """랭킹 저장"""
        with open(settings.RANKING_FILE, 'w') as f:
            for name, score in self.ranking[:5]:
                f.write(f"{name},{score}\n")
    
    def check_ranking(self):
        """현재 점수가 랭킹에 들어가는지 확인"""
        if len(self.ranking) < 5:
            return True
        return self.score > self.ranking[-1][1]
    
    def get_rank_position(self):
        """현재 점수의 순위 반환"""
        for i, (name, score) in enumerate(self.ranking):
            if self.score > score:
                return i
        if len(self.ranking) < 5:
            return len(self.ranking)
        return -1
    
    def add_to_ranking(self, name):
        """랭킹에 추가"""
        pos = self.get_rank_position()
        if pos >= 0:
            self.ranking.insert(pos, (name, self.score))
            self.ranking = self.ranking[:5]
            self.save_ranking()
            return pos
        return -1

    def save_high_score(self):
        with open(settings.HIGHSCORE_FILE, 'w') as f:
            f.write(str(self.high_score))
    
    def apply_difficulty_settings(self):
        diff = settings.DIFFICULTY_SETTINGS[settings.current_difficulty]
        settings.PLAYER_LIVES = diff['player_lives']
        settings.PLAYER_SPEED = diff['player_speed']
        settings.ENEMY_SPEED = diff['enemy_speed']
        settings.ENEMY_FIRE_CHANCE = diff['enemy_fire_chance']
        settings.ENEMY_BULLET_SPEED = diff['enemy_bullet_speed']
        settings.ENEMY_ROWS = diff['enemy_rows']
        settings.ENEMIES_PER_ROW = diff['enemies_per_row']
        self.powerup_manager.drop_chance = diff['powerup_drop_chance']
    
    def new_game(self):
        self.apply_difficulty_settings()
        self.score = 0
        self.combo_system.reset()
        self.all_sprites.empty()
        self.enemies.empty()
        self.bullets.empty()
        self.tractor_beams.empty()
        self.explosions.empty()
        self.powerups.empty()
        self.powerup_message = ""
        self.combo_message = ""
        self.nuclear_bomb = None
        self.player = Player(settings.SCREEN_WIDTH // 2, settings.SCREEN_HEIGHT - 60,
                            self.assets.get_image('player'), self.assets.get_image('player_bullet'))
        self.all_sprites.add(self.player)
        self.wave_manager = WaveManager(self.assets.get_image('enemy'), self.assets.get_image('boss'),
                                       self.assets.get_image('enemy_bullet'))
        self.wave_manager.set_player(self.player)
        self.wave_manager.current_wave = 1
        self.enemies = self.wave_manager.create_wave(1)
        self.all_sprites.add(self.enemies)
        self.player_being_captured = False
        self.capturing_beam = None
        self.capturing_boss = None
        self.state = settings.STATE_PLAYING
        if not self.bgm_playing:
            self.assets.play_bgm()
            self.bgm_playing = True
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if self.state == settings.STATE_MENU:
                    if event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                        self.state = settings.STATE_DIFFICULTY_SELECT
                    elif event.key == pygame.K_F4:
                        self.running = False
                elif self.state == settings.STATE_DIFFICULTY_SELECT:
                    if event.key == pygame.K_UP:
                        self.selected_difficulty = (self.selected_difficulty - 1) % 3
                        self.assets.play_sound('shoot')
                    elif event.key == pygame.K_DOWN:
                        self.selected_difficulty = (self.selected_difficulty + 1) % 3
                        self.assets.play_sound('shoot')
                    elif event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                        settings.set_difficulty(self.difficulty_names[self.selected_difficulty])
                        self.assets.play_sound('powerup')
                        self.new_game()
                    elif event.key == pygame.K_ESCAPE:
                        self.state = settings.STATE_MENU
                    elif event.key == pygame.K_F4:
                        self.running = False
                elif self.state == settings.STATE_PLAYING:
                    if event.key == pygame.K_p:
                        self.state = settings.STATE_PAUSED
                        self.assets.play_sound('capture')
                    elif event.key == pygame.K_x:
                        if self.player and self.player.can_use_ultimate():
                            self.launch_nuclear_bomb()
                    elif event.key == pygame.K_e:
                        if self.player:
                            weapon_name = self.player.change_weapon(1)
                            self.powerup_message = weapon_name
                            self.powerup_message_time = pygame.time.get_ticks()
                            self.assets.play_sound('shoot')
                    elif event.key == pygame.K_q:
                        if self.player:
                            weapon_name = self.player.change_weapon(-1)
                            self.powerup_message = weapon_name
                            self.powerup_message_time = pygame.time.get_ticks()
                            self.assets.play_sound('shoot')
                elif self.state == settings.STATE_PAUSED:
                    if event.key == pygame.K_p:
                        self.state = settings.STATE_PLAYING
                    elif event.key == pygame.K_ESCAPE:
                        self.state = settings.STATE_MENU
                        self.assets.stop_bgm()
                        self.bgm_playing = False
                    elif event.key == pygame.K_F4:
                        self.running = False
                elif self.state == settings.STATE_GAME_OVER:
                    if self.show_name_input:
                        if event.key == pygame.K_RETURN:
                            if self.player_name.strip():
                                self.add_to_ranking(self.player_name.strip())
                            else:
                                self.add_to_ranking("PLAYER")
                            self.show_name_input = False
                            self.ranking = self.load_ranking()
                        elif event.key == pygame.K_BACKSPACE:
                            self.player_name = self.player_name[:-1]
                        elif event.key == pygame.K_ESCAPE:
                            self.show_name_input = False
                        elif len(self.player_name) < 8:
                            if event.unicode.isalnum() or event.unicode == ' ':
                                self.player_name += event.unicode.upper()
                    else:
                        if event.key == pygame.K_r:
                            self.ranking = self.load_ranking()
                            self.state = settings.STATE_MENU
                            self.assets.stop_bgm()
                            self.bgm_playing = False
                        elif event.key == pygame.K_F4:
                            self.running = False
            elif event.type == pygame.MOUSEWHEEL:
                if self.state == settings.STATE_PLAYING and self.player:
                    weapon_name = self.player.change_weapon(-event.y)
                    self.powerup_message = weapon_name
                    self.powerup_message_time = pygame.time.get_ticks()
                    self.assets.play_sound('shoot')
    
    def update(self):
        self.background.update()
        self.screen_shake.update()
        self.flash_effect.update()
        self.combo_system.update()
        if self.nuclear_bomb:
            self.nuclear_bomb.update()
            if not self.nuclear_bomb.active:
                self.nuclear_bomb = None
        if self.state == settings.STATE_STAGE_CLEAR:
            if pygame.time.get_ticks() - self.stage_clear_time >= self.stage_clear_delay:
                self.stage_clear_time = 0
                self.enemies = self.wave_manager.next_wave()
                self.all_sprites.add(self.enemies)
                self.state = settings.STATE_PLAYING
            return
        if self.state != settings.STATE_PLAYING:
            return
        keys = pygame.key.get_pressed()
        if self.player and not self.player_being_captured:
            self.player.update(keys)
            if keys[pygame.K_SPACE]:
                if self.player.shoot(self.bullets):
                    self.assets.play_sound('shoot')
        for enemy in self.enemies:
            enemy.update()
            enemy.shoot(self.bullets)
            if enemy.is_boss and not self.player_being_captured:
                if enemy.shoot_tractor_beam(self.tractor_beams, self.assets.get_image('tractor_beam')):
                    self.assets.play_sound('enemy_shoot')
        for bullet in self.bullets:
            bullet.update(self.enemies)
        self.explosions.update()
        self.tractor_beams.update()
        self.powerups.update()
        self.handle_collisions()
        if len(self.enemies) == 0:
            if self.stage_clear_time == 0:
                self.stage_clear_time = pygame.time.get_ticks()
                self.state = settings.STATE_STAGE_CLEAR
                self.assets.play_sound('stage_clear')
        if self.wave_manager and self.wave_manager.is_bonus_stage:
            if self.wave_manager.is_bonus_stage_timeout():
                self.enemies.empty()
    
    def handle_collisions(self):
        if not self.player:
            return
        if self.nuclear_bomb:
            self.handle_nuclear_bomb_damage()
        score_gained, hit_positions, boss_killed_positions, split_children = check_bullet_enemy_collision(
            self.bullets, self.enemies)
        for child in split_children:
            if self.player:
                child.set_player_reference(self.player)
            self.enemies.add(child)
            self.all_sprites.add(child)
        if score_gained > 0:
            kill_count = len(hit_positions) + len(boss_killed_positions)
            combo_multiplier = 1.0
            for _ in range(kill_count):
                combo_multiplier = self.combo_system.add_kill()
                if self.player:
                    self.player.add_ultimate_charge(settings.ULTIMATE_CHARGE_PER_KILL)
            difficulty_multiplier = settings.get_difficulty_setting('score_multiplier')
            final_score = int(score_gained * combo_multiplier * difficulty_multiplier)
            self.score += final_score
            if self.combo_system.combo_count >= 3:
                self.combo_message = f"{self.combo_system.combo_count} COMBO! x{combo_multiplier:.1f}"
                self.combo_message_time = pygame.time.get_ticks()
            self.assets.play_sound('explosion')
            for pos in hit_positions:
                explosion = Explosion(pos[0], pos[1], self.assets.get_explosion_frames())
                self.explosions.add(explosion)
                self.powerup_manager.try_spawn(pos[0], pos[1], self.powerups)
                self.screen_shake.small_shake()
                self.flash_effect.small_flash()
            for pos in boss_killed_positions:
                explosion = Explosion(pos[0], pos[1], self.assets.get_explosion_frames())
                self.explosions.add(explosion)
                self.powerup_manager.spawn_boss_powerup(pos[0], pos[1], self.powerups)
                self.screen_shake.large_shake()
                self.flash_effect.large_flash()
            if self.score > self.high_score:
                self.high_score = self.score
                self.save_high_score()
        self.handle_powerup_collision()
        if check_player_bullet_collision(self.player, self.bullets):
            if not self.player.take_damage():
                self.game_over()
            else:
                self.assets.play_sound('explosion')
                self.screen_shake.medium_shake()
        if check_player_enemy_collision(self.player, self.enemies):
            if not self.player.take_damage():
                self.game_over()
            else:
                self.assets.play_sound('explosion')
                self.screen_shake.medium_shake()
        if not self.player_being_captured:
            beam = check_tractor_beam_player_collision(self.player, self.tractor_beams)
            if beam:
                beam.start_capture()
                self.player_being_captured = True
                self.capturing_beam = beam
                for enemy in self.enemies:
                    if enemy.is_boss:
                        self.capturing_boss = enemy
                        break
                self.assets.play_sound('capture')
        if self.player_being_captured and self.capturing_beam:
            if self.capturing_beam.is_capture_complete():
                self.player.get_captured()
                if self.capturing_boss:
                    self.capturing_boss.has_captured_ship = True
                self.capturing_beam.kill()
                self.player_being_captured = False
                self.capturing_beam = None
                if not self.player.take_damage():
                    self.game_over()
                else:
                    self.player = Player(settings.SCREEN_WIDTH // 2, settings.SCREEN_HEIGHT - 60,
                                        self.assets.get_image('player'), self.assets.get_image('player_bullet'))
                    self.all_sprites.add(self.player)
                    if self.wave_manager:
                        self.wave_manager.set_player(self.player)
        if self.capturing_boss and self.capturing_boss.has_captured_ship:
            for bullet in self.bullets:
                if bullet.bullet_type == 'player':
                    if pygame.sprite.collide_rect(bullet, self.capturing_boss):
                        bullet.kill()
                        self.capturing_boss.kill()
                        self.score += settings.SCORE_RESCUE
                        if self.player:
                            self.player.rescue_ship()
                        self.capturing_boss = None
                        self.assets.play_sound('rescue')
                        break
        if check_bullet_beam_collision(self.bullets, self.tractor_beams):
            self.assets.play_sound('explosion')
            if self.player_being_captured:
                self.player_being_captured = False
                self.capturing_beam = None
    
    def handle_powerup_collision(self):
        if not self.player:
            return
        for powerup in self.powerups:
            if pygame.sprite.collide_rect(self.player, powerup):
                message = self.player.powerups.apply_powerup(powerup)
                if message == "EXTRA_LIFE":
                    self.player.add_life()
                    message = "1UP!"
                if message:
                    self.powerup_message = message
                    self.powerup_message_time = pygame.time.get_ticks()
                self.assets.play_sound('powerup')
                powerup.kill()
    
    def launch_nuclear_bomb(self):
        if self.player.use_ultimate():
            self.nuclear_bomb = NuclearBomb(settings.SCREEN_WIDTH // 2, settings.SCREEN_HEIGHT // 2)
            self.screen_shake.large_shake()
            self.flash_effect.large_flash()
            self.assets.play_sound('boss_warning')
            self.powerup_message = "NUCLEAR BOMB!"
            self.powerup_message_time = pygame.time.get_ticks()
    
    def handle_nuclear_bomb_damage(self):
        if not self.nuclear_bomb:
            return
        radius = self.nuclear_bomb.get_current_radius()
        bomb_x = self.nuclear_bomb.x
        bomb_y = self.nuclear_bomb.y
        for enemy in list(self.enemies):
            dx = enemy.rect.centerx - bomb_x
            dy = enemy.rect.centery - bomb_y
            distance = math.sqrt(dx**2 + dy**2)
            if distance <= radius:
                pos = (enemy.rect.centerx, enemy.rect.centery)
                if enemy.take_damage(999):
                    self.score += enemy.get_score_value()
                    explosion = Explosion(pos[0], pos[1], self.assets.get_explosion_frames())
                    self.explosions.add(explosion)
                    if enemy.is_boss:
                        self.powerup_manager.spawn_boss_powerup(pos[0], pos[1], self.powerups)
    
    def game_over(self):
        self.state = settings.STATE_GAME_OVER
        self.assets.play_sound('game_over')
        self.screen_shake.large_shake()
        if self.check_ranking():
            self.show_name_input = True
            self.player_name = ""
            self.new_rank = self.get_rank_position()
        else:
            self.show_name_input = False
            self.new_rank = -1
    
    def draw(self):
        self.background.draw(self.game_surface)
        if self.state == settings.STATE_MENU:
            self.ui.draw_menu(self.game_surface)
        elif self.state == settings.STATE_DIFFICULTY_SELECT:
            self.ui.draw_difficulty_select(self.game_surface, self.selected_difficulty)
        elif self.state == settings.STATE_PLAYING:
            self.enemies.draw(self.game_surface)
            self.bullets.draw(self.game_surface)
            self.tractor_beams.draw(self.game_surface)
            self.explosions.draw(self.game_surface)
            for powerup in self.powerups:
                powerup.draw(self.game_surface)
            if self.player:
                self.player.draw(self.game_surface)
            self.ui.draw_hud(self.game_surface, self.score, self.high_score,
                            self.player.lives if self.player else 0,
                            self.wave_manager.current_wave if self.wave_manager else 1,
                            self.wave_manager.is_bonus_stage if self.wave_manager else False)
            self.draw_combo_display()
            self.draw_difficulty_indicator()
            self.draw_weapon_display()
            if self.player:
                self.draw_powerup_status()
                self.draw_ultimate_gauge()
            self.draw_powerup_message()
            self.draw_combo_message()
            if self.wave_manager and self.wave_manager.is_bonus_stage:
                remaining = self.wave_manager.get_bonus_stage_remaining_time()
                self.ui.draw_bonus_timer(self.game_surface, remaining)
            self.ui.draw_radar(self.game_surface, self.player, self.enemies, self.powerups)
            self.flash_effect.draw(self.game_surface)
            if self.nuclear_bomb:
                self.nuclear_bomb.draw(self.game_surface)
            if self.player_being_captured:
                self.ui.draw_capture_warning(self.game_surface)
        elif self.state == settings.STATE_PAUSED:
            self.enemies.draw(self.game_surface)
            self.bullets.draw(self.game_surface)
            if self.player:
                self.player.draw(self.game_surface)
            self.ui.draw_pause(self.game_surface)
        elif self.state == settings.STATE_GAME_OVER:
            self.ui.draw_game_over(self.game_surface, self.score, self.high_score)
            self.draw_game_stats()
            if self.show_name_input:
                self.draw_name_input()
            else:
                self.draw_ranking()
        elif self.state == settings.STATE_STAGE_CLEAR:
            self.ui.draw_stage_clear(self.game_surface,
                                     self.wave_manager.current_wave if self.wave_manager else 1)
        shake_x, shake_y = self.screen_shake.get_offset()
        self.screen.fill((0, 0, 0))
        self.screen.blit(self.game_surface, (shake_x, shake_y))
        pygame.display.flip()
    
    def draw_combo_display(self):
        if not self.combo_system.is_active():
            return
        font = pygame.font.Font(None, 36)
        combo = self.combo_system.combo_count
        multiplier = self.combo_system.get_multiplier()
        if combo < 5:
            color = (255, 255, 255)
        elif combo < 10:
            color = (255, 255, 0)
        elif combo < 20:
            color = (255, 165, 0)
        elif combo < 50:
            color = (255, 100, 100)
        else:
            color = (255, 0, 255)
        elapsed = pygame.time.get_ticks() - self.combo_system.combo_timer
        remaining = max(0, self.combo_system.combo_timeout - elapsed)
        bar_width = int(100 * remaining / self.combo_system.combo_timeout)
        bar_x = settings.SCREEN_WIDTH - 120
        bar_y = 75
        pygame.draw.rect(self.game_surface, (50, 50, 50), (bar_x, bar_y, 100, 8))
        pygame.draw.rect(self.game_surface, color, (bar_x, bar_y, bar_width, 8))
        text = f"x{multiplier:.1f}"
        surface = font.render(text, True, color)
        self.game_surface.blit(surface, (bar_x + 30, bar_y + 12))
    
    def draw_combo_message(self):
        if not self.combo_message:
            return
        elapsed = pygame.time.get_ticks() - self.combo_message_time
        if elapsed > self.combo_message_duration:
            self.combo_message = ""
            return
        alpha = 255
        if elapsed > self.combo_message_duration - 300:
            alpha = int(255 * (self.combo_message_duration - elapsed) / 300)
        y_offset = int(elapsed * 0.03)
        font = pygame.font.Font(None, 42)
        combo = self.combo_system.combo_count
        if combo < 10:
            color = (255, 255, 0)
        elif combo < 20:
            color = (255, 165, 0)
        elif combo < 50:
            color = (255, 100, 100)
        else:
            color = (255, 0, 255)
        text_surface = font.render(self.combo_message, True, color)
        text_surface.set_alpha(alpha)
        rect = text_surface.get_rect(center=(settings.SCREEN_WIDTH // 2,
                                             settings.SCREEN_HEIGHT // 2 - 100 - y_offset))
        self.game_surface.blit(text_surface, rect)
    
    def draw_game_stats(self):
        font = pygame.font.Font(None, 28)
        max_combo = self.combo_system.max_combo
        stats_text = f"Max Combo: {max_combo}"
        surface = font.render(stats_text, True, settings.CYAN)
        rect = surface.get_rect(center=(settings.SCREEN_WIDTH // 2, settings.SCREEN_HEIGHT // 2 + 160))
        self.game_surface.blit(surface, rect)
    
    def draw_difficulty_indicator(self):
        font = pygame.font.Font(None, 20)
        diff_colors = {
            settings.DIFFICULTY_EASY: settings.GREEN,
            settings.DIFFICULTY_NORMAL: settings.YELLOW,
            settings.DIFFICULTY_HARD: settings.RED,
        }
        color = diff_colors.get(settings.current_difficulty, settings.WHITE)
        text = settings.current_difficulty.upper()
        surface = font.render(text, True, color)
        self.game_surface.blit(surface, (settings.SCREEN_WIDTH - 60, 50))
    
    def draw_weapon_display(self):
        if not self.player:
            return
        font = pygame.font.Font(None, 24)
        weapon_name = self.player.get_weapon_name()
        weapon_color = self.player.get_weapon_color()
        text = f"[E/Q] {weapon_name}"
        surface = font.render(text, True, weapon_color)
        self.game_surface.blit(surface, (10, 90))
    
    def draw_ultimate_gauge(self):
        if not self.player:
            return
        gauge_x = settings.SCREEN_WIDTH - 130
        gauge_y = settings.SCREEN_HEIGHT - 50
        gauge_width = 120
        gauge_height = 15
        pygame.draw.rect(self.game_surface, (50, 50, 50), (gauge_x, gauge_y, gauge_width, gauge_height))
        fill_width = int(gauge_width * self.player.ultimate_charge / self.player.ultimate_max)
        if self.player.can_use_ultimate():
            if pygame.time.get_ticks() % 400 < 200:
                color = (255, 0, 0)
            else:
                color = (255, 100, 0)
        else:
            color = (255, 200, 0)
        pygame.draw.rect(self.game_surface, color, (gauge_x, gauge_y, fill_width, gauge_height))
        pygame.draw.rect(self.game_surface, (255, 255, 255), (gauge_x, gauge_y, gauge_width, gauge_height), 2)
        font = pygame.font.Font(None, 20)
        if self.player.can_use_ultimate():
            text = "[X] NUKE!"
            color = (255, 0, 0)
        else:
            text = f"ULTIMATE {self.player.ultimate_charge}%"
            color = (255, 255, 255)
        surface = font.render(text, True, color)
        self.game_surface.blit(surface, (gauge_x - 5, gauge_y - 20))
    
    def draw_powerup_status(self):
        if not self.player:
            return
        powerups = self.player.powerups
        x = 10
        y = settings.SCREEN_HEIGHT - 30
        font = pygame.font.Font(None, 20)
        active_powerups = []
        current_time = pygame.time.get_ticks()
        if powerups.speed_boost:
            remaining = max(0, (powerups.speed_end_time - current_time) // 1000)
            active_powerups.append(("SPEED", remaining, (100, 255, 100)))
        if powerups.shot_power > 1:
            remaining = max(0, (powerups.shot_power_end_time - current_time) // 1000)
            active_powerups.append(("POWER", remaining, (255, 100, 100)))
        if powerups.triple_shot:
            remaining = max(0, (powerups.triple_shot_end_time - current_time) // 1000)
            active_powerups.append(("TRIPLE", remaining, (100, 100, 255)))
        if powerups.shield_active:
            remaining = max(0, (powerups.shield_end_time - current_time) // 1000)
            active_powerups.append(("SHIELD", remaining, (100, 255, 255)))
        if powerups.rapid_fire:
            remaining = max(0, (powerups.rapid_fire_end_time - current_time) // 1000)
            active_powerups.append(("RAPID", remaining, (255, 255, 100)))
        for i, (name, remaining, color) in enumerate(active_powerups):
            text = f"{name}:{remaining}s"
            surface = font.render(text, True, color)
            self.game_surface.blit(surface, (x + i * 85, y))
    
    def draw_powerup_message(self):
        if not self.powerup_message:
            return
        elapsed = pygame.time.get_ticks() - self.powerup_message_time
        if elapsed > self.powerup_message_duration:
            self.powerup_message = ""
            return
        alpha = 255
        if elapsed > self.powerup_message_duration - 500:
            alpha = int(255 * (self.powerup_message_duration - elapsed) / 500)
        font = pygame.font.Font(None, 48)
        text_surface = font.render(self.powerup_message, True, (255, 255, 100))
        text_surface.set_alpha(alpha)
        rect = text_surface.get_rect(center=(settings.SCREEN_WIDTH // 2, settings.SCREEN_HEIGHT // 2 - 50))
        self.game_surface.blit(text_surface, rect)
    def draw_name_input(self):
        """이름 입력 UI"""
        font_large = pygame.font.Font(None, 36)
        font_small = pygame.font.Font(None, 28)
        
        # 배경 박스
        box_width = 300
        box_height = 120
        box_x = (settings.SCREEN_WIDTH - box_width) // 2
        box_y = settings.SCREEN_HEIGHT // 2 + 50
        
        pygame.draw.rect(self.game_surface, (0, 0, 50), (box_x, box_y, box_width, box_height))
        pygame.draw.rect(self.game_surface, (255, 255, 0), (box_x, box_y, box_width, box_height), 3)
        
        # 타이틀
        title = f"NEW RECORD! RANK #{self.new_rank + 1}"
        title_surface = font_large.render(title, True, (255, 255, 0))
        title_rect = title_surface.get_rect(center=(settings.SCREEN_WIDTH // 2, box_y + 25))
        self.game_surface.blit(title_surface, title_rect)
        
        # 이름 입력 필드
        name_text = self.player_name + "_"
        name_surface = font_large.render(name_text, True, (255, 255, 255))
        name_rect = name_surface.get_rect(center=(settings.SCREEN_WIDTH // 2, box_y + 60))
        self.game_surface.blit(name_surface, name_rect)
        
        # 안내
        hint = "Enter your name (max 8 chars)"
        hint_surface = font_small.render(hint, True, (150, 150, 150))
        hint_rect = hint_surface.get_rect(center=(settings.SCREEN_WIDTH // 2, box_y + 95))
        self.game_surface.blit(hint_surface, hint_rect)
    
    def draw_ranking(self):
        """랭킹 표시"""
        font_title = pygame.font.Font(None, 32)
        font_rank = pygame.font.Font(None, 28)
        font_hint = pygame.font.Font(None, 24)
        
        # 배경 박스
        box_width = 280
        box_height = 210
        box_x = (settings.SCREEN_WIDTH - box_width) // 2
        box_y = settings.SCREEN_HEIGHT // 2 + 50
        
        pygame.draw.rect(self.game_surface, (0, 0, 50), (box_x, box_y, box_width, box_height))
        pygame.draw.rect(self.game_surface, (100, 100, 255), (box_x, box_y, box_width, box_height), 2)
        
        # 타이틀
        title = "TOP 5 RANKING"
        title_surface = font_title.render(title, True, (100, 100, 255))
        title_rect = title_surface.get_rect(center=(settings.SCREEN_WIDTH // 2, box_y + 20))
        self.game_surface.blit(title_surface, title_rect)
        
        # 랭킹 목록
        colors = [(255, 215, 0), (192, 192, 192), (205, 127, 50), (255, 255, 255), (255, 255, 255)]
        
        for i in range(5):
            y = box_y + 45 + i * 25
            color = colors[i] if i < len(colors) else (255, 255, 255)
            
            if i < len(self.ranking):
                name, score = self.ranking[i]
                text = f"{i+1}. {name:8s} {score:>8}"
            else:
                text = f"{i+1}. -------- --------"
                color = (100, 100, 100)
            
            rank_surface = font_rank.render(text, True, color)
            rank_rect = rank_surface.get_rect(center=(settings.SCREEN_WIDTH // 2, y))
            self.game_surface.blit(rank_surface, rank_rect)
        
        # 안내 메시지
        hint = "R - Back to Menu    F4 - Quit"
        hint_surface = font_hint.render(hint, True, (150, 150, 150))
        hint_rect = hint_surface.get_rect(center=(settings.SCREEN_WIDTH // 2, box_y + 190))
        self.game_surface.blit(hint_surface, hint_rect)
            
    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(settings.FPS)
        pygame.quit()
        sys.exit()


def main():
    game = Game()
    game.run()


if __name__ == "__main__":
    main()