# wave_manager.py
"""
웨이브(스테이지) 관리
다양한 적 생성 및 편대 구성을 담당합니다.
"""
import pygame
import random
from typing import List
import settings
from enemy import Enemy


class WaveManager:
    """웨이브 관리 클래스"""
    
    def __init__(self, enemy_image: pygame.Surface,
                 boss_image: pygame.Surface,
                 bullet_image: pygame.Surface):
        """
        웨이브 매니저 초기화
        """
        self.enemy_image = enemy_image
        self.boss_image = boss_image
        self.bullet_image = bullet_image
        
        self.current_wave = 1
        self.is_bonus_stage = False
        self.bonus_stage_time_limit = 20000
        self.bonus_stage_start_time = 0
        
        # 플레이어 참조 (카미카제용)
        self.player = None
    
    def set_player(self, player) -> None:
        """플레이어 참조 설정"""
        self.player = player
    
    def create_wave(self, wave_number: int) -> pygame.sprite.Group:
        """특정 웨이브의 적들을 생성"""
        enemies = pygame.sprite.Group()
        
        if wave_number % settings.BONUS_STAGE_INTERVAL == 0:
            self.is_bonus_stage = True
            self.bonus_stage_start_time = pygame.time.get_ticks()
            enemies = self._create_bonus_stage()
        else:
            self.is_bonus_stage = False
            enemies = self._create_normal_wave(wave_number)
        
        return enemies
    
    def _get_enemy_type_weights(self, wave_number: int) -> dict:
        """웨이브에 따른 적 타입 가중치 반환"""
        # 기본 가중치
        weights = {
            Enemy.TYPE_NORMAL: 50,
            Enemy.TYPE_FAST: 0,
            Enemy.TYPE_TANK: 0,
            Enemy.TYPE_KAMIKAZE: 0,
            Enemy.TYPE_SPLITTER: 0,
        }
        
        # 웨이브 3부터 빠른 적 등장
        if wave_number >= 3:
            weights[Enemy.TYPE_FAST] = 15
            weights[Enemy.TYPE_NORMAL] = 40
        
        # 웨이브 5부터 탱크 적 등장
        if wave_number >= 5:
            weights[Enemy.TYPE_TANK] = 10
            weights[Enemy.TYPE_NORMAL] = 35
        
        # 웨이브 7부터 카미카제 적 등장
        if wave_number >= 7:
            weights[Enemy.TYPE_KAMIKAZE] = 12
            weights[Enemy.TYPE_NORMAL] = 30
        
        # 웨이브 9부터 분열 적 등장
        if wave_number >= 9:
            weights[Enemy.TYPE_SPLITTER] = 10
            weights[Enemy.TYPE_NORMAL] = 25
        
        # 후반 웨이브에서는 특수 적 비율 증가
        if wave_number >= 12:
            weights[Enemy.TYPE_NORMAL] = 20
            weights[Enemy.TYPE_FAST] = 20
            weights[Enemy.TYPE_TANK] = 15
            weights[Enemy.TYPE_KAMIKAZE] = 15
            weights[Enemy.TYPE_SPLITTER] = 15
        
        return weights
    
    def _choose_enemy_type(self, weights: dict) -> str:
        """가중치에 따라 적 타입 선택"""
        types = list(weights.keys())
        weight_values = list(weights.values())
        
        # 가중치가 0인 타입 제외
        valid_types = [(t, w) for t, w in zip(types, weight_values) if w > 0]
        if not valid_types:
            return Enemy.TYPE_NORMAL
        
        types, weight_values = zip(*valid_types)
        return random.choices(types, weights=weight_values)[0]
    
    def _create_normal_wave(self, wave_number: int) -> pygame.sprite.Group:
        """일반 웨이브 생성"""
        enemies = pygame.sprite.Group()
        
        # 웨이브에 따라 난이도 조정
        num_rows = min(settings.ENEMY_ROWS + wave_number // 3, 6)
        enemies_per_row = min(settings.ENEMIES_PER_ROW + wave_number // 5, 10)
        
        # 편대 배치 계산
        formation_start_x = settings.FORMATION_PADDING
        formation_start_y = 80
        spacing_x = (settings.SCREEN_WIDTH - 2 * settings.FORMATION_PADDING) // enemies_per_row
        spacing_y = 50
        
        path_types = ['circle', 'zigzag', 'straight', 'fast_dive']
        
        # 적 타입 가중치
        weights = self._get_enemy_type_weights(wave_number)
        
        for row in range(num_rows):
            for col in range(enemies_per_row):
                formation_x = formation_start_x + col * spacing_x
                formation_y = formation_start_y + row * spacing_y
                
                # 첫 번째 행은 보스
                if row == 0:
                    enemy_type = Enemy.TYPE_BOSS
                    image = self.boss_image
                else:
                    enemy_type = self._choose_enemy_type(weights)
                    image = self.enemy_image
                
                start_x = random.randint(0, settings.SCREEN_WIDTH)
                enemy = Enemy(
                    start_x, -50,
                    enemy_type,
                    image,
                    self.bullet_image
                )
                
                enemy.formation_x = formation_x
                enemy.formation_y = formation_y
                
                # 타입별 진입 경로
                if enemy_type == Enemy.TYPE_FAST:
                    path_type = 'fast_dive'
                elif enemy_type == Enemy.TYPE_KAMIKAZE:
                    path_type = 'straight'
                else:
                    path_type = random.choice(path_types)
                
                enemy.set_entry_path(path_type)
                
                # 카미카제에게 플레이어 참조 전달
                if enemy_type == Enemy.TYPE_KAMIKAZE and self.player:
                    enemy.set_player_reference(self.player)
                
                enemies.add(enemy)
        
        return enemies
    
    def _create_bonus_stage(self) -> pygame.sprite.Group:
        """보너스 스테이지 생성"""
        enemies = pygame.sprite.Group()
        
        num_enemies = 20
        
        for i in range(num_enemies):
            x = (i % 5) * 150 + 100
            y = -100 - (i // 5) * 80
            
            # 보너스 스테이지는 일반 적만
            enemy = Enemy(
                x, y,
                Enemy.TYPE_NORMAL,
                self.enemy_image,
                self.bullet_image
            )
            
            enemy.fire_chance = 0
            enemy.formation_x = x
            enemy.formation_y = 120 + (i // 5) * 60
            enemy.set_entry_path('zigzag')
            
            enemies.add(enemy)
        
        return enemies
    
    def is_bonus_stage_timeout(self) -> bool:
        """보너스 스테이지 시간 초과 확인"""
        if not self.is_bonus_stage:
            return False
        
        elapsed = pygame.time.get_ticks() - self.bonus_stage_start_time
        return elapsed >= self.bonus_stage_time_limit
    
    def get_bonus_stage_remaining_time(self) -> int:
        """보너스 스테이지 남은 시간"""
        if not self.is_bonus_stage:
            return 0
        
        elapsed = pygame.time.get_ticks() - self.bonus_stage_start_time
        remaining = max(0, self.bonus_stage_time_limit - elapsed)
        return remaining // 1000
    
    def next_wave(self) -> pygame.sprite.Group:
        """다음 웨이브로 진행"""
        self.current_wave += 1
        return self.create_wave(self.current_wave)