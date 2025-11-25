// 모험 시스템 효과음 시스템
class AdventureSound {
    constructor() {
        this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
        this.backgroundMusic = null;
        this.isMusicPlaying = false;
        this.soundEnabled = true;
    }

    // 배경음악 (무한 반복)
    playBackgroundMusic() {
        if (this.isMusicPlaying) return;
        this.isMusicPlaying = true;
        this._loopBackgroundMusic();
    }

    _loopBackgroundMusic() {
        if (!this.soundEnabled) return;
        const ctx = this.audioContext;
        const now = ctx.currentTime;
        const duration = 8; // 8초 루프 (포켓몬 스타일)

        // 포켓몬 게임 스타일 배경음악 - 아르페지오 패턴
        // 베이스 라인 (저음)
        const bassPattern = [
            { freq: 164.81, duration: 0.5, time: 0, vol: 0.1, type: 'sine' },       // E
            { freq: 196.0, duration: 0.5, time: 0.5, vol: 0.1, type: 'sine' },      // G
            { freq: 220.0, duration: 0.5, time: 1.0, vol: 0.1, type: 'sine' },      // A
            { freq: 196.0, duration: 0.5, time: 1.5, vol: 0.1, type: 'sine' },      // G
            { freq: 164.81, duration: 0.5, time: 2.0, vol: 0.1, type: 'sine' },     // E
            { freq: 196.0, duration: 0.5, time: 2.5, vol: 0.1, type: 'sine' },      // G
            { freq: 220.0, duration: 0.5, time: 3.0, vol: 0.1, type: 'sine' },      // A
            { freq: 196.0, duration: 0.5, time: 3.5, vol: 0.1, type: 'sine' },      // G
            { freq: 164.81, duration: 0.5, time: 4.0, vol: 0.1, type: 'sine' },     // E
            { freq: 196.0, duration: 0.5, time: 4.5, vol: 0.1, type: 'sine' },      // G
            { freq: 220.0, duration: 0.5, time: 5.0, vol: 0.1, type: 'sine' },      // A
            { freq: 196.0, duration: 0.5, time: 5.5, vol: 0.1, type: 'sine' },      // G
            { freq: 164.81, duration: 0.5, time: 6.0, vol: 0.1, type: 'sine' },     // E
            { freq: 196.0, duration: 0.5, time: 6.5, vol: 0.1, type: 'sine' },      // G
            { freq: 220.0, duration: 0.5, time: 7.0, vol: 0.1, type: 'sine' },      // A
            { freq: 196.0, duration: 0.5, time: 7.5, vol: 0.1, type: 'sine' }       // G
        ];

        // 중간 음역대 아르페지오 (주요 멜로디)
        const middlePattern = [
            { freq: 329.63, duration: 0.35, time: 0.2, vol: 0.14, type: 'sine' },   // E
            { freq: 392.0, duration: 0.35, time: 0.55, vol: 0.14, type: 'sine' },   // G
            { freq: 440.0, duration: 0.35, time: 0.9, vol: 0.14, type: 'sine' },    // A
            { freq: 392.0, duration: 0.35, time: 1.25, vol: 0.14, type: 'sine' },   // G
            { freq: 329.63, duration: 0.35, time: 1.6, vol: 0.14, type: 'sine' },   // E
            { freq: 392.0, duration: 0.35, time: 1.95, vol: 0.14, type: 'sine' },   // G
            { freq: 440.0, duration: 0.35, time: 2.3, vol: 0.14, type: 'sine' },    // A
            { freq: 392.0, duration: 0.35, time: 2.65, vol: 0.14, type: 'sine' },   // G
            { freq: 329.63, duration: 0.35, time: 3.0, vol: 0.14, type: 'sine' },   // E (반복)
            { freq: 392.0, duration: 0.35, time: 3.35, vol: 0.14, type: 'sine' },   // G
            { freq: 440.0, duration: 0.35, time: 3.7, vol: 0.14, type: 'sine' },    // A
            { freq: 392.0, duration: 0.35, time: 4.05, vol: 0.14, type: 'sine' },   // G
            { freq: 329.63, duration: 0.35, time: 4.4, vol: 0.14, type: 'sine' },   // E
            { freq: 392.0, duration: 0.35, time: 4.75, vol: 0.14, type: 'sine' },   // G
            { freq: 440.0, duration: 0.35, time: 5.1, vol: 0.14, type: 'sine' },    // A
            { freq: 392.0, duration: 0.35, time: 5.45, vol: 0.14, type: 'sine' },   // G
            { freq: 329.63, duration: 0.35, time: 5.8, vol: 0.14, type: 'sine' },   // E
            { freq: 392.0, duration: 0.35, time: 6.15, vol: 0.14, type: 'sine' },   // G
            { freq: 440.0, duration: 0.35, time: 6.5, vol: 0.14, type: 'sine' },    // A
            { freq: 392.0, duration: 0.35, time: 6.85, vol: 0.14, type: 'sine' }    // G
        ];

        // 높은 음역대 악센트 (맑고 밝은 느낌)
        const highPattern = [
            { freq: 659.25, duration: 0.25, time: 0.4, vol: 0.09, type: 'sine' },   // E (high)
            { freq: 783.99, duration: 0.25, time: 1.2, vol: 0.09, type: 'sine' },   // G (high)
            { freq: 880.0, duration: 0.25, time: 2.0, vol: 0.09, type: 'sine' },    // A (high)
            { freq: 783.99, duration: 0.25, time: 2.8, vol: 0.09, type: 'sine' },   // G (high)
            { freq: 659.25, duration: 0.25, time: 3.6, vol: 0.09, type: 'sine' },   // E (high)
            { freq: 783.99, duration: 0.25, time: 4.4, vol: 0.09, type: 'sine' },   // G (high)
            { freq: 880.0, duration: 0.25, time: 5.2, vol: 0.09, type: 'sine' },    // A (high)
            { freq: 783.99, duration: 0.25, time: 6.0, vol: 0.09, type: 'sine' }    // G (high)
        ];

        // 모든 패턴 재생
        bassPattern.forEach(note => {
            this._playTone(note.freq, note.duration, now + note.time, note.vol, note.type);
        });

        middlePattern.forEach(note => {
            this._playTone(note.freq, note.duration, now + note.time, note.vol, note.type);
        });

        highPattern.forEach(note => {
            this._playTone(note.freq, note.duration, now + note.time, note.vol, note.type);
        });

        if (this.isMusicPlaying) {
            setTimeout(() => this._loopBackgroundMusic(), duration * 1000);
        }
    }

