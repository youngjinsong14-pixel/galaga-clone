# assets_loader.py
"""
게임 에셋(이미지, 사운드) 로딩 및 생성
디테일한 픽셀아트 스타일 스프라이트 포함
"""
import os
import pygame
import math
import random
from typing import Dict, Optional, List
import settings
import sound_generator


class AssetsLoader:
    """게임 에셋을 로드하고 관리하는 클래스"""
    
    def __init__(self):
        """에셋 로더 초기화"""
        self.images: Dict[str, pygame.Surface] = {}
        self.sounds: Dict[str, pygame.mixer.Sound] = {}
        self.explosion_frames: List[pygame.Surface] = []
        
        os.makedirs(settings.ASSETS_DIR, exist_ok=True)
        os.makedirs(settings.SFX_DIR, exist_ok=True)
        
        self._generate_images()
        self._generate_explosion_frames()
        self._generate_sounds()
    
    def _generate_images(self) -> None:
        """디테일한 픽셀아트 스타일 스프라이트 생성"""
        self._create_player_ship()
        self._create_enemy_ship()
        self._create_boss_ship()
        self._create_bullets()
        self._create_tractor_beam()
        self._create_background()
    
    def _create_player_ship(self) -> None:
        """플레이어 우주선 생성"""
        width, height = 40, 48
        surface = pygame.Surface((width, height), pygame.SRCALPHA)
        
        body_main = (50, 150, 255)
        body_dark = (30, 100, 200)
        body_light = (100, 200, 255)
        cockpit = (200, 255, 255)
        engine = (255, 100, 50)
        engine_glow = (255, 200, 100)
        
        pygame.draw.polygon(surface, body_main, [
            (20, 5), (8, 35), (32, 35)
        ])
        
        pygame.draw.polygon(surface, body_dark, [
            (8, 25), (0, 40), (5, 42), (12, 30)
        ])
        
        pygame.draw.polygon(surface, body_dark, [
            (32, 25), (40, 40), (35, 42), (28, 30)
        ])
        
        pygame.draw.line(surface, body_light, (15, 10), (10, 30), 2)
        
        pygame.draw.ellipse(surface, cockpit, (15, 12, 10, 15))
        pygame.draw.ellipse(surface, (255, 255, 255), (17, 14, 4, 6))
        
        pygame.draw.rect(surface, engine_glow, (14, 36, 5, 8))
        pygame.draw.rect(surface, engine_glow, (21, 36, 5, 8))
        
        pygame.draw.polygon(surface, engine, [(14, 40), (16, 48), (19, 40)])
        pygame.draw.polygon(surface, engine, [(21, 40), (23, 48), (26, 40)])
        pygame.draw.polygon(surface, (255, 255, 100), [(15, 40), (16, 45), (18, 40)])
        pygame.draw.polygon(surface, (255, 255, 100), [(22, 40), (23, 45), (25, 40)])
        
        pygame.draw.rect(surface, (100, 100, 120), (18, 2, 4, 6))
        
        self.images['player'] = surface
    
    def _create_enemy_ship(self) -> None:
        """적 우주선 생성"""
        width, height = 36, 36
        surface = pygame.Surface((width, height), pygame.SRCALPHA)
        
        body_main = (220, 50, 50)
        body_dark = (150, 30, 30)
        body_light = (255, 100, 100)
        eye_color = (255, 255, 0)
        eye_pupil = (50, 50, 50)
        wing_color = (180, 40, 80)
        
        pygame.draw.ellipse(surface, body_main, (6, 8, 24, 22))
        pygame.draw.ellipse(surface, body_dark, (6, 14, 24, 14))
        pygame.draw.ellipse(surface, body_light, (10, 10, 16, 10))
        
        pygame.draw.ellipse(surface, body_main, (10, 2, 16, 12))
        pygame.draw.ellipse(surface, body_light, (12, 3, 10, 6))
        
        pygame.draw.circle(surface, eye_color, (13, 8), 4)
        pygame.draw.circle(surface, eye_pupil, (14, 8), 2)
        pygame.draw.circle(surface, (255, 255, 255), (12, 7), 1)
        
        pygame.draw.circle(surface, eye_color, (23, 8), 4)
        pygame.draw.circle(surface, eye_pupil, (24, 8), 2)
        pygame.draw.circle(surface, (255, 255, 255), (22, 7), 1)
        
        pygame.draw.line(surface, body_dark, (12, 3), (8, 0), 2)
        pygame.draw.circle(surface, eye_color, (8, 0), 2)
        pygame.draw.line(surface, body_dark, (24, 3), (28, 0), 2)
        pygame.draw.circle(surface, eye_color, (28, 0), 2)
        
        pygame.draw.polygon(surface, wing_color, [(6, 15), (0, 20), (0, 30), (6, 25)])
        pygame.draw.polygon(surface, body_light, [(5, 16), (2, 19), (2, 24), (5, 22)])
        
        pygame.draw.polygon(surface, wing_color, [(30, 15), (36, 20), (36, 30), (30, 25)])
        pygame.draw.polygon(surface, body_light, [(31, 16), (34, 19), (34, 24), (31, 22)])
        
        pygame.draw.polygon(surface, body_dark, [(14, 28), (18, 35), (22, 28)])
        
        self.images['enemy'] = surface
    
    def _create_boss_ship(self) -> None:
        """보스 우주선 생성"""
        width, height = 50, 45
        surface = pygame.Surface((width, height), pygame.SRCALPHA)
        
        body_main = (180, 50, 200)
        body_dark = (120, 30, 140)
        body_light = (220, 100, 255)
        gold = (255, 215, 0)
        eye_color = (0, 255, 200)
        
        pygame.draw.ellipse(surface, body_main, (8, 10, 34, 28))
        pygame.draw.ellipse(surface, body_dark, (8, 20, 34, 16))
        pygame.draw.ellipse(surface, body_light, (14, 12, 22, 14))
        
        pygame.draw.polygon(surface, gold, [(25, 0), (20, 10), (30, 10)])
        pygame.draw.polygon(surface, gold, [(15, 5), (12, 12), (20, 12)])
        pygame.draw.polygon(surface, gold, [(35, 5), (30, 12), (38, 12)])
        
        pygame.draw.ellipse(surface, eye_color, (14, 16, 8, 10))
        pygame.draw.ellipse(surface, (255, 255, 255), (16, 17, 3, 4))
        pygame.draw.ellipse(surface, (0, 100, 100), (18, 20, 3, 4))
        
        pygame.draw.ellipse(surface, eye_color, (28, 16, 8, 10))
        pygame.draw.ellipse(surface, (255, 255, 255), (30, 17, 3, 4))
        pygame.draw.ellipse(surface, (0, 100, 100), (32, 20, 3, 4))
        
        pygame.draw.polygon(surface, body_dark, [(8, 18), (0, 15), (0, 25), (4, 30), (8, 28)])
        pygame.draw.line(surface, gold, (2, 18), (2, 28), 2)
        
        pygame.draw.polygon(surface, body_dark, [(42, 18), (50, 15), (50, 25), (46, 30), (42, 28)])
        pygame.draw.line(surface, gold, (48, 18), (48, 28), 2)
        
        pygame.draw.ellipse(surface, (100, 255, 255), (20, 32, 10, 8))
        pygame.draw.ellipse(surface, (200, 255, 255), (22, 34, 6, 4))
        
        pygame.draw.polygon(surface, body_main, [(18, 36), (25, 44), (32, 36)])
        
        self.images['boss'] = surface
    
    def _create_bullets(self) -> None:
        """탄환 이미지 생성"""
        p_width, p_height = 6, 20
        p_surface = pygame.Surface((p_width, p_height), pygame.SRCALPHA)
        
        pygame.draw.rect(p_surface, (255, 255, 255), (2, 0, 2, p_height))
        pygame.draw.rect(p_surface, (100, 200, 255), (1, 0, 1, p_height))
        pygame.draw.rect(p_surface, (100, 200, 255), (4, 0, 1, p_height))
        pygame.draw.rect(p_surface, (50, 150, 255), (0, 0, 1, p_height))
        pygame.draw.rect(p_surface, (50, 150, 255), (5, 0, 1, p_height))
        
        self.images['player_bullet'] = p_surface
        
        e_size = 10
        e_surface = pygame.Surface((e_size, e_size), pygame.SRCALPHA)
        
        pygame.draw.circle(e_surface, (255, 100, 100, 100), (5, 5), 5)
        pygame.draw.circle(e_surface, (255, 150, 50), (5, 5), 4)
        pygame.draw.circle(e_surface, (255, 200, 100), (5, 5), 3)
        pygame.draw.circle(e_surface, (255, 255, 200), (5, 5), 2)
        
        self.images['enemy_bullet'] = e_surface
    
    def _create_tractor_beam(self) -> None:
        """트랙터 빔 생성"""
        width = settings.TRACTOR_BEAM_WIDTH
        height = settings.TRACTOR_BEAM_HEIGHT
        surface = pygame.Surface((width, height), pygame.SRCALPHA)
        
        for i in range(height):
            progress = i / height
            current_width = int(10 + (width - 10) * progress)
            x_offset = (width - current_width) // 2
            
            alpha = int(180 * (1 - abs(progress - 0.5) * 2) + 50)
            
            r = int(100 + 155 * progress)
            g = int(255 - 55 * progress)
            b = int(255 - 200 * progress)
            
            pygame.draw.line(surface, (r, g, b, alpha), (x_offset, i), (x_offset + current_width, i))
        
        self.images['tractor_beam'] = surface
    
    def _create_background(self) -> None:
        """우주 배경 생성"""
        surface = pygame.Surface((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT))
        surface.fill((5, 5, 20))
        
        random.seed(42)
        
        for _ in range(5):
            x = random.randint(0, settings.SCREEN_WIDTH)
            y = random.randint(0, settings.SCREEN_HEIGHT)
            radius = random.randint(100, 200)
            color = random.choice([
                (30, 20, 50),
                (20, 30, 50),
                (40, 20, 30),
            ])
            
            for r in range(radius, 0, -5):
                alpha = int(30 * (r / radius))
                temp_surface = pygame.Surface((r*2, r*2), pygame.SRCALPHA)
                pygame.draw.circle(temp_surface, (*color, alpha), (r, r), r)
                surface.blit(temp_surface, (x - r, y - r))
        
        for _ in range(150):
            x = random.randint(0, settings.SCREEN_WIDTH)
            y = random.randint(0, settings.SCREEN_HEIGHT)
            
            size_chance = random.random()
            if size_chance > 0.95:
                size = 3
                brightness = 255
            elif size_chance > 0.8:
                size = 2
                brightness = random.randint(200, 255)
            else:
                size = 1
                brightness = random.randint(100, 200)
            
            color_chance = random.random()
            if color_chance > 0.9:
                color = (brightness, brightness, int(brightness * 0.7))
            elif color_chance > 0.8:
                color = (int(brightness * 0.7), int(brightness * 0.8), brightness)
            else:
                color = (brightness, brightness, brightness)
            
            pygame.draw.circle(surface, color, (x, y), size)
            
            if size >= 2:
                pygame.draw.line(surface, (brightness, brightness, brightness),
                               (x - size - 1, y), (x + size + 1, y), 1)
                pygame.draw.line(surface, (brightness, brightness, brightness),
                               (x, y - size - 1), (x, y + size + 1), 1)
        
        self.images['background'] = surface
    
    def _generate_explosion_frames(self) -> None:
        """폭발 애니메이션 프레임 생성"""
        num_frames = 12
        max_radius = 30
        
        for frame in range(num_frames):
            progress = frame / (num_frames - 1)
            surface = pygame.Surface((max_radius * 2, max_radius * 2), pygame.SRCALPHA)
            
            if progress < 0.3:
                radius = int(max_radius * (progress / 0.3))
            else:
                radius = max_radius
            
            alpha = int(255 * (1 - progress))
            
            if radius > 0:
                color1 = (255, 150, 50, alpha)
                pygame.draw.circle(surface, color1, (max_radius, max_radius), radius)
                
                if radius > 5:
                    color2 = (255, 255, 100, min(255, alpha + 50))
                    pygame.draw.circle(surface, color2, (max_radius, max_radius), int(radius * 0.7))
                
                if radius > 10:
                    color3 = (255, 255, 255, min(255, alpha + 100))
                    pygame.draw.circle(surface, color3, (max_radius, max_radius), int(radius * 0.3))
                
                if 0.2 < progress < 0.8:
                    num_particles = 8
                    for i in range(num_particles):
                        angle = (2 * math.pi * i / num_particles) + (progress * 0.5)
                        dist = radius * (0.8 + progress * 0.5)
                        px = int(max_radius + math.cos(angle) * dist)
                        py = int(max_radius + math.sin(angle) * dist)
                        
                        particle_alpha = int(alpha * 0.8)
                        pygame.draw.circle(surface, (255, 200, 100, particle_alpha),
                                         (px, py), max(1, int(3 * (1 - progress))))
            
            self.explosion_frames.append(surface)
    
    def get_explosion_frames(self) -> List[pygame.Surface]:
        """폭발 애니메이션 프레임 가져오기"""
        return self.explosion_frames
    
    def _generate_sounds(self) -> None:
        """사운드 생성 및 로드"""
        pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
        
        self.sounds['shoot'] = sound_generator.generate_laser(0.15)
        self.sounds['explosion'] = sound_generator.generate_explosion(0.3)
        self.sounds['enemy_shoot'] = sound_generator.generate_beep(300, 0.1)
        self.sounds['capture'] = sound_generator.generate_beep(200, 0.5)
        self.sounds['rescue'] = sound_generator.generate_powerup(0.3)
        self.sounds['game_over'] = sound_generator.generate_game_over(2.0)
        self.sounds['stage_clear'] = sound_generator.generate_stage_clear(1.5)
        self.sounds['powerup'] = sound_generator.generate_powerup(0.3)
        self.sounds['boss_warning'] = sound_generator.generate_boss_warning(1.0)
        self.sounds['bgm'] = sound_generator.generate_bgm(30.0)
        
        for name, sound in self.sounds.items():
            if name == 'bgm':
                sound.set_volume(settings.BGM_VOLUME if hasattr(settings, 'BGM_VOLUME') else 0.3)
            else:
                sound.set_volume(settings.SFX_VOLUME)
    
    def play_bgm(self) -> None:
        """BGM 재생"""
        if 'bgm' in self.sounds:
            self.sounds['bgm'].play(-1)
    
    def stop_bgm(self) -> None:
        """BGM 정지"""
        if 'bgm' in self.sounds:
            self.sounds['bgm'].stop()
    
    def get_image(self, name: str) -> Optional[pygame.Surface]:
        """이미지 가져오기"""
        return self.images.get(name)
    
    def get_sound(self, name: str) -> Optional[pygame.mixer.Sound]:
        """사운드 가져오기"""
        return self.sounds.get(name)
    
    def play_sound(self, name: str) -> None:
        """사운드 재생"""
        sound = self.get_sound(name)
        if sound:
            sound.play()