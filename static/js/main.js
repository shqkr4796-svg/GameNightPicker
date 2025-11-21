// 라이프 시뮬레이션 게임 - 메인 JavaScript 파일

// 효과음 시스템
class SoundManager {
    constructor() {
        this.audioContext = null;
        this.enabled = localStorage.getItem('soundEnabled') !== 'false';
        this.volume = parseFloat(localStorage.getItem('soundVolume')) || 0.3;
        this.init();
    }

    async init() {
        try {
            this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
            this.setupSoundEvents();
        } catch (error) {
            console.log('오디오 컨텍스트 초기화 실패:', error);
            this.enabled = false;
        }
    }

    // 간단한 톤 생성
    createTone(frequency, duration, type = 'sine') {
        if (!this.enabled || !this.audioContext) return;

        const oscillator = this.audioContext.createOscillator();
        const gainNode = this.audioContext.createGain();

        oscillator.connect(gainNode);
        gainNode.connect(this.audioContext.destination);

        oscillator.frequency.value = frequency;
        oscillator.type = type;

        gainNode.gain.setValueAtTime(0, this.audioContext.currentTime);
        gainNode.gain.linearRampToValueAtTime(this.volume, this.audioContext.currentTime + 0.01);
        gainNode.gain.exponentialRampToValueAtTime(0.001, this.audioContext.currentTime + duration);

        oscillator.start(this.audioContext.currentTime);
        oscillator.stop(this.audioContext.currentTime + duration);
    }

    // 성공 사운드 (상승하는 톤)
    playSuccess() {
        this.createTone(523, 0.15); // C5
        setTimeout(() => this.createTone(659, 0.15), 100); // E5
        setTimeout(() => this.createTone(784, 0.2), 200); // G5
    }

    // 실패 사운드 (하강하는 톤)
    playError() {
        this.createTone(523, 0.15); // C5
        setTimeout(() => this.createTone(440, 0.15), 100); // A4
        setTimeout(() => this.createTone(349, 0.2), 200); // F4
    }

    // 버튼 클릭 사운드
    playClick() {
        this.createTone(800, 0.05, 'square');
    }

    // 퀴즈 정답 사운드 (딩동댕)
    playQuizCorrect() {
        // 딩동댕 효과음
        this.createTone(523, 0.12); // C5 (딩)
        setTimeout(() => this.createTone(659, 0.12), 120); // E5 (동)
        setTimeout(() => this.createTone(784, 0.18), 240); // G5 (댕)
    }

    // 퀴즈 오답 사운드 (땡)
    playQuizWrong() {
        // 땡 효과음 (낮은 음의 짧은 톤)
        this.createTone(220, 0.25, 'sawtooth'); // A3
        setTimeout(() => this.createTone(196, 0.25, 'sawtooth'), 50); // G3
    }

    // 돈 소리 (구매/판매)
    playMoney() {
        this.createTone(880, 0.05); // A5
        setTimeout(() => this.createTone(1109, 0.05), 50); // C#6
        setTimeout(() => this.createTone(1319, 0.1), 100); // E6
    }

    // 레벨업 소리
    playLevelUp() {
        for (let i = 0; i < 5; i++) {
            setTimeout(() => {
                this.createTone(523 + (i * 131), 0.1); // 상승하는 음계
            }, i * 100);
        }
    }

    // 작업 완료 소리 (ATM 돈 소리)
    playWorkComplete() {
        this.createTone(880, 0.08); // A5
        setTimeout(() => this.createTone(1109, 0.08), 80); // C#6
        setTimeout(() => this.createTone(1319, 0.12), 160); // E6
        setTimeout(() => this.createTone(1568, 0.1), 240); // G6 (추가)
    }

    // 잠자기 소리 (부드러운 톤)
    playSleep() {
        this.createTone(220, 0.5, 'sine'); // A3
        setTimeout(() => this.createTone(196, 0.5, 'sine'), 250); // G3
    }

