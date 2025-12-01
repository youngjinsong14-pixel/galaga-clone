# ui.py
"""
UI 요소 렌더링
점수, 목숨, HUD, 메뉴, 레이더 등을 표시합니다.
"""
import pygame
import math
from typing import Optional
import settings


class UI:
    """UI 렌더링 클래스"""
    
    def __init__(self):
        """UI 초기화"""
        self.font_large = pygame.font.Font(None, 72)
        self.font_medium = pygame.font.Font(None, 48)
        self.font_small = pygame.font.Font(None, 36)
        self.font_tiny = pygame.font.Font(None, 24)
        
        # 레이더 설정
        self.radar_width = 120
        self.radar_height = 90
        self.radar_x = settings.SCREEN_WIDTH - self.radar_width - 10
        self.radar_y = settings.SCREEN_HEIGHT - self.radar_height - 40
        self.radar_scale_x = self.radar_width / settings.SCREEN_WIDTH
        self.radar_scale_y = self.radar_height / settings.SCREEN_HEIGHT
        self.radar_scan_angle = 0
    
    def draw_hud(self, surface: pygame.Surface, score: int,
                high_score: int, lives: int, wave: int,
                is_bonus: bool = False) -> None:
        """게임 HUD 그리기"""
        score_text = self.font_small.render(f"SCORE: {score}", True, settings.WHITE)
        surface.blit(score_text, (10, 10))
        
        high_score_text = self.font_small.render(
            f"HIGH: {high_score}", True, settings.YELLOW
        )
        surface.blit(high_score_text, (10, 50))
        
        wave_label = "BONUS STAGE" if is_bonus else f"WAVE {wave}"
        wave_text = self.font_small.render(wave_label, True, settings.CYAN)
        wave_rect = wave_text.get_rect(center=(settings.SCREEN_WIDTH // 2, 20))
        surface.blit(wave_text, wave_rect)
        
        lives_text = self.font_small.render(f"LIVES: {lives}", True, settings.GREEN)
        lives_rect = lives_text.get_rect(topright=(settings.SCREEN_WIDTH - 10, 10))
        surface.blit(lives_text, lives_rect)
    
    def draw_radar(self, surface: pygame.Surface, player, enemies, powerups) -> None:
        """레이더/미니맵 그리기"""
        radar_surface = pygame.Surface((self.radar_width, self.radar_height), pygame.SRCALPHA)
        
        pygame.draw.rect(radar_surface, (0, 0, 0, 180), 
                        (0, 0, self.radar_width, self.radar_height))
        pygame.draw.rect(radar_surface, (0, 255, 100, 200), 
                        (0, 0, self.radar_width, self.radar_height), 2)
        
        for i in range(1, 4):
            y = self.radar_height * i // 4
            pygame.draw.line(radar_surface, (0, 100, 50, 100),
                           (0, y), (self.radar_width, y), 1)
        for i in range(1, 4):
            x = self.radar_width * i // 4
            pygame.draw.line(radar_surface, (0, 100, 50, 100),
                           (x, 0), (x, self.radar_height), 1)
        
        self.radar_scan_angle += 3
        if self.radar_scan_angle >= 360:
            self.radar_scan_angle = 0
        
        scan_x = self.radar_width // 2 + int(math.cos(math.radians(self.radar_scan_angle)) * self.radar_width // 2)
        scan_y = self.radar_height // 2 + int(math.sin(math.radians(self.radar_scan_angle)) * self.radar_height // 2)
        pygame.draw.line(radar_surface, (0, 255, 100, 100),
                        (self.radar_width // 2, self.radar_height // 2),
                        (scan_x, scan_y), 1)
        
        for enemy in enemies:
            rx = int(enemy.rect.centerx * self.radar_scale_x)
            ry = int(enemy.rect.centery * self.radar_scale_y)
            rx = max(2, min(self.radar_width - 2, rx))
            ry = max(2, min(self.radar_height - 2, ry))
            
            if enemy.is_boss:
                color = (255, 0, 255)
                size = 4
            elif enemy.enemy_type == 'fast':
                color = (0, 255, 0)
                size = 2
            elif enemy.enemy_type == 'tank':
                color = (100, 100, 255)
                size = 3
            elif enemy.enemy_type == 'kamikaze':
                color = (255, 150, 0)
                size = 2
            elif enemy.enemy_type == 'splitter':
                color = (200, 100, 255)
                size = 2
            else:
                color = (255, 0, 0)
                size = 2
            
            pygame.draw.circle(radar_surface, color, (rx, ry), size)
        
        for powerup in powerups:
            rx = int(powerup.rect.centerx * self.radar_scale_x)
            ry = int(powerup.rect.centery * self.radar_scale_y)
            rx = max(2, min(self.radar_width - 2, rx))
            ry = max(2, min(self.radar_height - 2, ry))
            
            if pygame.time.get_ticks() % 500 < 250:
                pygame.draw.circle(radar_surface, (255, 255, 0), (rx, ry), 3)
        
        if player and player.alive():
            px = int(player.rect.centerx * self.radar_scale_x)
            py = int(player.rect.centery * self.radar_scale_y)
            px = max(2, min(self.radar_width - 2, px))
            py = max(2, min(self.radar_height - 2, py))
            
            pygame.draw.polygon(radar_surface, (0, 255, 255), [
                (px, py - 4),
                (px - 3, py + 3),
                (px + 3, py + 3)
            ])
        
        label = self.font_tiny.render("RADAR", True, (0, 255, 100))
        radar_surface.blit(label, (self.radar_width // 2 - label.get_width() // 2, 2))
        
        surface.blit(radar_surface, (self.radar_x, self.radar_y))
        self._draw_offscreen_warnings(surface, enemies)
    
    def _draw_offscreen_warnings(self, surface: pygame.Surface, enemies) -> None:
        """화면 밖 적 경고"""
        margin = 30
        
        for enemy in enemies:
            if enemy.rect.bottom < 0:
                x = max(margin, min(settings.SCREEN_WIDTH - margin, enemy.rect.centerx))
                self._draw_arrow(surface, x, margin, 'down', (255, 255, 0))
            elif enemy.rect.top > settings.SCREEN_HEIGHT:
                x = max(margin, min(settings.SCREEN_WIDTH - margin, enemy.rect.centerx))
                self._draw_arrow(surface, x, settings.SCREEN_HEIGHT - margin, 'up', (255, 100, 0))
    
    def _draw_arrow(self, surface: pygame.Surface, x: int, y: int, 
                   direction: str, color: tuple) -> None:
        """방향 화살표 그리기"""
        size = 8
        
        if direction == 'down':
            points = [(x, y + size), (x - size, y - size), (x + size, y - size)]
        elif direction == 'up':
            points = [(x, y - size), (x - size, y + size), (x + size, y + size)]
        elif direction == 'left':
            points = [(x - size, y), (x + size, y - size), (x + size, y + size)]
        elif direction == 'right':
            points = [(x + size, y), (x - size, y - size), (x - size, y + size)]
        else:
            return
        
        if pygame.time.get_ticks() % 400 < 200:
            pygame.draw.polygon(surface, color, points)
            pygame.draw.polygon(surface, (255, 255, 255), points, 2)
    
    def draw_menu(self, surface: pygame.Surface) -> None:
        """메인 메뉴 그리기"""
        title_text = self.font_large.render("GALAGA CLONE", True, settings.YELLOW)
        title_rect = title_text.get_rect(
            center=(settings.SCREEN_WIDTH // 2, settings.SCREEN_HEIGHT // 4)
        )
        surface.blit(title_text, title_rect)
        
        start_text = self.font_medium.render(
            "Press SPACE to Start", True, settings.WHITE
        )
        start_rect = start_text.get_rect(
            center=(settings.SCREEN_WIDTH // 2, settings.SCREEN_HEIGHT // 2 - 20)
        )
        surface.blit(start_text, start_rect)
        
        quit_text = self.font_medium.render(
            "Press F4 to Quit", True, settings.RED
        )
        quit_rect = quit_text.get_rect(
            center=(settings.SCREEN_WIDTH // 2, settings.SCREEN_HEIGHT // 2 + 40)
        )
        surface.blit(quit_text, quit_rect)
        
        controls = [
            "Controls:",
            "Arrow Keys / W,A,S,D - Move",
            "SPACE - Shoot",
            "P - Pause",
        ]
        
        y_offset = settings.SCREEN_HEIGHT // 2 + 120
        for line in controls:
            control_text = self.font_tiny.render(line, True, settings.CYAN)
            control_rect = control_text.get_rect(
                center=(settings.SCREEN_WIDTH // 2, y_offset)
            )
            surface.blit(control_text, control_rect)
            y_offset += 25
    
    def draw_difficulty_select(self, surface: pygame.Surface, selected: int) -> None:
        """난이도 선택 화면 그리기"""
        title_text = self.font_large.render("SELECT DIFFICULTY", True, settings.YELLOW)
        title_rect = title_text.get_rect(
            center=(settings.SCREEN_WIDTH // 2, settings.SCREEN_HEIGHT // 4)
        )
        surface.blit(title_text, title_rect)
        
        difficulties = [
            ("EASY", settings.GREEN, "5 Lives, Slow Enemies, More Powerups"),
            ("NORMAL", settings.YELLOW, "3 Lives, Balanced Gameplay"),
            ("HARD", settings.RED, "2 Lives, Fast Enemies, Fewer Powerups"),
        ]
        
        y_start = settings.SCREEN_HEIGHT // 2 - 60
        
        for i, (name, color, desc) in enumerate(difficulties):
            y_pos = y_start + i * 80
            
            if i == selected:
                box_rect = pygame.Rect(
                    settings.SCREEN_WIDTH // 2 - 200,
                    y_pos - 20,
                    400, 70
                )
                pygame.draw.rect(surface, color, box_rect, 3)
                
                arrow_text = self.font_medium.render(">", True, color)
                surface.blit(arrow_text, (settings.SCREEN_WIDTH // 2 - 180, y_pos))
                
                name_text = self.font_medium.render(name, True, color)
            else:
                dim_color = tuple(c // 2 for c in color)
                name_text = self.font_medium.render(name, True, dim_color)
            
            name_rect = name_text.get_rect(
                center=(settings.SCREEN_WIDTH // 2, y_pos)
            )
            surface.blit(name_text, name_rect)
            
            if i == selected:
                desc_text = self.font_tiny.render(desc, True, settings.WHITE)
            else:
                desc_text = self.font_tiny.render(desc, True, (100, 100, 100))
            
            desc_rect = desc_text.get_rect(
                center=(settings.SCREEN_WIDTH // 2, y_pos + 30)
            )
            surface.blit(desc_text, desc_rect)
        
        help_text = self.font_tiny.render(
            "UP/DOWN: Select    SPACE/ENTER: Confirm    ESC: Back",
            True, settings.CYAN
        )
        help_rect = help_text.get_rect(
            center=(settings.SCREEN_WIDTH // 2, settings.SCREEN_HEIGHT - 50)
        )
        surface.blit(help_text, help_rect)
    
    def draw_pause(self, surface: pygame.Surface) -> None:
        """일시정지 화면 그리기"""
        overlay = pygame.Surface((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(settings.BLACK)
        surface.blit(overlay, (0, 0))
        
        pause_text = self.font_large.render("PAUSED", True, settings.YELLOW)
        pause_rect = pause_text.get_rect(
            center=(settings.SCREEN_WIDTH // 2, settings.SCREEN_HEIGHT // 2 - 60)
        )
        surface.blit(pause_text, pause_rect)
        
        resume_text = self.font_small.render(
            "P - Resume", True, settings.WHITE
        )
        resume_rect = resume_text.get_rect(
            center=(settings.SCREEN_WIDTH // 2, settings.SCREEN_HEIGHT // 2)
        )
        surface.blit(resume_text, resume_rect)
        
        menu_text = self.font_small.render(
            "ESC - Back to Menu", True, settings.CYAN
        )
        menu_rect = menu_text.get_rect(
            center=(settings.SCREEN_WIDTH // 2, settings.SCREEN_HEIGHT // 2 + 40)
        )
        surface.blit(menu_text, menu_rect)
        
        quit_text = self.font_small.render(
            "F4 - Quit Game", True, settings.RED
        )
        quit_rect = quit_text.get_rect(
            center=(settings.SCREEN_WIDTH // 2, settings.SCREEN_HEIGHT // 2 + 80)
        )
        surface.blit(quit_text, quit_rect)
    
    def draw_game_over(self, surface: pygame.Surface, score: int,
                      high_score: int) -> None:
        """게임 오버 화면 그리기"""
        game_over_text = self.font_large.render("GAME OVER", True, settings.RED)
        game_over_rect = game_over_text.get_rect(
            center=(settings.SCREEN_WIDTH // 2, settings.SCREEN_HEIGHT // 4)
        )
        surface.blit(game_over_text, game_over_rect)
        
        score_text = self.font_medium.render(f"Score: {score}", True, settings.WHITE)
        score_rect = score_text.get_rect(
            center=(settings.SCREEN_WIDTH // 2, settings.SCREEN_HEIGHT // 2 - 30)
        )
        surface.blit(score_text, score_rect)
        
        if score >= high_score:
            new_high_text = self.font_small.render(
                "NEW HIGH SCORE!", True, settings.YELLOW
            )
            new_high_rect = new_high_text.get_rect(
                center=(settings.SCREEN_WIDTH // 2, settings.SCREEN_HEIGHT // 2 + 20)
            )
            surface.blit(new_high_text, new_high_rect)
        else:
            high_text = self.font_small.render(
                f"High Score: {high_score}", True, settings.YELLOW
            )
            high_rect = high_text.get_rect(
                center=(settings.SCREEN_WIDTH // 2, settings.SCREEN_HEIGHT // 2 + 20)
            )
            surface.blit(high_text, high_rect)
        
        restart_text = self.font_small.render(
            "R - Restart", True, settings.WHITE
        )
        restart_rect = restart_text.get_rect(
            center=(settings.SCREEN_WIDTH // 2, settings.SCREEN_HEIGHT // 2 + 80)
        )
        surface.blit(restart_text, restart_rect)
        
        quit_text = self.font_small.render(
            "F4 - Quit Game", True, settings.RED
        )
        quit_rect = quit_text.get_rect(
            center=(settings.SCREEN_WIDTH // 2, settings.SCREEN_HEIGHT // 2 + 120)
        )
        surface.blit(quit_text, quit_rect)    
    def draw_stage_clear(self, surface: pygame.Surface, wave: int) -> None:
        """스테이지 클리어 화면 그리기"""
        clear_text = self.font_large.render("STAGE CLEAR!", True, settings.GREEN)
        clear_rect = clear_text.get_rect(
            center=(settings.SCREEN_WIDTH // 2, settings.SCREEN_HEIGHT // 2)
        )
        surface.blit(clear_text, clear_rect)
        
        wave_text = self.font_medium.render(
            f"Wave {wave} Complete", True, settings.WHITE
        )
        wave_rect = wave_text.get_rect(
            center=(settings.SCREEN_WIDTH // 2, settings.SCREEN_HEIGHT // 2 + 60)
        )
        surface.blit(wave_text, wave_rect)
    
    def draw_bonus_timer(self, surface: pygame.Surface, remaining_time: int) -> None:
        """보너스 스테이지 타이머 그리기"""
        timer_text = self.font_medium.render(
            f"TIME: {remaining_time}s", True, settings.YELLOW
        )
        timer_rect = timer_text.get_rect(
            center=(settings.SCREEN_WIDTH // 2, 60)
        )
        surface.blit(timer_text, timer_rect)
    
    def draw_capture_warning(self, surface: pygame.Surface) -> None:
        """트랙터 빔 포획 경고 표시"""
        warning_text = self.font_medium.render("CAPTURED!", True, settings.RED)
        warning_rect = warning_text.get_rect(
            center=(settings.SCREEN_WIDTH // 2, settings.SCREEN_HEIGHT - 100)
        )
        surface.blit(warning_text, warning_rect)