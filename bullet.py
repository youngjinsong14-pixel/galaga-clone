# bullet.py
"""
탄환 클래스 정의
플레이어와 적의 탄환, 다양한 무기 타입을 처리합니다.
"""
import pygame
import math
from typing import Literal, Optional, List
import settings


# 무기 타입 상수
WEAPON_NORMAL = 'normal'
WEAPON_LASER = 'laser'
WEAPON_MISSILE = 'missile'
WEAPON_HOMING = 'homing'
WEAPON_SPREAD = 'spread'
WEAPON_RAILGUN = 'railgun'
WEAPON_PLASMA = 'plasma'
WEAPON_WAVE = 'wave'

# 무기 정보
WEAPON_INFO = {
    WEAPON_NORMAL: {
        'name': 'Normal Shot',
        'damage': 1,
        'fire_delay': 250,
        'color': (0, 255, 255),
        'description': 'Basic weapon'
    },
    WEAPON_LASER: {
        'name': 'Laser Beam',
        'damage': 2,
        'fire_delay': 400,
        'color': (255, 0, 0),
        'description': 'Piercing laser'
    },
    WEAPON_MISSILE: {
        'name': 'Missile',
        'damage': 3,
        'fire_delay': 600,
        'color': (255, 165, 0),
        'description': 'High damage'
    },
    WEAPON_HOMING: {
        'name': 'Homing Shot',
        'damage': 1,
        'fire_delay': 350,
        'color': (0, 255, 0),
        'description': 'Tracks enemies'
    },
    WEAPON_SPREAD: {
        'name': 'Spread Shot',
        'damage': 1,
        'fire_delay': 300,
        'color': (255, 0, 255),
        'description': '5-way shot'
    },
    WEAPON_RAILGUN: {
        'name': 'Railgun',
        'damage': 5,
        'fire_delay': 800,
        'color': (0, 255, 255),
        'description': 'Ultra pierce'
    },
    WEAPON_PLASMA: {
        'name': 'Plasma Cannon',
        'damage': 4,
        'fire_delay': 500,
        'color': (150, 0, 255),
        'description': 'Explosive'
    },
    WEAPON_WAVE: {
        'name': 'Wave Beam',
        'damage': 2,
        'fire_delay': 200,
        'color': (255, 255, 0),
        'description': 'Wave pattern'
    },
}