    stopBackgroundMusic() {
        this.isMusicPlaying = false;
    }

    // 기술 선택 소리 (슬롯 1, 2, 3 다르게)
    playSkillSelectSound(slotIndex) {
        if (!this.soundEnabled) return;
        const ctx = this.audioContext;
        const now = ctx.currentTime;
        
        const frequencies = [
            [523.25, 659.25],     // 슬롯 1: C5, E5
            [587.33, 739.99],     // 슬롯 2: D5, F#5
            [659.25, 783.99]      // 슬롯 3: E5, G5
        ];

        const freqs = frequencies[slotIndex] || frequencies[0];
        
        // 2음 화음
        this._playTone(freqs[0], 0.2, now, 0.1, 'square');
        this._playTone(freqs[1], 0.2, now, 0.1, 'sine');
    }

    // 기술 발동 소리 (등급 + 기술별)
    playSkillCastSound(skillName, rarity) {
        if (!this.soundEnabled) return;
        const ctx = this.audioContext;
        const now = ctx.currentTime;

        // 등급별 기본 주파수
        const rarityBaseFreq = {
            '레어': 440,
            '에픽': 587.33,
            '유니크': 739.99,
            '레전드리': 987.77,
            '신화급': 1174.66
        };

        const baseFreq = rarityBaseFreq[rarity] || 440;

        // 기술별 패턴 (서로 다른 음향 효과)
        const skillPatterns = {
            '일반공격': () => {
                this._playTone(baseFreq, 0.3, now, 0.1, 'sine');
            },
            '강타': () => {
                this._playTone(baseFreq, 0.15, now, 0.15, 'square');
                this._playTone(baseFreq * 1.5, 0.15, now + 0.15, 0.15, 'square');
            },
            '불릿': () => {
                this._playTone(baseFreq * 2, 0.1, now, 0.1, 'sawtooth');
                this._playTone(baseFreq * 1.5, 0.1, now + 0.1, 0.1, 'sawtooth');
                this._playTone(baseFreq, 0.1, now + 0.2, 0.1, 'sine');
            },
            '방어': () => {
                this._playTone(baseFreq * 0.75, 0.4, now, 0.1, 'sine');
            },
            '회복': () => {
                this._playTone(baseFreq * 1.25, 0.1, now, 0.08, 'sine');
                this._playTone(baseFreq * 1.5, 0.1, now + 0.1, 0.08, 'sine');
                this._playTone(baseFreq * 1.75, 0.1, now + 0.2, 0.08, 'sine');
            },
            '특수기술': () => {
                this._playTone(baseFreq * 2, 0.2, now, 0.1, 'sawtooth');
                this._playTone(baseFreq, 0.2, now + 0.1, 0.1, 'square');
            }
        };

        // 기술 이름에 매칭되는 패턴 찾기
        let matched = false;
        for (const [key, func] of Object.entries(skillPatterns)) {
            if (skillName.includes(key) || skillName === key) {
                func();
                matched = true;
                break;
            }
        }

        // 매칭되지 않으면 기본 음향
        if (!matched) {
            this._playTone(baseFreq, 0.3, now, 0.1, 'sine');
        }
    }

