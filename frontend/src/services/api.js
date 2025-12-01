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
  load: () => api.get('/player/load')
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

export default api;
