import React, { useState, useEffect } from 'react';
import { View, Text, TouchableOpacity, StyleSheet, Alert, Vibration, ScrollView } from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';

export default function AllocateStatsScreen({ navigation }) {
  const [playerData, setPlayerData] = useState(null);
  const [allocations, setAllocations] = useState({
    힘: 0,
    지능: 0,
    외모: 0,
    체력: 0,
    운: 0
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadPlayerData();
  }, []);

  const loadPlayerData = async () => {
    try {
      const playerStr = await AsyncStorage.getItem('player_data');
      if (playerStr) {
        const player = JSON.parse(playerStr);
        setPlayerData(player);
        setLoading(false);
      }
    } catch (error) {
      Alert.alert('오류', '플레이어 데이터 로드 실패');
    }
  };

  const handleIncrement = (stat) => {
    const totalAllocated = Object.values(allocations).reduce((a, b) => a + b, 0);
    const availablePoints = playerData?.스탯포인트 || 0;

    if (totalAllocated < availablePoints) {
      setAllocations(prev => ({
        ...prev,
        [stat]: prev[stat] + 1
      }));
      Vibration.vibrate([0, 50]);
    } else {
      Alert.alert('경고', '사용 가능한 스탯 포인트가 없습니다.');
    }
  };

  const handleDecrement = (stat) => {
    if (allocations[stat] > 0) {
      setAllocations(prev => ({
        ...prev,
        [stat]: prev[stat] - 1
      }));
      Vibration.vibrate([0, 50]);
    }
  };

  const handleAllocate = async () => {
    const totalAllocated = Object.values(allocations).reduce((a, b) => a + b, 0);

    if (totalAllocated === 0) {
      Alert.alert('알림', '할당할 스탯을 선택해주세요.');
      return;
    }

    try {
      const updatedPlayer = { ...playerData };
      let allocatedCount = 0;

      // 각 스탯에 포인트 할당
      Object.entries(allocations).forEach(([stat, points]) => {
        if (points > 0) {
          const statMap = {
            힘: '힘',
            지능: '지능',
            외모: '외모',
            체력: '체력스탯',
            운: '운'
          };
          updatedPlayer[statMap[stat]] = (updatedPlayer[statMap[stat]] || 0) + points;
          allocatedCount += points;
        }
      });

      updatedPlayer.스탯포인트 = (updatedPlayer.스탯포인트 || 0) - allocatedCount;

      await AsyncStorage.setItem('player_data', JSON.stringify(updatedPlayer));
      setPlayerData(updatedPlayer);

      Vibration.vibrate([0, 100, 50, 100]);

      Alert.alert('성공! 🎉', `스탯을 할당했습니다.\n총 ${allocatedCount} 포인트 사용`, [
        {
          text: '확인',
          onPress: () => {
            setAllocations({
              힘: 0,
              지능: 0,
              외모: 0,
              체력: 0,
              운: 0
            });
            navigation.goBack();
          }
        }
      ]);
    } catch (error) {
      Alert.alert('오류', '스탯 할당 실패');
    }
  };

  const totalAllocated = Object.values(allocations).reduce((a, b) => a + b, 0);
  const availablePoints = playerData?.스탯포인트 || 0;

  if (loading || !playerData) {
    return (
      <View style={styles.container}>
        <Text style={styles.title}>로딩 중...</Text>
      </View>
    );
  }

  const stats = [
    { name: '힘', color: '#ef4444', desc: '공격력 증가' },
    { name: '지능', color: '#3b82f6', desc: '마나/스킬 증가' },
    { name: '외모', color: '#ec4899', desc: '매력도 증가' },
    { name: '체력', color: '#10b981', desc: '체력 증가' },
    { name: '운', color: '#f59e0b', desc: '운의 도움' }
  ];

  return (
    <ScrollView style={styles.container}>
      <Text style={styles.title}>📊 스탯 분배</Text>

      <View style={styles.pointsCard}>
        <View style={styles.pointsRow}>
          <Text style={styles.pointsLabel}>사용 가능한 포인트</Text>
          <Text style={styles.pointsValue}>{availablePoints}</Text>
        </View>
        <View style={styles.pointsRow}>
          <Text style={styles.pointsLabel}>할당할 포인트</Text>
          <Text style={styles.pointsAllocated}>{totalAllocated}</Text>
        </View>
      </View>

      {stats.map(stat => (
        <View key={stat.name} style={styles.statCard}>
          <View style={styles.statHeader}>
            <View>
              <Text style={styles.statName}>{stat.name}</Text>
              <Text style={styles.statDesc}>{stat.desc}</Text>
            </View>
            <View style={styles.currentStat}>
              <Text style={styles.currentStatLabel}>현재</Text>
              <Text style={[styles.currentStatValue, { color: stat.color }]}>
                {playerData[stat.name === '체력' ? '체력스탯' : stat.name] || 0}
              </Text>
            </View>
          </View>

          <View style={styles.allocatorContainer}>
            <TouchableOpacity
              style={styles.minusButton}
              onPress={() => handleDecrement(stat.name)}
            >
              <Text style={styles.buttonText}>−</Text>
            </TouchableOpacity>

            <View style={styles.allocatedBox}>
              <Text style={styles.allocatedText}>{allocations[stat.name]}</Text>
            </View>

            <TouchableOpacity
              style={[
                styles.plusButton,
                totalAllocated >= availablePoints && allocations[stat.name] === 0 && styles.plusButtonDisabled
              ]}
              onPress={() => handleIncrement(stat.name)}
              disabled={totalAllocated >= availablePoints && allocations[stat.name] === 0}
            >
              <Text style={styles.buttonText}>+</Text>
            </TouchableOpacity>

            <View style={[styles.previewBox, { borderLeftColor: stat.color }]}>
              <Text style={styles.previewLabel}>예상치</Text>
              <Text style={[styles.previewValue, { color: stat.color }]}>
                {(playerData[stat.name === '체력' ? '체력스탯' : stat.name] || 0) + allocations[stat.name]}
              </Text>
            </View>
          </View>
        </View>
      ))}

      <TouchableOpacity
        style={[styles.allocateButton, totalAllocated === 0 && styles.allocateButtonDisabled]}
        onPress={handleAllocate}
        disabled={totalAllocated === 0}
      >
        <Text style={styles.allocateButtonText}>
          ✨ {totalAllocated > 0 ? `확인 (${totalAllocated} 포인트)` : '할당할 포인트를 선택하세요'}
        </Text>
      </TouchableOpacity>

      <TouchableOpacity
        style={styles.cancelButton}
        onPress={() => navigation.goBack()}
      >
        <Text style={styles.cancelButtonText}>취소</Text>
      </TouchableOpacity>

      <View style={styles.infoBox}>
        <Text style={styles.infoTitle}>💡 스탯 분배 팁</Text>
        <Text style={styles.infoText}>• 스탯 포인트는 레벨업시 매번 지급됩니다</Text>
        <Text style={styles.infoText}>• 각 스탯은 다양한 이점을 제공합니다</Text>
        <Text style={styles.infoText}>• 전략적으로 분배해서 캐릭터를 강화하세요!</Text>
      </View>
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
    marginBottom: 20
  },
  pointsCard: {
    backgroundColor: '#2a2a2a',
    padding: 16,
    borderRadius: 8,
    marginBottom: 20,
    borderLeftWidth: 4,
    borderLeftColor: '#6366f1'
  },
  pointsRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 10
  },
  pointsLabel: {
    color: '#aaa',
    fontSize: 14
  },
  pointsValue: {
    color: '#6366f1',
    fontSize: 18,
    fontWeight: 'bold'
  },
  pointsAllocated: {
    color: '#22c55e',
    fontSize: 18,
    fontWeight: 'bold'
  },
  statCard: {
    backgroundColor: '#2a2a2a',
    padding: 16,
    borderRadius: 8,
    marginBottom: 12,
    borderWidth: 1,
    borderColor: '#3a3a3a'
  },
  statHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12
  },
  statName: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
    marginBottom: 4
  },
  statDesc: {
    color: '#888',
    fontSize: 12
  },
  currentStat: {
    alignItems: 'center'
  },
  currentStatLabel: {
    color: '#888',
    fontSize: 11,
    marginBottom: 4
  },
  currentStatValue: {
    fontSize: 18,
    fontWeight: 'bold'
  },
  allocatorContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 10
  },
  minusButton: {
    backgroundColor: '#3a3a3a',
    width: 40,
    height: 40,
    borderRadius: 6,
    justifyContent: 'center',
    alignItems: 'center'
  },
  plusButton: {
    backgroundColor: '#6366f1',
    width: 40,
    height: 40,
    borderRadius: 6,
    justifyContent: 'center',
    alignItems: 'center'
  },
  plusButtonDisabled: {
    backgroundColor: '#3a3a3a',
    opacity: 0.5
  },
  buttonText: {
    color: '#fff',
    fontSize: 24,
    fontWeight: 'bold'
  },
  allocatedBox: {
    backgroundColor: '#1a1a1a',
    paddingHorizontal: 12,
    paddingVertical: 8,
    borderRadius: 6,
    minWidth: 45,
    alignItems: 'center'
  },
  allocatedText: {
    color: '#fff',
    fontSize: 18,
    fontWeight: 'bold'
  },
  previewBox: {
    flex: 1,
    backgroundColor: '#1a1a1a',
    paddingHorizontal: 12,
    paddingVertical: 8,
    borderRadius: 6,
    borderLeftWidth: 3,
    alignItems: 'center'
  },
  previewLabel: {
    color: '#888',
    fontSize: 11,
    marginBottom: 4
  },
  previewValue: {
    fontSize: 16,
    fontWeight: 'bold'
  },
  allocateButton: {
    backgroundColor: '#6366f1',
    paddingVertical: 16,
    borderRadius: 8,
    alignItems: 'center',
    marginTop: 20,
    marginBottom: 10
  },
  allocateButtonDisabled: {
    backgroundColor: '#3a3a3a'
  },
  allocateButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold'
  },
  cancelButton: {
    backgroundColor: '#3a3a3a',
    paddingVertical: 12,
    borderRadius: 8,
    alignItems: 'center',
    marginBottom: 20
  },
  cancelButtonText: {
    color: '#aaa',
    fontSize: 14,
    fontWeight: '600'
  },
  infoBox: {
    backgroundColor: '#2a2a2a',
    padding: 12,
    borderRadius: 8,
    marginBottom: 30
  },
  infoTitle: {
    color: '#fff',
    fontSize: 13,
    fontWeight: 'bold',
    marginBottom: 8
  },
  infoText: {
    color: '#888',
    fontSize: 12,
    marginBottom: 4,
    lineHeight: 16
  }
});