    // 몬스터 수집 효과음 (상자 여는 소리)
    playMonsterCollected() {
        // 상자 여는 효과음 (딸깍 + 반짝이는 소리)
        this.createTone(800, 0.05, 'square'); // 딸깍
        setTimeout(() => this.createTone(1200, 0.08), 100); // 반짝1
        setTimeout(() => this.createTone(1500, 0.08), 200); // 반짝2
        setTimeout(() => this.createTone(1800, 0.1), 300); // 반짝3
        setTimeout(() => this.createTone(2000, 0.12), 400); // 반짝4
    }

    // 이벤트 리스너 설정
    setupSoundEvents() {
        // 모든 버튼에 클릭 사운드 추가
        document.addEventListener('click', (e) => {
            if (e.target.matches('button, .btn, input[type="submit"]')) {
                this.playClick();
            }
        });

        // 폼 제출 시 사운드
        document.addEventListener('submit', (e) => {
            const form = e.target;
            const action = form.action;
            
            if (action.includes('work')) {
                this.playWorkComplete();
            } else if (action.includes('sleep')) {
                this.playSleep();
            } else if (action.includes('buy') || action.includes('sell')) {
                this.playMoney();
            } else if (action.includes('quiz') || action.includes('take_quiz')) {
                // 퀴즈 사운드는 결과에 따라 별도 처리
            }
        });

        // 플래시 메시지 기반 사운드
        this.setupFlashMessageSounds();
    }

    // 플래시 메시지에 따른 사운드 재생
    setupFlashMessageSounds() {
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                mutation.addedNodes.forEach((node) => {
                    if (node.nodeType === 1 && node.classList) {
                        if (node.classList.contains('alert-success')) {
                            const text = node.textContent.toLowerCase();
                            if (text.includes('정답')) {
                                this.playQuizCorrect();
                            } else if (text.includes('레벨업') || text.includes('레벨이')) {
                                this.playLevelUp();
                            } else if (text.includes('새로운 몬스터를 도감에 추가')) {
                                this.playMonsterCollected();
                            } else {
                                this.playSuccess();
                            }
                        } else if (node.classList.contains('alert-danger') || node.classList.contains('alert-error')) {
                            const text = node.textContent.toLowerCase();
                            if (text.includes('틀렸습니다')) {
                                this.playQuizWrong();
                            } else {
                                this.playError();
                            }
                        }
                    }
                });
            });
        });

        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
    }

    // 음량 조절
    setVolume(volume) {
        this.volume = Math.max(0, Math.min(1, volume));
        localStorage.setItem('soundVolume', this.volume.toString());
    }

    // 효과음 켜기/끄기
    toggle() {
        this.enabled = !this.enabled;
        localStorage.setItem('soundEnabled', this.enabled.toString());
        return this.enabled;
    }
}

// 전역 사운드 매니저 인스턴스
let soundManager;

// 음성 합성 함수 - 네이티브 영어 발음
function speakWord(word) {
    if ('speechSynthesis' in window) {
        // 이전 음성이 재생 중이면 중단
        speechSynthesis.cancel();
        
        const utterance = new SpeechSynthesisUtterance(word);
        
        // 영어 네이티브 발음을 위한 설정
        utterance.lang = 'en-US';
        utterance.rate = 0.8;  // 자연스러운 속도
        utterance.volume = 1.0;
        utterance.pitch = 1.0;
        
        // 미국 영어 네이티브 음성 선택 시도 (우선순위)
        const voices = speechSynthesis.getVoices();
        
        // 미국 영어 음성만 필터링 (한국어 등 제외)
        const usEnglishVoices = voices.filter(voice => 
            (voice.lang === 'en-US' || voice.lang.startsWith('en-US')) &&
            !voice.name.includes('Korean') && 
            !voice.name.includes('한국') && 
            !voice.name.includes('KR')
        );
        
        if (usEnglishVoices.length > 0) {
            // 가장 자연스러운 미국 영어 음성 우선순위로 선택
            const preferredVoice = usEnglishVoices.find(voice => 
                voice.name.includes('Google US English') ||
                voice.name.includes('Microsoft David') ||
                voice.name.includes('Microsoft Zira') ||
                voice.name.includes('Alex') ||
                voice.name.includes('Samantha') ||
                voice.name.includes('Natural') ||
                voice.name.includes('Premium')
            ) || usEnglishVoices.find(voice => 
                voice.name.includes('Google') && voice.lang === 'en-US'
            ) || usEnglishVoices[0];
            
            utterance.voice = preferredVoice;
        }
        
        // 음성 효과음 재생
        if (soundManager) {
            soundManager.createTone(600, 0.05, 'sine');
        }
        
        speechSynthesis.speak(utterance);
    } else {
        alert('음성 합성을 지원하지 않는 브라우저입니다.');
    }
}

