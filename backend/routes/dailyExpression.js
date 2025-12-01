import express from 'express';
import { authMiddleware } from '../utils/auth.js';
import { loadPlayerData, savePlayerData } from '../utils/fileStorage.js';

const router = express.Router();

const DAILY_EXPRESSIONS = [
  { id: 1, 영어: "Hello, how are you?", 한글: "안녕하세요, 어떻게 지내세요?", 난이도: "쉬움" },
  { id: 2, 영어: "Nice to meet you.", 한글: "만나서 반갑습니다.", 난이도: "쉬움" },
  { id: 3, 영어: "What is your name?", 한글: "당신의 이름은 무엇입니까?", 난이도: "쉬움" },
  { id: 4, 영어: "How do you do?", 한글: "어떻게 지내세요?", 난이도: "중간" },
  { id: 5, 영어: "I am glad to see you.", 한글: "당신을 만나서 기쁩니다.", 난이도: "중간" },
  { id: 6, 영어: "Could you help me?", 한글: "저를 도와주실 수 있을까요?", 난이도: "중간" },
  { id: 7, 영어: "I would appreciate your assistance.", 한글: "당신의 도움을 감사하겠습니다.", 난이도: "어려움" },
  { id: 8, 영어: "How can I improve my English?", 한글: "영어를 어떻게 향상시킬 수 있습니까?", 난이도: "어려움" },
];

router.get('/', authMiddleware, (req, res) => {
  try {
    const difficulty = req.query.difficulty || 'all';
    const expressions = difficulty === 'all' 
      ? DAILY_EXPRESSIONS 
      : DAILY_EXPRESSIONS.filter(e => e.난이도 === difficulty);

    res.json({
      success: true,
      data: { expressions: expressions, total_count: DAILY_EXPRESSIONS.length }
    });
  } catch (error) {
    res.status(500).json({ success: false, error: '서버 오류가 발생했습니다.' });
  }
});

router.post('/:id/practice', authMiddleware, (req, res) => {
  try {
    const playerId = req.playerId;
    const expressionId = parseInt(req.params.id);
    const { user_answer } = req.body;

    const expression = DAILY_EXPRESSIONS.find(e => e.id === expressionId);
    if (!expression) {
      return res.status(404).json({ success: false, error: '존재하지 않는 표현입니다.' });
    }

    const loadResult = loadPlayerData(playerId);
    if (!loadResult.success) {
      return res.status(404).json({ success: false, error: '플레이어 데이터를 찾을 수 없습니다.' });
    }

    const playerData = loadResult.data;
    const isCorrect = user_answer?.toLowerCase().trim() === expression.영어.toLowerCase().trim();
    const exp_gained = isCorrect ? 50 : 10;

    playerData.경험치 = (playerData.경험치 || 0) + exp_gained;
    if (!playerData.일일_표현_학습) playerData.일일_표현_학습 = {};
    playerData.일일_표현_학습[expressionId] = { practiced: true, correct: isCorrect, attempted_at: new Date().toISOString() };

    savePlayerData(playerId, playerData);

    res.json({
      success: true,
      data: {
        correct: isCorrect,
        exp_gained: exp_gained,
        correct_answer: expression.영어,
        message: isCorrect ? '정답입니다!' : '다시 시도해보세요.'
      }
    });
  } catch (error) {
    res.status(500).json({ success: false, error: '서버 오류가 발생했습니다.' });
  }
});

export default router;
