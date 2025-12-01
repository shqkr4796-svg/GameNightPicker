import express from 'express';
import { authMiddleware } from '../utils/auth.js';
import { loadPlayerData, savePlayerData, loadGameData } from '../utils/fileStorage.js';

const router = express.Router();

const SKILL_ITEMS = [
  { id: '기술충전제', 이름: '기술충전제', 설명: '기술 횟수 부분 회복', 효과: '최대 제한 횟수의 1/2 회복' },
  { id: '기술초기화제', 이름: '기술초기화제', 설명: '모든 기술 횟수 리셋', 효과: '모든 기술 사용 횟수 완전 리셋' }
];

/**
 * GET /api/skill-items
 * 플레이어 기술 아이템 인벤토리
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
    const inventory = playerData.기술아이템_인벤토리 || {};

    res.json({
      success: true,
      data: {
        available_items: SKILL_ITEMS,
        inventory: inventory,
        total_items: Object.values(inventory).reduce((a, b) => a + b, 0)
      }
    });
  } catch (error) {
    console.error('Error fetching skill items:', error);
    res.status(500).json({
      success: false,
      error: '서버 오류가 발생했습니다.'
    });
  }
});

/**
 * POST /api/skill-items/use
 * 기술 아이템 사용
 */
router.post('/use', authMiddleware, (req, res) => {
  try {
    const playerId = req.playerId;
    const { item_id } = req.body;

    if (!item_id) {
      return res.status(400).json({
        success: false,
        error: 'item_id가 필요합니다.'
      });
    }

    const item = SKILL_ITEMS.find(i => i.id === item_id);
    if (!item) {
      return res.status(404).json({
        success: false,
        error: '존재하지 않는 아이템입니다.'
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
    const inventory = playerData.기술아이템_인벤토리 || {};

    // 아이템 보유 확인
    if (!inventory[item_id] || inventory[item_id] <= 0) {
      return res.status(400).json({
        success: false,
        error: '보유하지 않은 아이템입니다.'
      });
    }

    let effect_message = '';
    const skillUsage = playerData.기술_사용횟수 || {};
    const allSkills = loadGameData('skills');

    if (item_id === '기술충전제') {
      // 기술 횟수 부분 회복 (최대 제한 횟수의 1/2)
      allSkills.forEach(skill => {
        const skillName = skill.이름;
        const maxUsage = skill.사용_횟수 || 10;
        const currentUsage = skillUsage[skillName] || maxUsage;
        const recoveryAmount = Math.floor(maxUsage / 2);
        const newUsage = Math.min(maxUsage, currentUsage + recoveryAmount);
        skillUsage[skillName] = newUsage;
      });
      effect_message = '모든 기술의 사용 횟수가 50% 회복되었습니다.';
    } else if (item_id === '기술초기화제') {
      // 모든 기술 완전 리셋
      allSkills.forEach(skill => {
        const skillName = skill.이름;
        const maxUsage = skill.사용_횟수 || 10;
        skillUsage[skillName] = maxUsage;
      });
      effect_message = '모든 기술의 사용 횟수가 완전히 리셋되었습니다.';
    }

    // 아이템 소비
    inventory[item_id] -= 1;
    playerData.기술아이템_인벤토리 = inventory;
    playerData.기술_사용횟수 = skillUsage;

    savePlayerData(playerId, playerData);

    res.json({
      success: true,
      data: {
        message: effect_message,
        item_used: item,
        remaining_items: inventory[item_id],
        skill_usage: skillUsage
      }
    });
  } catch (error) {
    console.error('Error using skill item:', error);
    res.status(500).json({
      success: false,
      error: '서버 오류가 발생했습니다.'
    });
  }
});

/**
 * POST /api/skill-items/acquire
 * 기술 아이템 획득 (전투 후 드롭)
 */
router.post('/acquire', authMiddleware, (req, res) => {
  try {
    const playerId = req.playerId;
    const { item_id, quantity } = req.body;

    if (!item_id) {
      return res.status(400).json({
        success: false,
        error: 'item_id가 필요합니다.'
      });
    }

    const item = SKILL_ITEMS.find(i => i.id === item_id);
    if (!item) {
      return res.status(404).json({
        success: false,
        error: '존재하지 않는 아이템입니다.'
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
    const inventory = playerData.기술아이템_인벤토리 || {};
    const qty = quantity || 1;

    inventory[item_id] = (inventory[item_id] || 0) + qty;
    playerData.기술아이템_인벤토리 = inventory;

    savePlayerData(playerId, playerData);

    res.json({
      success: true,
      data: {
        message: `${item.이름}을(를) ${qty}개 획득했습니다!`,
        item: item,
        inventory: inventory
      }
    });
  } catch (error) {
    console.error('Error acquiring skill item:', error);
    res.status(500).json({
      success: false,
      error: '서버 오류가 발생했습니다.'
    });
  }
});

export default router;
