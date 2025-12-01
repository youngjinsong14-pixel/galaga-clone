# player.py
"""
플레이어 클래스 정의
"""
import pygame
import math
from typing import Optional
import settings
from bullet import (Bullet, WEAPON_NORMAL, WEAPON_LASER, WEAPON_MISSILE, 
                   WEAPON_HOMING, WEAPON_SPREAD, WEAPON_RAILGUN, 
                   WEAPON_PLASMA, WEAPON_WAVE, WEAPON_INFO)
from powerup import PlayerPowerUps


class Player(pygame.sprite.Sprite):
    """플레이어 스프라이트 클래스"""
    
    # 무기 목록
    WEAPONS = [WEAPON_NORMAL, WEAPON_LASER, WEAPON_MISSILE, WEAPON_HOMING, 
                        WEAPON_SPREAD, WEAPON_RAILGUN, WEAPON_PLASMA, WEAPON_WAVE]
    
    def __init__(self, x: int, y: int, image: pygame.Surface,
                 bullet_image: pygame.Surface):
        super().__init__()
        self.original_image = image.copy()
        self.image = image.copy()
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y
        self.bullet_image = bullet_image
        
        # 상태
        self.base_speed = settings.PLAYER_SPEED
        self.speed = self.base_speed
        self.lives = settings.PLAYER_LIVES
        self.is_double_fighter = False
        self.captured_ship: Optional[pygame.Surface] = None
        
        # 무기 시스템
        self.current_weapon_index = 0
        self.current_weapon = WEAPON_NORMAL
        self.weapon_changing = False
        self.weapon_change_time = 0
        
        # 발사 관련
        self.last_shot_time = 0
        self.base_fire_delay = settings.PLAYER_FIRE_DELAY
        self.fire_delay = self.base_fire_delay
        
        # 무적 시간
        self.invulnerable = False
        self.invulnerable_start_time = 0
        self.invulnerable_duration = 2000
        
        # 파워업 시스템
        self.powerups = PlayerPowerUps()
        
        # 쉴드 시각 효과
        self.shield_angle = 0
        
        # 궁극기 시스템
        self.ultimate_charge = 0
        self.ultimate_max = 100
    
    def update(self, keys: pygame.key.ScancodeWrapper) -> None:
        """플레이어 상태 업데이트"""
        # 파워업 타이머 업데이트
        self.powerups.update()
        
        # 파워업 효과 적용
        speed_mult = self.powerups.get_speed_multiplier()
        self.speed = int(self.base_speed * speed_mult)
        
        # 무기별 발사 딜레이 적용
        weapon_delay = WEAPON_INFO[self.current_weapon]['fire_delay']
        if self.powerups.rapid_fire:
            weapon_delay = weapon_delay // 2
        self.fire_delay = weapon_delay
        
        # 좌우 이동
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.rect.x += self.speed
        
        # 상하 이동
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.rect.y -= self.speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.rect.y += self.speed
        
        # 화면 경계 처리 (좌우)
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > settings.SCREEN_WIDTH:
            self.rect.right = settings.SCREEN_WIDTH
        
        # 화면 경계 처리 (상하)
        min_y = settings.SCREEN_HEIGHT // 2
        max_y = settings.SCREEN_HEIGHT - 20
        if self.rect.top < min_y:
            self.rect.top = min_y
        if self.rect.bottom > max_y:
            self.rect.bottom = max_y
        
        # 무적 시간 처리
        if self.invulnerable:
            elapsed = pygame.time.get_ticks() - self.invulnerable_start_time
            if elapsed >= self.invulnerable_duration:
                self.invulnerable = False
        
        # 쉴드 애니메이션
        self.shield_angle += 5
    
    def change_weapon(self, direction: int) -> str:
        """
        무기 변경
        
        Args:
            direction: 1이면 다음, -1이면 이전
            
        Returns:
            변경된 무기 이름
        """
        self.current_weapon_index = (self.current_weapon_index + direction) % len(self.WEAPONS)
        self.current_weapon = self.WEAPONS[self.current_weapon_index]
        self.weapon_changing = True
        self.weapon_change_time = pygame.time.get_ticks()
        return WEAPON_INFO[self.current_weapon]['name']

    def add_ultimate_charge(self, amount: int) -> None:
        """궁극기 게이지 충전"""
        self.ultimate_charge = min(self.ultimate_charge + amount, self.ultimate_max)
    
    def can_use_ultimate(self) -> bool:
        """궁극기 사용 가능 여부"""
        return self.ultimate_charge >= self.ultimate_max
    
    def use_ultimate(self) -> bool:
        """
        궁극기 사용
        
        Returns:
            사용 성공 여부
        """
        if not self.can_use_ultimate():
            return False
        
        self.ultimate_charge = 0
        return True
    

    def get_weapon_name(self) -> str:
        """현재 무기 이름 반환"""
        return WEAPON_INFO[self.current_weapon]['name']
    
    def get_weapon_color(self) -> tuple:
        """현재 무기 색상 반환"""
        return WEAPON_INFO[self.current_weapon]['color']
    
    def shoot(self, bullets_group: pygame.sprite.Group) -> bool:
        """탄환 발사"""
        current_time = pygame.time.get_ticks()
        if current_time - self.last_shot_time < self.fire_delay:
            return False
        
        self.last_shot_time = current_time
        
        # 파워업 데미지 보너스
        base_damage = WEAPON_INFO[self.current_weapon]['damage']
        damage = base_damage * self.powerups.shot_power
        
        # 트리플 샷 파워업
        if self.powerups.triple_shot:
            self._shoot_multi(bullets_group, damage)
        elif self.current_weapon == WEAPON_SPREAD:
            self._shoot_spread(bullets_group, damage)
        elif self.is_double_fighter:
            self._shoot_double(bullets_group, damage)
        else:
            self._shoot_single(bullets_group, damage)
        
        return True
    
    def _shoot_single(self, bullets_group: pygame.sprite.Group, damage: int) -> None:
        """단발 발사"""
        bullet = Bullet(
            self.rect.centerx,
            self.rect.top,
            'player',
            self.bullet_image,
            damage=damage,
            weapon_type=self.current_weapon
        )
        bullets_group.add(bullet)
    
    def _shoot_double(self, bullets_group: pygame.sprite.Group, damage: int) -> None:
        """더블 파이터 발사"""
        bullet1 = Bullet(
            self.rect.left + 10,
            self.rect.top,
            'player',
            self.bullet_image,
            damage=damage,
            weapon_type=self.current_weapon
        )
        bullet2 = Bullet(
            self.rect.right - 10,
            self.rect.top,
            'player',
            self.bullet_image,
            damage=damage,
            weapon_type=self.current_weapon
        )
        bullets_group.add(bullet1, bullet2)
    
    def _shoot_multi(self, bullets_group: pygame.sprite.Group, damage: int) -> None:
        """멀티 샷 발사 (3, 5, 7방향)"""
        shot_count = self.powerups.get_shot_count()
        
        if shot_count == 3:
            angles = [-15, 0, 15]
        elif shot_count == 5:
            angles = [-30, -15, 0, 15, 30]
        elif shot_count == 7:
            angles = [-45, -30, -15, 0, 15, 30, 45]
        else:
            angles = [0]
        
        for angle in angles:
            bullet = Bullet(
                self.rect.centerx,
                self.rect.top,
                'player',
                self.bullet_image,
                damage=damage,
                angle=angle,
                weapon_type=self.current_weapon
            )
            bullets_group.add(bullet)
    
    def _shoot_spread(self, bullets_group: pygame.sprite.Group, damage: int) -> None:
        """스프레드 샷 발사 (5방향)"""
        angles = [-30, -15, 0, 15, 30]
        for angle in angles:
            bullet = Bullet(
                self.rect.centerx,
                self.rect.top,
                'player',
                self.bullet_image,
                damage=damage,
                angle=angle,
                weapon_type=WEAPON_SPREAD
            )
            bullets_group.add(bullet)
    
    def take_damage(self) -> bool:
        """피해를 입음"""
        if self.invulnerable:
            return True
        
        # 쉴드 체크 (중첩 쉴드)
        if self.powerups.use_shield():
            self.invulnerable = True
            self.invulnerable_start_time = pygame.time.get_ticks()
            return True
        
        if self.is_double_fighter:
            self.is_double_fighter = False
            self.invulnerable = True
            self.invulnerable_start_time = pygame.time.get_ticks()
            return True
        else:
            self.lives -= 1
            if self.lives > 0:
                self.invulnerable = True
                self.invulnerable_start_time = pygame.time.get_ticks()
                self.powerups.reset()
                return True
            return False
    
    def add_life(self) -> None:
        """목숨 추가"""
        self.lives += 1
        if self.lives > 5:
            self.lives = 5
    
    def get_captured(self) -> None:
        """트랙터 빔에 포획됨"""
        self.captured_ship = self.image.copy()
        self.kill()
    
    def rescue_ship(self) -> None:
        """포획된 기체 구출"""
        if self.captured_ship:
            self.is_double_fighter = True
            self.captured_ship = None
    
    def draw(self, surface: pygame.Surface) -> None:
        """플레이어 그리기"""
        if self.invulnerable:
            if (pygame.time.get_ticks() // 100) % 2 == 0:
                surface.blit(self.image, self.rect)
        else:
            surface.blit(self.image, self.rect)
        
        if self.powerups.shield_active:
            self._draw_shield(surface)
        
        if self.powerups.speed_boost:
            self._draw_speed_effect(surface)
        
        # 무기 표시
        self._draw_weapon_indicator(surface)
    
    def _draw_shield(self, surface: pygame.Surface) -> None:
        """쉴드 이펙트"""
        shield_surface = pygame.Surface((60, 60), pygame.SRCALPHA)
        center = 30
        
        for i in range(6):
            angle = math.radians(self.shield_angle + i * 60)
            x = center + int(math.cos(angle) * 25)
            y = center + int(math.sin(angle) * 25)
            pygame.draw.circle(shield_surface, (100, 255, 255, 150), (x, y), 5)
        
        pygame.draw.circle(shield_surface, (100, 255, 255, 80), (center, center), 28, 2)
        
        shield_rect = shield_surface.get_rect(center=self.rect.center)
        surface.blit(shield_surface, shield_rect)
    
    def _draw_speed_effect(self, surface: pygame.Surface) -> None:
        """스피드 부스트 이펙트"""
        flame_surface = pygame.Surface((30, 20), pygame.SRCALPHA)
        
        pygame.draw.polygon(flame_surface, (100, 255, 100, 200), [
            (10, 0), (15, 20), (20, 0)
        ])
        pygame.draw.polygon(flame_surface, (200, 255, 200, 150), [
            (12, 0), (15, 15), (18, 0)
        ])
        
        flame_rect = flame_surface.get_rect(centerx=self.rect.centerx, top=self.rect.bottom - 5)
        surface.blit(flame_surface, flame_rect)
    
    def _draw_weapon_indicator(self, surface: pygame.Surface) -> None:
        """현재 무기 표시"""
        color = self.get_weapon_color()
        
        # 플레이어 위에 작은 점으로 무기 표시
        indicator_y = self.rect.top - 8
        pygame.draw.circle(surface, color, (self.rect.centerx, indicator_y), 4)
        pygame.draw.circle(surface, (255, 255, 255), (self.rect.centerx, indicator_y), 4, 1)