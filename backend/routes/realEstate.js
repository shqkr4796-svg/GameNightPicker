import express from 'express';
import { authMiddleware } from '../utils/auth.js';
import { loadPlayerData, savePlayerData } from '../utils/fileStorage.js';

const router = express.Router();

// 부동산 데이터
const REAL_ESTATE_PROPERTIES = [
  { id: 'apt_small', 이름: '작은 아파트', 가격: 10000, 월세: 1000, 설명: '입문용 주택', 가치: 15000 },
  { id: 'house_medium', 이름: '중형 주택', 가격: 50000, 월세: 5000, 설명: '중산층 주택', 가치: 75000 },
  { id: 'villa_large', 이름: '대형 빌라', 가격: 200000, 월세: 20000, 설명: '럭셔리 주택', 가치: 300000 },
  { id: 'office', 이름: '상업용 건물', 가격: 100000, 월세: 15000, 설명: '상업 공간', 가치: 150000 },
];

/**
 * GET /api/realestate
 * 부동산 목록 조회
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
    const properties = playerData.부동산 || [];

    res.json({
      success: true,
      data: {
        available_properties: REAL_ESTATE_PROPERTIES,
        owned_properties: properties,
        total_wealth: properties.reduce((sum, p) => sum + (p.가치 || 0), 0),
        player_money: playerData.돈 || 0
      }
    });
  } catch (error) {
    console.error('Error fetching real estate:', error);
    res.status(500).json({
      success: false,
      error: '서버 오류가 발생했습니다.'
    });
  }
});

/**
 * POST /api/realestate/buy
 * 부동산 구매
 */
router.post('/buy', authMiddleware, (req, res) => {
  try {
    const playerId = req.playerId;
    const { property_id } = req.body;

    if (!property_id) {
      return res.status(400).json({
        success: false,
        error: 'property_id가 필요합니다.'
      });
    }

    const property = REAL_ESTATE_PROPERTIES.find(p => p.id === property_id);
    if (!property) {
      return res.status(404).json({
        success: false,
        error: '존재하지 않는 부동산입니다.'
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
    const playerMoney = playerData.돈 || 0;

    if (playerMoney < property.가격) {
      return res.status(400).json({
        success: false,
        error: '돈이 부족합니다.'
      });
    }

    // 구매 처리
    playerData.돈 -= property.가격;
    const properties = playerData.부동산 || [];
    properties.push({
      ...property,
      purchased_at: new Date().toISOString(),
      monthly_income: property.월세
    });
    playerData.부동산 = properties;

    savePlayerData(playerId, playerData);

    res.json({
      success: true,
      data: {
        message: `${property.이름}을(를) 구매했습니다!`,
        property_purchased: property,
        remaining_money: playerData.돈,
        total_monthly_income: properties.reduce((sum, p) => sum + (p.월세 || 0), 0)
      }
    });
  } catch (error) {
    console.error('Error buying property:', error);
    res.status(500).json({
      success: false,
      error: '서버 오류가 발생했습니다.'
    });
  }
});

/**
 * POST /api/realestate/collect_rent
 * 월세 수금
 */
router.post('/collect_rent', authMiddleware, (req, res) => {
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
    const properties = playerData.부동산 || [];

    if (properties.length === 0) {
      return res.status(400).json({
        success: false,
        error: '소유한 부동산이 없습니다.'
      });
    }

    const totalRent = properties.reduce((sum, p) => sum + (p.월세 || 0), 0);
    playerData.돈 = (playerData.돈 || 0) + totalRent;
    playerData.마지막_월세수금 = new Date().toISOString();

    savePlayerData(playerId, playerData);

    res.json({
      success: true,
      data: {
        message: '월세를 수금했습니다.',
        total_rent_collected: totalRent,
        total_money: playerData.돈,
        properties_count: properties.length
      }
    });
  } catch (error) {
    console.error('Error collecting rent:', error);
    res.status(500).json({
      success: false,
      error: '서버 오류가 발생했습니다.'
    });
  }
});

export default router;
