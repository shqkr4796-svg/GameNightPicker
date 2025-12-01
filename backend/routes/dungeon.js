import express from 'express';
import { authMiddleware } from '../utils/auth.js';
import { loadPlayerData, savePlayerData, loadGameData } from '../utils/fileStorage.js';

const router = express.Router();

/**
 * GET /api/dungeon/list
 * 던전 목록 조회
 */
router.get('/list', authMiddleware, (req, res) => {
  try {
    // 던전 데이터 로드 (JSON에서)
    const dungeons = loadGameData('dungeons');

    res.json({
      success: true,
      data: {
        dungeons: dungeons.map(d => ({
          id: d.id,
          이름: d.이름,
          난이도: d.난이도,
          word_count: d.word_count || 30,
          reward_info: `${d.min_reward || 1000}~${d.max_reward || 2000}원 + 경험치`
        }))
      }
    });
  } catch (error) {
    console.error('Error fetching dungeons:', error);
    res.status(500).json({
      success: false,
      error: '서버 오류가 발생했습니다.'
    });
  }
});

/**
 * GET /api/dungeon/:dungeon_id/preview
 * 던전 미리보기
 */
router.get('/:dungeon_id/preview', authMiddleware, (req, res) => {
  try {
    const dungeonId = req.params.dungeon_id;
    const dungeons = loadGameData('dungeons');
    const dungeon = dungeons.find(d => d.id === dungeonId);

    if (!dungeon) {
      return res.status(404).json({
        success: false,
        error: '존재하지 않는 던전입니다.'
      });
    }

    // 던전의 단어 데이터 로드
    const words = loadGameData(`dungeon_words_${dungeonId}`);

    res.json({
      success: true,
      data: {
        dungeon: dungeon,
        all_words: words,
        total_words: words.length
      }
    });
  } catch (error) {
    console.error('Error fetching dungeon preview:', error);
    res.status(500).json({
      success: false,
      error: '서버 오류가 발생했습니다.'
    });
  }
});

/**
 * POST /api/dungeon/start
 * 던전 시작
 */
router.post('/start', authMiddleware, (req, res) => {
  try {
    const playerId = req.playerId;
    const { dungeon_id } = req.body;

    if (!dungeon_id) {
      return res.status(400).json({
        success: false,
        error: '던전 ID가 필요합니다.'
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
    if ((playerData.기력 || 10) < 1) {
      return res.status(400).json({
        success: false,
        error: '던전에 입장하려면 최소 기력 1이 필요합니다.'
      });
    }

    // 기력 소모
    playerData.기력 -= 1;

    // 던전 실행 상태 생성
    const dungeonRun = {
      dungeon_id: dungeon_id,
      current_monster: {
        id: 'slime_1',
        이름: 'Slime',
        등급: '레어',
        체력: 5,
        공격력: 2
      },
      monster_progress: 0,
      monster_hp: 5,
      cleared_words: 0,
      current_word_index: 0,
      wrong_questions: []
    };

    // 플레이어 데이터 저장
    savePlayerData(playerId, playerData);

    res.json({
      success: true,
      data: {
        dungeon_run: dungeonRun,
        message: '던전에 입장했습니다!'
      }
    });
  } catch (error) {
    console.error('Error starting dungeon:', error);
    res.status(500).json({
      success: false,
      error: '서버 오류가 발생했습니다.'
    });
  }
});

/**
 * POST /api/dungeon/answer
 * 던전 답변 처리
 */
router.post('/answer', authMiddleware, (req, res) => {
  try {
    const { dungeon_run_id, choice } = req.body;

    if (choice === undefined || choice === null) {
      return res.status(400).json({
        success: false,
        error: '선택이 필요합니다.'
      });
    }

    // 간단한 응답 (실제로는 더 복잡한 로직이 필요)
    const isCorrect = choice === 0; // 첫 번째 선택지가 정답

    res.json({
      success: true,
      data: {
        correct: isCorrect,
        message: isCorrect ? '정답입니다!' : '틀렸습니다.',
        monster_defeated: false,
        captured: false
      }
    });
  } catch (error) {
    console.error('Error answering dungeon question:', error);
    res.status(500).json({
      success: false,
      error: '서버 오류가 발생했습니다.'
    });
  }
});

/**
 * POST /api/dungeon/leave
 * 던전 나가기
 */
router.post('/leave', authMiddleware, (req, res) => {
  try {
    res.json({
      success: true,
      message: '던전에서 나갔습니다.'
    });
  } catch (error) {
    console.error('Error leaving dungeon:', error);
    res.status(500).json({
      success: false,
      error: '서버 오류가 발생했습니다.'
    });
  }
});

export default router;