    // 피해 효과음
    playDamageSound(damageAmount = 1) {
        if (!this.soundEnabled) return;
        const ctx = this.audioContext;
        const now = ctx.currentTime;

        // 피해량에 따라 다른 음향
        if (damageAmount > 50) {
            // 큰 피해: 낮은 음
            this._playTone(110, 0.2, now, 0.15, 'square');
            this._playTone(82.41, 0.15, now + 0.1, 0.15, 'sine');
        } else if (damageAmount > 20) {
            // 중간 피해
            this._playTone(220, 0.15, now, 0.1, 'square');
            this._playTone(165.41, 0.1, now + 0.1, 0.1, 'sine');
        } else {
            // 작은 피해: 높은 음
            this._playTone(440, 0.1, now, 0.08, 'sine');
            this._playTone(330, 0.08, now + 0.08, 0.08, 'sine');
        }
    }

    // 전투 시작 소리
    playBattleStartSound() {
        if (!this.soundEnabled) return;
        const ctx = this.audioContext;
        const now = ctx.currentTime;

        // 웅장한 팡파레
        this._playTone(392.0, 0.2, now, 0.15, 'sine');
        this._playTone(523.25, 0.2, now + 0.2, 0.15, 'sine');
        this._playTone(659.25, 0.3, now + 0.4, 0.15, 'sine');
    }

    // 전투 종료 (승리)
    playVictorySound() {
        if (!this.soundEnabled) return;
        const ctx = this.audioContext;
        const now = ctx.currentTime;

        // 승리 팡파레
        const notes = [
            { freq: 523.25, time: 0 },
            { freq: 659.25, time: 0.2 },
            { freq: 783.99, time: 0.4 }
        ];

        notes.forEach(note => {
            this._playTone(note.freq, 0.3, now + note.time, 0.15, 'sine');
        });
    }

    // 전투 종료 (패배)
    playDefeatSound() {
        if (!this.soundEnabled) return;
        const ctx = this.audioContext;
        const now = ctx.currentTime;

        // 패배 음
        this._playTone(392.0, 0.3, now, 0.2, 'sine');
        this._playTone(329.63, 0.3, now + 0.3, 0.2, 'sine');
        this._playTone(261.63, 0.4, now + 0.6, 0.2, 'sine');
    }

    // 몬스터 처치 소리
    playMonsterDefeatedSound() {
        if (!this.soundEnabled) return;
        const ctx = this.audioContext;
        const now = ctx.currentTime;

        // 휘익 소리
        this._playSweep(1000, 200, 0.3, now, 0.15);
    }

    // 힌트 음향
    playSkillGainedSound() {
        if (!this.soundEnabled) return;
        const ctx = this.audioContext;
        const now = ctx.currentTime;

        // 반짝이는 소리
        this._playTone(800, 0.1, now, 0.08, 'sine');
        this._playTone(1000, 0.1, now + 0.1, 0.08, 'sine');
        this._playTone(1200, 0.15, now + 0.2, 0.08, 'sine');
    }

    // 기본 톤 재생
    _playTone(frequency, duration, startTime, volume = 0.1, waveType = 'sine') {
        const ctx = this.audioContext;
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();

        osc.connect(gain);
        gain.connect(ctx.destination);

        osc.frequency.value = frequency;
        osc.type = waveType;

        // 부드러운 페이드인/아웃
        gain.gain.setValueAtTime(0, startTime);
        gain.gain.linearRampToValueAtTime(volume, startTime + 0.05);
        gain.gain.exponentialRampToValueAtTime(0.01, startTime + duration - 0.05);

        osc.start(startTime);
        osc.stop(startTime + duration);
    }

    // 주파수 스윕 (화살표 음)
    _playSweep(startFreq, endFreq, duration, startTime, volume = 0.1) {
        const ctx = this.audioContext;
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();

        osc.connect(gain);
        gain.connect(ctx.destination);

        osc.frequency.setValueAtTime(startFreq, startTime);
        osc.frequency.exponentialRampToValueAtTime(endFreq, startTime + duration);

        gain.gain.setValueAtTime(volume, startTime);
        gain.gain.exponentialRampToValueAtTime(0.01, startTime + duration);

        osc.start(startTime);
        osc.stop(startTime + duration);
    }

    // 사운드 토글
    toggleSound() {
        this.soundEnabled = !this.soundEnabled;
        if (!this.soundEnabled) {
            this.stopBackgroundMusic();
        } else {
            this.playBackgroundMusic();
        }
        return this.soundEnabled;
    }
}

// 전역 사운드 인스턴스
const adventureSound = new AdventureSound();