class Bullet(pygame.sprite.Sprite):
    """탄환 스프라이트 클래스"""
    
    def __init__(self, x: int, y: int, 
                 bullet_type: Literal['player', 'enemy'],
                 image: pygame.Surface,
                 damage: int = 1,
                 angle: float = 0,
                 weapon_type: str = WEAPON_NORMAL):
        super().__init__()
        self.original_image = image.copy()
        self.bullet_type = bullet_type
        self.damage = damage
        self.angle = angle
        self.weapon_type = weapon_type
        self.hits = []
        
        # 속도 설정
        if bullet_type == 'player':
            base_speed = settings.BULLET_SPEED
            if weapon_type == WEAPON_LASER:
                base_speed = settings.BULLET_SPEED * 1.5
            elif weapon_type == WEAPON_MISSILE:
                base_speed = settings.BULLET_SPEED * 0.8
            elif weapon_type == WEAPON_HOMING:
                base_speed = settings.BULLET_SPEED * 0.9
            elif weapon_type == WEAPON_RAILGUN:
                base_speed = settings.BULLET_SPEED * 2.5
            elif weapon_type == WEAPON_PLASMA:
                base_speed = settings.BULLET_SPEED * 1.2
            elif weapon_type == WEAPON_WAVE:
                base_speed = settings.BULLET_SPEED * 1.3
            
            self.speed_x = math.sin(math.radians(angle)) * base_speed
            self.speed_y = -math.cos(math.radians(angle)) * base_speed
        else:
            base_speed = settings.ENEMY_BULLET_SPEED
            self.speed_x = math.sin(math.radians(angle)) * base_speed
            self.speed_y = math.cos(math.radians(angle)) * base_speed
        
        self.base_speed = base_speed
        
        # 무기별 특성
        self.piercing = (weapon_type in [WEAPON_LASER, WEAPON_RAILGUN])
        self.explosive = (weapon_type == WEAPON_PLASMA)
        self.wave_weapon = (weapon_type == WEAPON_WAVE)
        
        # 파동 무기용
        self.wave_offset = 0
        self.wave_amplitude = 30
        
        # 무기 타입별 이미지 생성
        self.image = self._create_weapon_image()
        
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y
        
        self.float_x = float(x)
        self.float_y = float(y)
        
        # 호밍 미사일용
        self.target = None
        self.homing_strength = 5
    
    def _create_weapon_image(self) -> pygame.Surface:
        """무기 타입별 이미지 생성"""
        if self.bullet_type == 'enemy':
            if self.angle != 0:
                return pygame.transform.rotate(self.original_image, -self.angle)
            return self.original_image.copy()
        
        if self.weapon_type == WEAPON_NORMAL:
            return self._create_normal_image()
        elif self.weapon_type == WEAPON_LASER:
            return self._create_laser_image()
        elif self.weapon_type == WEAPON_MISSILE:
            return self._create_missile_image()
        elif self.weapon_type == WEAPON_HOMING:
            return self._create_homing_image()
        elif self.weapon_type == WEAPON_SPREAD:
            return self._create_spread_image()
        elif self.weapon_type == WEAPON_RAILGUN:
            return self._create_railgun_image()
        elif self.weapon_type == WEAPON_PLASMA:
            return self._create_plasma_image()
        elif self.weapon_type == WEAPON_WAVE:
            return self._create_wave_image()
        else:
            return self.original_image.copy()
    
    def _create_normal_image(self) -> pygame.Surface:
        """일반 탄환 이미지"""
        surface = pygame.Surface((6, 15), pygame.SRCALPHA)
        pygame.draw.rect(surface, (0, 255, 255), (1, 0, 4, 15))
        pygame.draw.rect(surface, (255, 255, 255), (2, 0, 2, 15))
        
        if self.damage > 1:
            glow = pygame.Surface((10, 19), pygame.SRCALPHA)
            pygame.draw.rect(glow, (255, 100, 100, 100), (0, 0, 10, 19))
            glow.blit(surface, (2, 2))
            return glow
        
        if self.angle != 0:
            return pygame.transform.rotate(surface, -self.angle)
        return surface
    
    def _create_laser_image(self) -> pygame.Surface:
        """레이저 이미지"""
        surface = pygame.Surface((8, 30), pygame.SRCALPHA)
        pygame.draw.rect(surface, (255, 50, 50, 100), (0, 0, 8, 30))
        pygame.draw.rect(surface, (255, 100, 100), (1, 0, 6, 30))
        pygame.draw.rect(surface, (255, 200, 200), (2, 0, 4, 30))
        pygame.draw.rect(surface, (255, 255, 255), (3, 0, 2, 30))
        
        if self.angle != 0:
            return pygame.transform.rotate(surface, -self.angle)
        return surface
    
    def _create_missile_image(self) -> pygame.Surface:
        """미사일 이미지"""
        surface = pygame.Surface((10, 20), pygame.SRCALPHA)
        pygame.draw.rect(surface, (150, 150, 150), (2, 4, 6, 12))
        pygame.draw.polygon(surface, (255, 100, 0), [
            (5, 0), (2, 6), (8, 6)
        ])
        pygame.draw.polygon(surface, (100, 100, 100), [
            (0, 14), (2, 10), (2, 16)
        ])
        pygame.draw.polygon(surface, (100, 100, 100), [
            (10, 14), (8, 10), (8, 16)
        ])
        pygame.draw.polygon(surface, (255, 200, 0), [
            (3, 16), (5, 20), (7, 16)
        ])
        pygame.draw.polygon(surface, (255, 100, 0), [
            (4, 16), (5, 18), (6, 16)
        ])
        
        if self.angle != 0:
            return pygame.transform.rotate(surface, -self.angle)
        return surface
    
    def _create_homing_image(self) -> pygame.Surface:
        """호밍탄 이미지"""
        surface = pygame.Surface((12, 12), pygame.SRCALPHA)
        pygame.draw.circle(surface, (0, 255, 0, 150), (6, 6), 6)
        pygame.draw.circle(surface, (100, 255, 100), (6, 6), 4)
        pygame.draw.circle(surface, (200, 255, 200), (6, 6), 2)
        return surface
    
    def _create_spread_image(self) -> pygame.Surface:
        """스프레드샷 이미지"""
        surface = pygame.Surface((8, 12), pygame.SRCALPHA)
        pygame.draw.ellipse(surface, (255, 0, 255), (0, 0, 8, 12))
        pygame.draw.ellipse(surface, (255, 150, 255), (2, 2, 4, 8))
        
        if self.angle != 0:
            return pygame.transform.rotate(surface, -self.angle)
        return surface
    
    def _create_railgun_image(self) -> pygame.Surface:
        """레일건 이미지"""
        surface = pygame.Surface((10, 40), pygame.SRCALPHA)
        pygame.draw.rect(surface, (0, 255, 255, 150), (0, 0, 10, 40))
        pygame.draw.rect(surface, (150, 255, 255), (2, 0, 6, 40))
        pygame.draw.rect(surface, (255, 255, 255), (4, 0, 2, 40))
        
        for i in range(0, 40, 8):
            pygame.draw.line(surface, (200, 255, 255), (1, i), (9, i+4), 1)
        
        if self.angle != 0:
            return pygame.transform.rotate(surface, -self.angle)
        return surface
    
    def _create_plasma_image(self) -> pygame.Surface:
        """플라즈마 캐논 이미지"""
        surface = pygame.Surface((16, 16), pygame.SRCALPHA)
        pygame.draw.circle(surface, (150, 0, 255, 200), (8, 8), 8)
        pygame.draw.circle(surface, (200, 50, 255), (8, 8), 6)
        pygame.draw.circle(surface, (255, 100, 255), (8, 8), 4)
        pygame.draw.circle(surface, (255, 200, 255), (8, 8), 2)
        pygame.draw.circle(surface, (255, 255, 255), (8, 8), 7, 1)
        return surface
    
    def _create_wave_image(self) -> pygame.Surface:
        """웨이브 빔 이미지"""
        surface = pygame.Surface((12, 20), pygame.SRCALPHA)
        for i in range(5):
            y = i * 4
            alpha = 255 - i * 40
            pygame.draw.ellipse(surface, (255, 255, 0, alpha), (0, y, 12, 8))
        pygame.draw.rect(surface, (255, 255, 200), (5, 0, 2, 20))
        
        if self.angle != 0:
            return pygame.transform.rotate(surface, -self.angle)
        return surface
    
    def set_target(self, target) -> None:
        """호밍 타겟 설정"""
        self.target = target
    
    def find_nearest_enemy(self, enemies) -> None:
        """가장 가까운 적 찾기"""
        if self.weapon_type != WEAPON_HOMING:
            return
        
        nearest = None
        min_dist = float('inf')
        
        for enemy in enemies:
            dx = enemy.rect.centerx - self.rect.centerx
            dy = enemy.rect.centery - self.rect.centery
            dist = math.sqrt(dx**2 + dy**2)
            
            if dist < min_dist:
                min_dist = dist
                nearest = enemy
        
        self.target = nearest
    
    def update(self, enemies=None) -> None:
        """탄환 위치 업데이트"""
        if self.weapon_type == WEAPON_HOMING and self.bullet_type == 'player':
            if enemies:
                self.find_nearest_enemy(enemies)
            
            if self.target and self.target.alive():
                dx = self.target.rect.centerx - self.rect.centerx
                dy = self.target.rect.centery - self.rect.centery
                dist = math.sqrt(dx**2 + dy**2)
                
                if dist > 0:
                    target_angle = math.atan2(dx, -dy)
                    current_angle = math.atan2(self.speed_x, -self.speed_y)
                    
                    angle_diff = target_angle - current_angle
                    while angle_diff > math.pi:
                        angle_diff -= 2 * math.pi
                    while angle_diff < -math.pi:
                        angle_diff += 2 * math.pi
                    
                    turn_rate = 0.1
                    new_angle = current_angle + angle_diff * turn_rate
                    
                    self.speed_x = math.sin(new_angle) * self.base_speed
                    self.speed_y = -math.cos(new_angle) * self.base_speed
        
        if self.wave_weapon and self.bullet_type == 'player':
            self.wave_offset += 0.3
            wave_x = math.sin(self.wave_offset) * self.wave_amplitude
            self.float_x += self.speed_x + wave_x * 0.1
        else:
            self.float_x += self.speed_x
        
        self.float_y += self.speed_y
        
        self.rect.centerx = int(self.float_x)
        self.rect.centery = int(self.float_y)
        
        if (self.rect.bottom < 0 or self.rect.top > settings.SCREEN_HEIGHT or
            self.rect.right < 0 or self.rect.left > settings.SCREEN_WIDTH):
            self.kill()
    
    def can_hit(self, enemy) -> bool:
        """해당 적을 맞출 수 있는지"""
        if not self.piercing:
            return True
        return id(enemy) not in self.hits
    
    def register_hit(self, enemy) -> None:
        """적 맞춤 기록"""
        if self.piercing:
            self.hits.append(id(enemy))


class TractorBeam(pygame.sprite.Sprite):
    """트랙터 빔 클래스"""
    
    def __init__(self, x: int, y: int, image: pygame.Surface):
        super().__init__()
        self.image = image.copy()
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.top = y
        self.speed = settings.TRACTOR_BEAM_SPEED
        self.capturing = False
        self.capture_start_time = 0
    
    def update(self) -> None:
        if not self.capturing:
            self.rect.y += self.speed
            if self.rect.top > settings.SCREEN_HEIGHT:
                self.kill()
    
    def start_capture(self) -> None:
        self.capturing = True
        self.capture_start_time = pygame.time.get_ticks()
    
    def is_capture_complete(self) -> bool:
        if not self.capturing:
            return False
        elapsed = pygame.time.get_ticks() - self.capture_start_time
        return elapsed >= settings.TRACTOR_BEAM_CAPTURE_TIME