// 퀴즈 AJAX 답변 제출
function submitQuizAnswer(event) {
    event.preventDefault();
    
    const form = document.getElementById('quiz-form');
    const formData = new FormData(form);
    const submitBtn = document.getElementById('submit-btn');
    const answerInput = document.getElementById('answer-input');
    
    // 제출 버튼 비활성화
    submitBtn.disabled = true;
    const originalText = submitBtn.innerHTML;
    submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>처리 중...';
    
    // AJAX 요청
    fetch('/take_quiz', {
        method: 'POST',
        body: formData,
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // 결과 메시지 표시 (플래시 메시지)
            const messageType = data.message_type === 'success' ? 'success' : 'danger';
            const alertDiv = document.createElement('div');
            alertDiv.className = `alert alert-${messageType} alert-dismissible fade show`;
            alertDiv.setAttribute('role', 'alert');
            alertDiv.innerHTML = `
                <i class="fas fa-${messageType === 'success' ? 'check-circle' : 'times-circle'} me-2"></i>
                ${data.message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            `;
            
            const resultDiv = document.getElementById('quiz-result');
            resultDiv.innerHTML = '';
            resultDiv.appendChild(alertDiv);
            
            // 효과음 재생
            if (soundManager) {
                if (data.correct) {
                    soundManager.playQuizCorrect();
                } else {
                    soundManager.playQuizWrong();
                }
            }
            
            // 진행률 업데이트
            const progressText = document.querySelector('.badge.bg-primary');
            if (progressText) {
                progressText.textContent = `${data.completed_words}/${data.total_words}`;
            }
            
            const progressBar = document.querySelector('.progress-bar');
            if (progressBar && data.total_words > 0) {
                const percentage = (data.completed_words / data.total_words) * 100;
                progressBar.style.width = percentage + '%';
            }
            
            // 틀린 문제 재도전 버튼 동적 업데이트
            if (data.has_wrong_questions) {
                const wrongBtnContainer = document.getElementById('wrong-btn-container');
                const wrongCount = document.getElementById('wrong-count');
                if (wrongBtnContainer) {
                    wrongBtnContainer.style.display = 'inline';
                }
                if (wrongCount) {
                    wrongCount.textContent = data.wrong_questions_count;
                }
            }
            
            // 모든 단어 완료 여부 확인
            if (data.all_completed) {
                // 모든 단어 완료 페이지로 이동
                setTimeout(() => {
                    window.location.reload();
                }, 1500);
            } else {
                // 다음 단어로 업데이트
                const nextWord = data.next_word;
                const nextQuestionType = data.next_question_type;
                
                // 단어 카드 업데이트
                const wordCard = document.querySelector('.word-card .word');
                if (wordCard) {
                    if (nextQuestionType === '뜻맞히기') {
                        wordCard.textContent = nextWord['뜻'];
                    } else {
                        wordCard.textContent = nextWord['단어'];
                    }
                }
                
                // 질문 제목 업데이트
                const questionTitle = document.querySelector('.text-center h4');
                if (questionTitle) {
                    if (nextQuestionType === '뜻맞히기') {
                        questionTitle.textContent = '단어 뜻 맞히기';
                    } else {
                        questionTitle.textContent = '단어를 보고 뜻 맞히기';
                    }
                }
                
                // form 필드 업데이트
                form.querySelector('input[name="question_type"]').value = nextQuestionType;
                form.querySelector('input[name="correct_answer"]').value = 
                    nextQuestionType === '뜻맞히기' ? nextWord['단어'] : nextWord['뜻'];
                form.querySelector('input[name="quiz_word"]').value = nextWord['단어'];
                
                // 입력 필드 초기화 및 포커스
                answerInput.value = '';
                answerInput.focus();
                
                // 발음 듣기 버튼 업데이트 (있으면)
                const speakBtn = document.querySelector('.btn-outline-info, .btn-outline-primary');
                if (speakBtn) {
                    speakBtn.onclick = function() {
                        if (nextQuestionType === '뜻맞히기') {
                            speakWord(nextWord['단어'], this);
                        } else {
                            speakWord(nextWord['단어'], this);
                        }
                    };
                }
                
                // 결과 메시지를 스크롤해서 보이게 함
                resultDiv.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }
        }
    })
    .catch(error => {
        console.error('Error:', error);
        const alertDiv = document.createElement('div');
        alertDiv.className = 'alert alert-danger alert-dismissible fade show';
        alertDiv.innerHTML = `
            <i class="fas fa-times-circle me-2"></i>
            오류가 발생했습니다: ${error.message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        document.getElementById('quiz-result').appendChild(alertDiv);
    })
    .finally(() => {
        // 제출 버튼 활성화
        submitBtn.disabled = false;
        submitBtn.innerHTML = originalText;
    });
}

// 퀴즈 카테고리 변경
function changeQuizCategory(category) {
    window.location.href = `/quiz?category=${category}`;
}

// 퀴즈 세션 리셋
function resetQuizSession(category) {
    const form = document.createElement('form');
    form.method = 'POST';
    form.action = '/reset_quiz_session';
    
    const categoryInput = document.createElement('input');
    categoryInput.type = 'hidden';
    categoryInput.name = 'selected_category';
    categoryInput.value = category;
    
    form.appendChild(categoryInput);
    document.body.appendChild(form);
    
    // 스크롤 위치 저장
    const scrollY = window.scrollY;
    sessionStorage.setItem('scrollPosition', scrollY);
    
    form.submit();
}

// 틀린 문제 재도전
function retryWrongQuestions(category) {
    if (confirm('틀린 문제들만 다시 풀어보시겠습니까?')) {
        window.location.href = '/quiz/retry_wrong?category=' + encodeURIComponent(category);
    }
}

document.addEventListener('DOMContentLoaded', function() {
    // 효과음 시스템 초기화
    soundManager = new SoundManager();

    // Feather icons 초기화
    if (typeof feather !== 'undefined') {
        feather.replace();
    }

    // 부트스트랩 툴팁 초기화
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // 부트스트랩 팝오버 초기화
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Flash 메시지는 이제 기본 Bootstrap으로 처리됩니다

    // 자동 저장 알림
    showAutoSaveStatus();

    // 숫자 애니메이션
    animateNumbers();

    // 진행 바 애니메이션
    animateProgressBars();

    // 실시간 시계 (게임 내 시간)
    updateGameClock();

    // 키보드 단축키
    setupKeyboardShortcuts();

    // 확인 대화상자
    setupConfirmDialogs();

    // 효과음 설정 UI 추가
    addSoundControlUI();
});

// 효과음 제어 UI 추가
function addSoundControlUI() {
    const controlDiv = document.createElement('div');
    controlDiv.id = 'sound-controls';
    controlDiv.className = 'position-fixed';
    controlDiv.style.cssText = `
        bottom: 20px;
        left: 20px;
        z-index: 9999;
        padding: 8px;
    `;
    // 저장된 설정 불러오기
    const savedVolume = Math.round((soundManager.volume || 0.3) * 100);
    const isEnabled = soundManager.enabled;
    
    controlDiv.innerHTML = `
        <div class="d-flex flex-column align-items-center">
            <button id="sound-toggle" class="btn btn-sm ${isEnabled ? 'btn-dark' : 'btn-danger'} mb-2" 
                    title="효과음 켜기/끄기" style="width: 40px; height: 40px; display: flex; justify-content: center; align-items: center;">
                <i id="sound-icon" class="fas ${isEnabled ? 'fa-volume-up' : 'fa-volume-mute'}" style="font-size: 16px; color: white;"></i>
            </button>
            <input type="range" id="volume-slider" class="form-range" 
                   min="0" max="100" value="${savedVolume}" 
                   style="width: 80px; height: 4px;"
                   title="음량 조절">
            <small id="volume-display" class="text-dark mt-1" style="color: black !important;">${savedVolume}%</small>
        </div>
    `;
    
    document.body.appendChild(controlDiv);
    
    // 이벤트 리스너 설정
    const toggleBtn = document.getElementById('sound-toggle');
    const volumeSlider = document.getElementById('volume-slider');
    const soundIcon = document.getElementById('sound-icon');
    const volumeDisplay = document.getElementById('volume-display');
    
    toggleBtn.addEventListener('click', () => {
        const enabled = soundManager.toggle();
        soundIcon.className = enabled ? 'fas fa-volume-up' : 'fas fa-volume-mute';
        toggleBtn.className = enabled ? 'btn btn-sm btn-dark mb-2' : 'btn btn-sm btn-danger mb-2';
        
        // 상태 알림 표시
        showSoundStatusNotification(enabled ? '효과음이 켜졌습니다' : '효과음이 꺼졌습니다', enabled);
    });
    
    volumeSlider.addEventListener('input', (e) => {
        const volume = e.target.value / 100;
        soundManager.setVolume(volume);
        volumeDisplay.textContent = `${e.target.value}%`;
        
        // 음량 변경 시 간단한 테스트 사운드
        if (soundManager.enabled) {
            soundManager.createTone(800, 0.05, 'sine');
        }
    });
}

// 효과음 상태 알림 표시

function showSoundStatusNotification(message, isEnabled) {
    // 간단한 콘솔 로그로 대체
    console.log(message);
}






// 자동 저장 상태 표시
function showAutoSaveStatus() {
    const saveIndicator = document.createElement('div');
    saveIndicator.id = 'save-indicator';
    saveIndicator.className = 'position-fixed bottom-0 end-0 m-3 alert alert-success alert-dismissible fade';
    saveIndicator.style.zIndex = '9999';
    saveIndicator.innerHTML = `
        <i data-feather="save" size="16" class="me-2"></i>
        게임이 자동 저장되었습니다
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    // 폼 제출 시 저장 알림 표시
    document.addEventListener('submit', function() {
        document.body.appendChild(saveIndicator);
        saveIndicator.classList.add('show');
        feather.replace();
        
        setTimeout(() => {
            if (saveIndicator.parentNode) {
                saveIndicator.parentNode.removeChild(saveIndicator);
            }
        }, 3000);
    });
}

// 숫자 카운트업 애니메이션
function animateNumbers() {
    const numberElements = document.querySelectorAll('.animate-number');
    
    numberElements.forEach(element => {
        const targetValue = parseInt(element.textContent.replace(/,/g, ''));
        const duration = 1500;
        const startValue = 0;
        const startTime = performance.now();
        
        function updateNumber(currentTime) {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);
            const currentValue = Math.floor(startValue + (targetValue - startValue) * easeOutCubic(progress));
            
            element.textContent = currentValue.toLocaleString();
            
            if (progress < 1) {
                requestAnimationFrame(updateNumber);
            }
        }
        
        requestAnimationFrame(updateNumber);
    });
}

