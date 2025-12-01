import express from 'express';
import { authMiddleware } from '../utils/auth.js';
import { loadPlayerData, savePlayerData, loadGameData } from '../utils/fileStorage.js';

const router = express.Router();

/**
 * GET /api/skills
 * 플레이어가 소유한 스킬 목록
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
    const currentSkills = playerData.모험_기술 || ['박치기'];
    const acquiredSkills = playerData.모험_획득스킬 || [];
    const allSkills = loadGameData('skills');

    const skillDetails = currentSkills.map(skillName => {
      return allSkills.find(s => s.이름 === skillName);
    });

    res.json({
      success: true,
      data: {
        current_skills: skillDetails,
        acquired_skills: acquiredSkills,
        max_skills: 4,
        total_acquired: acquiredSkills.length
      }
    });
  } catch (error) {
    console.error('Error fetching skills:', error);
    res.status(500).json({
      success: false,
      error: '서버 오류가 발생했습니다.'
    });
  }
});

/**
 * GET /api/skills/:skill_name
 * 특정 스킬 상세 정보
 */
router.get('/:skill_name', authMiddleware, (req, res) => {
  try {
    const skillName = req.params.skill_name;
    const allSkills = loadGameData('skills');
    const skill = allSkills.find(s => s.이름 === skillName);

    if (!skill) {
      return res.status(404).json({
        success: false,
        error: '존재하지 않는 스킬입니다.'
      });
    }

    res.json({
      success: true,
      data: { skill }
    });
  } catch (error) {
    console.error('Error fetching skill:', error);
    res.status(500).json({
      success: false,
      error: '서버 오류가 발생했습니다.'
    });
  }
});

/**
 * POST /api/skills/acquire
 * 새 스킬 획득 (전투 후 드롭된 스킬 카드)
 */
router.post('/acquire', authMiddleware, (req, res) => {
  try {
    const playerId = req.playerId;
    const { skill_name } = req.body;

    if (!skill_name) {
      return res.status(400).json({
        success: false,
        error: 'skill_name이 필요합니다.'
      });
    }

    const allSkills = loadGameData('skills');
    const skill = allSkills.find(s => s.이름 === skill_name);

    if (!skill) {
      return res.status(404).json({
        success: false,
        error: '존재하지 않는 스킬입니다.'
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
    const currentSkills = playerData.모험_기술 || ['박치기'];
    const acquiredSkills = playerData.모험_획득스킬 || [];

    // 이미 소유한 스킬인지 확인
    if (currentSkills.includes(skill_name)) {
      return res.status(400).json({
        success: false,
        error: '이미 소유한 스킬입니다.'
      });
    }

    // 슬롯이 있으면 자동 추가
    if (currentSkills.length < 4) {
      currentSkills.push(skill_name);
      playerData.모험_기술 = currentSkills;
    } else {
      // 슬롯이 없으면 획득 스킬 목록에만 추가
      if (!acquiredSkills.includes(skill_name)) {
        acquiredSkills.push(skill_name);
      }
      playerData.모험_획득스킬 = acquiredSkills;
    }

    savePlayerData(playerId, playerData);

    res.json({
      success: true,
      data: {
        message: '스킬을 획득했습니다!',
        skill: skill,
        current_skills: playerData.모험_기술,
        auto_added: currentSkills.length <= 4,
        message_detail: currentSkills.length <= 4 
          ? `${skill_name}이(가) 자동으로 추가되었습니다.`
          : `${skill_name}이(가) 보유 목록에 추가되었습니다. 스킬을 교체하면 사용할 수 있습니다.`
      }
    });
  } catch (error) {
    console.error('Error acquiring skill:', error);
    res.status(500).json({
      success: false,
      error: '서버 오류가 발생했습니다.'
    });
  }
});

/**
 * POST /api/skills/replace
 * 스킬 교체
 */
router.post('/replace', authMiddleware, (req, res) => {
  try {
    const playerId = req.playerId;
    const { old_skill_name, new_skill_name } = req.body;

    if (!old_skill_name || !new_skill_name) {
      return res.status(400).json({
        success: false,
        error: 'old_skill_name과 new_skill_name이 필요합니다.'
      });
    }

    const allSkills = loadGameData('skills');
    const oldSkill = allSkills.find(s => s.이름 === old_skill_name);
    const newSkill = allSkills.find(s => s.이름 === new_skill_name);

    if (!oldSkill || !newSkill) {
      return res.status(404).json({
        success: false,
        error: '존재하지 않는 스킬입니다.'
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
    const currentSkills = playerData.모험_기술 || ['박치기'];
    const acquiredSkills = playerData.모험_획득스킬 || [];

    // 현재 소유 스킬 확인
    if (!currentSkills.includes(old_skill_name)) {
      return res.status(400).json({
        success: false,
        error: '소유하지 않은 스킬입니다.'
      });
    }

    // 획득 스킬 목록에서 새 스킬 확인
    if (!acquiredSkills.includes(new_skill_name)) {
      return res.status(400).json({
        success: false,
        error: '획득하지 않은 스킬입니다.'
      });
    }

    // 교체 처리
    const index = currentSkills.indexOf(old_skill_name);
    currentSkills[index] = new_skill_name;
    
    // 획득 목록에서 제거
    acquiredSkills.splice(acquiredSkills.indexOf(new_skill_name), 1);
    
    // 기존 스킬을 획득 목록에 추가
    acquiredSkills.push(old_skill_name);

    playerData.모험_기술 = currentSkills;
    playerData.모험_획득스킬 = acquiredSkills;

    savePlayerData(playerId, playerData);

    res.json({
      success: true,
      data: {
        message: `${old_skill_name}을(를) ${new_skill_name}로 교체했습니다.`,
        current_skills: currentSkills,
        acquired_skills: acquiredSkills
      }
    });
  } catch (error) {
    console.error('Error replacing skill:', error);
    res.status(500).json({
      success: false,
      error: '서버 오류가 발생했습니다.'
    });
  }
});

export default router;
