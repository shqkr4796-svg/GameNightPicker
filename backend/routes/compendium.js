import express from 'express';
import { authMiddleware } from '../utils/auth.js';
import { loadPlayerData, savePlayerData, loadGameData } from '../utils/fileStorage.js';

const router = express.Router();

/**
 * GET /api/compendium
 * 플레이어의 몬스터 도감 조회
 */
router.get('/', authMiddleware, (req, res) => {
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
    const compendium = playerData.도감 || [];
    
    // 도감 통계
    const stats = {
      total_captured: compendium.length,
      by_rarity: {
        '레어': compendium.filter(m => m.등급 === '레어').length,
        '에픽': compendium.filter(m => m.등급 === '에픽').length,
        '유니크': compendium.filter(m => m.등급 === '유니크').length,
        '레전드리': compendium.filter(m => m.등급 === '레전드리').length
      }
    };

    res.json({
      success: true,
      data: {
        compendium: compendium,
        stats: stats
      }
    });
  } catch (error) {
    console.error('Error fetching compendium:', error);
    res.status(500).json({
      success: false,
      error: '서버 오류가 발생했습니다.'
    });
  }
});

/**
 * GET /api/compendium/:monster_id
 * 특정 몬스터 도감 상세 조회
 */
router.get('/:monster_id', authMiddleware, (req, res) => {
  try {
    const playerId = req.playerId;
    const monsterId = req.params.monster_id;
    
    const loadResult = loadPlayerData(playerId);
    if (!loadResult.success) {
      return res.status(404).json({
        success: false,
        error: '플레이어 데이터를 찾을 수 없습니다.'
      });
    }

    const playerData = loadResult.data;
    const compendium = playerData.도감 || [];
    
    // 도감에서 해당 몬스터 찾기
    const monsterEntry = compendium.find(m => m.id === monsterId);

    if (!monsterEntry) {
      return res.status(404).json({
        success: false,
        error: '도감에 없는 몬스터입니다.'
      });
    }

    // 게임 데이터에서 기본 정보 로드
    const allMonsters = loadGameData('monsters');
    const baseMonster = allMonsters[monsterId] || {};

    res.json({
      success: true,
      data: {
        monster: {
          ...baseMonster,
          ...monsterEntry,
          captured_at: monsterEntry.captured_at,
          times_encountered: monsterEntry.times_encountered || 1,
          times_defeated: monsterEntry.times_defeated || 1
        }
      }
    });
  } catch (error) {
    console.error('Error fetching monster details:', error);
    res.status(500).json({
      success: false,
      error: '서버 오류가 발생했습니다.'
    });
  }
});

/**
 * POST /api/compendium/capture
 * 몬스터 포획
 */
router.post('/capture', authMiddleware, (req, res) => {
  try {
    const playerId = req.playerId;
    const { monster_id, monster_data } = req.body;

    if (!monster_id || !monster_data) {
      return res.status(400).json({
        success: false,
        error: '몬스터 ID와 데이터가 필요합니다.'
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
    const compendium = playerData.도감 || [];

    // 이미 포획한 몬스터인지 확인
    const existingMonster = compendium.find(m => m.id === monster_id);

    if (existingMonster) {
      // 이미 포획한 몬스터: 카운트 증가
      existingMonster.times_encountered = (existingMonster.times_encountered || 1) + 1;
    } else {
      // 새로 포획한 몬스터: 추가
      compendium.push({
        id: monster_id,
        ...monster_data,
        captured_at: new Date().toISOString(),
        times_encountered: 1,
        times_defeated: 1
      });
    }

    playerData.도감 = compendium;
    savePlayerData(playerId, playerData);

    res.json({
      success: true,
      data: {
        message: '몬스터가 포획되었습니다!',
        compendium_count: compendium.length,
        is_new: !existingMonster
      }
    });
  } catch (error) {
    console.error('Error capturing monster:', error);
    res.status(500).json({
      success: false,
      error: '서버 오류가 발생했습니다.'
    });
  }
});

export default router;
