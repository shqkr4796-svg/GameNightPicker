import express from 'express';
import { authMiddleware } from '../utils/auth.js';
import { loadPlayerData, savePlayerData } from '../utils/fileStorage.js';

const router = express.Router();

// 상점 아이템 데이터
const SHOP_ITEMS = [
  { id: '회복약', 이름: '회복약', 가격: 500, 설명: '체력 50 회복', 타입: '소비' },
  { id: '마나약', 이름: '마나약', 가격: 300, 설명: '마나 30 회복', 타입: '소비' },
  { id: '풀회복약', 이름: '풀회복약', 가격: 1000, 설명: '체력과 마나 완전 회복', 타입: '소비' },
  { id: '경험치_부스터', 이름: '경험치 부스터', 가격: 2000, 설명: '다음 던전에서 경험치 2배', 타입: '버프' },
  { id: '보물_상자', 이름: '보물 상자', 가격: 5000, 설명: '1000~5000원 얻기', 타입: '보상' }
];

/**
 * GET /api/shop
 * 상점 조회
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

    res.json({
      success: true,
      data: {
        items: SHOP_ITEMS,
        player_money: playerData.돈 || 0,
        inventory: playerData.인벤토리 || {}
      }
    });
  } catch (error) {
    console.error('Error fetching shop:', error);
    res.status(500).json({
      success: false,
      error: '서버 오류가 발생했습니다.'
    });
  }
});

/**
 * POST /api/shop/buy
 * 아이템 구매
 */
router.post('/buy', authMiddleware, (req, res) => {
  try {
    const playerId = req.playerId;
    const { item_id, quantity } = req.body;

    if (!item_id || !quantity) {
      return res.status(400).json({
        success: false,
        error: 'item_id와 quantity가 필요합니다.'
      });
    }

    const item = SHOP_ITEMS.find(i => i.id === item_id);
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
    const totalCost = item.가격 * quantity;
    const playerMoney = playerData.돈 || 0;

    if (playerMoney < totalCost) {
      return res.status(400).json({
        success: false,
        error: '돈이 부족합니다.'
      });
    }

    // 구매 처리
    playerData.돈 -= totalCost;
    const inventory = playerData.인벤토리 || {};
    inventory[item_id] = (inventory[item_id] || 0) + quantity;
    playerData.인벤토리 = inventory;

    savePlayerData(playerId, playerData);

    res.json({
      success: true,
      data: {
        message: `${item.이름} ${quantity}개를 구매했습니다.`,
        remaining_money: playerData.돈,
        inventory: inventory
      }
    });
  } catch (error) {
    console.error('Error buying item:', error);
    res.status(500).json({
      success: false,
      error: '서버 오류가 발생했습니다.'
    });
  }
});

/**
 * POST /api/shop/use_item
 * 아이템 사용
 */
router.post('/use_item', authMiddleware, (req, res) => {
  try {
    const playerId = req.playerId;
    const { item_id } = req.body;

    if (!item_id) {
      return res.status(400).json({
        success: false,
        error: 'item_id가 필요합니다.'
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
    const inventory = playerData.인벤토리 || {};

    if (!inventory[item_id] || inventory[item_id] <= 0) {
      return res.status(400).json({
        success: false,
        error: '소유하지 않은 아이템입니다.'
      });
    }

    const item = SHOP_ITEMS.find(i => i.id === item_id);

    // 아이템별 효과 처리
    let effect_message = '';
    if (item_id === '회복약') {
      playerData.체력 = (playerData.체력 || 100) + 50;
      effect_message = '체력이 50 회복되었습니다.';
    } else if (item_id === '마나약') {
      playerData.마나 = (playerData.마나 || 50) + 30;
      effect_message = '마나가 30 회복되었습니다.';
    } else if (item_id === '풀회복약') {
      playerData.체력 = 100;
      playerData.마나 = 50;
      effect_message = '체력과 마나가 완전 회복되었습니다.';
    }

    inventory[item_id] -= 1;
    playerData.인벤토리 = inventory;
    savePlayerData(playerId, playerData);

    res.json({
      success: true,
      data: {
        message: effect_message,
        inventory: inventory
      }
    });
  } catch (error) {
    console.error('Error using item:', error);
    res.status(500).json({
      success: false,
      error: '서버 오류가 발생했습니다.'
    });
  }
});

export default router;
