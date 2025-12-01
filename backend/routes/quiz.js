import express from 'express';
import { authMiddleware } from '../utils/auth.js';
import { loadPlayerData, savePlayerData } from '../utils/fileStorage.js';

const router = express.Router();

/**
 * GET /api/quiz
 * 퀴즈 목록 조회
 */
router.get('/', authMiddleware, (req, res) => {
  try {
    const category = req.query.category || 'all';
    const language = req.query.language || 'random';

    // 기본 단어 데이터 (실제로는 데이터베이스에서 로드)
    const wordBank = [
      { 단어: 'apple', 뜻: '사과', 카테고리: '기본' },
      { 단어: 'banana', 뜻: '바나나', 카테고리: '기본' },
      { 단어: 'orange', 뜻: '오렌지', 카테고리: '기본' }
    ];

    res.json({
      success: true,
      data: {
        word_bank: wordBank,
        categories: ['기본', 'TOEIC'],
        completed_words: 0,
        total_words: wordBank.length,
        current_question: {
          type: '뜻맞히기',
          word: 'apple',
          options: ['사과', '바나나', '딸기', '포도'],
          correct_answer: '사과'
        }
      }
    });
  } catch (error) {
    console.error('Error fetching quiz:', error);
    res.status(500).json({
      success: false,
      error: '서버 오류가 발생했습니다.'
    });
  }
});

/**
 * POST /api/quiz/answer
 * 퀴즈 답변 처리
 */
router.post('/answer', authMiddleware, (req, res) => {
  try {
    const playerId = req.playerId;
    const { answer, correct_answer, quiz_word } = req.body;

    if (!answer || !correct_answer) {
      return res.status(400).json({
        success: false,
        error: '답변이 필요합니다.'
      });
    }

    const isCorrect = answer.toLowerCase().trim() === correct_answer.toLowerCase().trim();

    const loadResult = loadPlayerData(playerId);
    if (loadResult.success) {
      const playerData = loadResult.data;
      
      if (isCorrect) {
        playerData.경험치 = (playerData.경험치 || 0) + 10;
      }

      savePlayerData(playerId, playerData);
    }

    res.json({
      success: true,
      data: {
        correct: isCorrect,
        exp_gained: isCorrect ? 10 : 0,
        message: isCorrect ? '정답!' : '틀렸습니다.',
        completed_words: 1,
        total_words: 100,
        all_completed: false
      }
    });
  } catch (error) {
    console.error('Error answering quiz:', error);
    res.status(500).json({
      success: false,
      error: '서버 오류가 발생했습니다.'
    });
  }
});

export default router;
