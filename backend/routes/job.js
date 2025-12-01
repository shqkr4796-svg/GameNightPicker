import express from 'express';
import { authMiddleware } from '../utils/auth.js';
import { loadPlayerData, savePlayerData } from '../utils/fileStorage.js';

const router = express.Router();

const JOBS = [
  { id: 'warrior', 이름: '전사', 설명: '높은 공격력과 체력', 공격력보정: 1.3, 초기급여: 1000 },
  { id: 'mage', 이름: '마법사', 설명: '높은 마나', 마나보정: 1.5, 초기급여: 1200 },
  { id: 'archer', 이름: '궁수', 설명: '균형잡힌 스탯', 공격력보정: 1.1, 초기급여: 1100 },
];

router.get('/list', authMiddleware, (req, res) => {
  try {
    const playerId = req.playerId;
    const loadResult = loadPlayerData(playerId);
    if (!loadResult.success) return res.status(404).json({ success: false, error: '플레이어 데이터를 찾을 수 없습니다.' });
    const playerData = loadResult.data;
    res.json({ success: true, data: { available_jobs: JOBS, current_job: playerData.직업 || null, job_level: playerData.직업_레벨 || 0 } });
  } catch (error) {
    res.status(500).json({ success: false, error: '서버 오류가 발생했습니다.' });
  }
});

router.post('/choose', authMiddleware, (req, res) => {
  try {
    const playerId = req.playerId;
    const { job_id } = req.body;
    if (!job_id) return res.status(400).json({ success: false, error: 'job_id가 필요합니다.' });
    const job = JOBS.find(j => j.id === job_id);
    if (!job) return res.status(404).json({ success: false, error: '존재하지 않는 직업입니다.' });
    const loadResult = loadPlayerData(playerId);
    if (!loadResult.success) return res.status(404).json({ success: false, error: '플레이어 데이터를 찾을 수 없습니다.' });
    const playerData = loadResult.data;
    playerData.직업 = job_id;
    playerData.직업_이름 = job.이름;
    playerData.직업_레벨 = 1;
    playerData.급여 = job.초기급여;
    if (job.공격력보정) playerData.공격력 = Math.floor((playerData.공격력 || 10) * job.공격력보정);
    savePlayerData(playerId, playerData);
    res.json({ success: true, data: { message: `${job.이름} 직업을 선택했습니다!`, job: job } });
  } catch (error) {
    res.status(500).json({ success: false, error: '서버 오류가 발생했습니다.' });
  }
});

router.post('/work', authMiddleware, (req, res) => {
  try {
    const playerId = req.playerId;
    const loadResult = loadPlayerData(playerId);
    if (!loadResult.success) return res.status(404).json({ success: false, error: '플레이어 데이터를 찾을 수 없습니다.' });
    const playerData = loadResult.data;
    if (!playerData.직업) return res.status(400).json({ success: false, error: '선택된 직업이 없습니다.' });
    const jobExp = 100;
    const salary = Math.floor((playerData.급여 || 1000) * 0.1);
    playerData.직업_경험치 = (playerData.직업_경험치 || 0) + jobExp;
    playerData.경험치 = (playerData.경험치 || 0) + jobExp;
    playerData.돈 = (playerData.돈 || 0) + salary;
    if (playerData.직업_경험치 >= 1000) {
      playerData.직업_레벨 = (playerData.직업_레벨 || 1) + 1;
      playerData.직업_경험치 -= 1000;
      playerData.급여 = Math.floor((playerData.급여 || 1000) * 1.1);
    }
    savePlayerData(playerId, playerData);
    res.json({ success: true, data: { message: '일했습니다!', salary_earned: salary, total_money: playerData.돈 } });
  } catch (error) {
    res.status(500).json({ success: false, error: '서버 오류가 발생했습니다.' });
  }
});

export default router;
