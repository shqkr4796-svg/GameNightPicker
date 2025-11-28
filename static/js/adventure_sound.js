// 모험 시스템 효과음 시스템
class AdventureSound {
    constructor() {
        this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
        this.backgroundMusic = null;
        this.isMusicPlaying = false;
        this.soundEnabled = true;
        this.activeOscillators = [];
        this.musicLoopTimeout = null;
        
        // Master Gain Node 생성 (모든 사운드 제어용)
        this.masterGain = this.audioContext.createGain();
        this.masterGain.connect(this.audioContext.destination);
        this.masterGain.gain.value = 1;
    }

    // 배경음악 (무한 반복)
    playBackgroundMusic() {
        return; // 배경음악 비활성화
        
        // 모든 기존 음악 정지
        this.isMusicPlaying = false;
        if (this.musicLoopTimeout) {
            clearTimeout(this.musicLoopTimeout);
            this.musicLoopTimeout = null;
        }
        
        // 활성 oscillators 즉시 정지 (이전 재생이 겹치지 않도록)
        this.activeOscillators.forEach(osc => {
            try {
                osc.stop(this.audioContext.currentTime);
            } catch (e) {}
        });
        this.activeOscillators = [];
        
        // Master Gain 리셋 (모든 소리 정지)
        this.masterGain.gain.setValueAtTime(0, this.audioContext.currentTime);
        
        // 약간의 딜레이 후 음악 시작
        setTimeout(() => {
            if (!this.isMusicPlaying && this.soundEnabled) {
                this.masterGain.gain.setValueAtTime(1, this.audioContext.currentTime);
                this.isMusicPlaying = true;
                this._loopBackgroundMusic();
            }
        }, 50);
    }