// Ease out cubic 애니메이션 함수
function easeOutCubic(t) {
    return 1 - Math.pow(1 - t, 3);
}

// 진행 바 애니메이션
function animateProgressBars() {
    const progressBars = document.querySelectorAll('.progress-bar');
    
    progressBars.forEach(bar => {
        const width = bar.style.width;
        bar.style.width = '0%';
        bar.style.transition = 'width 1s ease-out';
        
        setTimeout(() => {
            bar.style.width = width;
        }, 100);
    });
}

// 게임 내 시계 업데이트
function updateGameClock() {
    const clockElement = document.querySelector('#game-clock');
    if (!clockElement) return;
    
    setInterval(() => {
        const now = new Date();
        clockElement.textContent = now.toLocaleTimeString('ko-KR');
    }, 1000);
}

// 키보드 단축키 설정
function setupKeyboardShortcuts() {
    document.addEventListener('keydown', function(e) {
        // Ctrl/Cmd + 키 조합만 처리
        if (!(e.ctrlKey || e.metaKey)) return;
        
        switch(e.key) {
            case 'h': // 홈/대시보드
                e.preventDefault();
                window.location.href = '/dashboard';
                break;
            case 'q': // 퀴즈
                e.preventDefault();
                window.location.href = '/quiz';
                break;
            case 'j': // 직업
                e.preventDefault();
                window.location.href = '/job';
                break;
            case 'r': // 부동산
                e.preventDefault();
                window.location.href = '/real_estate';
                break;
            case 's': // 상점
                e.preventDefault();
                window.location.href = '/shop';
                break;
            case 'a': // 성취
                e.preventDefault();
                window.location.href = '/achievements';
                break;
        }
    });
}

