import express from 'express';
import { generateToken, authMiddleware } from '../utils/auth.js';
import { savePlayerData, loadPlayerData } from '../utils/fileStorage.js';
import { createNewPlayer, checkLevelUp, allocateStatPoints, sleep } from '../utils/gameLogic.js';

const router = express.Router();

/**
 * POST /api/player/start
 * 새 게임 시작
 */
router.post('/start', (req, res) => {
  try {
    const playerData = createNewPlayer();
    const token = generateToken(playerData);
    
    // 플레이어 데이터 저장
    const saveResult = savePlayerData(playerData.id, playerData);
    
    if (!saveResult.success) {
      return res.status(500).json({
        success: false,
        error: '게임을 시작할 수 없습니다.'
      });
    }

    res.json({
      success: true,
      data: {
        player: playerData,
        token: token
      },
      message: '새로운 인생이 시작되었습니다!'
    });
  } catch (error) {
    console.error('Error starting game:', error);
    res.status(500).json({
      success: false,
      error: '서버 오류가 발생했습니다.'
    });
  }
});

/**
 * POST /api/player/load
 * 저장된 게임 로드
 */
router.post('/load', (req, res) => {
  try {
    const playerId = req.body.playerId || 'default';
    const loadResult = loadPlayerData(playerId);

    if (!loadResult.success) {
      return res.status(404).json({
        success: false,
        error: '저장된 게임이 없습니다.'
      });
    }

    const playerData = loadResult.data;
    const token = generateToken(playerData);

    res.json({
      success: true,
      data: {
        player: playerData,
        token: token
      },
      message: '게임을 불러왔습니다.'
    });
  } catch (error) {
    console.error('Error loading game:', error);
    res.status(500).json({
      success: false,
      error: '서버 오류가 발생했습니다.'
    });
  }
});

/**
 * POST /api/player/save
 * 게임 저장 (인증 필요)
 */
router.post('/save', authMiddleware, (req, res) => {
  try {
    const playerData = req.body.player_data;

    if (!playerData || !playerData.id) {
      return res.status(400).json({
        success: false,
        error: '플레이어 데이터가 없습니다.'
      });
    }

    const saveResult = savePlayerData(playerData.id, playerData);

    if (!saveResult.success) {
      return res.status(500).json({
        success: false,
        error: saveResult.error
      });
    }

    res.json({
      success: true,
      message: '게임이 저장되었습니다.'
    });
  } catch (error) {
    console.error('Error saving game:', error);
    res.status(500).json({
      success: false,
      error: '서버 오류가 발생했습니다.'
    });
  }
});

/**
 * GET /api/player/info
 * 플레이어 정보 조회 (인증 필요)
 */
router.get('/info', authMiddleware, (req, res) => {
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

    res.json({
      success: true,
      data: {
        레벨: playerData.레벨,
        경험치: playerData.경험치,
        돈: playerData.돈,
        힘: playerData.힘,
        지능: playerData.지능,
        외모: playerData.외모,
        체력스탯: playerData.체력스탯,
        운: playerData.운,
        체력: playerData.체력,
        기력: playerData.기력,
        최대기력: playerData.최대기력,
        직장: playerData.직장,
        거주지: playerData.거주지,
        날짜: playerData.날짜,
        시간: playerData.시간
      }
    });
  } catch (error) {
    console.error('Error fetching player info:', error);
    res.status(500).json({
      success: false,
      error: '서버 오류가 발생했습니다.'
    });
  }
});

/**
 * POST /api/player/sleep
 * 잠자기 (인증 필요)
 */
router.post('/sleep', authMiddleware, (req, res) => {
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
    const sleepResult = sleep(playerData);

    // 저장
    savePlayerData(playerId, playerData);

    res.json({
      success: true,
      data: {
        player: playerData,
        ...sleepResult
      }
    });
  } catch (error) {
    console.error('Error sleeping:', error);
    res.status(500).json({
      success: false,
      error: '서버 오류가 발생했습니다.'
    });
  }
});

/**
 * POST /api/player/allocate-stats
 * 스탯 분배 (인증 필요)
 */
router.post('/allocate-stats', authMiddleware, (req, res) => {
  try {
    const playerId = req.playerId;
    const { stat_type, points } = req.body;

    if (!stat_type || !points) {
      return res.status(400).json({
        success: false,
        error: '스탯 타입과 포인트가 필요합니다.'
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
    const allocateResult = allocateStatPoints(playerData, stat_type, points);

    if (!allocateResult.success) {
      return res.status(400).json({
        success: false,
        error: allocateResult.message
      });
    }

    // 저장
    savePlayerData(playerId, playerData);

    res.json({
      success: true,
      data: {
        player: playerData,
        ...allocateResult
      }
    });
  } catch (error) {
    console.error('Error allocating stats:', error);
    res.status(500).json({
      success: false,
      error: '서버 오류가 발생했습니다.'
    });
  }
});

export default router;
