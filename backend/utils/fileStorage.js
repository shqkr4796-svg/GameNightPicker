import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const SAVE_DIR = process.env.SAVE_DIR || './saves';
const DATA_DIR = process.env.DATA_DIR || './data';

/**
 * 플레이어 저장 파일 경로
 */
function getPlayerFilePath(playerId) {
  return path.join(SAVE_DIR, `player_${playerId}.json`);
}

/**
 * 플레이어 데이터 저장
 */
export function savePlayerData(playerId, playerData) {
  try {
    const filePath = getPlayerFilePath(playerId);
    fs.writeFileSync(filePath, JSON.stringify(playerData, null, 2), 'utf-8');
    return { success: true, message: '플레이어 데이터가 저장되었습니다.' };
  } catch (error) {
    console.error('Error saving player data:', error);
    return { success: false, error: error.message };
  }
}

/**
 * 플레이어 데이터 로드
 */
export function loadPlayerData(playerId) {
  try {
    const filePath = getPlayerFilePath(playerId);
    if (!fs.existsSync(filePath)) {
      return { success: false, error: '저장된 게임이 없습니다.' };
    }
    const data = fs.readFileSync(filePath, 'utf-8');
    return { success: true, data: JSON.parse(data) };
  } catch (error) {
    console.error('Error loading player data:', error);
    return { success: false, error: error.message };
  }
}

/**
 * 플레이어 데이터 삭제
 */
export function deletePlayerData(playerId) {
  try {
    const filePath = getPlayerFilePath(playerId);
    if (fs.existsSync(filePath)) {
      fs.unlinkSync(filePath);
    }
    return { success: true, message: '플레이어 데이터가 삭제되었습니다.' };
  } catch (error) {
    console.error('Error deleting player data:', error);
    return { success: false, error: error.message };
  }
}

/**
 * 게임 데이터 (JSON) 로드 (읽기 전용)
 */
export function loadGameData(fileName) {
  try {
    const filePath = path.join(DATA_DIR, `${fileName}.json`);
    if (!fs.existsSync(filePath)) {
      console.warn(`Game data file not found: ${filePath}`);
      return [];
    }
    const data = fs.readFileSync(filePath, 'utf-8');
    const parsed = JSON.parse(data);
    
    // 몬스터 데이터: id를 key로 하는 객체로 변환
    if (fileName === 'monsters' && Array.isArray(parsed)) {
      const monstersMap = {};
      parsed.forEach(monster => {
        monstersMap[monster.id] = monster;
      });
      return monstersMap;
    }
    
    return parsed;
  } catch (error) {
    console.error(`Error loading game data (${fileName}):`, error);
    return [];
  }
}

export default {
  savePlayerData,
  loadPlayerData,
  deletePlayerData,
  loadGameData
};
