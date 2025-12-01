# tests/test_collision.py
"""
충돌 처리 로직 테스트
"""
import pytest
import pygame
import sys
import os

# 상위 디렉토리를 path에 추가
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import settings
from bullet import Bullet
from enemy import Enemy
from player import Player
from collision import *


@pytest.fixture
def pygame_init():
    """pygame 초기화"""
    pygame.init()
    yield
    pygame.quit()


def test_bullet_enemy_collision(pygame_init):
    """탄환과 적 충돌 테스트"""
    # 더미 이미지 생성
    bullet_image = pygame.Surface((10, 10))
    enemy_image = pygame.Surface((30, 30))
    
    # 적 생성
    enemy = Enemy(100, 100, 'normal', enemy_image, bullet_image)
    enemies = pygame.sprite.Group(enemy)
    
    # 탄환 생성 (적과 같은 위치)
    bullet = Bullet(100, 100, 'player', bullet_image)
    bullets = pygame.sprite.Group(bullet)
    
    # 충돌 확인
    score = check_bullet_enemy_collision(bullets, enemies)
    
    assert score == settings.SCORE_ENEMY
    assert len(enemies) == 0  # 적이 제거되었는지
    assert len(bullets) == 0  # 탄환이 제거되었는지


def test_player_bullet_collision(pygame_init):
    """플레이어와 적 탄환 충돌 테스트"""
    bullet_image = pygame.Surface((10, 10))
    player_image = pygame.Surface((40, 30))
    
    # 플레이어 생성
    player = Player(100, 100, player_image, bullet_image)
    
    # 적 탄환 생성 (플레이어와 같은 위치)
    enemy_bullet = Bullet(100, 100, 'enemy', bullet_image)
    bullets = pygame.sprite.Group(enemy_bullet)
    
    # 충돌 확인
    collision = check_player_bullet_collision(player, bullets)
    
    assert collision == True
    assert len(bullets) == 0  # 탄환이 제거되었는지


def test_no_collision_when_far(pygame_init):
    """거리가 멀 때 충돌하지 않는지 테스트"""
    bullet_image = pygame.Surface((10, 10))
    enemy_image = pygame.Surface((30, 30))
    
    # 적 생성
    enemy = Enemy(100, 100, 'normal', enemy_image, bullet_image)
    enemies = pygame.sprite.Group(enemy)
    
    # 탄환 생성 (멀리 떨어진 위치)
    bullet = Bullet(500, 500, 'player', bullet_image)
    bullets = pygame.sprite.Group(bullet)
    
    # 충돌 확인
    score = check_bullet_enemy_collision(bullets, enemies)
    
    assert score == 0
    assert len(enemies) == 1  # 적이 그대로 있는지
    assert len(bullets) == 1  # 탄환이 그대로 있는지


if __name__ == "__main__":
    pytest.main([__file__])