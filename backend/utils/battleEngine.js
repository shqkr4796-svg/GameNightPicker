import { loadGameData } from './fileStorage.js';

// 전투 상태 메모리 (프로토타입용)
const battleSessions = {};

/**
 * 데미지 계산
 */
export function calculateDamage(attacker, skill) {
  const baseAttack = attacker.공격력 || 10;
  const multiplier = skill.공격력_보정_min + 
    Math.random() * (skill.공격력_보정_max - skill.공격력_보정_min);
  const damage = Math.floor(baseAttack * multiplier);
  return Math.max(1, damage);
}

/**
 * 전투 시작
 */
export function startBattle(playerId, stageId, playerData) {
  const battleId = `battle_${playerId}_${Date.now()}`;
  const stageDifficulty = playerData.모험_심화 ? '심화' : '일반';
  
  let enemyHp = 50 + stageId * 5;
  let enemyAttack = 5 + Math.floor(stageId / 10);
  
  // 심화 난이도는 2배
  if (stageDifficulty === '심화') {
    enemyHp *= 2;
    enemyAttack *= 2;
  }
  
  battleSessions[battleId] = {
    playerId,
    stageId,
    stageDifficulty,
    playerHp: playerData.체력 || 100,
    playerMaxHp: playerData.최대체력 || 100,
    playerAttack: playerData.공격력 || 10,
    playerSkills: playerData.모험_기술 || ['박치기'],
    skillUsageCount: playerData.기술_사용횟수 || {},
    
    enemyHp,
    enemyMaxHp: enemyHp,
    enemyAttack,
    
    playerTurn: true,
    turnCount: 0,
    battleLog: [],
    skillCardDropped: false,
    skillCardName: null
  };
  
  return battleId;
}

/**
 * 스킬 사용 (플레이어 턴)
 */
export function useSkill(battleId, skillName) {
  const battle = battleSessions[battleId];
  if (!battle) return { success: false, error: '존재하지 않는 전투입니다.' };
  
  const skills = loadGameData('skills');
  const skill = skills.find(s => s.이름 === skillName);
  
  if (!skill) {
    return { success: false, error: '존재하지 않는 스킬입니다.' };
  }
  
  // 데미지 계산 및 적 체력 감소
  const damage = calculateDamage({ 공격력: battle.playerAttack }, skill);
  battle.enemyHp -= damage;
  battle.turnCount++;
  battle.battleLog.push(`플레이어가 ${skillName}를 사용했습니다. 데미지: ${damage}`);
  
  // 적이 패배했는지 확인
  if (battle.enemyHp <= 0) {
    return completeAdventure(battleId, true);
  }
  
  // 적의 턴
  return executeEnemyTurn(battleId);
}

/**
 * 적의 턴 (기본 공격)
 */
function executeEnemyTurn(battleId) {
  const battle = battleSessions[battleId];
  
  // 적이 기본 공격
  const damage = Math.floor(battle.enemyAttack * (0.9 + Math.random() * 0.2));
  battle.playerHp -= damage;
  battle.battleLog.push(`적이 기본 공격했습니다. 데미지: ${damage}`);
  
  // 플레이어가 패배했는지 확인
  if (battle.playerHp <= 0) {
    return completeAdventure(battleId, false);
  }
  
  return {
    success: true,
    battleState: getBattleState(battleId),
    playerTurn: true,
    gameOver: false
  };
}

/**
 * 전투 완료 (승리/패배)
 */
function completeAdventure(battleId, isVictory) {
  const battle = battleSessions[battleId];
  
  if (isVictory) {
    // 승리 시 보상 계산
    const baseExp = 50 + battle.stageId * 5;
    const baseMoney = 100 + battle.stageId * 10;
    
    // 심화 난이도는 1.5배 보상
    const expMultiplier = battle.stageDifficulty === '심화' ? 1.5 : 1;
    const exp = Math.floor(baseExp * expMultiplier);
    const money = Math.floor(baseMoney * expMultiplier);
    
    // 기술 카드 드롭 확률
    const dropRate = battle.stageId === 1 ? 0.0002 : Math.min(0.01, 0.0002 * (battle.stageId ** 1.5));
    const finalDropRate = battle.stageDifficulty === '심화' ? dropRate * 2 : dropRate;
    const skillDropped = Math.random() < finalDropRate;
    
    let skillCard = null;
    if (skillDropped) {
      const allSkills = loadGameData('skills');
      skillCard = allSkills[Math.floor(Math.random() * allSkills.length)];
      battle.skillCardDropped = true;
      battle.skillCardName = skillCard.이름;
    }
    
    delete battleSessions[battleId];
    
    return {
      success: true,
      victory: true,
      rewards: { exp, money, skillCard },
      stageId: battle.stageId,
      stageDifficulty: battle.stageDifficulty
    };
  } else {
    // 패배 시 기본 보상만 (절반)
    const exp = Math.floor((50 + battle.stageId * 5) * 0.3);
    const money = Math.floor((100 + battle.stageId * 10) * 0.3);
    
    delete battleSessions[battleId];
    
    return {
      success: true,
      victory: false,
      rewards: { exp, money },
      stageId: battle.stageId,
      stageDifficulty: battle.stageDifficulty
    };
  }
}

/**
 * 현재 전투 상태 조회
 */
export function getBattleState(battleId) {
  const battle = battleSessions[battleId];
  if (!battle) return null;
  
  return {
    battleId,
    playerHp: battle.playerHp,
    playerMaxHp: battle.playerMaxHp,
    playerAttack: battle.playerAttack,
    playerSkills: battle.playerSkills,
    
    enemyHp: battle.enemyHp,
    enemyMaxHp: battle.enemyMaxHp,
    enemyAttack: battle.enemyAttack,
    
    turnCount: battle.turnCount,
    battleLog: battle.battleLog.slice(-3), // 최근 3개 로그
    playerTurn: battle.playerTurn
  };
}

/**
 * 전투 포기
 */
export function fleeBattle(battleId) {
  if (battleSessions[battleId]) {
    delete battleSessions[battleId];
  }
  return { success: true, message: '전투에서 도망쳤습니다.' };
}

export default {
  startBattle,
  useSkill,
  getBattleState,
  fleeBattle
};
