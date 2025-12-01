import axios from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';

const API_BASE_URL = process.env.API_BASE_URL || 'http://localhost:3000';

const api = axios.create({
  baseURL: `${API_BASE_URL}/api`,
  timeout: 10000
});

// 요청 인터셉터: 토큰 자동 추가
api.interceptors.request.use(
  async (config) => {
    const token = await AsyncStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// 응답 인터셉터: 에러 처리
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      // 토큰 만료 시 로그아웃
      await AsyncStorage.removeItem('auth_token');
    }
    return Promise.reject(error);
  }
);

// 플레이어 API
export const playerAPI = {
  start: () => api.post('/player/start'),
  getInfo: () => api.get('/player/info'),
  save: (playerData) => api.post('/player/save', playerData),
  load: () => api.get('/player/load'),
  sleep: () => api.post('/player/sleep')
};

// 모험 API
export const adventureAPI = {
  select: () => api.get('/adventure/select'),
  start: (stageId, monsterIds) => api.post('/adventure/start', { stage_id: stageId, monster_ids: monsterIds }),
  action: (battleId, skillName) => api.post('/adventure/action', { battle_id: battleId, skill_name: skillName }),
  flee: (battleId) => api.post('/adventure/flee', { battle_id: battleId })
};

// 스킬 API
export const skillsAPI = {
  list: () => api.get('/skills'),
  acquire: (skillName) => api.post('/skills/acquire', { skill_name: skillName }),
  replace: (oldSkill, newSkill) => api.post('/skills/replace', { old_skill_name: oldSkill, new_skill_name: newSkill })
};

// 도감 API
export const compendiumAPI = {
  list: () => api.get('/compendium'),
  details: (monsterId) => api.get(`/compendium/${monsterId}`),
  capture: (monsterId, monsterData) => api.post('/compendium/capture', { monster_id: monsterId, monster_data: monsterData })
};

// 상점 API
export const shopAPI = {
  list: () => api.get('/shop'),
  buy: (itemId, quantity) => api.post('/shop/buy', { item_id: itemId, quantity }),
  useItem: (itemId) => api.post('/shop/use_item', { item_id: itemId })
};

// 퀴즈 API
export const quizAPI = {
  list: () => api.get('/quiz'),
  getCategory: (category) => api.get(`/quiz/category/${category}`),
  submit: (category, score, questions) => api.post('/quiz/submit', { category, score, questions }),
  getWrongQuestions: (category) => api.get(`/quiz/wrong/${category}`)
};

// 던전 API
export const dungeonAPI = {
  list: () => api.get('/dungeon'),
  start: (dungeonId) => api.post('/dungeon/start', { dungeon_id: dungeonId }),
  answer: (dungeonId, answer) => api.post('/dungeon/answer', { dungeon_id: dungeonId, answer }),
  complete: (dungeonId) => api.post('/dungeon/complete', { dungeon_id: dungeonId })
};

// 표현학습 API
export const expressionsAPI = {
  list: () => api.get('/expressions'),
  submit: (expressionId, answer) => api.post('/expressions/submit', { expression_id: expressionId, answer }),
  getDailyTask: () => api.get('/expressions/daily')
};

// 대시보드 API
export const dashboardAPI = {
  getStats: () => api.get('/dashboard/stats'),
  getLevelInfo: () => api.get('/dashboard/level'),
  getProgress: () => api.get('/dashboard/progress')
};

// 인벤토리 API
export const inventoryAPI = {
  list: () => api.get('/inventory'),
  useItem: (itemId) => api.post('/inventory/use', { item_id: itemId }),
  equip: (itemId) => api.post('/inventory/equip', { item_id: itemId })
};

// 직업 API
export const jobAPI = {
  list: () => api.get('/job'),
  apply: (jobId) => api.post('/job/apply', { job_id: jobId }),
  work: () => api.post('/job/work'),
  quit: () => api.post('/job/quit')
};

// 부동산 API
export const realEstateAPI = {
  list: () => api.get('/real-estate'),
  buy: (propertyId) => api.post('/real-estate/buy', { property_id: propertyId }),
  sell: (propertyId) => api.post('/real-estate/sell', { property_id: propertyId }),
  changeResidence: (propertyId) => api.post('/real-estate/change', { property_id: propertyId })
};

// 업적 API
export const achievementsAPI = {
  list: () => api.get('/achievements'),
  progress: () => api.get('/achievements/progress'),
  claim: (achievementId) => api.post('/achievements/claim', { achievement_id: achievementId })
};

export default api;
