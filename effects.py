# effects.py
"""
게임 이펙트 (폭발, 파티클 등)
"""
import pygame
import random
from typing import List


class Explosion(pygame.sprite.Sprite):
    """폭발 애니메이션 스프라이트"""
    
    def __init__(self, x: int, y: int, frames: List[pygame.Surface]):
        """
        폭발 초기화
        
        Args:
            x: 중심 x 좌표
            y: 중심 y 좌표
            frames: 애니메이션 프레임 리스트
        """
        super().__init__()
        self.frames = frames
        self.current_frame = 0
        self.image = self.frames[0]
        self.rect = self.image.get_rect(center=(x, y))
        
        self.animation_speed = 0.5
        self.frame_progress = 0.0
    
    def update(self) -> None:
        """애니메이션 업데이트"""
        self.frame_progress += self.animation_speed
        self.current_frame = int(self.frame_progress)
        
        if self.current_frame >= len(self.frames):
            self.kill()
        else:
            self.image = self.frames[self.current_frame]
            center = self.rect.center
            self.rect = self.image.get_rect(center=center)


class EngineFlame(pygame.sprite.Sprite):
    """엔진 화염 이펙트"""
    
    def __init__(self, player):
        """
        엔진 화염 초기화
        
        Args:
            player: 플레이어 객체
        """
        super().__init__()
        self.player = player
        self.frame = 0
        self._create_frames()
        self.image = self.frames[0]
        self.rect = self.image.get_rect()
    
    def _create_frames(self) -> None:
        """화염 애니메이션 프레임 생성"""
        self.frames = []
        
        for i in range(4):
            surface = pygame.Surface((20, 15 + i * 3), pygame.SRCALPHA)
            height = 15 + i * 3
            
            pygame.draw.polygon(surface, (255, 150, 50), [
                (4, 0), (10, height), (16, 0)
            ])
            
            pygame.draw.polygon(surface, (255, 255, 100), [
                (7, 0), (10, height - 5), (13, 0)
            ])
            
            pygame.draw.polygon(surface, (255, 255, 255), [
                (9, 0), (10, height - 10), (11, 0)
            ])
            
            self.frames.append(surface)
    
    def update(self) -> None:
        """화염 애니메이션 업데이트"""
        self.frame = (self.frame + 1) % (len(self.frames) * 2)
        self.image = self.frames[self.frame // 2]
        
        if self.player and self.player.alive():
            self.rect.centerx = self.player.rect.centerx
            self.rect.top = self.player.rect.bottom - 5
        else:
            self.kill()


class ScreenShake:
    """화면 흔들림 효과 관리"""
    
    def __init__(self):
        self.shake_amount = 0
        self.shake_duration = 0
        self.shake_intensity = 0
        self.offset_x = 0
        self.offset_y = 0
    
    def start_shake(self, intensity: int, duration: int) -> None:
        """
        화면 흔들림 시작
        
        Args:
            intensity: 흔들림 강도 (픽셀)
            duration: 지속 시간 (밀리초)
        """
        self.shake_intensity = intensity
        self.shake_duration = duration
        self.shake_amount = duration
    
    def small_shake(self) -> None:
        """작은 흔들림 (피격 시)"""
        self.start_shake(4, 150)
    
    def medium_shake(self) -> None:
        """중간 흔들림 (적 처치 시)"""
        self.start_shake(6, 200)
    
    def large_shake(self) -> None:
        """큰 흔들림 (보스 처치 시)"""
        self.start_shake(12, 400)
    
    def update(self) -> None:
        """흔들림 업데이트"""
        if self.shake_amount > 0:
            progress = self.shake_amount / self.shake_duration
            current_intensity = int(self.shake_intensity * progress)
            
            self.offset_x = random.randint(-current_intensity, current_intensity)
            self.offset_y = random.randint(-current_intensity, current_intensity)
            
            self.shake_amount -= 16
        else:
            self.offset_x = 0
            self.offset_y = 0
    
    def get_offset(self) -> tuple:
        """현재 오프셋 반환"""
        return (self.offset_x, self.offset_y)
    
    def is_shaking(self) -> bool:
        """흔들림 중인지 확인"""
        return self.shake_amount > 0


class FlashEffect:
    """섬광 효과 관리"""
    
    def __init__(self):
        self.flashing = False
        self.flash_start_time = 0
        self.flash_duration = 0
        self.flash_intensity = 0
    
    def trigger_flash(self, duration: int = 50, intensity: int = 100) -> None:
        """섬광 효과 시작"""
        self.flashing = True
        self.flash_start_time = pygame.time.get_ticks()
        self.flash_duration = duration
        self.flash_intensity = intensity
    
    def small_flash(self) -> None:
        """작은 섬광"""
        self.trigger_flash(30, 60)
    
    def medium_flash(self) -> None:
        """중간 섬광"""
        self.trigger_flash(50, 100)
    
    def large_flash(self) -> None:
        """큰 섬광"""
        self.trigger_flash(100, 150)
    
    def update(self) -> None:
        """섬광 상태 업데이트"""
        if self.flashing:
            elapsed = pygame.time.get_ticks() - self.flash_start_time
            if elapsed >= self.flash_duration:
                self.flashing = False
    
    def draw(self, surface: pygame.Surface) -> None:
        """섬광 그리기"""
        if not self.flashing:
            return
        
        elapsed = pygame.time.get_ticks() - self.flash_start_time
        progress = elapsed / self.flash_duration
        
        alpha = int(self.flash_intensity * (1 - progress))
        
        if alpha > 0:
            flash_surface = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
            flash_surface.fill((255, 255, 255, alpha))
            surface.blit(flash_surface, (0, 0))
    
    def is_flashing(self) -> bool:
        """섬광 중인지 확인"""
        return self.flashing