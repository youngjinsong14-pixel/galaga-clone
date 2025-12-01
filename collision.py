# collision.py
"""
충돌 처리 모듈
"""
import pygame
from typing import Tuple, List
import settings


def check_bullet_enemy_collision(bullets: pygame.sprite.Group,
                                  enemies: pygame.sprite.Group) -> Tuple[int, List, List, List]:
    """
    플레이어 탄환과 적의 충돌 처리
    
    Returns:
        (획득한 점수, 일반 충돌 위치 리스트, 보스 충돌 위치 리스트, 분열 자식 리스트)
    """
    score = 0
    hit_positions = []
    boss_killed_positions = []
    split_children = []
    
    for bullet in list(bullets):
        if bullet.bullet_type != 'player':
            continue
        
        for enemy in list(enemies):
            if pygame.sprite.collide_rect(bullet, enemy):
                # 관통 무기의 경우 이미 맞은 적인지 확인
                if hasattr(bullet, 'can_hit') and not bullet.can_hit(enemy):
                    continue
                
                pos = (enemy.rect.centerx, enemy.rect.centery)
                
                # 관통 무기는 맞춤 기록
                if hasattr(bullet, 'piercing') and bullet.piercing:
                    bullet.register_hit(enemy)
                else:
                    bullet.kill()
                
                # 분열 적 체크
                if enemy.can_split():
                    children = enemy.get_split_children()
                    split_children.extend(children)
                
                if enemy.take_damage(bullet.damage):
                    score += enemy.get_score_value()
                    
                    if enemy.is_boss:
                        boss_killed_positions.append(pos)
                    else:
                        hit_positions.append(pos)
                
                # 관통 무기가 아니면 다음 탄환으로
                if not (hasattr(bullet, 'piercing') and bullet.piercing):
                    break
    
    return score, hit_positions, boss_killed_positions, split_children


def check_player_bullet_collision(player, bullets: pygame.sprite.Group) -> bool:
    """플레이어와 적 탄환의 충돌 처리"""
    if not player or not player.alive():
        return False
    
    for bullet in bullets:
        if bullet.bullet_type == 'enemy':
            if pygame.sprite.collide_rect(player, bullet):
                bullet.kill()
                return True
    
    return False


def check_player_enemy_collision(player, enemies: pygame.sprite.Group) -> bool:
    """플레이어와 적의 직접 충돌 처리"""
    if not player or not player.alive():
        return False
    
    for enemy in enemies:
        if pygame.sprite.collide_rect(player, enemy):
            enemy.kill()
            return True
    
    return False


def check_tractor_beam_player_collision(player, tractor_beams: pygame.sprite.Group):
    """트랙터 빔과 플레이어의 충돌 처리"""
    if not player or not player.alive():
        return None
    
    for beam in tractor_beams:
        if pygame.sprite.collide_rect(player, beam):
            return beam
    
    return None


def check_bullet_beam_collision(bullets: pygame.sprite.Group,
                                 tractor_beams: pygame.sprite.Group) -> bool:
    """플레이어 탄환과 트랙터 빔의 충돌 처리"""
    for bullet in bullets:
        if bullet.bullet_type != 'player':
            continue
        
        for beam in tractor_beams:
            if pygame.sprite.collide_rect(bullet, beam):
                bullet.kill()
                beam.kill()
                return True
    
    return False