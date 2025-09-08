// 라이프 시뮬레이션 게임 - 메인 JavaScript 파일

document.addEventListener('DOMContentLoaded', function() {
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
});

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

// 글로벌 변수로 Utils 노출
window.GameUtils = Utils;
