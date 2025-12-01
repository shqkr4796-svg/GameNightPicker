/**
 * 게임 로직 유틸리티
 * Flask의 game_logic.py에서 필요한 함수들을 JavaScript로 포팅
 */

/**
 * 새 플레이어 생성
 */
export function createNewPlayer() {
  return {
    id: Date.now().toString(),
    레벨: 1,
    경험치: 0,
    경험치최대: 100,
    스탯포인트: 0,
    힘: 0,
    지능: 0,
    외모: 0,
    체력스탯: 0,
    운: 0,
    체력: 10,
    기력: 10,
    최대기력: 10,
    직장: null,
    직장정보: null,
    돈: 0,
    거주지: null,
    날짜: 1,
    시간: 8,
    질병: null,
    인벤토리: [],
    성취: [],
    총_퀴즈: 0,
    정답_퀴즈: 0,
    도감: [],
    던전클리어횟수: 0,
    무기_인벤토리: {},
    장착된_무기: null,
    던전_인벤토리: {},
    일일표현_완료: false,
    일일표현_마지막날짜: 0,
    일일표현_진도: 0,
    학습한_표현_인덱스: [],
    모험_현재스테이지: 1,
    모험_클리어스테이지: 0,
    모험_기술: ['박치기'],
    모험_대표몬스터: null,
    모험_아이템: {},
    모험_기력: 100,
    모험_기력최대: 100,
    모험_정답_퀴즈: 0,
    모험_난이도: '일반'
  };
}

/**
 * 경험치로부터 레벨 계산
 */
export function calculateLevelFromExp(totalExp) {
  let level = 1;
  let expThreshold = 100;
  let currentExp = totalExp;

  while (currentExp >= expThreshold) {
    currentExp -= expThreshold;
    level++;
    expThreshold = Math.floor(100 * Math.pow(level, 1.1));
  }

  return { level, currentExp, nextThreshold: expThreshold };
}

/**
 * 레벨업 체크
 */
export function checkLevelUp(playerData) {
  const currentLevel = playerData.레벨 || 1;
  const { level, currentExp, nextThreshold } = calculateLevelFromExp(playerData.경험치);

  if (level > currentLevel) {
    playerData.레벨 = level;
    playerData.스탯포인트 = (playerData.스탯포인트 || 0) + (level - currentLevel) * 5;
    return level - currentLevel;
  }

  return 0;
}

/**
 * 스탯 분배
 */
export function allocateStatPoints(playerData, statType, points) {
  const validStats = ['힘', '지능', '외모', '체력스탯', '운'];

  if (!validStats.includes(statType)) {
    return { success: false, message: '유효하지 않은 스탯입니다.' };
  }

  const availablePoints = playerData.스탯포인트 || 0;
  if (availablePoints < points) {
    return { success: false, message: '스탯 포인트가 부족합니다.' };
  }

  playerData[statType] = (playerData[statType] || 0) + points;
  playerData.스탯포인트 = availablePoints - points;

  return { 
    success: true, 
    message: `${statType}에 ${points}포인트를 분배했습니다.`,
    updated_stat: playerData[statType],
    remaining_points: playerData.스탯포인트
  };
}

/**
 * 부동산 월세 데이터
 */
const REAL_ESTATE_RENT_DATA = {
  '작은 아파트': 1000,
  '중형 주택': 5000,
  '대형 빌라': 20000,
  '상업용 건물': 15000
};

/**
 * 랜덤 이벤트 데이터
 */
const RANDOM_EVENTS = [
  // 긍정적 금전 이벤트
  { name: '복권 당첨', message: '복권에 당첨되었습니다!', effects: { 돈: 10000 } },
  { name: '길에서 돈 발견', message: '길을 걷다가 돈을 주웠습니다.', effects: { 돈: 1000 } },
  { name: '보너스 지급', message: '갑작스럽게 보너스가 지급되었습니다!', effects: { 돈: 5000 } },
  { name: '친척 선물', message: '친척에게서 생일 선물로 돈을 받았습니다.', effects: { 돈: 3000 } },
  
  // 부정적 금전 이벤트
  { name: '지갑 잃어버림', message: '지갑을 잃어버렸습니다.', effects: { 돈: -3000 } },
  { name: '휴대폰 깨짐', message: '휴대폰을 떨어뜨려 화면이 깨졌습니다.', effects: { 돈: -2000 } },
  { name: '사기당함', message: '누군가에게 돈을 사기당했습니다.', effects: { 돈: -4000 } },
  
  // 건강 관련 이벤트
  { name: '감기 걸림', message: '감기에 걸렸습니다.', effects: { 체력: -2, 기력: -1 } },
  { name: '건강검진 좋은 결과', message: '건강검진에서 모든 수치가 정상입니다!', effects: { 체력: 3 } },
  { name: '영양제 효과', message: '꾸준히 섭취한 영양제의 효과가 나타났습니다.', effects: { 체력: 2 } },
  
  // 기력 관련 이벤트
  { name: '친구와의 만남', message: '오랜 친구를 만나 즐거운 시간을 보냈습니다.', effects: { 기력: 2 } },
  { name: '좋은 소식', message: '좋은 소식을 들어 기분이 좋아졌습니다.', effects: { 기력: 1 } },
  { name: '영화 감상', message: '재미있는 영화를 봐서 기분이 좋아졌습니다.', effects: { 기력: 3 } },
  { name: '스트레스 폭발', message: '스트레스가 극에 달해 모든 것이 짜증납니다.', effects: { 기력: -3 } },
  
  // 스탯 증가 이벤트
  { name: '운동 효과', message: '꾸준한 운동의 효과가 나타났습니다.', effects: { 힘: 1, 체력스탯: 1 } },
  { name: '독서의 즐거움', message: '좋은 책을 읽어 지식이 늘었습니다.', effects: { 지능: 1 } },
  { name: '패션 감각 up', message: '패션 감각이 늘었습니다.', effects: { 외모: 1 } },
  { name: '명상 연습', message: '명상으로 마음이 편안해졌습니다.', effects: { 지능: 1, 기력: 2 } }
];