    _loopBackgroundMusic() {
        if (!this.soundEnabled) return;
        const ctx = this.audioContext;
        const now = ctx.currentTime;
        const duration = 8; // 8초 루프 (빠른 전투 음악)

        // === 드럼 비트 (강한 타격) ===
        const drumBeat = [
            // 킥드럼 (Kick): 강한 베이스 펀치
            { freq: 60, duration: 0.15, time: 0, vol: 0.06, type: 'sine' },
            { freq: 60, duration: 0.15, time: 0.5, vol: 0.06, type: 'sine' },
            { freq: 60, duration: 0.15, time: 1, vol: 0.06, type: 'sine' },
            { freq: 60, duration: 0.15, time: 1.5, vol: 0.06, type: 'sine' },
            { freq: 60, duration: 0.15, time: 2, vol: 0.06, type: 'sine' },
            { freq: 60, duration: 0.15, time: 2.5, vol: 0.06, type: 'sine' },
            { freq: 60, duration: 0.15, time: 3, vol: 0.06, type: 'sine' },
            { freq: 60, duration: 0.15, time: 3.5, vol: 0.06, type: 'sine' },
            { freq: 60, duration: 0.15, time: 4, vol: 0.06, type: 'sine' },
            { freq: 60, duration: 0.15, time: 4.5, vol: 0.06, type: 'sine' },
            { freq: 60, duration: 0.15, time: 5, vol: 0.06, type: 'sine' },
            { freq: 60, duration: 0.15, time: 5.5, vol: 0.06, type: 'sine' },
            { freq: 60, duration: 0.15, time: 6, vol: 0.06, type: 'sine' },
            { freq: 60, duration: 0.15, time: 6.5, vol: 0.06, type: 'sine' },
            { freq: 60, duration: 0.15, time: 7, vol: 0.06, type: 'sine' },
            { freq: 60, duration: 0.15, time: 7.5, vol: 0.06, type: 'sine' }
        ];

        // === 베이스 라인 (Am-G-C-F 단조 진행) ===
        const bassLine = [
            // Am (A2 = 110Hz)
            { freq: 110, duration: 0.5, time: 0, vol: 0.05, type: 'sine' },
            { freq: 110, duration: 0.5, time: 0.5, vol: 0.05, type: 'sine' },
            // G (G2 = 98Hz)
            { freq: 98, duration: 0.5, time: 1, vol: 0.05, type: 'sine' },
            { freq: 98, duration: 0.5, time: 1.5, vol: 0.05, type: 'sine' },
            // C (C3 = 130.81Hz)
            { freq: 130.81, duration: 0.5, time: 2, vol: 0.05, type: 'sine' },
            { freq: 130.81, duration: 0.5, time: 2.5, vol: 0.05, type: 'sine' },
            // F (F2 = 87.31Hz)
            { freq: 87.31, duration: 0.5, time: 3, vol: 0.05, type: 'sine' },
            { freq: 87.31, duration: 0.5, time: 3.5, vol: 0.05, type: 'sine' },
            // 반복
            { freq: 110, duration: 0.5, time: 4, vol: 0.05, type: 'sine' },
            { freq: 110, duration: 0.5, time: 4.5, vol: 0.05, type: 'sine' },
            { freq: 98, duration: 0.5, time: 5, vol: 0.05, type: 'sine' },
            { freq: 98, duration: 0.5, time: 5.5, vol: 0.05, type: 'sine' },
            { freq: 130.81, duration: 0.5, time: 6, vol: 0.05, type: 'sine' },
            { freq: 130.81, duration: 0.5, time: 6.5, vol: 0.05, type: 'sine' },
            { freq: 87.31, duration: 0.5, time: 7, vol: 0.05, type: 'sine' },
            { freq: 87.31, duration: 0.25, time: 7.5, vol: 0.05, type: 'sine' }
        ];

        // === 메인 멜로디 (반복되는 짧은 hook + 당김음) ===
        const mainMelody = [
            // 후크 1: E5-G5-E5-A5 (A단조 내) - 당김음 리듬
            { freq: 659.25, duration: 0.2, time: 0, vol: 0.06, type: 'square' },    // E5
            { freq: 783.99, duration: 0.2, time: 0.25, vol: 0.06, type: 'square' }, // G5
            { freq: 659.25, duration: 0.2, time: 0.45, vol: 0.06, type: 'square' }, // E5
            { freq: 880.0, duration: 0.25, time: 0.7, vol: 0.06, type: 'square' },  // A5
            // 반 박자 쉼
            // 후크 2: G5-F5-G5-B5 (변주)
            { freq: 783.99, duration: 0.2, time: 1.1, vol: 0.06, type: 'square' },  // G5
            { freq: 698.46, duration: 0.2, time: 1.35, vol: 0.06, type: 'square' }, // F5
            { freq: 783.99, duration: 0.2, time: 1.55, vol: 0.06, type: 'square' }, // G5
            { freq: 987.77, duration: 0.25, time: 1.8, vol: 0.06, type: 'square' }, // B5
            // 후크 1 반복
            { freq: 659.25, duration: 0.2, time: 2.2, vol: 0.06, type: 'square' },  // E5
            { freq: 783.99, duration: 0.2, time: 2.45, vol: 0.06, type: 'square' }, // G5
            { freq: 659.25, duration: 0.2, time: 2.65, vol: 0.06, type: 'square' }, // E5
            { freq: 880.0, duration: 0.25, time: 2.9, vol: 0.06, type: 'square' },  // A5
            // 후크 3: C6-B5-C6-E5 (긴장감)
            { freq: 1046.5, duration: 0.15, time: 3.3, vol: 0.06, type: 'square' }, // C6
            { freq: 987.77, duration: 0.15, time: 3.5, vol: 0.06, type: 'square' }, // B5
            { freq: 1046.5, duration: 0.15, time: 3.7, vol: 0.06, type: 'square' }, // C6
            { freq: 659.25, duration: 0.2, time: 3.9, vol: 0.06, type: 'square' },  // E5 (불협화)
            // 후크 1 반복 (높게)
            { freq: 659.25, duration: 0.2, time: 4.2, vol: 0.06, type: 'square' },  // E5
            { freq: 783.99, duration: 0.2, time: 4.45, vol: 0.06, type: 'square' }, // G5
            { freq: 659.25, duration: 0.2, time: 4.65, vol: 0.06, type: 'square' }, // E5
            { freq: 880.0, duration: 0.25, time: 4.9, vol: 0.06, type: 'square' },  // A5
            // 후크 2 반복
            { freq: 783.99, duration: 0.2, time: 5.1, vol: 0.06, type: 'square' },  // G5
            { freq: 698.46, duration: 0.2, time: 5.35, vol: 0.06, type: 'square' }, // F5
            { freq: 783.99, duration: 0.2, time: 5.55, vol: 0.06, type: 'square' }, // G5
            { freq: 987.77, duration: 0.25, time: 5.8, vol: 0.06, type: 'square' }, // B5
            // 클라이맥스: 상승하는 패턴
            { freq: 659.25, duration: 0.15, time: 6.2, vol: 0.06, type: 'square' },  // E5
            { freq: 783.99, duration: 0.15, time: 6.4, vol: 0.06, type: 'square' },  // G5
            { freq: 880.0, duration: 0.15, time: 6.6, vol: 0.06, type: 'square' },   // A5
            { freq: 1046.5, duration: 0.25, time: 6.8, vol: 0.06, type: 'square' }   // C6 (클라이맥스)
        ];

        // === 불협화음 (긴장감) - Diminished chord (Em7b5) ===
        const dissonance = [
            // 배경에서 울리는 불협화음
            { freq: 622.25, duration: 0.4, time: 1.5, vol: 0.03, type: 'sine' },   // Eb5 (불협화음)
            { freq: 622.25, duration: 0.4, time: 3.5, vol: 0.03, type: 'sine' },   // Eb5
            { freq: 622.25, duration: 0.4, time: 5.5, vol: 0.03, type: 'sine' }    // Eb5
        ];

        // === 신디사이저 같은 현대적 사운드 (고음역 리드) ===
        const synth = [
            { freq: 1174.66, duration: 0.15, time: 0.1, vol: 0.03, type: 'sine' },   // D6
            { freq: 1174.66, duration: 0.15, time: 0.3, vol: 0.03, type: 'sine' },   // D6
            { freq: 1046.5, duration: 0.15, time: 0.5, vol: 0.03, type: 'sine' },    // C6
            { freq: 1174.66, duration: 0.15, time: 2.1, vol: 0.03, type: 'sine' },   // D6
            { freq: 1046.5, duration: 0.15, time: 2.3, vol: 0.03, type: 'sine' },    // C6
            { freq: 987.77, duration: 0.15, time: 2.5, vol: 0.03, type: 'sine' },    // B5
            { freq: 1174.66, duration: 0.15, time: 4.1, vol: 0.03, type: 'sine' },   // D6
            { freq: 1174.66, duration: 0.15, time: 4.3, vol: 0.03, type: 'sine' },   // D6
            { freq: 1046.5, duration: 0.15, time: 4.5, vol: 0.03, type: 'sine' },    // C6
            { freq: 1174.66, duration: 0.15, time: 6.1, vol: 0.03, type: 'sine' },   // D6
            { freq: 1296.83, duration: 0.15, time: 6.3, vol: 0.03, type: 'sine' },   // E6 (상승)
            { freq: 1396.91, duration: 0.15, time: 6.5, vol: 0.04, type: 'sine' }   // F6 (클라이맥스)
        ];

        // 모든 패턴 재생
        [...drumBeat, ...bassLine, ...mainMelody, ...dissonance, ...synth].forEach(note => {
            this._playTone(note.freq, note.duration, now + note.time, note.vol, note.type);
        });

        if (this.isMusicPlaying && this.soundEnabled) {
            this.musicLoopTimeout = setTimeout(() => this._loopBackgroundMusic(), duration * 1000);
        }
    }

