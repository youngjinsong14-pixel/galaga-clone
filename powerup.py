# powerup.py
"""
파워업 아이템 시스템
"""
import pygame
import random
import math
from typing import Optional
import settings


class PowerUp(pygame.sprite.Sprite):
    """파워업 아이템 스프라이트"""
    
    # 파워업 타입 정의
    SPEED_UP = 'speed_up'
    SHOT_POWER = 'shot_power'
    TRIPLE_SHOT = 'triple_shot'
    SHIELD = 'shield'
    EXTRA_LIFE = 'extra_life'
    RAPID_FIRE = 'rapid_fire'
    
    # 파워업 색상
    COLORS = {
        SPEED_UP: (100, 255, 100),      # 초록
        SHOT_POWER: (255, 100, 100),    # 빨강
        TRIPLE_SHOT: (100, 100, 255),   # 파랑
        SHIELD: (100, 255, 255),        # 시안
        EXTRA_LIFE: (255, 100, 255),    # 마젠타
        RAPID_FIRE: (255, 255, 100),    # 노랑
    }
    
    # 파워업 지속 시간 (밀리초, 0이면 영구)
    DURATIONS = {
        SPEED_UP: 10000,      # 10초
        SHOT_POWER: 15000,    # 15초
        TRIPLE_SHOT: 12000,   # 12초
        SHIELD: 8000,         # 8초
        EXTRA_LIFE: 0,        # 영구 (목숨 추가)
        RAPID_FIRE: 10000,    # 10초
    }
    
    def __init__(self, x: int, y: int, powerup_type: Optional[str] = None):
        """
        파워업 초기화
        
        Args:
            x: x 좌표
            y: y 좌표
            powerup_type: 파워업 타입 (None이면 랜덤)
        """
        super().__init__()
        
        # 타입 결정 (랜덤 또는 지정)
        if powerup_type is None:
            # 가중치 적용 랜덤 선택 (extra_life는 희귀)
            weights = [20, 20, 20, 15, 5, 20]  # speed, shot, triple, shield, life, rapid
            types = [self.SPEED_UP, self.SHOT_POWER, self.TRIPLE_SHOT, 
                    self.SHIELD, self.EXTRA_LIFE, self.RAPID_FIRE]
            self.powerup_type = random.choices(types, weights=weights)[0]
        else:
            self.powerup_type = powerup_type
        
        self.color = self.COLORS[self.powerup_type]
        self.duration = self.DURATIONS[self.powerup_type]
        
        # 이미지 생성
        self.size = 24
        self.image = self._create_image()
        self.rect = self.image.get_rect(center=(x, y))
        
        # 이동 및 애니메이션
        self.speed = 2
        self.float_offset = 0
        self.float_speed = 0.1
        self.rotation = 0
        self.rotation_speed = 3
        
        # 깜빡임 (사라지기 전 경고)
        self.spawn_time = pygame.time.get_ticks()
        self.lifetime = 8000  # 8초 후 사라짐
        self.blink_start = 6000  # 6초부터 깜빡임
        self.visible = True
    
    def _create_image(self) -> pygame.Surface:
        """파워업 이미지 생성"""
        surface = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        center = self.size // 2
        
        # 외곽 글로우
        pygame.draw.circle(surface, (*self.color, 100), (center, center), center)
        
        # 메인 원
        pygame.draw.circle(surface, self.color, (center, center), center - 4)
        
        # 밝은 중심
        pygame.draw.circle(surface, (255, 255, 255), (center, center), center - 8)
        pygame.draw.circle(surface, self.color, (center, center), center - 10)
        
        # 타입별 아이콘
        self._draw_icon(surface, center)
        
        return surface
    
    def _draw_icon(self, surface: pygame.Surface, center: int) -> None:
        """타입별 아이콘 그리기"""
        icon_color = (255, 255, 255)
        
        if self.powerup_type == self.SPEED_UP:
            # 화살표 (>>)
            pygame.draw.polygon(surface, icon_color, [
                (center - 6, center - 4),
                (center, center),
                (center - 6, center + 4)
            ])
            pygame.draw.polygon(surface, icon_color, [
                (center, center - 4),
                (center + 6, center),
                (center, center + 4)
            ])
        
        elif self.powerup_type == self.SHOT_POWER:
            # 폭발 모양
            pygame.draw.circle(surface, icon_color, (center, center), 4)
            for i in range(4):
                angle = i * math.pi / 2
                x1 = center + int(math.cos(angle) * 3)
                y1 = center + int(math.sin(angle) * 3)
                x2 = center + int(math.cos(angle) * 7)
                y2 = center + int(math.sin(angle) * 7)
                pygame.draw.line(surface, icon_color, (x1, y1), (x2, y2), 2)
        
        elif self.powerup_type == self.TRIPLE_SHOT:
            # 세 줄
            pygame.draw.line(surface, icon_color, (center - 4, center - 5), (center - 4, center + 5), 2)
            pygame.draw.line(surface, icon_color, (center, center - 5), (center, center + 5), 2)
            pygame.draw.line(surface, icon_color, (center + 4, center - 5), (center + 4, center + 5), 2)
        
        elif self.powerup_type == self.SHIELD:
            # 방패 모양
            pygame.draw.arc(surface, icon_color, 
                          (center - 6, center - 6, 12, 12), 
                          math.pi * 0.2, math.pi * 0.8, 2)
            pygame.draw.arc(surface, icon_color,
                          (center - 5, center - 3, 10, 10),
                          math.pi * 1.2, math.pi * 1.8, 2)
        
        elif self.powerup_type == self.EXTRA_LIFE:
            # 하트 모양
            pygame.draw.circle(surface, icon_color, (center - 3, center - 2), 3)
            pygame.draw.circle(surface, icon_color, (center + 3, center - 2), 3)
            pygame.draw.polygon(surface, icon_color, [
                (center - 6, center),
                (center, center + 6),
                (center + 6, center)
            ])
        
        elif self.powerup_type == self.RAPID_FIRE:
            # 번개 모양
            pygame.draw.polygon(surface, icon_color, [
                (center + 2, center - 6),
                (center - 3, center),
                (center, center),
                (center - 2, center + 6),
                (center + 3, center),
                (center, center)
            ])
    
    def update(self) -> None:
        """파워업 업데이트"""
        # 아래로 이동
        self.rect.y += self.speed
        
        # 좌우 흔들림
        self.float_offset += self.float_speed
        self.rect.x += int(math.sin(self.float_offset) * 0.5)
        
        # 화면 밖으로 나가면 제거
        if self.rect.top > settings.SCREEN_HEIGHT:
            self.kill()
        
        # 수명 체크
        elapsed = pygame.time.get_ticks() - self.spawn_time
        if elapsed > self.lifetime:
            self.kill()
        elif elapsed > self.blink_start:
            # 깜빡임
            self.visible = (elapsed // 100) % 2 == 0
    
    def draw(self, screen: pygame.Surface) -> None:
        """화면에 그리기"""
        if self.visible:
            screen.blit(self.image, self.rect)


class PowerUpManager:
    """파워업 드롭 관리"""
    
    def __init__(self):
        self.drop_chance = 0.15  # 15% 확률로 드롭
    
    def try_spawn(self, x: int, y: int, powerups_group: pygame.sprite.Group) -> bool:
        """
        적 처치 시 파워업 드롭 시도
        
        Args:
            x: 드롭 위치 x
            y: 드롭 위치 y
            powerups_group: 파워업 스프라이트 그룹
        
        Returns:
            드롭 성공 여부
        """
        if random.random() < self.drop_chance:
            powerup = PowerUp(x, y)
            powerups_group.add(powerup)
            return True
        return False
    
    def spawn_boss_powerup(self, x: int, y: int, powerups_group: pygame.sprite.Group) -> None:
        """
        보스 처치 시 확정 파워업 드롭 (좋은 아이템)
        
        Args:
            x: 드롭 위치 x
            y: 드롭 위치 y
            powerups_group: 파워업 스프라이트 그룹
        """
        # 보스는 좋은 아이템 드롭
        good_types = [PowerUp.TRIPLE_SHOT, PowerUp.SHIELD, PowerUp.RAPID_FIRE]
        powerup_type = random.choice(good_types)
        powerup = PowerUp(x, y, powerup_type)
        powerups_group.add(powerup)


class PlayerPowerUps:
    """플레이어의 현재 파워업 상태 관리 (중첩 시스템)"""
    
    def __init__(self):
        self.reset()
    
    def reset(self) -> None:
        """파워업 상태 초기화"""
        # 속도 (1.0 ~ 2.5배, 0.5씩 증가)
        self.speed_level = 0
        self.speed_boost = False
        self.speed_end_time = 0
        
        # 공격력 (1 ~ 4배)
        self.power_level = 0
        self.shot_power = 1
        self.shot_power_end_time = 0
        
        # 샷 개수 (1 → 3 → 5 → 7방향)
        self.shot_level = 0
        self.triple_shot = False
        self.triple_shot_end_time = 0
        
        # 쉴드 (1 ~ 3회 방어)
        self.shield_count = 0
        self.shield_active = False
        self.shield_end_time = 0
        
        # 연사 (1 ~ 3단계)
        self.rapid_level = 0
        self.rapid_fire = False
        self.rapid_fire_end_time = 0
    
    def apply_powerup(self, powerup: PowerUp) -> str:
        """
        파워업 적용 (중첩 가능)
        
        Args:
            powerup: 획득한 파워업
        
        Returns:
            적용된 파워업 이름
        """
        current_time = pygame.time.get_ticks()
        duration = powerup.duration
        
        if powerup.powerup_type == PowerUp.SPEED_UP:
            self.speed_boost = True
            self.speed_end_time = current_time + duration
            self.speed_level = min(self.speed_level + 1, 3)
            multiplier = self.get_speed_multiplier()
            return f"SPEED x{multiplier:.1f}!"
        
        elif powerup.powerup_type == PowerUp.SHOT_POWER:
            self.power_level = min(self.power_level + 1, 3)
            self.shot_power = 1 + self.power_level
            self.shot_power_end_time = current_time + duration
            return f"POWER x{self.shot_power}!"
        
        elif powerup.powerup_type == PowerUp.TRIPLE_SHOT:
            self.triple_shot = True
            self.triple_shot_end_time = current_time + duration
            self.shot_level = min(self.shot_level + 1, 3)
            shot_count = self.get_shot_count()
            return f"{shot_count}-WAY SHOT!"
        
        elif powerup.powerup_type == PowerUp.SHIELD:
            self.shield_active = True
            self.shield_end_time = current_time + duration
            self.shield_count = min(self.shield_count + 1, 3)
            return f"SHIELD x{self.shield_count}!"
        
        elif powerup.powerup_type == PowerUp.EXTRA_LIFE:
            return "EXTRA_LIFE"
        
        elif powerup.powerup_type == PowerUp.RAPID_FIRE:
            self.rapid_fire = True
            self.rapid_fire_end_time = current_time + duration
            self.rapid_level = min(self.rapid_level + 1, 3)
            return f"RAPID LV{self.rapid_level}!"
        
        return ""
    
    def update(self) -> None:
        """파워업 타이머 업데이트"""
        current_time = pygame.time.get_ticks()
        
        if self.speed_boost and current_time > self.speed_end_time:
            self.speed_boost = False
            self.speed_level = 0
        
        if self.power_level > 0 and current_time > self.shot_power_end_time:
            self.power_level = 0
            self.shot_power = 1
        
        if self.triple_shot and current_time > self.triple_shot_end_time:
            self.triple_shot = False
            self.shot_level = 0
        
        if self.shield_active and current_time > self.shield_end_time:
            self.shield_active = False
            self.shield_count = 0
        
        if self.rapid_fire and current_time > self.rapid_fire_end_time:
            self.rapid_fire = False
            self.rapid_level = 0
    
    def get_speed_multiplier(self) -> float:
        """속도 배율 반환 (1.0 ~ 2.5)"""
        if not self.speed_boost:
            return 1.0
        return 1.0 + (self.speed_level * 0.5)
    
    def get_shot_count(self) -> int:
        """샷 개수 반환 (1, 3, 5, 7)"""
        if not self.triple_shot:
            return 1
        return 1 + (self.shot_level * 2)
    
    def get_fire_delay(self) -> int:
        """발사 딜레이 반환 (밀리초)"""
        base_delay = 250
        if self.rapid_fire:
            # 레벨별 딜레이 감소: 125ms → 83ms → 62ms
            return base_delay // (1 + self.rapid_level)
        return base_delay
    
    def use_shield(self) -> bool:
        """
        쉴드 사용 (피격 시 호출)
        
        Returns:
            쉴드로 방어 성공 여부
        """
        if self.shield_active and self.shield_count > 0:
            self.shield_count -= 1
            if self.shield_count <= 0:
                self.shield_active = False
                self.shield_end_time = 0
            return True
        return False