/**
 * 랜덤 이벤트 발생 확인 (1% 확률)
 */
function checkRandomEvent(playerData) {
  if (Math.random() > 0.01) {
    return null; // 1% 확률에 미달
  }

  const event = RANDOM_EVENTS[Math.floor(Math.random() * RANDOM_EVENTS.length)];
  
  // 이벤트 효과 적용
  if (event.effects) {
    for (const [stat, value] of Object.entries(event.effects)) {
      if (stat in playerData && typeof playerData[stat] === 'number') {
        playerData[stat] = Math.max(0, (playerData[stat] || 0) + value);
      }
    }
  }

  return event;
}

/**
 * 잠자기 (시간 진행, 기력 회복, 월세 수입, 랜덤 이벤트)
 */
export function sleep(playerData) {
  // 시간 진행
  playerData.시간 = (playerData.시간 || 8) + 8;
  let rentMessages = [];
  let eventInfo = null;
  
  if (playerData.시간 >= 24) {
    playerData.시간 -= 24;
    playerData.날짜 = (playerData.날짜 || 1) + 1;
    
    // 월세 수입 처리
    if (playerData.부동산 && playerData.부동산.length > 0) {
      for (let i = 0; i < playerData.부동산.length; i++) {
        const prop = playerData.부동산[i];
        const lastRentDate = prop.last_rent_date || prop.buy_date || playerData.날짜 - 31;
        const daysSinceLastRent = playerData.날짜 - lastRentDate;
        
        // 30일마다 월세 지급
        if (daysSinceLastRent >= 30) {
          const propName = prop.name || prop.이름;
          const rentAmount = REAL_ESTATE_RENT_DATA[propName] || 5000;
          const rentCycles = Math.floor(daysSinceLastRent / 30);
          
          // 월세 적립
          playerData.돈 = (playerData.돈 || 0) + (rentAmount * rentCycles);
          playerData.부동산[i].last_rent_date = playerData.날짜;
          
          // 월세 메시지
          if (rentCycles > 1) {
            rentMessages.push(`${propName} 월세 ${rentAmount.toLocaleString()}원 (${rentCycles}개월분)`);
          } else {
            rentMessages.push(`${propName} 월세 ${rentAmount.toLocaleString()}원`);
          }
        }
      }
    }
    
    // 랜덤 이벤트 확인
    eventInfo = checkRandomEvent(playerData);
  }

  // 기력 회복
  const maxEnergy = playerData.최대기력 || 10;
  playerData.기력 = Math.min((playerData.기력 || 5) + 5, maxEnergy);

  // 메시지 생성
  let baseMessage = `잠을 자서 기력이 ${playerData.기력}까지 회복되었습니다.`;
  if (rentMessages.length > 0) {
    baseMessage += ` ${rentMessages.join(', ')}`;
  }
  if (eventInfo) {
    baseMessage += ` 이벤트: ${eventInfo.message}`;
  }

  return {
    success: true,
    message: baseMessage,
    current_time: `${playerData.날짜}일 ${playerData.시간}시`,
    current_energy: playerData.기력,
    rent_income: rentMessages.length > 0 ? rentMessages : null,
    event: eventInfo ? { name: eventInfo.name, message: eventInfo.message, effects: eventInfo.effects } : null,
    total_money: playerData.돈
  };
}

/**
 * 몬스터 레어도 확률
 */
export const MONSTER_RARITY_RATES = {
  '레어': { min: 1, max: 10, capture_rate: 0.50, spawn_rate: 0.70 },
  '에픽': { min: 11, max: 20, capture_rate: 0.10, spawn_rate: 0.20 },
  '유니크': { min: 21, max: 30, capture_rate: 0.05, spawn_rate: 0.08 },
  '레전드리': { min: 31, max: 42, capture_rate: 0.01, spawn_rate: 0.02 },
  '신화급': { min: 43, max: 53, capture_rate: 0.001, spawn_rate: 0.001 }
};

/**
 * 랜덤 몬스터 생성 (레어도별)
 */
export function generateRandomMonster(allMonsters) {
  const rarity = getRandomRarityByRate();
  const rarityData = MONSTER_RARITY_RATES[rarity];
  
  const monstersInRarity = allMonsters.filter(m => 
    m.레어도_범위 && 
    m.레어도_범위.min >= rarityData.min && 
    m.레어도_범위.max <= rarityData.max
  );

  if (monstersInRarity.length === 0) {
    return null;
  }

  return monstersInRarity[Math.floor(Math.random() * monstersInRarity.length)];
}

/**
 * 레어도별 확률로 선택
 */
export function getRandomRarityByRate() {
  const rand = Math.random();
  let cumulative = 0;

  const rarities = [
    { name: '레어', rate: 0.70 },
    { name: '에픽', rate: 0.20 },
    { name: '유니크', rate: 0.08 },
    { name: '레전드리', rate: 0.015 },
    { name: '신화급', rate: 0.005 }
  ];

  for (const rarity of rarities) {
    cumulative += rarity.rate;
    if (rand <= cumulative) {
      return rarity.name;
    }
  }

  return '레어';
}

export default {
  createNewPlayer,
  calculateLevelFromExp,
  checkLevelUp,
  allocateStatPoints,
  sleep,
  generateRandomMonster,
  getRandomRarityByRate,
  MONSTER_RARITY_RATES
};