    stopBackgroundMusic() {
        this.isMusicPlaying = false;
        if (this.musicLoopTimeout) {
            clearTimeout(this.musicLoopTimeout);
            this.musicLoopTimeout = null;
        }
        // Master Gain을 0으로 즉시 설정해서 모든 음악 음소거
        this.masterGain.gain.setValueAtTime(0, this.audioContext.currentTime);
        // 활성 oscillators 즉시 정지
        this.activeOscillators.forEach(osc => {
            try {
                osc.stop(this.audioContext.currentTime);
            } catch (e) {
                // 이미 정지된 oscillator 무시
            }
        });
        this.activeOscillators = [];
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
        gain.connect(this.masterGain);

        osc.frequency.value = frequency;
        osc.type = waveType;

        // 부드러운 페이드인/아웃
        gain.gain.setValueAtTime(0, startTime);
        gain.gain.linearRampToValueAtTime(volume, startTime + 0.05);
        gain.gain.exponentialRampToValueAtTime(0.01, startTime + duration - 0.05);

        osc.start(startTime);
        osc.stop(startTime + duration);
        
        // 활성 oscillator 추적
        this.activeOscillators.push(osc);
        setTimeout(() => {
            const idx = this.activeOscillators.indexOf(osc);
            if (idx > -1) this.activeOscillators.splice(idx, 1);
        }, (duration + 0.1) * 1000);
    }

    // 주파수 스윕 (화살표 음)
    _playSweep(startFreq, endFreq, duration, startTime, volume = 0.1) {
        const ctx = this.audioContext;
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();

        osc.connect(gain);
        gain.connect(this.masterGain);

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
