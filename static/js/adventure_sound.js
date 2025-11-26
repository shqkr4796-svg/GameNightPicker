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
        const duration = 12; // 12초 루프 (긴 포켓몬 전투 음악)

        // === 섹션 1 (0-3초): 신나는 메인 테마 ===
        const section1Main = [
            { freq: 523.25, duration: 0.3, time: 0, vol: 0.16, type: 'square' },    // C5
            { freq: 587.33, duration: 0.3, time: 0.35, vol: 0.16, type: 'square' }, // D5
            { freq: 659.25, duration: 0.4, time: 0.7, vol: 0.17, type: 'square' },  // E5
            { freq: 587.33, duration: 0.3, time: 1.15, vol: 0.16, type: 'square' }, // D5
            { freq: 523.25, duration: 0.3, time: 1.5, vol: 0.16, type: 'square' },  // C5
            { freq: 587.33, duration: 0.3, time: 1.85, vol: 0.16, type: 'square' }, // D5
            { freq: 659.25, duration: 0.4, time: 2.2, vol: 0.17, type: 'square' },  // E5
            { freq: 783.99, duration: 0.3, time: 2.65, vol: 0.16, type: 'square' }, // G5
            { freq: 740.0, duration: 0.3, time: 3.0, vol: 0.16, type: 'square' }    // F#5
        ];

        // === 섹션 2 (3-6초): 상승하는 멜로디 ===
        const section2Main = [
            { freq: 659.25, duration: 0.25, time: 3.0, vol: 0.17, type: 'square' },  // E5
            { freq: 698.46, duration: 0.25, time: 3.3, vol: 0.17, type: 'square' },  // F5
            { freq: 783.99, duration: 0.25, time: 3.6, vol: 0.17, type: 'square' },  // G5
            { freq: 880.0, duration: 0.3, time: 3.9, vol: 0.18, type: 'square' },    // A5
            { freq: 987.77, duration: 0.35, time: 4.3, vol: 0.18, type: 'square' },  // B5
            { freq: 1046.5, duration: 0.4, time: 4.7, vol: 0.18, type: 'square' },   // C6
            { freq: 987.77, duration: 0.3, time: 5.2, vol: 0.17, type: 'square' },   // B5
            { freq: 880.0, duration: 0.25, time: 5.55, vol: 0.16, type: 'square' },  // A5
            { freq: 783.99, duration: 0.25, time: 5.85, vol: 0.16, type: 'square' }  // G5
        ];

        // === 섹션 3 (6-9초): 다른 멜로디 변주 ===
        const section3Main = [
            { freq: 440.0, duration: 0.3, time: 6.0, vol: 0.16, type: 'square' },    // A4
            { freq: 523.25, duration: 0.3, time: 6.35, vol: 0.16, type: 'square' },  // C5
            { freq: 587.33, duration: 0.3, time: 6.7, vol: 0.16, type: 'square' },   // D5
            { freq: 659.25, duration: 0.35, time: 7.05, vol: 0.17, type: 'square' }, // E5
            { freq: 740.0, duration: 0.3, time: 7.45, vol: 0.17, type: 'square' },   // F#5
            { freq: 659.25, duration: 0.3, time: 7.8, vol: 0.16, type: 'square' },   // E5
            { freq: 587.33, duration: 0.3, time: 8.15, vol: 0.16, type: 'square' },  // D5
            { freq: 523.25, duration: 0.3, time: 8.5, vol: 0.16, type: 'square' },   // C5
            { freq: 587.33, duration: 0.25, time: 8.85, vol: 0.16, type: 'square' }  // D5
        ];

        // === 섹션 4 (9-12초): 클라이맥스 테마 ===
        const section4Main = [
            { freq: 659.25, duration: 0.2, time: 9.0, vol: 0.17, type: 'square' },   // E5
            { freq: 783.99, duration: 0.2, time: 9.25, vol: 0.17, type: 'square' },  // G5
            { freq: 659.25, duration: 0.2, time: 9.5, vol: 0.17, type: 'square' },   // E5
            { freq: 880.0, duration: 0.2, time: 9.75, vol: 0.18, type: 'square' },   // A5
            { freq: 783.99, duration: 0.2, time: 10.0, vol: 0.17, type: 'square' },  // G5
            { freq: 1046.5, duration: 0.3, time: 10.25, vol: 0.19, type: 'square' }, // C6
            { freq: 987.77, duration: 0.25, time: 10.6, vol: 0.18, type: 'square' }, // B5
            { freq: 880.0, duration: 0.25, time: 10.9, vol: 0.17, type: 'square' },  // A5
            { freq: 783.99, duration: 0.3, time: 11.2, vol: 0.17, type: 'square' }   // G5
        ];

        // 베이스 펄스 (지속적인 리듬)
        const bassPulse = [
            { freq: 110, duration: 0.2, time: 0, vol: 0.12, type: 'sine' },        // A2
            { freq: 110, duration: 0.2, time: 0.5, vol: 0.12, type: 'sine' },      // A2
            { freq: 123.47, duration: 0.2, time: 1, vol: 0.12, type: 'sine' },     // B2
            { freq: 110, duration: 0.2, time: 1.5, vol: 0.12, type: 'sine' },      // A2
            { freq: 110, duration: 0.2, time: 2, vol: 0.12, type: 'sine' },        // A2
            { freq: 110, duration: 0.2, time: 2.5, vol: 0.12, type: 'sine' },      // A2
            { freq: 147.93, duration: 0.2, time: 3, vol: 0.12, type: 'sine' },     // D3
            { freq: 110, duration: 0.2, time: 3.5, vol: 0.12, type: 'sine' },      // A2
            { freq: 110, duration: 0.2, time: 4, vol: 0.12, type: 'sine' },        // A2
            { freq: 110, duration: 0.2, time: 4.5, vol: 0.12, type: 'sine' },      // A2
            { freq: 123.47, duration: 0.2, time: 5, vol: 0.12, type: 'sine' },     // B2
            { freq: 110, duration: 0.2, time: 5.5, vol: 0.12, type: 'sine' },      // A2
            { freq: 110, duration: 0.2, time: 6, vol: 0.12, type: 'sine' },        // A2
            { freq: 110, duration: 0.2, time: 6.5, vol: 0.12, type: 'sine' },      // A2
            { freq: 147.93, duration: 0.2, time: 7, vol: 0.12, type: 'sine' },     // D3
            { freq: 110, duration: 0.2, time: 7.5, vol: 0.12, type: 'sine' },      // A2
            { freq: 110, duration: 0.2, time: 8, vol: 0.12, type: 'sine' },        // A2
            { freq: 110, duration: 0.2, time: 8.5, vol: 0.12, type: 'sine' },      // A2
            { freq: 123.47, duration: 0.2, time: 9, vol: 0.12, type: 'sine' },     // B2
            { freq: 110, duration: 0.2, time: 9.5, vol: 0.12, type: 'sine' },      // A2
            { freq: 110, duration: 0.2, time: 10, vol: 0.12, type: 'sine' },       // A2
            { freq: 110, duration: 0.2, time: 10.5, vol: 0.12, type: 'sine' },     // A2
            { freq: 147.93, duration: 0.2, time: 11, vol: 0.12, type: 'sine' },    // D3
            { freq: 110, duration: 0.2, time: 11.5, vol: 0.12, type: 'sine' }      // A2
        ];

        // 리드 라인 (높은 음역대 - 변주)
        const leadLine = [
            { freq: 880.0, duration: 0.25, time: 0.2, vol: 0.11, type: 'sine' },   // A5
            { freq: 932.33, duration: 0.25, time: 0.5, vol: 0.11, type: 'sine' },  // B♭5
            { freq: 1046.5, duration: 0.3, time: 0.8, vol: 0.12, type: 'sine' },   // C6
            { freq: 932.33, duration: 0.25, time: 1.2, vol: 0.11, type: 'sine' },  // B♭5
            { freq: 1174.66, duration: 0.3, time: 3.2, vol: 0.12, type: 'sine' },  // D6
            { freq: 1046.5, duration: 0.25, time: 3.55, vol: 0.11, type: 'sine' }, // C6
            { freq: 987.77, duration: 0.25, time: 3.85, vol: 0.11, type: 'sine' }, // B5
            { freq: 1046.5, duration: 0.3, time: 4.15, vol: 0.12, type: 'sine' },  // C6
            { freq: 1174.66, duration: 0.25, time: 4.5, vol: 0.12, type: 'sine' }, // D6
            { freq: 1046.5, duration: 0.25, time: 4.8, vol: 0.11, type: 'sine' },  // C6
            { freq: 987.77, duration: 0.25, time: 5.1, vol: 0.11, type: 'sine' },  // B5
            { freq: 1174.66, duration: 0.3, time: 6.2, vol: 0.12, type: 'sine' },  // D6
            { freq: 1046.5, duration: 0.25, time: 6.55, vol: 0.11, type: 'sine' }, // C6
            { freq: 1046.5, duration: 0.3, time: 9.2, vol: 0.12, type: 'sine' },   // C6
            { freq: 1174.66, duration: 0.25, time: 9.55, vol: 0.12, type: 'sine' },// D6
            { freq: 1046.5, duration: 0.25, time: 9.85, vol: 0.11, type: 'sine' }  // C6
        ];

        // 코드 배경음 (아래쪽 - 변화)
        const chordBg = [
            { freq: 261.63, duration: 0.6, time: 0, vol: 0.09, type: 'sine' },     // C4
            { freq: 329.63, duration: 0.6, time: 0.7, vol: 0.09, type: 'sine' },   // E4
            { freq: 392.0, duration: 0.6, time: 1.4, vol: 0.09, type: 'sine' },    // G4
            { freq: 329.63, duration: 0.6, time: 2.1, vol: 0.09, type: 'sine' },   // E4
            { freq: 293.66, duration: 0.6, time: 3.0, vol: 0.09, type: 'sine' },   // D4
            { freq: 349.23, duration: 0.6, time: 3.7, vol: 0.09, type: 'sine' },   // F4
            { freq: 440.0, duration: 0.6, time: 4.4, vol: 0.09, type: 'sine' },    // A4
            { freq: 392.0, duration: 0.6, time: 5.1, vol: 0.09, type: 'sine' },    // G4
            { freq: 329.63, duration: 0.6, time: 6.0, vol: 0.09, type: 'sine' },   // E4
            { freq: 392.0, duration: 0.6, time: 6.7, vol: 0.09, type: 'sine' },    // G4
            { freq: 440.0, duration: 0.6, time: 7.4, vol: 0.09, type: 'sine' },    // A4
            { freq: 349.23, duration: 0.6, time: 8.1, vol: 0.09, type: 'sine' },   // F4
            { freq: 261.63, duration: 0.6, time: 9.0, vol: 0.09, type: 'sine' },   // C4
            { freq: 329.63, duration: 0.6, time: 9.7, vol: 0.09, type: 'sine' },   // E4
            { freq: 392.0, duration: 0.6, time: 10.4, vol: 0.09, type: 'sine' },   // G4
            { freq: 329.63, duration: 0.6, time: 11.1, vol: 0.09, type: 'sine' }   // E4
        ];

        // 모든 패턴 재생
        [...section1Main, ...section2Main, ...section3Main, ...section4Main].forEach(note => {
            this._playTone(note.freq, note.duration, now + note.time, note.vol, note.type);
        });

        bassPulse.forEach(note => {
            this._playTone(note.freq, note.duration, now + note.time, note.vol, note.type);
        });

        leadLine.forEach(note => {
            this._playTone(note.freq, note.duration, now + note.time, note.vol, note.type);
        });

        chordBg.forEach(note => {
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

    // 음량 조절 (0-1 범위)
    setVolume(volumePercent) {
        this.masterVolume = volumePercent / 100;
    }

    // 마스터 볼륨 적용 헬퍼
    _getVolume(baseVolume) {
        return baseVolume * (this.masterVolume || 1);
    }
}

// 전역 사운드 인스턴스
const adventureSound = new AdventureSound();