// 확인 대화상자 설정
function setupConfirmDialogs() {
    // 위험한 액션에 확인 대화상자 추가
    const dangerousActions = document.querySelectorAll('[data-confirm]');
    
    dangerousActions.forEach(element => {
        element.addEventListener('click', function(e) {
            const message = this.getAttribute('data-confirm');
            if (!confirm(message)) {
                e.preventDefault();
            }
        });
    });
}

// 스탯 차트 생성 (대시보드용)
function createStatsChart(canvasId, statsData) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;
    
    return new Chart(ctx, {
        type: 'radar',
        data: {
            labels: statsData.labels,
            datasets: [{
                label: '능력치',
                data: statsData.stats,
                borderColor: 'rgba(54, 162, 235, 1)',
                backgroundColor: 'rgba(54, 162, 235, 0.2)',
                borderWidth: 2,
                pointBackgroundColor: 'rgba(54, 162, 235, 1)',
                pointBorderColor: '#fff',
                pointHoverBackgroundColor: '#fff',
                pointHoverBorderColor: 'rgba(54, 162, 235, 1)'
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                r: {
                    beginAtZero: true,
                    max: Math.max(...statsData.stats) + 5,
                    ticks: {
                        stepSize: 5
                    },
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    },
                    angleLines: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    },
                    pointLabels: {
                        color: 'rgba(255, 255, 255, 0.8)'
                    }
                }
            },
            animation: {
                duration: 1500,
                easing: 'easeOutCubic'
            }
        }
    });
}

