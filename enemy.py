# enemy.py
"""
적 클래스 정의
다양한 종류의 적을 포함합니다.
"""
import pygame
import random
import math
from typing import Optional, Tuple, List
import settings
from bullet import Bullet, TractorBeam


class Enemy(pygame.sprite.Sprite):
    """적 스프라이트 클래스"""
    
    # 적 타입 상수
    TYPE_NORMAL = 'normal'
    TYPE_BOSS = 'boss'
    TYPE_FAST = 'fast'
    TYPE_TANK = 'tank'
    TYPE_KAMIKAZE = 'kamikaze'
    TYPE_SPLITTER = 'splitter'
    
    def __init__(self, x: int, y: int, enemy_type: str,
                 image: pygame.Surface, bullet_image: pygame.Surface,
                 is_split_child: bool = False):
        """
        적 초기화
        
        Args:
            x: 초기 x 좌표
            y: 초기 y 좌표
            enemy_type: 적 타입
            image: 적 이미지
            bullet_image: 탄환 이미지
            is_split_child: 분열로 생성된 자식인지 여부
        """
        super().__init__()
        self.enemy_type = enemy_type
        self.bullet_image = bullet_image
        self.is_split_child = is_split_child
        
        # 타입별 이미지 생성
        self.image = self._create_type_image(image)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        
        # 편대 위치
        self.formation_x = x
        self.formation_y = y
        
        # 진입 경로
        self.path: List[Tuple[float, float]] = []
        self.path_index = 0
        self.in_formation = True
        
        # 타입별 스탯 설정
        self._setup_stats()
        
        # 보스 전용
        self.is_boss = (enemy_type == self.TYPE_BOSS)
        self.has_captured_ship = False
        self.tractor_beam_cooldown = 0
        self.tractor_beam_delay = 5000
        
        # 보스 패턴 관련
        self.boss_pattern = 'idle'
        self.pattern_timer = 0
        self.pattern_duration = 0
        self.attack_cooldown = 0
        self.dive_target_x = 0
        self.dive_target_y = 0
        self.dive_return = False
        self.spiral_angle = 0
        self.strafe_direction = 1
        
        # 카미카제 전용
        self.kamikaze_activated = False
        self.target_player = None
        
        # 분열 전용
        self.has_split = False
    
    def _create_type_image(self, base_image: pygame.Surface) -> pygame.Surface:
        """타입별 이미지 생성"""
        if self.enemy_type == self.TYPE_NORMAL:
            return base_image.copy()
        
        elif self.enemy_type == self.TYPE_BOSS:
            return base_image.copy()
        
        elif self.enemy_type == self.TYPE_FAST:
            return self._create_fast_enemy_image()
        
        elif self.enemy_type == self.TYPE_TANK:
            return self._create_tank_enemy_image()
        
        elif self.enemy_type == self.TYPE_KAMIKAZE:
            return self._create_kamikaze_enemy_image()
        
        elif self.enemy_type == self.TYPE_SPLITTER:
            return self._create_splitter_enemy_image()
        
        return base_image.copy()
    
    def _create_fast_enemy_image(self) -> pygame.Surface:
        """빠른 적 이미지 생성 - 날렵한 모양"""
        width, height = 30, 30
        surface = pygame.Surface((width, height), pygame.SRCALPHA)
        
        # 몸체 (날렵한 삼각형)
        body_color = (100, 255, 100)  # 초록색
        dark_color = (50, 180, 50)
        
        pygame.draw.polygon(surface, body_color, [
            (15, 0), (0, 25), (30, 25)
        ])
        pygame.draw.polygon(surface, dark_color, [
            (15, 5), (5, 22), (25, 22)
        ])
        
        # 눈
        pygame.draw.circle(surface, (255, 255, 0), (10, 15), 3)
        pygame.draw.circle(surface, (255, 255, 0), (20, 15), 3)
        pygame.draw.circle(surface, (0, 0, 0), (11, 15), 1)
        pygame.draw.circle(surface, (0, 0, 0), (21, 15), 1)
        
        # 속도 라인
        pygame.draw.line(surface, (150, 255, 150), (5, 26), (5, 30), 2)
        pygame.draw.line(surface, (150, 255, 150), (15, 26), (15, 30), 2)
        pygame.draw.line(surface, (150, 255, 150), (25, 26), (25, 30), 2)
        
        return surface
    
    def _create_tank_enemy_image(self) -> pygame.Surface:
        """탱크 적 이미지 생성 - 크고 단단한 모양"""
        width, height = 44, 40
        surface = pygame.Surface((width, height), pygame.SRCALPHA)
        
        # 외곽 장갑
        armor_color = (100, 100, 150)  # 회청색
        dark_color = (60, 60, 100)
        highlight = (150, 150, 200)
        
        pygame.draw.ellipse(surface, armor_color, (2, 5, 40, 30))
        pygame.draw.ellipse(surface, dark_color, (2, 15, 40, 18))
        pygame.draw.ellipse(surface, highlight, (8, 8, 28, 12))
        
        # 장갑판
        pygame.draw.rect(surface, dark_color, (0, 10, 8, 20))
        pygame.draw.rect(surface, dark_color, (36, 10, 8, 20))
        pygame.draw.rect(surface, armor_color, (1, 12, 6, 16))
        pygame.draw.rect(surface, armor_color, (37, 12, 6, 16))
        
        # 눈 (붉은색 - 위협적)
        pygame.draw.circle(surface, (255, 50, 50), (15, 18), 4)
        pygame.draw.circle(surface, (255, 50, 50), (29, 18), 4)
        pygame.draw.circle(surface, (255, 200, 200), (14, 17), 2)
        pygame.draw.circle(surface, (255, 200, 200), (28, 17), 2)
        
        # 체력바 표시용 상단 장식
        pygame.draw.rect(surface, (80, 80, 120), (12, 2, 20, 4))
        
        return surface
    
    def _create_kamikaze_enemy_image(self) -> pygame.Surface:
        """자폭 적 이미지 생성 - 불꽃 모양"""
        width, height = 32, 32
        surface = pygame.Surface((width, height), pygame.SRCALPHA)
        
        # 몸체 (오렌지/빨강 - 폭발적)
        body_color = (255, 100, 0)
        dark_color = (200, 50, 0)
        glow_color = (255, 200, 50)
        
        # 중앙 몸체
        pygame.draw.circle(surface, body_color, (16, 16), 12)
        pygame.draw.circle(surface, dark_color, (16, 18), 10)
        pygame.draw.circle(surface, glow_color, (16, 14), 6)
        
        # 불꽃 이펙트
        flame_points = [
            [(16, 0), (12, 8), (20, 8)],
            [(4, 8), (8, 14), (10, 8)],
            [(28, 8), (22, 8), (24, 14)],
        ]
        for points in flame_points:
            pygame.draw.polygon(surface, (255, 150, 0), points)
        
        # 위험 표시 눈
        pygame.draw.circle(surface, (255, 255, 255), (12, 14), 3)
        pygame.draw.circle(surface, (255, 255, 255), (20, 14), 3)
        pygame.draw.circle(surface, (255, 0, 0), (12, 14), 2)
        pygame.draw.circle(surface, (255, 0, 0), (20, 14), 2)
        
        return surface
    
    def _create_splitter_enemy_image(self) -> pygame.Surface:
        """분열 적 이미지 생성 - 세포 분열 모양"""
        if self.is_split_child:
            # 분열 후 작은 버전
            width, height = 24, 24
        else:
            width, height = 38, 38
        
        surface = pygame.Surface((width, height), pygame.SRCALPHA)
        
        # 몸체 (보라색 - 신비로운)
        body_color = (180, 80, 220)
        dark_color = (120, 40, 160)
        nucleus_color = (255, 150, 255)
        
        center = width // 2
        radius = width // 2 - 2
        
        # 외막
        pygame.draw.circle(surface, body_color, (center, center), radius)
        pygame.draw.circle(surface, dark_color, (center, center + 2), radius - 2)
        
        # 핵 (분열 전에는 2개)
        if not self.is_split_child:
            pygame.draw.circle(surface, nucleus_color, (center - 6, center - 2), 5)
            pygame.draw.circle(surface, nucleus_color, (center + 6, center - 2), 5)
            pygame.draw.circle(surface, (255, 255, 255), (center - 7, center - 3), 2)
            pygame.draw.circle(surface, (255, 255, 255), (center + 5, center - 3), 2)
        else:
            pygame.draw.circle(surface, nucleus_color, (center, center - 2), 4)
            pygame.draw.circle(surface, (255, 255, 255), (center - 1, center - 3), 2)
        
        # 분열 라인 (분열 전에만)
        if not self.is_split_child:
            pygame.draw.line(surface, dark_color, (center, 4), (center, height - 4), 2)
        
        return surface
    
    def _setup_stats(self) -> None:
        """타입별 스탯 설정"""
        if self.enemy_type == self.TYPE_NORMAL:
            self.speed = settings.ENEMY_SPEED
            self.fire_chance = settings.ENEMY_FIRE_CHANCE
            self.max_hp = 1
            self.score_value = settings.SCORE_ENEMY
        
        elif self.enemy_type == self.TYPE_BOSS:
            self.speed = settings.ENEMY_SPEED
            self.fire_chance = settings.ENEMY_FIRE_CHANCE * 2
            self.max_hp = 5
            self.score_value = settings.SCORE_BOSS
        
        elif self.enemy_type == self.TYPE_FAST:
            self.speed = settings.ENEMY_SPEED * 2.5
            self.fire_chance = settings.ENEMY_FIRE_CHANCE * 0.5
            self.max_hp = 1
            self.score_value = settings.SCORE_ENEMY + 50
        
        elif self.enemy_type == self.TYPE_TANK:
            self.speed = settings.ENEMY_SPEED * 0.6
            self.fire_chance = settings.ENEMY_FIRE_CHANCE * 1.5
            self.max_hp = 4
            self.score_value = settings.SCORE_ENEMY + 100
        
        elif self.enemy_type == self.TYPE_KAMIKAZE:
            self.speed = settings.ENEMY_SPEED * 1.2
            self.fire_chance = 0  # 발사 안함
            self.max_hp = 1
            self.score_value = settings.SCORE_ENEMY + 30
        
        elif self.enemy_type == self.TYPE_SPLITTER:
            if self.is_split_child:
                self.speed = settings.ENEMY_SPEED * 1.5
                self.fire_chance = settings.ENEMY_FIRE_CHANCE
                self.max_hp = 1
                self.score_value = settings.SCORE_ENEMY
            else:
                self.speed = settings.ENEMY_SPEED * 0.8
                self.fire_chance = settings.ENEMY_FIRE_CHANCE
                self.max_hp = 2
                self.score_value = settings.SCORE_ENEMY + 50
        
        else:
            self.speed = settings.ENEMY_SPEED
            self.fire_chance = settings.ENEMY_FIRE_CHANCE
            self.max_hp = 1
            self.score_value = settings.SCORE_ENEMY
        
        self.hp = self.max_hp
    
    def set_entry_path(self, path_type: str) -> None:
        """진입 경로 설정"""
        start_x = self.rect.x
        start_y = -50
        
        if path_type == 'circle':
            center_x = settings.SCREEN_WIDTH // 2
            center_y = settings.SCREEN_HEIGHT // 4
            radius = 150
            steps = 30
            
            for i in range(steps):
                angle = math.pi + (math.pi * i / steps)
                x = center_x + radius * math.cos(angle)
                y = center_y + radius * math.sin(angle)
                self.path.append((x, y))
        
        elif path_type == 'zigzag':
            steps = 20
            amplitude = 100
            
            for i in range(steps):
                x = start_x + amplitude * math.sin(i * 0.5)
                y = start_y + i * 30
                self.path.append((x, y))
        
        elif path_type == 'fast_dive':
            # 빠른 적용 급강하 경로
            steps = 10
            for i in range(steps):
                x = start_x + math.sin(i * 0.3) * 50
                y = start_y + i * 50
                self.path.append((x, y))
        
        else:  # straight
            steps = 15
            for i in range(steps):
                x = start_x
                y = start_y + i * 30
                self.path.append((x, y))
        
        self.path.append((self.formation_x, self.formation_y))
    
    def set_player_reference(self, player) -> None:
        """플레이어 참조 설정 (카미카제용)"""
        self.target_player = player
    
    def update(self) -> None:
        """적 상태 업데이트"""
        if not self.in_formation:
            self._follow_entry_path()
        else:
            if self.is_boss:
                self._update_boss_pattern()
            elif self.enemy_type == self.TYPE_KAMIKAZE:
                self._update_kamikaze()
            else:
                self._idle_movement()
        
        # 쿨다운 감소
        if self.tractor_beam_cooldown > 0:
            self.tractor_beam_cooldown -= 16
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 16
    
    def _follow_entry_path(self) -> None:
        """진입 경로를 따라 이동"""
        if self.path_index < len(self.path):
            target_x, target_y = self.path[self.path_index]
            
            dx = target_x - self.rect.centerx
            dy = target_y - self.rect.centery
            distance = math.sqrt(dx**2 + dy**2)
            
            if distance < 5:
                self.path_index += 1
            else:
                move_speed = self.speed
                if self.enemy_type == self.TYPE_FAST:
                    move_speed = self.speed * 1.5
                
                self.rect.x += (dx / distance) * move_speed
                self.rect.y += (dy / distance) * move_speed
        else:
            self.in_formation = True
            
            # 카미카제는 편대 도착 후 바로 돌진 모드
            if self.enemy_type == self.TYPE_KAMIKAZE:
                self.kamikaze_activated = True
    
    def _idle_movement(self) -> None:
        """편대에서 대기 시 흔들림"""
        offset = math.sin(pygame.time.get_ticks() * 0.002 + hash(id(self)) % 100) * 2
        self.rect.x = int(self.formation_x + offset)
        self.rect.y = int(self.formation_y)
    
    def _update_kamikaze(self) -> None:
        """카미카제 적 업데이트"""
        if not self.kamikaze_activated:
            self._idle_movement()
            
            # 랜덤하게 돌진 시작
            if random.random() < 0.008:
                self.kamikaze_activated = True
            return
        
        # 플레이어를 향해 돌진
        if self.target_player and self.target_player.alive():
            dx = self.target_player.rect.centerx - self.rect.centerx
            dy = self.target_player.rect.centery - self.rect.centery
            distance = math.sqrt(dx**2 + dy**2)
            
            if distance > 0:
                # 빠른 속도로 추적
                chase_speed = self.speed * 2
                self.rect.x += (dx / distance) * chase_speed
                self.rect.y += (dy / distance) * chase_speed
        else:
            # 플레이어가 없으면 아래로 직진
            self.rect.y += self.speed * 2
        
        # 화면 밖으로 나가면 제거
        if self.rect.top > settings.SCREEN_HEIGHT:
            self.kill()
    
    def _update_boss_pattern(self) -> None:
        """보스 패턴 업데이트"""
        if self.boss_pattern == 'idle':
            self._idle_movement()
            
            if random.random() < 0.005:
                self._start_random_pattern()
        
        elif self.boss_pattern == 'dive':
            self._execute_dive_pattern()
        
        elif self.boss_pattern == 'spiral':
            self._execute_spiral_pattern()
        
        elif self.boss_pattern == 'strafe':
            self._execute_strafe_pattern()
        
        if self.pattern_duration > 0:
            self.pattern_duration -= 16
            if self.pattern_duration <= 0:
                self._return_to_formation()
    
    def _start_random_pattern(self) -> None:
        """랜덤 공격 패턴 시작"""
        pattern = random.choice(['dive', 'spiral', 'strafe'])
        
        if pattern == 'dive':
            self.boss_pattern = 'dive'
            self.dive_target_x = random.randint(100, settings.SCREEN_WIDTH - 100)
            self.dive_target_y = settings.SCREEN_HEIGHT - 150
            self.dive_return = False
            self.pattern_duration = 5000
        
        elif pattern == 'spiral':
            self.boss_pattern = 'spiral'
            self.spiral_angle = 0
            self.pattern_duration = 3000
        
        elif pattern == 'strafe':
            self.boss_pattern = 'strafe'
            self.pattern_duration = 4000
            self.strafe_direction = 1 if random.random() > 0.5 else -1
    
    def _execute_dive_pattern(self) -> None:
        """돌진 패턴"""
        if not self.dive_return:
            dx = self.dive_target_x - self.rect.centerx
            dy = self.dive_target_y - self.rect.centery
            distance = math.sqrt(dx**2 + dy**2)
            
            if distance < 10:
                self.dive_return = True
            else:
                speed = self.speed * 2.5
                self.rect.x += (dx / distance) * speed
                self.rect.y += (dy / distance) * speed
        else:
            dx = self.formation_x - self.rect.centerx
            dy = self.formation_y - self.rect.centery
            distance = math.sqrt(dx**2 + dy**2)
            
            if distance < 10:
                self.boss_pattern = 'idle'
                self.rect.centerx = self.formation_x
                self.rect.centery = self.formation_y
            else:
                speed = self.speed * 2
                self.rect.x += (dx / distance) * speed
                self.rect.y += (dy / distance) * speed
    
    def _execute_spiral_pattern(self) -> None:
        """나선형 패턴"""
        self.spiral_angle += 5
        
        offset_x = math.cos(math.radians(self.spiral_angle)) * 30
        offset_y = math.sin(math.radians(self.spiral_angle * 0.5)) * 20
        
        self.rect.centerx = self.formation_x + offset_x
        self.rect.centery = self.formation_y + offset_y
    
    def _execute_strafe_pattern(self) -> None:
        """좌우 이동 패턴"""
        self.rect.x += self.speed * 2 * self.strafe_direction
        
        if self.rect.left < 50:
            self.strafe_direction = 1
        elif self.rect.right > settings.SCREEN_WIDTH - 50:
            self.strafe_direction = -1
        
        self.rect.centery = self.formation_y
    
    def _return_to_formation(self) -> None:
        """편대 복귀"""
        self.boss_pattern = 'idle'
    
    def shoot(self, bullets_group: pygame.sprite.Group) -> None:
        """탄환 발사"""
        if not self.in_formation and self.boss_pattern == 'idle':
            return
        
        if self.enemy_type == self.TYPE_KAMIKAZE:
            return  # 카미카제는 발사 안함
        
        if self.is_boss:
            self._boss_shoot(bullets_group)
        else:
            if random.random() < self.fire_chance:
                bullet = Bullet(
                    self.rect.centerx,
                    self.rect.bottom,
                    'enemy',
                    self.bullet_image
                )
                bullets_group.add(bullet)
    
    def _boss_shoot(self, bullets_group: pygame.sprite.Group) -> None:
        """보스 특수 공격"""
        if self.attack_cooldown > 0:
            return
        
        if self.boss_pattern == 'idle':
            if random.random() < self.fire_chance * 2:
                bullet = Bullet(
                    self.rect.centerx,
                    self.rect.bottom,
                    'enemy',
                    self.bullet_image
                )
                bullets_group.add(bullet)
                self.attack_cooldown = 500
        
        elif self.boss_pattern == 'dive':
            if random.random() < 0.1:
                bullet = Bullet(
                    self.rect.centerx,
                    self.rect.bottom,
                    'enemy',
                    self.bullet_image
                )
                bullets_group.add(bullet)
                self.attack_cooldown = 200
        
        elif self.boss_pattern == 'spiral':
            if self.attack_cooldown <= 0:
                for i in range(3):
                    angle = self.spiral_angle + i * 120
                    bullet = Bullet(
                        self.rect.centerx,
                        self.rect.centery,
                        'enemy',
                        self.bullet_image,
                        angle=angle
                    )
                    bullets_group.add(bullet)
                self.attack_cooldown = 150
        
        elif self.boss_pattern == 'strafe':
            if random.random() < 0.08:
                for dx in [-15, 0, 15]:
                    bullet = Bullet(
                        self.rect.centerx + dx,
                        self.rect.bottom,
                        'enemy',
                        self.bullet_image
                    )
                    bullets_group.add(bullet)
                self.attack_cooldown = 300
    
    def shoot_tractor_beam(self, beams_group: pygame.sprite.Group,
                          beam_image: pygame.Surface) -> bool:
        """트랙터 빔 발사"""
        if not self.is_boss or not self.in_formation:
            return False
        
        if self.boss_pattern != 'idle':
            return False
        
        if self.tractor_beam_cooldown > 0:
            return False
        
        if random.random() > 0.002:
            return False
        
        beam = TractorBeam(
            self.rect.centerx,
            self.rect.bottom,
            beam_image
        )
        beams_group.add(beam)
        
        self.tractor_beam_cooldown = self.tractor_beam_delay
        return True
    
    def take_damage(self, damage: int = 1) -> bool:
        """
        적이 데미지를 받음
        
        Returns:
            적이 죽었으면 True
        """
        self.hp -= damage
        
        if self.hp <= 0:
            self.kill()
            return True
        
        # 피격 효과
        self._flash_effect()
        return False
    
    def _flash_effect(self) -> None:
        """피격 시 깜빡임 효과"""
        # 임시로 밝게
        bright_image = self.image.copy()
        bright_image.fill((100, 100, 100), special_flags=pygame.BLEND_RGB_ADD)
        self.image = bright_image
    
    def can_split(self) -> bool:
        """분열 가능 여부"""
        return (self.enemy_type == self.TYPE_SPLITTER and 
                not self.is_split_child and 
                not self.has_split)
    
    def get_split_children(self) -> List['Enemy']:
        """분열 시 자식 생성"""
        if not self.can_split():
            return []
        
        self.has_split = True
        children = []
        
        for offset in [-20, 20]:
            child = Enemy(
                self.rect.centerx + offset,
                self.rect.centery,
                self.TYPE_SPLITTER,
                self.image,
                self.bullet_image,
                is_split_child=True
            )
            child.in_formation = True
            child.formation_x = self.formation_x + offset
            child.formation_y = self.formation_y
            children.append(child)
        
        return children
    
    def get_score_value(self) -> int:
        """점수 반환"""
        return self.score_value