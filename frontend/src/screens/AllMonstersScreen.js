import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  FlatList,
  Alert,
  ActivityIndicator,
  Modal,
  Vibration,
  ScrollView
} from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';

export default function AllMonstersScreen({ navigation }) {
  const [allMonsters, setAllMonsters] = useState([]);
  const [filteredMonsters, setFilteredMonsters] = useState([]);
  const [capturedMonsterIds, setCapturedMonsterIds] = useState(new Set());
  const [loading, setLoading] = useState(true);
  const [selectedRarity, setSelectedRarity] = useState('all');
  const [selectedMonster, setSelectedMonster] = useState(null);
  const [modalVisible, setModalVisible] = useState(false);

  const rarities = ['all', 'Rare', 'Epic', 'Unique', 'Legendary', 'Mythic'];
  const rarityLabels = {
    all: '전체 (53)',
    Rare: '레어 (12)',
    Epic: '에픽 (12)',
    Unique: '유니크 (12)',
    Legendary: '레전드리 (14)',
    Mythic: '신화급 (3)'
  };

  useEffect(() => {
    loadAllMonsters();
  }, []);

  useEffect(() => {
    filterMonsters(selectedRarity);
  }, [selectedRarity, allMonsters]);

  const loadAllMonsters = async () => {
    setLoading(true);
    try {
      // 플레이어 데이터에서 포획한 몬스터 확인
      const playerStr = await AsyncStorage.getItem('player_data');
      if (playerStr) {
        const player = JSON.parse(playerStr);
        const captured = new Set(
          (player.compendium || []).map(m => m.id)
        );
        setCapturedMonsterIds(captured);
      }

      // 샘플 몬스터 데이터 (실제로는 API에서 가져와야 함)
      const sampleMonsters = generateSampleMonsters();
      setAllMonsters(sampleMonsters);
    } catch (error) {
      console.log('몬스터 데이터 로드 실패');
      Alert.alert('오류', '몬스터 데이터 로드 실패');
    } finally {
      setLoading(false);
    }
  };

  const generateSampleMonsters = () => {
    // 간단한 샘플 데이터 (실제로는 API에서 가져옴)
    const monsters = [];
    
    // 레어 12마리
    for (let i = 1; i <= 12; i++) {
      monsters.push({
        id: `rare_${i}`,
        name: `레어몬스터${i}`,
        rarity: 'Rare',
        attack: `${5 + i}_${10 + i}`,
        hp: `${10 + i * 2}_${20 + i * 2}`,
        description: '낮은 난이도의 몬스터입니다.'
      });
    }

    // 에픽 12마리
    for (let i = 1; i <= 12; i++) {
      monsters.push({
        id: `epic_${i}`,
        name: `에픽몬스터${i}`,
        rarity: 'Epic',
        attack: `${15 + i}_${25 + i}`,
        hp: `${30 + i * 2}_${50 + i * 2}`,
        description: '중간 난이도의 몬스터입니다.'
      });
    }

    // 유니크 12마리
    for (let i = 1; i <= 12; i++) {
      monsters.push({
        id: `unique_${i}`,
        name: `유니크몬스터${i}`,
        rarity: 'Unique',
        attack: `${30 + i}_${45 + i}`,
        hp: `${60 + i * 2}_${90 + i * 2}`,
        description: '높은 난이도의 몬스터입니다.'
      });
    }

    // 레전드리 14마리
    for (let i = 1; i <= 14; i++) {
      monsters.push({
        id: `legendary_${i}`,
        name: `레전드리몬스터${i}`,
        rarity: 'Legendary',
        attack: `${50 + i}_${70 + i}`,
        hp: `${100 + i * 3}_${150 + i * 3}`,
        description: '매우 높은 난이도의 최상위 몬스터입니다.'
      });
    }

    // 신화급 3마리
    for (let i = 1; i <= 3; i++) {
      monsters.push({
        id: `mythic_${i}`,
        name: `신화몬스터${i}`,
        rarity: 'Mythic',
        attack: `${80 + i * 5}_${100 + i * 5}`,
        hp: `${200 + i * 10}_${300 + i * 10}`,
        description: '합성으로만 획득 가능한 전설의 몬스터입니다!'
      });
    }

    return monsters;
  };

  const filterMonsters = (rarity) => {
    if (rarity === 'all') {
      setFilteredMonsters(allMonsters);
    } else {
      setFilteredMonsters(allMonsters.filter(m => m.rarity === rarity));
    }
  };

  const handleMonsterPress = (monster) => {
    playRaritySound(monster.rarity);
    setSelectedMonster(monster);
    setModalVisible(true);
  };

  const playRaritySound = (rarity) => {
    if (rarity === 'Rare') {
      Vibration.vibrate([0, 100]);
    } else if (rarity === 'Epic') {
      Vibration.vibrate([0, 50, 50, 100]);
    } else if (rarity === 'Unique') {
      Vibration.vibrate([0, 100, 50, 50, 100]);
    } else if (rarity === 'Legendary') {
      Vibration.vibrate([0, 200, 100, 200]);
    } else if (rarity === 'Mythic') {
      Vibration.vibrate([0, 150, 100, 150, 100, 150]);
    }
  };

  const getRarityColor = (rarity) => {
    const colors = {
      Rare: '#10b981',
      Epic: '#3b82f6',
      Unique: '#f59e0b',
      Legendary: '#dc2626',
      Mythic: '#06b6d4'
    };
    return colors[rarity] || '#666';
  };

  const getRarityBgColor = (rarity) => {
    const colors = {
      Rare: '#1e5631',
      Epic: '#1e40af',
      Unique: '#78350f',
      Legendary: '#7f1d1d',
      Mythic: '#0d4d6d'
    };
    return colors[rarity] || '#1a1a1a';
  };

  const isCaptured = (monsterId) => capturedMonsterIds.has(monsterId);

  const renderMonsterCard = ({ item }) => (
    <TouchableOpacity
      style={[
        styles.monsterCard,
        {
          borderLeftColor: getRarityColor(item.rarity),
          backgroundColor: getRarityBgColor(item.rarity)
        }
      ]}
      onPress={() => handleMonsterPress(item)}
    >
      <View style={styles.monsterImagePlaceholder}>
        {isCaptured(item.id) ? (
          <Text style={styles.monsterEmoji}>🐉</Text>
        ) : (
          <Text style={styles.lockedEmoji}>🔒</Text>
        )}
      </View>
      <Text
        style={styles.monsterName}
        numberOfLines={2}
      >
        {item.name}
      </Text>
      <Text
        style={[
          styles.rarity,
          { color: getRarityColor(item.rarity) }
        ]}
      >
        {item.rarity === 'Rare'
          ? '레어'
          : item.rarity === 'Epic'
          ? '에픽'
          : item.rarity === 'Unique'
          ? '유니크'
          : item.rarity === 'Legendary'
          ? '레전드리'
          : '신화급'}
      </Text>
      {!isCaptured(item.id) && (
        <View style={styles.notCapturedBadge}>
          <Text style={styles.notCapturedText}>미포획</Text>
        </View>
      )}
    </TouchableOpacity>
  );

  if (loading) {
    return (
      <View style={styles.container}>
        <ActivityIndicator color="#6366f1" size="large" />
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <Text style={styles.title}>📖 모든 몬스터</Text>

      {/* 필터 버튼 */}
      <ScrollView
        horizontal
        showsHorizontalScrollIndicator={false}
        style={styles.filterContainer}
      >
        {rarities.map(rarity => (
          <TouchableOpacity
            key={rarity}
            style={[
              styles.filterButton,
              selectedRarity === rarity && styles.filterButtonActive,
              selectedRarity === rarity && {
                backgroundColor: getRarityColor(rarity)
              }
            ]}
            onPress={() => setSelectedRarity(rarity)}
          >
            <Text
              style={[
                styles.filterButtonText,
                selectedRarity === rarity && styles.filterButtonTextActive
              ]}
            >
              {rarityLabels[rarity]}
            </Text>
          </TouchableOpacity>
        ))}
      </ScrollView>

      {/* 몬스터 그리드 */}
      {filteredMonsters.length === 0 ? (
        <View style={styles.emptyContainer}>
          <Text style={styles.emptyText}>해당 등급 몬스터가 없습니다</Text>
        </View>
      ) : (
        <FlatList
          data={filteredMonsters}
          renderItem={renderMonsterCard}
          keyExtractor={item => item.id}
          numColumns={2}
          columnWrapperStyle={styles.columnWrapper}
          contentContainerStyle={styles.gridContainer}
          scrollEnabled={true}
        />
      )}

      {/* 몬스터 상세 정보 모달 */}
      <Modal
        visible={modalVisible}
        transparent={true}
        animationType="slide"
        onRequestClose={() => setModalVisible(false)}
      >
        <View style={styles.modalContainer}>
          <View style={styles.modalContent}>
            <TouchableOpacity
              style={styles.closeButton}
              onPress={() => setModalVisible(false)}
            >
              <Text style={styles.closeButtonText}>✕</Text>
            </TouchableOpacity>

            {selectedMonster && (
              <>
                <View
                  style={[
                    styles.modalHeader,
                    { backgroundColor: getRarityColor(selectedMonster.rarity) }
                  ]}
                >
                  <Text style={styles.modalTitle}>{selectedMonster.name}</Text>
                  <Text style={styles.modalRarity}>
                    {selectedMonster.rarity === 'Rare'
                      ? '레어'
                      : selectedMonster.rarity === 'Epic'
                      ? '에픽'
                      : selectedMonster.rarity === 'Unique'
                      ? '유니크'
                      : selectedMonster.rarity === 'Legendary'
                      ? '레전드리'
                      : '신화급'}
                  </Text>
                </View>

                <View style={styles.modalImagePlaceholder}>
                  {isCaptured(selectedMonster.id) ? (
                    <Text style={styles.modalEmoji}>🐉</Text>
                  ) : (
                    <>
                      <Text style={styles.lockedEmoji}>🔒</Text>
                      <Text style={styles.notCapturedMessage}>
                        아직 포획하지 않은 몬스터입니다
                      </Text>
                    </>
                  )}
                </View>

                <View style={styles.modalStats}>
                  <View style={styles.modalStatItem}>
                    <Text style={styles.modalStatLabel}>공격력</Text>
                    <Text style={styles.modalStatValue}>
                      {selectedMonster.attack}
                    </Text>
                  </View>
                  <View style={styles.modalStatItem}>
                    <Text style={styles.modalStatLabel}>체력</Text>
                    <Text style={styles.modalStatValue}>
                      {selectedMonster.hp}
                    </Text>
                  </View>
                </View>

                <View style={styles.modalDescription}>
                  <Text style={styles.descriptionLabel}>정보</Text>
                  <Text style={styles.descriptionText}>
                    {selectedMonster.description}
                  </Text>
                </View>

                <TouchableOpacity
                  style={styles.closeModalButton}
                  onPress={() => setModalVisible(false)}
                >
                  <Text style={styles.closeModalButtonText}>닫기</Text>
                </TouchableOpacity>
              </>
            )}
          </View>
        </View>
      </Modal>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#1a1a1a',
    paddingHorizontal: 12,
    paddingTop: 16
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#fff',
    marginBottom: 12
  },
  filterContainer: {
    marginBottom: 12,
    paddingVertical: 8
  },
  filterButton: {
    paddingHorizontal: 12,
    paddingVertical: 6,
    marginRight: 8,
    borderRadius: 6,
    backgroundColor: '#2a2a2a',
    borderWidth: 1,
    borderColor: '#3a3a3a'
  },
  filterButtonActive: {
    borderColor: 'transparent'
  },
  filterButtonText: {
    color: '#aaa',
    fontSize: 11,
    fontWeight: '600'
  },
  filterButtonTextActive: {
    color: '#fff'
  },
  gridContainer: {
    paddingBottom: 20
  },
  columnWrapper: {
    justifyContent: 'space-between',
    marginBottom: 8
  },
  monsterCard: {
    width: '48%',
    backgroundColor: '#2a2a2a',
    borderRadius: 8,
    padding: 12,
    borderLeftWidth: 4,
    alignItems: 'center'
  },
  monsterImagePlaceholder: {
    width: 60,
    height: 60,
    backgroundColor: '#1a1a1a',
    borderRadius: 8,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 8
  },
  monsterEmoji: {
    fontSize: 32
  },
  lockedEmoji: {
    fontSize: 32
  },
  monsterName: {
    color: '#fff',
    fontSize: 12,
    fontWeight: '600',
    textAlign: 'center',
    marginBottom: 4
  },
  rarity: {
    fontSize: 10,
    fontWeight: 'bold',
    marginBottom: 4
  },
  notCapturedBadge: {
    position: 'absolute',
    top: 8,
    right: 8,
    backgroundColor: '#3a3a3a',
    paddingHorizontal: 6,
    paddingVertical: 2,
    borderRadius: 3
  },
  notCapturedText: {
    color: '#aaa',
    fontSize: 8,
    fontWeight: '600'
  },
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center'
  },
  emptyText: {
    color: '#aaa',
    fontSize: 14
  },
  modalContainer: {
    flex: 1,
    backgroundColor: 'rgba(0, 0, 0, 0.8)',
    justifyContent: 'center',
    alignItems: 'center'
  },
  modalContent: {
    width: '90%',
    maxHeight: '80%',
    backgroundColor: '#2a2a2a',
    borderRadius: 12,
    overflow: 'hidden'
  },
  closeButton: {
    position: 'absolute',
    top: 12,
    right: 12,
    zIndex: 10,
    width: 32,
    height: 32,
    borderRadius: 16,
    backgroundColor: '#1a1a1a',
    justifyContent: 'center',
    alignItems: 'center'
  },
  closeButtonText: {
    color: '#fff',
    fontSize: 18,
    fontWeight: 'bold'
  },
  modalHeader: {
    padding: 20,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center'
  },
  modalTitle: {
    color: '#fff',
    fontSize: 20,
    fontWeight: 'bold'
  },
  modalRarity: {
    color: '#fff',
    fontSize: 12,
    fontWeight: 'bold',
    backgroundColor: 'rgba(255, 255, 255, 0.2)',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 4
  },
  modalImagePlaceholder: {
    width: '100%',
    height: 150,
    backgroundColor: '#1a1a1a',
    justifyContent: 'center',
    alignItems: 'center'
  },
  modalEmoji: {
    fontSize: 64
  },
  notCapturedMessage: {
    color: '#aaa',
    fontSize: 12,
    marginTop: 12
  },
  modalStats: {
    flexDirection: 'row',
    paddingHorizontal: 20,
    paddingVertical: 16,
    justifyContent: 'space-around',
    borderBottomWidth: 1,
    borderBottomColor: '#1a1a1a'
  },
  modalStatItem: {
    alignItems: 'center'
  },
  modalStatLabel: {
    color: '#aaa',
    fontSize: 12,
    marginBottom: 4
  },
  modalStatValue: {
    color: '#6366f1',
    fontSize: 16,
    fontWeight: 'bold'
  },
  modalDescription: {
    paddingHorizontal: 20,
    paddingVertical: 16
  },
  descriptionLabel: {
    color: '#fff',
    fontSize: 12,
    fontWeight: '600',
    marginBottom: 8
  },
  descriptionText: {
    color: '#aaa',
    fontSize: 12,
    lineHeight: 18
  },
  closeModalButton: {
    marginHorizontal: 20,
    marginBottom: 16,
    paddingVertical: 12,
    backgroundColor: '#6366f1',
    borderRadius: 8,
    alignItems: 'center'
  },
  closeModalButtonText: {
    color: '#fff',
    fontSize: 14,
    fontWeight: 'bold'
  }
});