// 경험치 바 애니메이션
function animateExpBar(current, max) {
    const expBar = document.querySelector('.exp-progress');
    if (!expBar) return;
    
    const percentage = (current / max) * 100;
    expBar.style.width = '0%';
    expBar.style.transition = 'width 2s ease-out';
    
    setTimeout(() => {
        expBar.style.width = percentage + '%';
    }, 500);
}

// 토스트 알림 표시
function showToast(message, type = 'success') {
    const toastContainer = getOrCreateToastContainer();
    
    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-white bg-${type} border-0`;
    toast.setAttribute('role', 'alert');
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                <i data-feather="${getToastIcon(type)}" size="16" class="me-2"></i>
                ${message}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
    `;
    
    toastContainer.appendChild(toast);
    feather.replace();
    
    const bsToast = new bootstrap.Toast(toast);
    bsToast.show();
    
    // 토스트가 사라진 후 DOM에서 제거
    toast.addEventListener('hidden.bs.toast', () => {
        toast.remove();
    });
}

// 토스트 컨테이너 생성 또는 가져오기
function getOrCreateToastContainer() {
    let container = document.querySelector('.toast-container');
    if (!container) {
        container = document.createElement('div');
        container.className = 'toast-container position-fixed bottom-0 end-0 p-3';
        container.style.zIndex = '9999';
        document.body.appendChild(container);
    }
    return container;
}

