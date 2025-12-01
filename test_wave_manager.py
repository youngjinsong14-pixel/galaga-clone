# Galaga Clone - Python/Pygame 슈팅 게임

클래식 아케이드 게임 Galaga의 완전한 클론 구현입니다.

## 주요 기능

- ✈️ **플레이어 조작**: 좌우 이동, 발사, 더블 파이터 모드
- 👾 **다양한 적**: 일반 적과 보스 적, 다양한 진입 패턴
- 🎯 **트랙터 빔**: 보스가 플레이어를 포획하고 구출 시 더블 파이터 활성화
- 🌊 **웨이브 시스템**: 점진적 난이도 상승, 보너스 스테이지
- 🎨 **프로그램 생성 그래픽**: 외부 파일 없이 실행 가능
- 🔊 **사운드 효과**: 프로그램 생성 비프음 및 효과음
- 📊 **점수 시스템**: 최고 점수 저장 및 표시

## 시스템 요구사항

- Python 3.10 이상
- Pygame 2.5.0 이상
- NumPy (사운드 생성용)

## 설치 및 실행

### 1. 저장소 클론 또는 파일 다운로드
```bash
git clone <repository-url>
cd galaga_clone
```

### 2. 가상환경 생성 (권장)
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 3. 의존성 설치
```bash
pip install -r requirements.txt
```

### 4. 게임 실행
```bash
python main.py
```

## 게임 조작

| 키 | 기능 |
|---|---|
| ← → 또는 A, D | 플레이어 좌우 이동 |
| SPACE | 발사 |
| P | 일시정지 |
| R | 재시작 (게임 오버 시) |

## 게임플레이 가이드

### 기본 규칙

1. **목표**: 모든 적을 격파하고 최대한 높은 점수 획득
2. **목숨**: 3개로 시작, 피격 시 1개씩 감소
3. **웨이브**: 각 웨이브를 클리어하면 다음 웨이브로 진행

### 특수 메카닉

#### 트랙터 빔
- 보스 적이 노란색 트랙터 빔을 발사합니다
- 빔에 맞으면 플레이어가 포획됩니다
- 포획한 보스를 다시 격파하면 기체를 구출하여 **더블 파이터** 모드 활성화!

#### 더블 파이터
- 2연발 탄환 발사
- 한 번 피격 시 일반 모드로 돌아감

#### 보너스 스테이지
- 3 웨이브마다 등장
- 적들이 공격하지 않음
- 20초 안에 모두 격파하면 높은 점수 획득

### 점수 시스템

- 일반 적: 100점
- 보스 적: 500점
- 보너스 적: 200점
- 기체 구출: 1000점

## 프로젝트 구조
```
galaga_clone/
├─ main.py              # 메인 게임 루프
├─ settings.py          # 게임 설정 및 상수
├─ player.py            # 플레이어 클래스
├─ enemy.py             # 적 클래스
├─ bullet.py            # 탄환 및 트랙터 빔
├─ wave_manager.py      # 웨이브 관리
├─ collision.py         # 충돌 처리
├─ ui.py                # UI 렌더링
├─ assets_loader.py     # 에셋 로더
├─ sound_generator.py   # 사운드 생성
├─ requirements.txt     # 의존성
├─ README.md            # 이 파일
├─ tests/               # 테스트
│  ├─ test_collision.py
│  └─ test_wave_manager.py
└─ docs/
   └─ design.md         # 설계 문서
```

## 테스트 실행
```bash
pytest tests/
```

## 확장 및 커스터마이징

### 난이도 조정

`settings.py`에서 다음 값들을 수정하세요:
```python
PLAYER_SPEED = 5          # 플레이어 이동 속도
ENEMY_FIRE_CHANCE = 0.01  # 적 발사 확률
PLAYER_LIVES = 3          # 시작 목숨
```

### 해상도 변경
```python
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
```

### 커스텀 에셋 사용

`assets_loader.py`의 `_generate_images()` 메서드를 수정하거나,
외부 PNG 파일을 로드하도록 변경할 수 있습니다:
```python
def _generate_images(self):
    self.images['player'] = pygame.image.load('assets/player.png')
    # ...
```

## 알려진 제한사항

1. **사운드**: 간단한 비프음만 지원. 더 풍부한 사운드는 외부 파일 사용 필요
2. **그래픽**: 프로그램 생성 도형. 픽셀 아트는 외부 파일 사용 필요
3. **세이브**: 최고 점수만 저장. 진행 상황 세이브 미지원

## 향후 개선 사항

### 구현 가능한 기능들

- [ ] 파워업 시스템 (무기 강화, 실드, 속도 증가)
- [ ] 다양한 적 타입 및 공격 패턴
- [ ] 보스 스테이지
- [ ] 배경 스크롤 및 시각 효과
- [ ] 사운드트랙 및 효과음 개선
- [ ] 리플레이 시스템
- [ ] 설정 메뉴 (볼륨, 키맵, 해상도)
- [ ] 멀티플레이어 (로컬 협동)
- [ ] 리더보드 (온라인)

### 모바일 포팅

터치 입력을 위한 수정 사항:
```python
# player.py에 추가
def handle_touch(self, touch_pos):
    if touch_pos[0] < self.rect.centerx:
        self.rect.x -= self.speed
    else:
        self.rect.x += self.speed
```

## 라이선스

MIT License

Copyright (c) 2024

본 프로젝트는 교육 및 학습 목적으로 제작되었습니다.

### 사용된 기술

- **Pygame**: LGPL 라이선스
- **NumPy**: BSD 라이선스

### 에셋 라이선스

모든 그래픽과 사운드는 프로그램으로 생성되며, 외부 저작권 제한이 없습니다.
외부 에셋을 사용할 경우 각 에셋의 라이선스를 확인하세요.

#### 추천 무료 에셋 출처

- **그래픽**: 
  - OpenGameArt.org (CC0, CC-BY)
  - Kenney.nl (CC0)
  - itch.io (다양한 라이선스)

- **사운드**:
  - Freesound.org (CC0, CC-BY)
  - OpenGameArt.org (CC0, CC-BY)
  - JSFXR (프로그램 생성)

## 기여

버그 리포트, 기능 제안, 풀 리퀘스트를 환영합니다!

## 문제 해결

### 게임이 실행되지 않음
```bash
# pygame 재설치
pip uninstall pygame
pip install pygame
```

### 사운드가 들리지 않음

- 시스템 볼륨 확인
- `settings.py`에서 `SFX_VOLUME` 값 증가

### 성능 문제

- `settings.py`에서 `FPS` 값 감소
- 적 수 감소: `ENEMIES_PER_ROW`, `ENEMY_ROWS` 값 조정

## 연락처

프로젝트 관련 문의사항이 있으시면 이슈를 등록해주세요.

---

**즐거운 게임 되세요! 🎮**