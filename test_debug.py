import pygame
pygame.init()
import settings
from assets_loader import AssetsLoader
from player import Player
from enemy import Enemy
from wave_manager import WaveManager

assets = AssetsLoader()
print('Player image:', assets.get_image('player'))
print('Enemy image:', assets.get_image('enemy'))

player = Player(360, 900, assets.get_image('player'), assets.get_image('player_bullet'))
print('Player rect:', player.rect)

enemy = Enemy(100, 100, assets.get_image('enemy'), assets.get_image('enemy_bullet'), 'normal')
print('Enemy rect:', enemy.rect)

wave_manager = WaveManager(assets.get_image('enemy'), assets.get_image('boss'), assets.get_image('enemy_bullet'))
wave_manager.set_player(player)
enemies = wave_manager.create_wave(1)
print('Enemies count:', len(enemies))

for i, e in enumerate(enemies):
    if i < 5:
        print(f'  Enemy {i}: rect={e.rect}, type={e.enemy_type}')

print('Test complete!')