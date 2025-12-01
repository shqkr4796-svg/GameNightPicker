import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  ScrollView,
  Alert,
  ActivityIndicator,
  Vibration,
  FlatList
} from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';

export default function FusionScreen({ navigation }) {
  const [compendium, setCompendium] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedMonsters, setSelectedMonsters] = useState([]);
  const [selectedRarity, setSelectedRarity] = useState(null);
  const [fusionResult, setFusionResult] = useState(null);

  useEffect(() => {
    loadCompendium();
  }, []);

  const loadCompendium = async () => {
    try {
      const playerStr = await AsyncStorage.getItem('player_data');
      if (playerStr) {
        const player = JSON.parse(playerStr);
        setCompendium(player.compendium || []);
      }
    } catch (error) {
      console.log('도감 로드 실패');
    } finally {
      setLoading(false);
    }
  };

  const rarityOrder = ['레어', '에픽', '유니크', '레전드리'];

  // 등급별로 몬스터 분류
  const monstersByRarity = rarityOrder.reduce((acc, rarity) => {
    acc[rarity] = compendium.filter(m => m.rarity === rarity);
    return acc;
  }, {});

  const handleSelectMonster = (index, monster) => {
    // 이미 선택된 몬스터면 제거
    if (selectedMonsters.some(m => m.index === index)) {
      setSelectedMonsters(selectedMonsters.filter(m => m.index !== index));
      return;
    }

    // 3개 이미 선택됨
    if (selectedMonsters.length >= 3) {
      Alert.alert('알림', '최대 3마리까지만 선택할 수 있습니다.');
      return;
    }

    // 다른 등급 선택 시도
    if (selectedRarity && selectedRarity !== monster.rarity) {
      Alert.alert('알림', '같은 등급의 몬스터만 선택할 수 있습니다.');
      return;
    }

    setSelectedRarity(monster.rarity);
    setSelectedMonsters([...selectedMonsters, { index, monster }]);
    Vibration.vibrate([0, 50]);
  };

  const handlePerformFusion = async () => {
    if (selectedMonsters.length !== 3) {
      Alert.alert('알림', '3마리를 정확히 선택해주세요.');
      return;
    }

    setLoading(true);
    try {
      // API 호출 또는 로컬 로직 실행
      const result = performFusion(selectedMonsters, selectedRarity);

      Vibration.vibrate([0, 100, 50, 100, 50, 100]);

      // 결과 표시
      setFusionResult(result);

      // 플레이어 데이터 업데이트
      const playerStr = await AsyncStorage.getItem('player_data');
      if (playerStr) {
        const player = JSON.parse(playerStr);

        // 선택된 몬스터 제거 (뒤에서부터)
        const newCompendium = player.compendium.filter(
          (_, idx) => !selectedMonsters.some(m => m.index === idx)
        );

        // 합성 결과 추가
        newCompendium.push(result.resultMonster);

        player.compendium = newCompendium;
        await AsyncStorage.setItem('player_data', JSON.stringify(player));
      }

      // 상태 초기화
      setSelectedMonsters([]);
      setSelectedRarity(null);

      // 결과 표시 후 2초 뒤 목록 새로고침
      setTimeout(() => {
        loadCompendium();
        setFusionResult(null);
      }, 3000);
    } catch (error) {
      Alert.alert('오류', '합성 중 오류가 발생했습니다.');
    } finally {
      setLoading(false);
    }
  };

  const performFusion = (selected, rarity) => {
    const upgradeChances = {
      '레어': 0.3,
      '에픽': 0.2,
      '유니크': 0.1
    };

    const isMythicAttempt = rarity === '레전드리';
    const upgradeChance = upgradeChances[rarity] || 0;

    let resultRarity = rarity;
    let isMythic = false;
    let isUpgraded = false;

    if (isMythicAttempt) {
      // 신화급 시도: 30% 확률
      if (Math.random() < 0.3) {
        resultRarity = '신화급';
        isMythic = true;
        isUpgraded = true;
      }
    } else {
      // 다른 등급: 확률에 따라 업그레이드
      if (Math.random() < upgradeChance) {
        const rarities = ['레어', '에픽', '유니크', '레전드리'];
        const currentIndex = rarities.indexOf(rarity);
        if (currentIndex < rarities.length - 1) {
          resultRarity = rarities[currentIndex + 1];
          isUpgraded = true;
        }
      }
    }

    // 몬스터 데이터 (간단한 예시)
    const resultMonster = {
      id: `fusion_${Date.now()}`,
      name: `합성 몬스터`,
      rarity: resultRarity,
      attack: Math.floor(Math.random() * 100) + 50,
      hp: Math.floor(Math.random() * 150) + 100,
      captured_date: new Date().toISOString()
    };

    return {
      resultMonster,
      isMythic,
      isUpgraded,
      message: isMythic
        ? '축하합니다! 신화급 몬스터를 획득했습니다! 🎉'
        : isUpgraded
        ? `축하합니다! ${resultRarity} 몬스터를 획득했습니다!`
        : `합성 성공! ${resultRarity} 몬스터를 획득했습니다.`
    };
  };

  if (loading) {
    return (
      <View style={styles.container}>
        <ActivityIndicator color="#6366f1" size="large" />
      </View>
    );
  }

  // 합성 결과 표시
  if (fusionResult) {
    return (
      <View style={styles.container}>
        <View style={[styles.resultCard, fusionResult.isMythic && styles.resultMythic]}>
          <Text style={styles.resultIcon}>✨</Text>
          <Text style={styles.resultTitle}>
            {fusionResult.isMythic ? '신화급!' : '합성 성공!'}
          </Text>
          <Text style={styles.resultMonsterName}>
            {fusionResult.resultMonster.name}
          </Text>
          <View style={styles.resultStatsContainer}>
            <View style={styles.resultStat}>
              <Text style={styles.resultStatLabel}>등급</Text>
              <Text style={styles.resultStatValue}>
                {fusionResult.resultMonster.rarity}
              </Text>
            </View>
            <View style={styles.resultStat}>
              <Text style={styles.resultStatLabel}>공격력</Text>
              <Text style={styles.resultStatValue}>
                {fusionResult.resultMonster.attack}
              </Text>
            </View>
            <View style={styles.resultStat}>
              <Text style={styles.resultStatLabel}>체력</Text>
              <Text style={styles.resultStatValue}>
                {fusionResult.resultMonster.hp}
              </Text>
            </View>
          </View>
          <Text style={styles.resultMessage}>{fusionResult.message}</Text>
        </View>
      </View>
    );
  }

  // 도감이 비어있음
  if (compendium.length === 0) {
    return (
      <View style={styles.container}>
        <View style={styles.emptyState}>
          <Text style={styles.emptyIcon}>📚</Text>
          <Text style={styles.emptyText}>도감이 비어있습니다</Text>
          <Text style={styles.emptySubText}>던전에서 몬스터를 포획해주세요</Text>
          <TouchableOpacity
            style={styles.emptyButton}
            onPress={() => navigation.navigate('Dungeon')}
          >
            <Text style={styles.emptyButtonText}>던전으로 가기</Text>
          </TouchableOpacity>
        </View>
      </View>
    );
  }

  return (
    <ScrollView style={styles.container}>
      <Text style={styles.title}>✨ 몬스터 합성</Text>

      {/* 합성 규칙 */}
      <View style={styles.rulesCard}>
        <Text style={styles.rulesTitle}>💡 합성 규칙</Text>
        <Text style={styles.ruleItem}>• 같은 등급 3마리를 선택해야 합니다</Text>
        <Text style={styles.ruleItem}>• 레어: 30% 확률로 에픽 획득</Text>
        <Text style={styles.ruleItem}>• 에픽: 20% 확률로 유니크 획득</Text>
        <Text style={styles.ruleItem}>• 유니크: 10% 확률로 레전드리 획득</Text>
        <Text style={styles.ruleItem}>• 레전드리: 30% 확률로 신화급 획득</Text>
      </View>

      {/* 선택 상태 */}
      <View style={styles.selectionStatus}>
        <Text style={styles.selectionText}>
          선택: {selectedMonsters.length}/3
        </Text>
        {selectedRarity && (
          <Text style={styles.selectionRarity}>등급: {selectedRarity}</Text>
        )}
      </View>

      {/* 등급별 몬스터 선택 */}
      {rarityOrder.map(rarity => {
        const monsters = monstersByRarity[rarity];
        if (monsters.length === 0) return null;

        return (
          <View key={rarity} style={styles.raritySection}>
            <View style={[styles.rarityHeader, styles[`rarity_${rarity}`]]}>
              <Text style={styles.rarityTitle}>
                ⭐ {rarity} ({monsters.length}마리)
              </Text>
            </View>

            <View style={styles.monsterGrid}>
              {monsters.map((monster, idx) => {
                const isSelected = selectedMonsters.some(
                  m => m.monster.id === monster.id
                );
                return (
                  <TouchableOpacity
                    key={`${rarity}_${idx}`}
                    style={[
                      styles.monsterCard,
                      isSelected && styles.monsterCardSelected
                    ]}
                    onPress={() =>
                      handleSelectMonster(
                        compendium.findIndex(m => m.id === monster.id),
                        monster
                      )
                    }
                  >
                    <View style={styles.monsterImagePlaceholder}>
                      <Text style={styles.monsterEmoji}>🐉</Text>
                    </View>
                    <Text style={styles.monsterName}>{monster.name}</Text>
                    <Text style={styles.monsterStats}>
                      ⚔️ {monster.attack}
                    </Text>
                    <Text style={styles.monsterStats}>❤️ {monster.hp}</Text>
                    {isSelected && (
                      <View style={styles.selectedBadge}>
                        <Text style={styles.selectedBadgeText}>✓</Text>
                      </View>
                    )}
                  </TouchableOpacity>
                );
              })}
            </View>
          </View>
        );
      })}

      {/* 합성 버튼 */}
      <TouchableOpacity
        style={[
          styles.fusionButton,
          selectedMonsters.length === 3 ? styles.fusionButtonActive : styles.fusionButtonDisabled
        ]}
        onPress={handlePerformFusion}
        disabled={selectedMonsters.length !== 3}
      >
        <Text style={styles.fusionButtonText}>
          {selectedMonsters.length === 3
            ? '✨ 몬스터 합성 실행'
            : '✨ 3마리를 선택하세요'}
        </Text>
      </TouchableOpacity>

      {/* 선택 초기화 버튼 */}
      {selectedMonsters.length > 0 && (
        <TouchableOpacity
          style={styles.resetButton}
          onPress={() => {
            setSelectedMonsters([]);
            setSelectedRarity(null);
            Vibration.vibrate([0, 50]);
          }}
        >
          <Text style={styles.resetButtonText}>선택 초기화</Text>
        </TouchableOpacity>
      )}

      <View style={styles.spacer} />
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
    marginBottom: 15
  },
  rulesCard: {
    backgroundColor: '#2a2a2a',
    padding: 15,
    borderRadius: 8,
    marginBottom: 20,
    borderLeftWidth: 4,
    borderLeftColor: '#fbbf24'
  },
  rulesTitle: {
    color: '#fbbf24',
    fontSize: 14,
    fontWeight: '600',
    marginBottom: 10
  },
  ruleItem: {
    color: '#aaa',
    fontSize: 12,
    marginBottom: 6,
    lineHeight: 16
  },
  selectionStatus: {
    backgroundColor: '#2a2a2a',
    padding: 12,
    borderRadius: 8,
    marginBottom: 20,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center'
  },
  selectionText: {
    color: '#6366f1',
    fontSize: 14,
    fontWeight: '600'
  },
  selectionRarity: {
    backgroundColor: '#6366f1',
    color: '#fff',
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 4,
    fontSize: 12,
    fontWeight: '600'
  },
  raritySection: {
    marginBottom: 20
  },
  rarityHeader: {
    padding: 12,
    borderRadius: 8,
    marginBottom: 12
  },
  rarity_레어: {
    backgroundColor: '#1e5631'
  },
  rarity_에픽: {
    backgroundColor: '#1e40af'
  },
  rarity_유니크: {
    backgroundColor: '#78350f'
  },
  rarity_레전드리: {
    backgroundColor: '#7f1d1d'
  },
  rarityTitle: {
    color: '#fff',
    fontSize: 14,
    fontWeight: '600'
  },
  monsterGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 12
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
  monsterCardSelected: {
    borderColor: '#fbbf24',
    backgroundColor: '#3a3a3a'
  },
  monsterImagePlaceholder: {
    width: 60,
    height: 60,
    backgroundColor: '#1a1a1a',
    borderRadius: 6,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 8
  },
  monsterEmoji: {
    fontSize: 32
  },
  monsterName: {
    color: '#fff',
    fontSize: 11,
    fontWeight: '600',
    textAlign: 'center',
    marginBottom: 6
  },
  monsterStats: {
    color: '#aaa',
    fontSize: 10,
    marginBottom: 2
  },
  selectedBadge: {
    position: 'absolute',
    top: 6,
    right: 6,
    backgroundColor: '#fbbf24',
    width: 24,
    height: 24,
    borderRadius: 12,
    justifyContent: 'center',
    alignItems: 'center'
  },
  selectedBadgeText: {
    color: '#1a1a1a',
    fontSize: 14,
    fontWeight: 'bold'
  },
  fusionButton: {
    paddingVertical: 14,
    borderRadius: 8,
    alignItems: 'center',
    marginBottom: 12,
    marginTop: 20
  },
  fusionButtonActive: {
    backgroundColor: '#fbbf24'
  },
  fusionButtonDisabled: {
    backgroundColor: '#3a3a3a'
  },
  fusionButtonText: {
    color: fusionButtonActive ? '#1a1a1a' : '#aaa',
    fontSize: 14,
    fontWeight: 'bold'
  },
  resetButton: {
    paddingVertical: 10,
    borderRadius: 8,
    alignItems: 'center',
    backgroundColor: '#3a3a3a',
    marginBottom: 20
  },
  resetButtonText: {
    color: '#aaa',
    fontSize: 12,
    fontWeight: '600'
  },
  resultCard: {
    backgroundColor: '#2a2a2a',
    padding: 30,
    borderRadius: 12,
    alignItems: 'center',
    marginTop: 60,
    borderWidth: 2,
    borderColor: '#6366f1'
  },
  resultMythic: {
    borderColor: '#fbbf24',
    backgroundColor: '#3a3a3a'
  },
  resultIcon: {
    fontSize: 60,
    marginBottom: 15
  },
  resultTitle: {
    color: '#fff',
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 10
  },
  resultMonsterName: {
    color: '#fbbf24',
    fontSize: 20,
    fontWeight: '600',
    marginBottom: 20
  },
  resultStatsContainer: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    width: '100%',
    marginBottom: 20,
    backgroundColor: '#1a1a1a',
    padding: 15,
    borderRadius: 8
  },
  resultStat: {
    alignItems: 'center'
  },
  resultStatLabel: {
    color: '#aaa',
    fontSize: 12,
    marginBottom: 5
  },
  resultStatValue: {
    color: '#6366f1',
    fontSize: 16,
    fontWeight: 'bold'
  },
  resultMessage: {
    color: '#fff',
    fontSize: 14,
    textAlign: 'center',
    fontStyle: 'italic'
  },
  emptyState: {
    justifyContent: 'center',
    alignItems: 'center',
    paddingVertical: 60
  },
  emptyIcon: {
    fontSize: 48,
    marginBottom: 15
  },
  emptyText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
    marginBottom: 5
  },
  emptySubText: {
    color: '#aaa',
    fontSize: 12,
    marginBottom: 20
  },
  emptyButton: {
    backgroundColor: '#6366f1',
    paddingVertical: 10,
    paddingHorizontal: 20,
    borderRadius: 6
  },
  emptyButtonText: {
    color: '#fff',
    fontWeight: 'bold'
  },
  spacer: {
    height: 30
  }
});