// 토스트 아이콘 가져오기
function getToastIcon(type) {
    const icons = {
        'success': 'check-circle',
        'danger': 'x-circle',
        'warning': 'alert-triangle',
        'info': 'info'
    };
    return icons[type] || 'info';
}

// 로딩 스피너 표시/숨기기
function showLoading(element) {
    const spinner = document.createElement('div');
    spinner.className = 'spinner-border spinner-border-sm me-2';
    spinner.setAttribute('role', 'status');
    
    const originalText = element.innerHTML;
    element.innerHTML = '';
    element.appendChild(spinner);
    element.appendChild(document.createTextNode('처리 중...'));
    element.disabled = true;
    
    return function hideLoading() {
        element.innerHTML = originalText;
        element.disabled = false;
        feather.replace();
    };
}

// 스무스 스크롤
function smoothScrollTo(target) {
    const element = document.querySelector(target);
    if (element) {
        element.scrollIntoView({
            behavior: 'smooth',
            block: 'start'
        });
    }
}

// 폼 검증
function validateForm(formElement) {
    const inputs = formElement.querySelectorAll('input[required], select[required], textarea[required]');
    let isValid = true;
    
    inputs.forEach(input => {
        if (!input.value.trim()) {
            input.classList.add('is-invalid');
            isValid = false;
        } else {
            input.classList.remove('is-invalid');
        }
    });
    
    return isValid;
}

// 유틸리티 함수들
const Utils = {
    // 숫자 포맷팅 (한국어 천 단위 구분)
    formatNumber: function(num) {
        return num.toLocaleString('ko-KR');
    },
    
    // 퍼센트 계산
    calculatePercentage: function(value, total) {
        if (total === 0) return 0;
        return Math.round((value / total) * 100);
    },
    
    // 랜덤 메시지 선택
    getRandomMessage: function(messages) {
        return messages[Math.floor(Math.random() * messages.length)];
    },
    
    // 디바운스 함수
    debounce: function(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }
};

// 게임 상태 체크 (주기적)
setInterval(function() {
    // 기력/체력이 낮을 때 경고
    const currentPage = window.location.pathname;
    if (currentPage === '/dashboard') {
        checkPlayerStatus();
    }
}, 30000); // 30초마다 체크

function checkPlayerStatus() {
    // 이 함수는 대시보드에서 플레이어 상태를 체크하고 
    // 필요시 알림을 표시하는 용도로 사용할 수 있습니다.
    // 실제 구현은 서버 데이터가 필요하므로 여기서는 기본 구조만 제공합니다.
}

// 글로벌 변수로 Utils 및 피드백 함수들 노출
window.GameUtils = Utils;

// 페이지 로드 시 스크롤 위치 복원
function restoreScrollPosition() {
    const scrollY = sessionStorage.getItem('scrollPosition');
    if (scrollY) {
        window.scrollTo(0, parseInt(scrollY));
        sessionStorage.removeItem('scrollPosition');
    }
}

// 페이지 상단 스크롤 방지 및 상호작용 개선
document.addEventListener('DOMContentLoaded', function() {
    // 스크롤 위치 복원
    restoreScrollPosition();
    
    
    
    
});
