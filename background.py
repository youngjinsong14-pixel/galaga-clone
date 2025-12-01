# background.py
"""
스크롤 배경 시스템
"""
import pygame
import random
import math
from typing import List, Tuple
import settings


class Star:
    """개별 별 클래스"""
    
    def __init__(self, x: int, y: int, size: int, speed: float, color: Tuple[int, int, int]):
        self.x = x
        self.y = y
        self.size = size
        self.speed = speed
        self.color = color
        self.twinkle_offset = random.random() * math.pi * 2
    
    def update(self) -> None:
        """별 위치 업데이트"""
        self.y += self.speed
        
        # 화면 아래로 나가면 위에서 다시 시작
        if self.y > settings.SCREEN_HEIGHT:
            self.y = -self.size
            self.x = random.randint(0, settings.SCREEN_WIDTH)
    
    def draw(self, surface: pygame.Surface) -> None:
        """별 그리기"""
        # 반짝임 효과
        twinkle = math.sin(pygame.time.get_ticks() * 0.005 + self.twinkle_offset)
        brightness = max(0.5, min(1.0, 0.75 + twinkle * 0.25))
        
        color = tuple(int(c * brightness) for c in self.color)
        
        pygame.draw.circle(surface, color, (int(self.x), int(self.y)), self.size)
        
        # 큰 별은 십자 효과
        if self.size >= 2:
            pygame.draw.line(surface, color,
                           (int(self.x) - self.size - 1, int(self.y)),
                           (int(self.x) + self.size + 1, int(self.y)), 1)
            pygame.draw.line(surface, color,
                           (int(self.x), int(self.y) - self.size - 1),
                           (int(self.x), int(self.y) + self.size + 1), 1)


class Nebula:
    """성운 클래스"""
    
    def __init__(self, x: int, y: int, radius: int, color: Tuple[int, int, int]):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.speed = 0.3
        self.surface = self._create_surface()
    
    def _create_surface(self) -> pygame.Surface:
        """성운 서피스 생성"""
        size = self.radius * 2
        surface = pygame.Surface((size, size), pygame.SRCALPHA)
        
        for r in range(self.radius, 0, -5):
            alpha = int(25 * (r / self.radius))
            pygame.draw.circle(surface, (*self.color, alpha), 
                             (self.radius, self.radius), r)
        
        return surface
    
    def update(self) -> None:
        """성운 위치 업데이트"""
        self.y += self.speed
        
        if self.y > settings.SCREEN_HEIGHT + self.radius:
            self.y = -self.radius * 2
            self.x = random.randint(0, settings.SCREEN_WIDTH)
    
    def draw(self, surface: pygame.Surface) -> None:
        """성운 그리기"""
        surface.blit(self.surface, 
                    (int(self.x) - self.radius, int(self.y) - self.radius))


class ShootingStar:
    """유성 클래스"""
    
    def __init__(self):
        self.reset()
    
    def reset(self) -> None:
        """유성 초기화"""
        self.active = False
        self.x = 0
        self.y = 0
        self.speed_x = 0
        self.speed_y = 0
        self.length = 0
        self.life = 0
    
    def spawn(self) -> None:
        """유성 생성"""
        self.active = True
        self.x = random.randint(0, settings.SCREEN_WIDTH)
        self.y = random.randint(-50, 0)
        
        # 대각선 방향
        angle = random.uniform(math.pi / 6, math.pi / 3)
        speed = random.uniform(8, 15)
        self.speed_x = math.cos(angle) * speed
        self.speed_y = math.sin(angle) * speed
        
        self.length = random.randint(20, 40)
        self.life = 60  # 프레임
    
    def update(self) -> None:
        """유성 업데이트"""
        if not self.active:
            # 랜덤하게 생성
            if random.random() < 0.002:  # 0.2% 확률
                self.spawn()
            return
        
        self.x += self.speed_x
        self.y += self.speed_y
        self.life -= 1
        
        if (self.life <= 0 or self.x > settings.SCREEN_WIDTH or 
            self.y > settings.SCREEN_HEIGHT):
            self.reset()
    
    def draw(self, surface: pygame.Surface) -> None:
        """유성 그리기"""
        if not self.active:
            return
        
        # 꼬리 그리기
        tail_x = self.x - self.speed_x * 3
        tail_y = self.y - self.speed_y * 3
        
        # 그라데이션 꼬리
        for i in range(5):
            alpha = 255 - i * 50
            start_x = self.x - self.speed_x * i * 0.5
            start_y = self.y - self.speed_y * i * 0.5
            end_x = self.x - self.speed_x * (i + 1) * 0.5
            end_y = self.y - self.speed_y * (i + 1) * 0.5
            
            color = (255, 255, 255, max(0, alpha))
            pygame.draw.line(surface, (255, 255, 255), 
                           (int(start_x), int(start_y)),
                           (int(end_x), int(end_y)), 
                           max(1, 3 - i))


