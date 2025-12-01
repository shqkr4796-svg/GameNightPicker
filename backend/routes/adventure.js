import express from 'express';
import { authMiddleware } from '../utils/auth.js';
import { loadPlayerData, savePlayerData, loadGameData } from '../utils/fileStorage.js';
import { startBattle, useSkill, getBattleState, fleeBattle } from '../utils/battleEngine.js';

const router = express.Router();

// 플레이어 전투 세션 추적
const playerBattles = {};

/**
 * GET /api/adventure/select
 * 모험 선택 페이지
 */
router.get('/select', authMiddleware, (req, res) => {
  try {
    const playerId = req.playerId;
    const loadResult = loadPlayerData(playerId);

    if (!loadResult.success) {
      return res.status(404).json({
        success: false,
        error: '플레이어 데이터를 찾을 수 없습니다.'
      });
    }

    const playerData = loadResult.data;

    // 기본 스테이지 데이터
    const stages = Array.from({ length: 200 }, (_, i) => ({
      stage_id: i + 1,
      name: `Stage ${i + 1}`,
      difficulty: '일반',
      enemy_level: Math.floor((i + 1) / 10) + 1,
      reward: { exp: 50 + i * 5, money: 100 + i * 10 }
    }));

    res.json({
      success: true,
      data: {
        available_monsters: playerData.도감 || [],
        stages: stages,
        current_stage: playerData.모험_현재스테이지 || 1,
        cleared_stage: playerData.모험_클리어스테이지 || 0,
        adventure_energy: playerData.모험_기력 || 100
      }
    });
  } catch (error) {
    console.error('Error fetching adventure select:', error);
    res.status(500).json({
      success: false,
      error: '서버 오류가 발생했습니다.'
    });
  }
});

/**
 * POST /api/adventure/start
 * 모험 시작
 */
router.post('/start', authMiddleware, (req, res) => {
  try {
    const playerId = req.playerId;
    const { stage_id, monster_ids } = req.body;

    if (!stage_id || !monster_ids || monster_ids.length === 0) {
      return res.status(400).json({
        success: false,
        error: '스테이지와 몬스터를 선택해주세요.'
      });
    }

    if (monster_ids.length > 3) {
      return res.status(400).json({
        success: false,
        error: '최대 3마리까지만 선택 가능합니다.'
      });
    }

    const loadResult = loadPlayerData(playerId);
    if (!loadResult.success) {
      return res.status(404).json({
        success: false,
        error: '플레이어 데이터를 찾을 수 없습니다.'
      });
    }

    const playerData = loadResult.data;

    // 기력 확인
    if ((playerData.모험_기력 || 100) <= 0) {
      return res.status(400).json({
        success: false,
        error: '모험 기력이 부족합니다.'
      });
    }

    // 기력 소모
    playerData.모험_기력 -= 1;

    // 전투 시작
    const battleId = startBattle(playerId, stage_id, playerData);
    const battleState = getBattleState(battleId);

    savePlayerData(playerId, playerData);

    res.json({
      success: true,
      data: {
        battle_id: battleId,
        battle_state: battleState,
        message: '전투가 시작되었습니다!'
      }
    });
  } catch (error) {
    console.error('Error starting adventure:', error);
    res.status(500).json({
      success: false,
      error: '서버 오류가 발생했습니다.'
    });
  }
});

/**
 * POST /api/adventure/action
 * 모험 액션 (스킬 사용)
 */
router.post('/action', authMiddleware, (req, res) => {
  try {
    const playerId = req.playerId;
    const { battle_id, skill_name } = req.body;

    if (!battle_id || !skill_name) {
      return res.status(400).json({
        success: false,
        error: 'battle_id와 skill_name이 필요합니다.'
      });
    }

    // 스킬 사용 처리
    const result = useSkill(battle_id, skill_name);

    if (!result.success) {
      return res.status(400).json({
        success: false,
        error: result.error || '스킬 사용 실패'
      });
    }

    // 전투 종료 여부 확인
    if (result.victory !== undefined) {
      // 전투 완료
      const loadResult = loadPlayerData(playerId);
      if (loadResult.success) {
        const playerData = loadResult.data;
        
        // 보상 처리
        playerData.경험치 = (playerData.경험치 || 0) + result.rewards.exp;
        playerData.돈 = (playerData.돈 || 0) + result.rewards.money;
        
        // 스테이지 진행도 업데이트
        if (result.victory) {
          playerData.모험_클리어스테이지 = Math.max(
            playerData.모험_클리어스테이지 || 0,
            result.stageId
          );
          
          // 스킬 카드 획득
          if (result.rewards.skillCard) {
            const acquiredSkills = playerData.모험_획득스킬 || [];
            acquiredSkills.push(result.rewards.skillCard);
            playerData.모험_획득스킬 = acquiredSkills;
          }
        }
        
        savePlayerData(playerId, playerData);
      }

      res.json({
        success: true,
        data: {
          gameOver: true,
          victory: result.victory,
          rewards: result.rewards
        }
      });
    } else {
      // 전투 진행 중
      res.json({
        success: true,
        data: {
          gameOver: false,
          battleState: result.battleState,
          playerTurn: result.playerTurn
        }
      });
    }
  } catch (error) {
    console.error('Error executing adventure action:', error);
    res.status(500).json({
      success: false,
      error: '서버 오류가 발생했습니다.'
    });
  }
});

/**
 * POST /api/adventure/flee
 * 전투에서 도망치기
 */
router.post('/flee', authMiddleware, (req, res) => {
  try {
    const { battle_id } = req.body;

    if (!battle_id) {
      return res.status(400).json({
        success: false,
        error: 'battle_id가 필요합니다.'
      });
    }

    const result = fleeBattle(battle_id);

    res.json({
      success: true,
      data: result
    });
  } catch (error) {
    console.error('Error fleeing battle:', error);
    res.status(500).json({
      success: false,
      error: '서버 오류가 발생했습니다.'
    });
  }
});

export default router;
