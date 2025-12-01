# sound_generator.py
"""
프로그램으로 사운드 생성
외부 파일 없이 게임 사운드를 생성합니다.
"""
import pygame
import numpy as np
import math


def generate_sine_wave(frequency: float, duration: float, volume: float = 0.5,
                       sample_rate: int = 22050) -> pygame.mixer.Sound:
    """사인파 생성"""
    n_samples = int(duration * sample_rate)
    t = np.linspace(0, duration, n_samples, False)
    wave = np.sin(2 * np.pi * frequency * t) * volume
    wave = (wave * 32767).astype(np.int16)
    stereo_wave = np.column_stack((wave, wave))
    return pygame.mixer.Sound(buffer=stereo_wave)


def generate_laser(duration: float = 0.15) -> pygame.mixer.Sound:
    """레이저 발사음 생성"""
    sample_rate = 22050
    n_samples = int(duration * sample_rate)
    t = np.linspace(0, duration, n_samples, False)
    
    # 주파수가 높은 곳에서 낮은 곳으로 떨어지는 효과
    frequency = 1200 * np.exp(-t * 15) + 200
    wave = np.sin(2 * np.pi * frequency * t / sample_rate * np.arange(n_samples))
    
    # 볼륨 감쇠
    envelope = np.exp(-t * 10)
    wave = wave * envelope * 0.4
    
    wave = (wave * 32767).astype(np.int16)
    stereo_wave = np.column_stack((wave, wave))
    return pygame.mixer.Sound(buffer=stereo_wave)


def generate_explosion(duration: float = 0.4) -> pygame.mixer.Sound:
    """폭발음 생성"""
    sample_rate = 22050
    n_samples = int(duration * sample_rate)
    t = np.linspace(0, duration, n_samples, False)
    
    # 노이즈 기반 폭발음
    noise = np.random.uniform(-1, 1, n_samples)
    
    # 저주파 필터 효과
    filtered = np.zeros(n_samples)
    alpha = 0.1
    filtered[0] = noise[0]
    for i in range(1, n_samples):
        filtered[i] = alpha * noise[i] + (1 - alpha) * filtered[i-1]
    
    # 볼륨 감쇠
    envelope = np.exp(-t * 6)
    wave = filtered * envelope * 0.6
    
    # 저주파 추가
    low_freq = np.sin(2 * np.pi * 60 * t) * np.exp(-t * 8) * 0.3
    wave = wave + low_freq
    
    wave = np.clip(wave, -1, 1)
    wave = (wave * 32767).astype(np.int16)
    stereo_wave = np.column_stack((wave, wave))
    return pygame.mixer.Sound(buffer=stereo_wave)


def generate_powerup(duration: float = 0.3) -> pygame.mixer.Sound:
    """파워업 획득음 생성"""
    sample_rate = 22050
    n_samples = int(duration * sample_rate)
    t = np.linspace(0, duration, n_samples, False)
    
    # 상승하는 아르페지오
    freq1 = 400
    freq2 = 600
    freq3 = 800
    
    wave = np.zeros(n_samples)
    third = n_samples // 3
    
    wave[:third] = np.sin(2 * np.pi * freq1 * t[:third])
    wave[third:2*third] = np.sin(2 * np.pi * freq2 * t[third:2*third])
    wave[2*third:] = np.sin(2 * np.pi * freq3 * t[2*third:])
    
    # 부드러운 엔벨로프
    envelope = np.ones(n_samples)
    fade_len = n_samples // 10
    envelope[:fade_len] = np.linspace(0, 1, fade_len)
    envelope[-fade_len:] = np.linspace(1, 0, fade_len)
    
    wave = wave * envelope * 0.4
    wave = (wave * 32767).astype(np.int16)
    stereo_wave = np.column_stack((wave, wave))
    return pygame.mixer.Sound(buffer=stereo_wave)