class ScrollingBackground:
    """스크롤 배경 관리 클래스"""
    
    def __init__(self):
        self.stars: List[Star] = []
        self.nebulae: List[Nebula] = []
        self.shooting_stars: List[ShootingStar] = []
        
        self._create_stars()
        self._create_nebulae()
        self._create_shooting_stars()
    
    def _create_stars(self) -> None:
        """별 생성"""
        # 레이어별로 별 생성 (먼 별 = 느리고 작음, 가까운 별 = 빠르고 큼)
        
        # 먼 배경 별 (작고 느림)
        for _ in range(80):
            x = random.randint(0, settings.SCREEN_WIDTH)
            y = random.randint(0, settings.SCREEN_HEIGHT)
            size = 1
            speed = random.uniform(0.3, 0.7)
            brightness = random.randint(80, 150)
            color = (brightness, brightness, brightness)
            self.stars.append(Star(x, y, size, speed, color))
        
        # 중간 별
        for _ in range(40):
            x = random.randint(0, settings.SCREEN_WIDTH)
            y = random.randint(0, settings.SCREEN_HEIGHT)
            size = random.choice([1, 2])
            speed = random.uniform(0.8, 1.5)
            brightness = random.randint(150, 220)
            
            # 가끔 색이 있는 별
            if random.random() > 0.8:
                color = random.choice([
                    (brightness, brightness, int(brightness * 0.7)),  # 노란색
                    (int(brightness * 0.7), int(brightness * 0.8), brightness),  # 파란색
                    (brightness, int(brightness * 0.7), int(brightness * 0.7)),  # 빨간색
                ])
            else:
                color = (brightness, brightness, brightness)
            
            self.stars.append(Star(x, y, size, speed, color))
        
        # 가까운 밝은 별 (크고 빠름)
        for _ in range(15):
            x = random.randint(0, settings.SCREEN_WIDTH)
            y = random.randint(0, settings.SCREEN_HEIGHT)
            size = random.choice([2, 3])
            speed = random.uniform(1.8, 3.0)
            color = (255, 255, 255)
            self.stars.append(Star(x, y, size, speed, color))
    
    def _create_nebulae(self) -> None:
        """성운 생성"""
        nebula_colors = [
            (40, 20, 60),   # 보라색
            (20, 40, 60),   # 파란색
            (60, 20, 40),   # 붉은색
            (20, 50, 50),   # 청록색
        ]
        
        for _ in range(4):
            x = random.randint(0, settings.SCREEN_WIDTH)
            y = random.randint(0, settings.SCREEN_HEIGHT)
            radius = random.randint(100, 200)
            color = random.choice(nebula_colors)
            self.nebulae.append(Nebula(x, y, radius, color))
    
    def _create_shooting_stars(self) -> None:
        """유성 생성"""
        for _ in range(3):
            self.shooting_stars.append(ShootingStar())
    
    def update(self) -> None:
        """배경 업데이트"""
        for star in self.stars:
            star.update()
        
        for nebula in self.nebulae:
            nebula.update()
        
        for shooting_star in self.shooting_stars:
            shooting_star.update()
    
    def draw(self, surface: pygame.Surface) -> None:
        """배경 그리기"""
        # 기본 배경색
        surface.fill((5, 5, 15))
        
        # 성운 (가장 뒤)
        for nebula in self.nebulae:
            nebula.draw(surface)
        
        # 별
        for star in self.stars:
            star.draw(surface)
        
        # 유성
        for shooting_star in self.shooting_stars:
            shooting_star.draw(surface)