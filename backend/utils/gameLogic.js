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
 * 잠자기 (시간 진행, 기력 회복, 월세 수입)
 */
export function sleep(playerData) {
  // 시간 진행
  playerData.시간 = (playerData.시간 || 8) + 8;
  let rentMessages = [];
  
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
  }

  // 기력 회복
  const maxEnergy = playerData.최대기력 || 10;
  playerData.기력 = Math.min((playerData.기력 || 5) + 5, maxEnergy);

  // 메시지 생성
  let baseMessage = `잠을 자서 기력이 ${playerData.기력}까지 회복되었습니다.`;
  if (rentMessages.length > 0) {
    baseMessage += ` ${rentMessages.join(', ')}`;
  }

  return {
    success: true,
    message: baseMessage,
    current_time: `${playerData.날짜}일 ${playerData.시간}시`,
    current_energy: playerData.기력,
    rent_income: rentMessages.length > 0 ? rentMessages : null,
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