def generate_beep(frequency: float, duration: float) -> pygame.mixer.Sound:
    """단순 비프음 생성"""
    sample_rate = 22050
    n_samples = int(duration * sample_rate)
    t = np.linspace(0, duration, n_samples, False)
    
    wave = np.sin(2 * np.pi * frequency * t)
    
    # 엔벨로프
    envelope = np.ones(n_samples)
    fade_len = min(n_samples // 10, 1000)
    envelope[:fade_len] = np.linspace(0, 1, fade_len)
    envelope[-fade_len:] = np.linspace(1, 0, fade_len)
    
    wave = wave * envelope * 0.3
    wave = (wave * 32767).astype(np.int16)
    stereo_wave = np.column_stack((wave, wave))
    return pygame.mixer.Sound(buffer=stereo_wave)


def generate_boss_warning(duration: float = 1.0) -> pygame.mixer.Sound:
    """보스 경고음 생성"""
    sample_rate = 22050
    n_samples = int(duration * sample_rate)
    t = np.linspace(0, duration, n_samples, False)
    
    # 두 음이 번갈아 나오는 경고음
    freq1 = 440
    freq2 = 880
    
    # 0.25초마다 번갈아
    switch_freq = 4  # Hz
    switch = (np.sin(2 * np.pi * switch_freq * t) > 0).astype(float)
    
    wave = (np.sin(2 * np.pi * freq1 * t) * (1 - switch) + 
            np.sin(2 * np.pi * freq2 * t) * switch)
    
    envelope = np.ones(n_samples)
    fade_len = n_samples // 20
    envelope[-fade_len:] = np.linspace(1, 0, fade_len)
    
    wave = wave * envelope * 0.35
    wave = (wave * 32767).astype(np.int16)
    stereo_wave = np.column_stack((wave, wave))
    return pygame.mixer.Sound(buffer=stereo_wave)


def generate_bgm(duration: float = 30.0) -> pygame.mixer.Sound:
    """배경 음악 생성 (간단한 루프)"""
    sample_rate = 22050
    n_samples = int(duration * sample_rate)
    t = np.linspace(0, duration, n_samples, False)
    
    # 베이스 라인 (낮은 주파수)
    bass_freq = 55  # A1
    bass = np.sin(2 * np.pi * bass_freq * t) * 0.2
    
    # 베이스 리듬 (4비트)
    beat_freq = 2  # 2Hz = 120 BPM
    bass_rhythm = (np.sin(2 * np.pi * beat_freq * t) > 0.7).astype(float)
    bass = bass * (0.3 + bass_rhythm * 0.7)
    
    # 아르페지오
    arp_notes = [110, 138.59, 164.81, 220]  # A2, C#3, E3, A3
    arp_speed = 8  # Hz
    arp_index = (t * arp_speed).astype(int) % len(arp_notes)
    
    arp = np.zeros(n_samples)
    for i, note in enumerate(arp_notes):
        mask = (arp_index == i)
        arp[mask] = np.sin(2 * np.pi * note * t[mask])
    
    arp = arp * 0.15
    
    # 패드 (부드러운 배경음)
    pad_freq = 220
    pad = np.sin(2 * np.pi * pad_freq * t) * 0.08
    pad += np.sin(2 * np.pi * pad_freq * 1.5 * t) * 0.05  # 5도
    pad += np.sin(2 * np.pi * pad_freq * 2 * t) * 0.03    # 옥타브
    
    # LFO로 패드 볼륨 변조
    lfo = (np.sin(2 * np.pi * 0.2 * t) + 1) / 2
    pad = pad * (0.5 + lfo * 0.5)
    
    # 믹스
    wave = bass + arp + pad
    wave = wave / np.max(np.abs(wave)) * 0.4  # 정규화
    
    # 페이드 인/아웃
    fade_samples = sample_rate * 2
    wave[:fade_samples] *= np.linspace(0, 1, fade_samples)
    wave[-fade_samples:] *= np.linspace(1, 0, fade_samples)
    
    wave = (wave * 32767).astype(np.int16)
    stereo_wave = np.column_stack((wave, wave))
    return pygame.mixer.Sound(buffer=stereo_wave)


def generate_game_over(duration: float = 2.0) -> pygame.mixer.Sound:
    """게임 오버 음악 생성"""
    sample_rate = 22050
    n_samples = int(duration * sample_rate)
    t = np.linspace(0, duration, n_samples, False)
    
    # 하강하는 음계
    frequencies = [392, 349.23, 329.63, 293.66, 261.63]  # G4 -> C4
    note_duration = duration / len(frequencies)
    note_samples = int(note_duration * sample_rate)
    
    wave = np.zeros(n_samples)
    
    for i, freq in enumerate(frequencies):
        start = i * note_samples
        end = min((i + 1) * note_samples, n_samples)
        note_t = t[start:end] - t[start]
        
        # 감쇠하는 음
        note = np.sin(2 * np.pi * freq * note_t)
        note *= np.exp(-note_t * 2)
        
        wave[start:end] = note
    
    wave = wave * 0.4
    wave = (wave * 32767).astype(np.int16)
    stereo_wave = np.column_stack((wave, wave))
    return pygame.mixer.Sound(buffer=stereo_wave)


def generate_stage_clear(duration: float = 1.5) -> pygame.mixer.Sound:
    """스테이지 클리어 음악 생성"""
    sample_rate = 22050
    n_samples = int(duration * sample_rate)
    t = np.linspace(0, duration, n_samples, False)
    
    # 상승하는 팡파레
    frequencies = [261.63, 329.63, 392, 523.25]  # C4 -> C5
    note_duration = duration / len(frequencies)
    note_samples = int(note_duration * sample_rate)
    
    wave = np.zeros(n_samples)
    
    for i, freq in enumerate(frequencies):
        start = i * note_samples
        end = min((i + 1) * note_samples, n_samples)
        note_t = t[start:end] - t[start]
        
        # 밝은 음색 (하모닉스 추가)
        note = np.sin(2 * np.pi * freq * note_t)
        note += np.sin(2 * np.pi * freq * 2 * note_t) * 0.3
        note += np.sin(2 * np.pi * freq * 3 * note_t) * 0.1
        
        # 엔벨로프
        env_len = len(note)
        envelope = np.ones(env_len)
        attack = env_len // 10
        envelope[:attack] = np.linspace(0, 1, attack)
        envelope[-attack:] = np.linspace(1, 0.3, attack)
        
        wave[start:end] = note * envelope
    
    wave = wave / np.max(np.abs(wave)) * 0.4
    wave = (wave * 32767).astype(np.int16)
    stereo_wave = np.column_stack((wave, wave))
    return pygame.mixer.Sound(buffer=stereo_wave)