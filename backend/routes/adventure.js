import express from 'express';
import { authMiddleware } from '../utils/auth.js';
import { loadPlayerData, savePlayerData } from '../utils/fileStorage.js';

const router = express.Router();

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

    // 전투 상태 생성
    const battleState = {
      stage_id: stage_id,
      player_hp: 100,
      player_mp: 50,
      enemy_hp: 50 + stage_id * 5,
      player_turn: true,
      player_skills: playerData.모험_기술 || ['박치기'],
      enemy_skills: ['기본공격'],
      skill_usage_count: {}
    };

    savePlayerData(playerId, playerData);

    res.json({
      success: true,
      data: {
        battle_state: battleState,
        battle_id: `battle_${Date.now()}`
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
 * 모험 액션
 */
router.post('/action', authMiddleware, (req, res) => {
  try {
    const { action_type, skill_name } = req.body;

    if (!action_type) {
      return res.status(400).json({
        success: false,
        error: '액션 타입이 필요합니다.'
      });
    }

    const battleState = {
      player_hp: 90,
      enemy_hp: 40,
      player_turn: false,
      game_over: false
    };

    res.json({
      success: true,
      data: {
        battle_state: battleState,
        game_over: false,
        skill_usage: { 박치기: 1 }
      }
    });
  } catch (error) {
    console.error('Error executing adventure action:', error);
    res.status(500).json({
      success: false,
      error: '서버 오류가 발생했습니다.'
    });
  }
});

export default router;
