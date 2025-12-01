import React, { useState, useEffect } from 'react';
import { View, Text, TouchableOpacity, StyleSheet, Alert, ScrollView, ActivityIndicator } from 'react-native';
import { adventureAPI, skillsAPI } from '../services/api';

export default function AdventureScreen({ navigation }) {
  const [stages, setStages] = useState([]);
  const [selectedStage, setSelectedStage] = useState(null);
  const [currentSkills, setCurrentSkills] = useState([]);
  const [loading, setLoading] = useState(true);
  const [battleActive, setBattleActive] = useState(false);
  const [battleState, setBattleState] = useState(null);

  useEffect(() => {
    loadAdventureData();
  }, []);

  const loadAdventureData = async () => {
    setLoading(true);
    try {
      const [adventureRes, skillsRes] = await Promise.all([
        adventureAPI.select(),
        skillsAPI.list()
      ]);

      if (adventureRes.data.success) {
        setStages(adventureRes.data.data.stages || []);
      }
      if (skillsRes.data.success) {
        setCurrentSkills(skillsRes.data.data.current_skills || []);
      }
    } catch (error) {
      Alert.alert('오류', '모험 데이터 로드 실패');
    } finally {
      setLoading(false);
    }
  };

  const handleStartBattle = async () => {
    if (!selectedStage) {
      Alert.alert('알림', '스테이지를 선택해주세요.');
      return;
    }

    setBattleActive(true);
    try {
      const response = await adventureAPI.start(selectedStage.stage_id, []);
      if (response.data.success) {
        setBattleState({
          battle_id: response.data.data.battle_id,
          enemy: response.data.data.enemy,
          playerHP: response.data.data.player_hp,
          enemyHP: response.data.data.enemy_hp,
          turn: 0,
          log: ['전투 시작!']
        });
      }
    } catch (error) {
      Alert.alert('오류', '전투 시작 실패');
      setBattleActive(false);
    }
  };

  const handleUseSkill = async (skillName) => {
    if (!battleState) return;

    try {
      const response = await adventureAPI.action(battleState.battle_id, skillName);
      
      if (response.data.success) {
        const newLog = [...battleState.log];
        newLog.push(`플레이어: ${skillName} 사용!`);
        
        if (response.data.data.enemy_hp <= 0) {
          newLog.push('적을 물리쳤습니다! 전투 승리!');
          setBattleState({
            ...battleState,
            log: newLog,
            victory: true
          });
        } else if (response.data.data.player_hp <= 0) {
          newLog.push('플레이어가 쓰러졌습니다. 전투 패배!');
          setBattleState({
            ...battleState,
            log: newLog,
            defeat: true
          });
        } else {
          // 적의 공격
          newLog.push(`적: 기본 공격 ${response.data.data.damage || 5} 데미지!`);
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
        {/* 적 정보 */}
        <View style={styles.enemySection}>
          <Text style={styles.enemyName}>{battleState.enemy.name}</Text>
          <View style={styles.hpBar}>
            <View
              style={[
                styles.hpFill,
                {
                  width: `${Math.max(0, (battleState.enemyHP / battleState.enemy.hp) * 100)}%`
                }
              ]}
            />
          </View>
          <Text style={styles.hpText}>
            {battleState.enemyHP} / {battleState.enemy.hp}
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
            <Text style={styles.stageDifficulty}>난이도: {stage.difficulty}</Text>
            <Text style={styles.stageEnemy}>
              {stage.enemy_count}마리 전투
            </Text>
          </TouchableOpacity>
        ))}
      </View>

      {selectedStage && (
        <View style={styles.actionContainer}>
          <TouchableOpacity
            style={styles.startButton}
            onPress={handleStartBattle}
          >
            <Text style={styles.startButtonText}>전투 시작</Text>
          </TouchableOpacity>
        </View>
      )}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#1a1a1a',
    padding: 20
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
  actionContainer: {
    gap: 10
  },
  startButton: {
    backgroundColor: '#6366f1',
    padding: 15,
    borderRadius: 8,
    alignItems: 'center'
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
    padding: 20,
    justifyContent: 'space-between'
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
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 10
  },
  playerName: {
    color: '#22c55e',
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 10
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
