import React, { useState, useEffect } from 'react';
import { View, Text, TouchableOpacity, StyleSheet, Alert, ScrollView, ActivityIndicator, Vibration } from 'react-native';
import { adventureAPI, skillsAPI, compendiumAPI } from '../services/api';

export default function AdventureScreen({ navigation }) {
  const [stages, setStages] = useState([]);
  const [selectedStage, setSelectedStage] = useState(null);
  const [availableMonsters, setAvailableMonsters] = useState([]);
  const [selectedMonsters, setSelectedMonsters] = useState([]);
  const [currentSkills, setCurrentSkills] = useState([]);
  const [adventureEnergy, setAdventureEnergy] = useState(100);
  const [loading, setLoading] = useState(true);
  const [battleActive, setBattleActive] = useState(false);
  const [battleState, setBattleState] = useState(null);
  const [difficulty, setDifficulty] = useState('normal');

  useEffect(() => {
    loadAdventureData();
  }, []);

  const loadAdventureData = async () => {
    setLoading(true);
    try {
      const [adventureRes, skillsRes, compendiumRes] = await Promise.all([
        adventureAPI.select(),
        skillsAPI.list(),
        compendiumAPI.list()
      ]);

      if (adventureRes.data.success) {
        setStages(adventureRes.data.data.stages || []);
        setAdventureEnergy(adventureRes.data.data.energy || 100);
        setDifficulty(adventureRes.data.data.difficulty || 'normal');
      }
      if (skillsRes.data.success) {
        setCurrentSkills(skillsRes.data.data.current_skills || []);
      }
      if (compendiumRes.data.success) {
        setAvailableMonsters(compendiumRes.data.data.monsters || []);
      }
    } catch (error) {
      Alert.alert('오류', '모험 데이터 로드 실패');
    } finally {
      setLoading(false);
    }
  };

  const toggleMonster = (monsterId) => {
    if (selectedMonsters.includes(monsterId)) {
      setSelectedMonsters(selectedMonsters.filter(id => id !== monsterId));
    } else {
      if (selectedMonsters.length < 3) {
        setSelectedMonsters([...selectedMonsters, monsterId]);
      } else {
        Alert.alert('알림', '최대 3마리까지만 선택 가능합니다.');
      }
    }
  };

  const handleStartBattle = async () => {
    if (!selectedStage) {
      Alert.alert('알림', '스테이지를 선택해주세요.');
      return;
    }
    if (selectedMonsters.length === 0) {
      Alert.alert('알림', '최소 1마리의 몬스터를 선택해주세요.');
      return;
    }
    if (adventureEnergy < (selectedStage.energy_cost || 10)) {
      Alert.alert('알림', '모험 기력이 부족합니다.');
      return;
    }

    Vibration.vibrate([0, 50, 50, 50, 50, 50]);
    setBattleActive(true);

    try {
      const response = await adventureAPI.start(selectedStage.stage_id, selectedMonsters);
      if (response.data.success) {
        setBattleState({
          battle_id: response.data.data.battle_id,
          stage_name: selectedStage.name,
          enemies: response.data.data.enemies || [],
          currentEnemyIndex: 0,
          playerHP: response.data.data.player_hp || 100,
          enemyHP: response.data.data.enemy_hp || 50,
          turn: 0,
          log: ['전투 시작!', `${selectedStage.name} 시작`]
        });
      }
    } catch (error) {
      Alert.alert('오류', '전투 시작 실패');
      setBattleActive(false);
    }
  };

  const playBattleSound = (type) => {
    if (type === 'attack') {
      Vibration.vibrate([0, 100, 50, 100]);
    } else if (type === 'damage') {
      Vibration.vibrate([0, 200, 100, 200]);
    } else if (type === 'victory') {
      Vibration.vibrate([0, 100, 50, 100, 50, 100]);
    } else if (type === 'defeat') {
      Vibration.vibrate(500);
    }
  };

  const handleUseSkill = async (skillName) => {
    if (!battleState) return;

    playBattleSound('attack');

    try {
      const response = await adventureAPI.action(battleState.battle_id, skillName);

      if (response.data.success) {
        const newLog = [...battleState.log];
        newLog.push(`플레이어: ${skillName} 사용!`);

        if (response.data.data.damage > 0) {
          playBattleSound('damage');
          newLog.push(`${response.data.data.damage} 데미지!`);
        }

        if (response.data.data.enemy_hp <= 0) {
          newLog.push('적을 물리쳤습니다!');
          playBattleSound('victory');
          setBattleState({
            ...battleState,
            log: newLog,
            victory: true,
            enemyHP: 0
          });
        } else if (response.data.data.player_hp <= 0) {
          newLog.push('플레이어가 쓰러졌습니다!');
          playBattleSound('defeat');
          setBattleState({
            ...battleState,
            log: newLog,
            defeat: true,
            playerHP: 0
          });
        } else {
          newLog.push(`상대: 공격 ${response.data.data.enemy_damage || 5} 데미지!`);
          setBattleState({
            ...battleState,
            playerHP: response.data.data.player_hp,
            enemyHP: response.data.data.enemy_hp,
            log: newLog,
            turn: battleState.turn + 1
          });
        }
      }
    } catch (error) {
      Alert.alert('오류', '스킬 사용 실패');
    }
  };

  const handleFlee = async () => {
    if (!battleState) return;

    try {
      const response = await adventureAPI.flee(battleState.battle_id);
      if (response.data.success) {
        Alert.alert('알림', '전투에서 도망쳤습니다.');
        setBattleActive(false);
        setBattleState(null);
        loadAdventureData();
      }
    } catch (error) {
      Alert.alert('오류', '도망 실패');
    }
  };

  if (loading) {
    return (
      <View style={styles.container}>
        <ActivityIndicator color="#6366f1" size="large" />
      </View>
    );
  }

  // 전투 중인 경우
  if (battleActive && battleState) {
    return (
      <View style={styles.battleContainer}>
        <Text style={styles.stageTitle}>{battleState.stage_name}</Text>

        {/* 적 정보 */}
        <View style={styles.enemySection}>
          <Text style={styles.enemyName}>적</Text>
          <View style={styles.hpBar}>
            <View
              style={[
                styles.hpFill,
                {
                  width: `${Math.max(0, (battleState.enemyHP / 100) * 100)}%`
                }
              ]}
            />
          </View>
          <Text style={styles.hpText}>
            {battleState.enemyHP} / 100
          </Text>
        </View>

        {/* 플레이어 정보 */}
        <View style={styles.playerSection}>
          <Text style={styles.playerName}>플레이어</Text>
          <View style={styles.hpBar}>
            <View
              style={[
                styles.hpFill,
                { backgroundColor: '#22c55e' },
                {
                  width: `${Math.max(0, (battleState.playerHP / 100) * 100)}%`
                }
              ]}
            />
          </View>
          <Text style={styles.hpText}>{battleState.playerHP} / 100</Text>
        </View>

        {/* 전투 로그 */}
        <ScrollView style={styles.logContainer}>
          {battleState.log.map((entry, idx) => (
            <Text key={idx} style={styles.logEntry}>
              {entry}
            </Text>
          ))}
        </ScrollView>

        {/* 전투 액션 */}
        {!battleState.victory && !battleState.defeat ? (
          <View style={styles.skillButtonContainer}>
            {currentSkills.map((skill, idx) => (
              <TouchableOpacity
                key={idx}
                style={styles.skillButton}
                onPress={() => handleUseSkill(skill.이름)}
              >
                <Text style={styles.skillButtonText}>
                  {skill.이름}
                </Text>
                <Text style={styles.skillDamage}>
                  {skill.데미지_최소}-{skill.데미지_최대}
                </Text>
              </TouchableOpacity>
            ))}
            <TouchableOpacity
              style={[styles.skillButton, styles.fleeButton]}
              onPress={handleFlee}
            >
              <Text style={styles.skillButtonText}>도망</Text>
            </TouchableOpacity>
          </View>
        ) : (
          <TouchableOpacity
            style={styles.continueButton}
            onPress={() => {
              setBattleActive(false);
              setBattleState(null);
              loadAdventureData();
            }}
          >
            <Text style={styles.continueButtonText}>
              {battleState.victory ? '다음 스테이지' : '돌아가기'}
            </Text>
          </TouchableOpacity>
        )}
      </View>
    );
  }

  // 스테이지 선택 화면
  return (
    <ScrollView style={styles.container}>
      <Text style={styles.title}>모험</Text>
      <Text style={styles.subtitle}>스테이지를 선택하여 진행하세요</Text>

      {/* 모험 기력 표시 */}
      <View style={styles.energyCard}>
        <Text style={styles.energyLabel}>모험 기력</Text>
        <Text style={styles.energyValue}>{adventureEnergy} / 100</Text>
        <Text style={styles.energyNote}>난이도: {difficulty === 'normal' ? '일반' : '심화'}</Text>
      </View>

      {/* 스테이지 목록 */}
      <Text style={styles.sectionTitle}>스테이지 선택</Text>
      <View style={styles.stageList}>
        {stages.map((stage, idx) => (
          <TouchableOpacity
            key={idx}
            style={[
              styles.stageButton,
              selectedStage?.stage_id === stage.stage_id && styles.selectedStage
            ]}
            onPress={() => setSelectedStage(stage)}
          >
            <Text style={styles.stageNumber}>Stage {stage.stage_id}</Text>
            <Text style={styles.stageDifficulty}>난이도: {stage.난이도 || 'Normal'}</Text>
            <Text style={styles.stageEnemy}>
              {stage.enemy_count || 3}마리 전투
            </Text>
          </TouchableOpacity>
        ))}
      </View>

      {/* 몬스터 선택 */}
      {selectedStage && (
        <>
          <Text style={styles.sectionTitle}>팀 구성 (최대 3마리)</Text>
          <View style={styles.monsterGrid}>
            {availableMonsters.map((monster, idx) => (
              <TouchableOpacity
                key={idx}
                style={[
                  styles.monsterCard,
                  selectedMonsters.includes(monster.id) && styles.selectedMonster
                ]}
                onPress={() => toggleMonster(monster.id)}
              >
                <Text style={styles.monsterEmoji}>
                  {monster.emoji || monster.rarity_emoji || '🐉'}
                </Text>
                <Text style={styles.monsterName}>{monster.name}</Text>
                <Text style={styles.monsterRarity}>{monster.rarity}</Text>
              </TouchableOpacity>
            ))}
          </View>

          {/* 선택된 몬스터 표시 */}
          <View style={styles.selectedMonsterList}>
            <Text style={styles.selectedCountText}>
              선택된 몬스터: {selectedMonsters.length} / 3
            </Text>
            {selectedMonsters.length > 0 && (
              <View style={styles.selectedMonsterIndicator}>
                {selectedMonsters.map((id, idx) => (
                  <Text key={idx} style={styles.monsterBadge}>
                    {idx + 1}
                  </Text>
                ))}
              </View>
            )}
          </View>

          {/* 전투 시작 버튼 */}
          <TouchableOpacity
            style={styles.startButton}
            onPress={handleStartBattle}
          >
            <Text style={styles.startButtonText}>전투 시작</Text>
          </TouchableOpacity>
        </>
      )}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#1a1a1a',
    padding: 16
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#fff',
    marginBottom: 5
  },
  subtitle: {
    fontSize: 14,
    color: '#aaa',
    marginBottom: 20
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#6366f1',
    marginBottom: 12,
    marginTop: 16
  },
  energyCard: {
    backgroundColor: '#2a2a2a',
    padding: 15,
    borderRadius: 8,
    marginBottom: 20,
    borderLeftWidth: 4,
    borderLeftColor: '#6366f1'
  },
  energyLabel: {
    color: '#aaa',
    fontSize: 12,
    marginBottom: 5
  },
  energyValue: {
    color: '#fff',
    fontSize: 20,
    fontWeight: 'bold',
    marginBottom: 5
  },
  energyNote: {
    color: '#6366f1',
    fontSize: 12
  },
  stageList: {
    gap: 10,
    marginBottom: 20
  },
  stageButton: {
    backgroundColor: '#2a2a2a',
    padding: 15,
    borderRadius: 8,
    borderLeftWidth: 4,
    borderLeftColor: '#666',
    borderWidth: 2,
    borderColor: 'transparent'
  },
  selectedStage: {
    borderColor: '#6366f1',
    borderLeftColor: '#6366f1'
  },
  stageNumber: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
    marginBottom: 5
  },
  stageDifficulty: {
    color: '#aaa',
    fontSize: 12,
    marginBottom: 5
  },
  stageEnemy: {
    color: '#6366f1',
    fontSize: 12
  },
  monsterGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 10,
    marginBottom: 20
  },
  monsterCard: {
    width: '31%',
    backgroundColor: '#2a2a2a',
    padding: 12,
    borderRadius: 8,
    alignItems: 'center',
    borderWidth: 2,
    borderColor: 'transparent'
  },
  selectedMonster: {
    borderColor: '#6366f1',
    backgroundColor: '#1a1a4d'
  },
  monsterEmoji: {
    fontSize: 32,
    marginBottom: 5
  },
  monsterName: {
    color: '#fff',
    fontSize: 12,
    fontWeight: '600',
    textAlign: 'center',
    marginBottom: 3
  },
  monsterRarity: {
    color: '#6366f1',
    fontSize: 10
  },
  selectedMonsterList: {
    backgroundColor: '#2a2a2a',
    padding: 15,
    borderRadius: 8,
    marginBottom: 20,
    alignItems: 'center'
  },
  selectedCountText: {
    color: '#fff',
    fontSize: 14,
    fontWeight: '600',
    marginBottom: 10
  },
  selectedMonsterIndicator: {
    flexDirection: 'row',
    gap: 8
  },
  monsterBadge: {
    backgroundColor: '#6366f1',
    color: '#fff',
    width: 30,
    height: 30,
    borderRadius: 15,
    textAlign: 'center',
    lineHeight: 30,
    fontWeight: 'bold'
  },
  startButton: {
    backgroundColor: '#6366f1',
    padding: 15,
    borderRadius: 8,
    alignItems: 'center',
    marginBottom: 30
  },
  startButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold'
  },
  // Battle Styles
  battleContainer: {
    flex: 1,
    backgroundColor: '#1a1a1a',
    padding: 16,
    justifyContent: 'space-between'
  },
  stageTitle: {
    color: '#fff',
    fontSize: 18,
    fontWeight: 'bold',
    textAlign: 'center',
    marginBottom: 15
  },
  enemySection: {
    backgroundColor: '#2a2a2a',
    padding: 15,
    borderRadius: 8,
    marginBottom: 20
  },
  playerSection: {
    backgroundColor: '#2a2a2a',
    padding: 15,
    borderRadius: 8,
    marginBottom: 20
  },
  enemyName: {
    color: '#ef4444',
    fontSize: 16,
    fontWeight: 'bold',
    marginBottom: 8
  },
  playerName: {
    color: '#22c55e',
    fontSize: 16,
    fontWeight: 'bold',
    marginBottom: 8
  },
  hpBar: {
    height: 20,
    backgroundColor: '#1a1a1a',
    borderRadius: 4,
    overflow: 'hidden',
    marginBottom: 5
  },
  hpFill: {
    height: '100%',
    backgroundColor: '#ef4444'
  },
  hpText: {
    color: '#aaa',
    fontSize: 12
  },
  logContainer: {
    flex: 1,
    backgroundColor: '#0a0a0a',
    padding: 10,
    borderRadius: 8,
    marginBottom: 20,
    maxHeight: 150
  },
  logEntry: {
    color: '#aaa',
    fontSize: 12,
    marginBottom: 5
  },
  skillButtonContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 10
  },
  skillButton: {
    flex: 1,
    minWidth: '45%',
    backgroundColor: '#6366f1',
    padding: 12,
    borderRadius: 8,
    alignItems: 'center'
  },
  skillButtonText: {
    color: '#fff',
    fontWeight: 'bold',
    fontSize: 12
  },
  skillDamage: {
    color: '#e0e7ff',
    fontSize: 10,
    marginTop: 3
  },
  fleeButton: {
    backgroundColor: '#ef4444'
  },
  continueButton: {
    backgroundColor: '#6366f1',
    padding: 15,
    borderRadius: 8,
    alignItems: 'center'
  },
  continueButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold'
  }
});
