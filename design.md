# Galaga Clone - 설계 문서

## 개요

본 문서는 Galaga Clone 프로젝트의 핵심 알고리즘과 설계 결정사항을 설명합니다.

## 아키텍처

### 모듈 구조
```
Game (main.py)
├─ AssetsLoader (assets_loader.py)
├─ Player (player.py)
├─ Enemy (enemy.py)
├─ WaveManager (wave_manager.py)
├─ UI (ui.py)
└─ Collision (collision.py)
```

### 주요 디자인 패턴

#### 1. 스프라이트 그룹 패턴
Pygame의 `sprite.Group`을 활용하여 객체 관리:
- 자동 업데이트 및 렌더링
- 효율적인 충돌 감지
- 메모리 관리 간소화

#### 2. 상태 머신 패턴
게임 상태 관리:
```python
STATE_MENU
STATE_PLAYING
STATE_PAUSED
STATE_GAME_OVER
STATE_STAGE_CLEAR
```

## 핵심 알고리즘

### 1. 적 진입 패턴 (Entry Path)

#### 원형 진입 (Circle Entry)
```python
def circle_entry(steps=30):
    for i in range(steps):
        angle = π + (π * i / steps)
        x = center_x + radius * cos(angle)
        y = center_y + radius * sin(angle)
```

**장점**: 시각적으로 화려하고 예측 가능

#### 지그재그 진입 (Zigzag Entry)
```python
def zigzag_entry(steps=20, amplitude=100):
    for i in range(steps):
        x = start_x + amplitude * sin(i * 0.5)
        y = start_y + i * 30
```

**장점**: 탄환 회피가 어려워 난이도 증가

### 2. 트랙터 빔 메카닉

#### 포획 프로세스
1. 보스가 트랙터 빔 발사
2. 빔이 플레이어와 충돌
3. `TRACTOR_BEAM_CAPTURE_TIME` (1초) 동안 포획 진행
4. 완료 시 플레이어 기체 제거 및 보스에 저장
5. 보스 재격파 시 더블 파이터 모드 활성화
```python
# 포획 진행
if beam.is_capture_complete():
    player.get_captured()
    boss.has_captured_ship = True
```

**설계 이유**: 원작 Galaga의 핵심 메카닉 재현

### 3. 충돌 처리 최적화

#### 사각형 충돌 (Rect Collision)
```python
pygame.sprite.collide_rect(sprite1, sprite2)
```
- **복잡도**: O(1)
- **용도**: 대부분의 충돌
- **장점**: 빠르고 효율적

#### 원형 충돌 (Circle Collision)
```python
def circle_collision(sprite1, sprite2):
    distance = sqrt(dx² + dy²)
    return distance < (radius1 + radius2)
```
- **복잡도**: O(1)
- **용도**: 정밀한 충돌 필요 시
- **장점**: 더 정확함

### 4. 웨이브 생성 알고리즘

#### 난이도 스케일링
```python
num_rows = min(ENEMY_ROWS + wave_number // 3, 6)
enemy_speed += wave_number * 0.1
fire_chance += wave_number * 0.002
```

**설계 원칙**:
- 선형 증가로 예측 가능성 유지
- 상한선 설정으로 난이도 폭발 방지
- 3 웨이브마다 보너스 스테이지로 긴장 완화

#### 보너스 스테이지
```python
if wave_number % BONUS_STAGE_INTERVAL == 0:
    create_bonus_stage()
```

**특징**:
- 적 공격 없음 (`fire_chance = 0`)
- 시간 제한 (20초)
- 높은 점수 보상

### 5. 발사 속도 제한 (Fire Rate Limiting)
```python
current_time = get_ticks()
if current_time - last_shot_time >= fire_delay:
    shoot()
    last_shot_time = current_time
```

**목적**:
- 게임 밸런스 유지
- 연사 방지
- 탄환 스팸 방지

## 성능 최적화

### 1. 객체 풀링 (Object Pooling)

현재 구현에서는 Pygame의 `kill()` 메서드로 간단히 처리하지만,
대규모 탄환 생성 시 객체 풀 패턴 적용 가능:
```python
class BulletPool:
    def __init__(self, size=100):
        self.bullets = [Bullet(...) for _ in range(size)]
        self.available = list(self.bullets)
    
    def get_bullet(self):
        if self.available:
            return self.available.pop()
        return None
    
    def return_bullet(self, bullet):
        bullet.reset()
        self.available.append(bullet)
```

### 2
class Quadtree:
    def __init__(self, boundary, capacity=4):
        self.boundary = boundary  # 영역
        self.capacity = capacity  # 최대 수용 개체 수
        self.objects = []
        self.divided = False
    
    def insert(self, obj):
        # 객체 삽입 로직
        if not self.boundary.contains(obj):
            return False
        
        if len(self.objects) < self.capacity:
            self.objects.append(obj)
            return True
        
        if not self.divided:
            self.subdivide()
        
        return (self.northeast.insert(obj) or
                self.northwest.insert(obj) or
                self.southeast.insert(obj) or
                self.southwest.insert(obj))
    
    def query(self, range_rect):
        # 범위 내 객체 반환
        found = []
        if not self.boundary.intersects(range_rect):
            return found
        
        for obj in self.objects:
            if range_rect.contains(obj):
                found.append(obj)
        
        if self.divided:
            found.extend(self.northeast.query(range_rect))
            found.extend(self.northwest.query(range_rect))
            found.extend(self.southeast.query(range_rect))
            found.extend(self.southwest.query(range_rect))
        
        return found