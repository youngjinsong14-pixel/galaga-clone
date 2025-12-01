# settings.py
"""
게임 전역 설정 및 상수 정의
"""
from typing import Tuple

# 화면 설정
SCREEN_WIDTH = 720
SCREEN_HEIGHT = 960
BASE_WIDTH = SCREEN_WIDTH  # 동일하게 유지
BASE_HEIGHT = SCREEN_HEIGHT  # 동일하게 유지
FPS: int = 60
TITLE: str = "Galaga Clone"

# 사용 가능한 스케일
SCALE_OPTIONS = [1.0, 1.25, 1.5, 1.75, 2.0]
SCREEN_SCALE = 1.0

# 색상 정의 (R, G, B)
BLACK: Tuple[int, int, int] = (0, 0, 0)
WHITE: Tuple[int, int, int] = (255, 255, 255)
RED: Tuple[int, int, int] = (255, 0, 0)
GREEN: Tuple[int, int, int] = (0, 255, 0)
BLUE: Tuple[int, int, int] = (0, 100, 255)
YELLOW: Tuple[int, int, int] = (255, 255, 0)
CYAN: Tuple[int, int, int] = (0, 255, 255)

# 난이도 설정
DIFFICULTY_EASY = 'easy'
DIFFICULTY_NORMAL = 'normal'
DIFFICULTY_HARD = 'hard'

# 현재 난이도 (기본값)
current_difficulty = DIFFICULTY_NORMAL

# 난이도별 설정값
DIFFICULTY_SETTINGS = {
    DIFFICULTY_EASY: {
        'player_lives': 5,
        'player_speed': 6,
        'enemy_speed': 1.5,
        'enemy_fire_chance': 0.005,
        'enemy_bullet_speed': 3,
        'boss_hp': 3,
        'score_multiplier': 0.8,
        'powerup_drop_chance': 0.20,
        'enemy_rows': 3,
        'enemies_per_row': 8,
    },
    DIFFICULTY_NORMAL: {
        'player_lives': 3,
        'player_speed': 5,
        'enemy_speed': 2,
        'enemy_fire_chance': 0.01,
        'enemy_bullet_speed': 5,
        'boss_hp': 5,
        'score_multiplier': 1.0,
        'powerup_drop_chance': 0.15,
        'enemy_rows': 4,
        'enemies_per_row': 10,
    },
    DIFFICULTY_HARD: {
        'player_lives': 2,
        'player_speed': 5,
        'enemy_speed': 3,
        'enemy_fire_chance': 0.02,
        'enemy_bullet_speed': 7,
        'boss_hp': 8,
        'score_multiplier': 1.5,
        'powerup_drop_chance': 0.10,
        'enemy_rows': 5,
        'enemies_per_row': 12,
    },
}

def get_difficulty_setting(key: str):
    """현재 난이도의 설정값 가져오기"""
    return DIFFICULTY_SETTINGS[current_difficulty].get(key)

def set_difficulty(difficulty: str):
    """난이도 설정"""
    global current_difficulty
    if difficulty in DIFFICULTY_SETTINGS:
        current_difficulty = difficulty

# 플레이어 설정
PLAYER_SPEED: int = 5
PLAYER_WIDTH: int = 40
PLAYER_HEIGHT: int = 30
PLAYER_LIVES: int = 3
PLAYER_FIRE_DELAY: int = 250

# 적 설정
ENEMY_WIDTH: int = 30
ENEMY_HEIGHT: int = 30
ENEMY_SPEED: int = 2
ENEMY_FIRE_CHANCE: float = 0.01
BOSS_WIDTH: int = 50
BOSS_HEIGHT: int = 40

# 탄환 설정
BULLET_WIDTH: int = 4
BULLET_HEIGHT: int = 15
BULLET_SPEED: int = 7
ENEMY_BULLET_SPEED: int = 5

# 트랙터 빔 설정
TRACTOR_BEAM_WIDTH: int = 30
TRACTOR_BEAM_HEIGHT: int = 100
TRACTOR_BEAM_SPEED: int = 3
TRACTOR_BEAM_CAPTURE_TIME: int = 1000

# 웨이브 설정
ENEMIES_PER_ROW: int = 10
ENEMY_ROWS: int = 4
FORMATION_PADDING: int = 50
BONUS_STAGE_INTERVAL: int = 3

# 점수 설정
SCORE_ENEMY: int = 100
SCORE_BOSS: int = 500
SCORE_BONUS_ENEMY: int = 200
SCORE_RESCUE: int = 1000

# 사운드 볼륨
MUSIC_VOLUME: float = 0.5
SFX_VOLUME: float = 0.7
BGM_VOLUME: float = 0.3

# 게임 상태
STATE_MENU: str = "menu"
STATE_DIFFICULTY_SELECT: str = "difficulty_select"
STATE_PLAYING: str = "playing"
STATE_PAUSED: str = "paused"
STATE_GAME_OVER: str = "game_over"
STATE_STAGE_CLEAR: str = "stage_clear"
STATE_BONUS_STAGE: str = "bonus_stage"

# 파일 경로
ASSETS_DIR: str = "assets"
SFX_DIR: str = "assets/sfx"
HIGHSCORE_FILE: str = "highscore.txt"

# 궁극기 설정
ULTIMATE_CHARGE_MAX = 100  # 최대 차지
ULTIMATE_CHARGE_PER_KILL = 5  # 처치당 차지량

# 랭킹 설정
RANKING_FILE = 'ranking.txt'
RANKING_MAX = 5