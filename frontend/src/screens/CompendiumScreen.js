import React, { useState, useEffect } from 'react';
import { View, Text, TouchableOpacity, StyleSheet, FlatList, Alert, ActivityIndicator, Modal } from 'react-native';
import { compendiumAPI } from '../services/api';

export default function CompendiumScreen({ navigation }) {
  const [monsters, setMonsters] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedMonster, setSelectedMonster] = useState(null);
  const [modalVisible, setModalVisible] = useState(false);
  const [stats, setStats] = useState(null);

  useEffect(() => {
    loadCompendium();
  }, []);

  const loadCompendium = async () => {
    setLoading(true);
    try {
      const response = await compendiumAPI.list();
      if (response.data.success) {
        setMonsters(response.data.data.compendium || []);
        setStats(response.data.data.stats);
      }
    } catch (error) {
      Alert.alert('오류', '도감 데이터 로드 실패');
    } finally {
      setLoading(false);
    }
  };

  const handleMonsterPress = async (monster) => {
    try {
      const response = await compendiumAPI.details(monster.monster_id);
      if (response.data.success) {
        setSelectedMonster(response.data.data);
        setModalVisible(true);
      }
    } catch (error) {
      Alert.alert('오류', '몬스터 상세 정보 로드 실패');
    }
  };

  const getRarityColor = (rarity) => {
    const colors = {
      'Rare': '#3b82f6',
      'Epic': '#a855f7',
      'Unique': '#f59e0b',
      'Legendary': '#dc2626'
    };
    return colors[rarity] || '#666';
  };

  const renderMonsterCard = ({ item }) => (
    <TouchableOpacity
      style={[
        styles.monsterCard,
        { borderLeftColor: getRarityColor(item.rarity) }
      ]}
      onPress={() => handleMonsterPress(item)}
    >
      <View style={styles.monsterHeader}>
        <Text style={styles.monsterName}>{item.name}</Text>
        <Text style={[styles.rarity, { color: getRarityColor(item.rarity) }]}>
          {item.rarity}
        </Text>
      </View>
      <Text style={styles.monsterInfo}>Lv. {item.level || 1}</Text>
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
      <Text style={styles.title}>도감</Text>
      
      {stats && (
        <View style={styles.statsContainer}>
          <View style={styles.stat}>
            <Text style={styles.statLabel}>포획한 몬스터</Text>
            <Text style={styles.statValue}>{stats.total_captured}/{stats.total_monsters}</Text>
          </View>
          <View style={styles.stat}>
            <Text style={styles.statLabel}>완성도</Text>
            <Text style={styles.statValue}>{stats.completion_percent}%</Text>
          </View>
        </View>
      )}

      {monsters.length === 0 ? (
        <View style={styles.emptyContainer}>
          <Text style={styles.emptyText}>아직 포획한 몬스터가 없습니다.</Text>
          <Text style={styles.emptySubtext}>던전과 모험에서 몬스터를 포획해보세요!</Text>
        </View>
      ) : (
        <FlatList
          data={monsters}
          renderItem={renderMonsterCard}
          keyExtractor={(item) => item.monster_id.toString()}
          contentContainerStyle={styles.listContainer}
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
                <Text style={styles.modalTitle}>{selectedMonster.name}</Text>
                
                <View style={styles.modalStats}>
                  <View style={styles.modalStatItem}>
                    <Text style={styles.modalStatLabel}>레어도</Text>
                    <Text
                      style={[
                        styles.modalStatValue,
                        { color: getRarityColor(selectedMonster.rarity) }
                      ]}
                    >
                      {selectedMonster.rarity}
                    </Text>
                  </View>

                  <View style={styles.modalStatItem}>
                    <Text style={styles.modalStatLabel}>체력</Text>
                    <Text style={styles.modalStatValue}>{selectedMonster.hp}</Text>
                  </View>

                  <View style={styles.modalStatItem}>
                    <Text style={styles.modalStatLabel}>공격력</Text>
                    <Text style={styles.modalStatValue}>{selectedMonster.attack}</Text>
                  </View>

                  <View style={styles.modalStatItem}>
                    <Text style={styles.modalStatLabel}>방어력</Text>
                    <Text style={styles.modalStatValue}>{selectedMonster.defense}</Text>
                  </View>
                </View>

                {selectedMonster.description && (
                  <View style={styles.descriptionBox}>
                    <Text style={styles.descriptionLabel}>설명</Text>
                    <Text style={styles.description}>{selectedMonster.description}</Text>
                  </View>
                )}

                <TouchableOpacity
                  style={styles.modalCloseButton}
                  onPress={() => setModalVisible(false)}
                >
                  <Text style={styles.modalCloseButtonText}>닫기</Text>
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
    padding: 20
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#fff',
    marginBottom: 15
  },
  statsContainer: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    backgroundColor: '#2a2a2a',
    padding: 15,
    borderRadius: 8,
    marginBottom: 20
  },
  stat: {
    alignItems: 'center'
  },
  statLabel: {
    color: '#aaa',
    fontSize: 12,
    marginBottom: 5
  },
  statValue: {
    color: '#6366f1',
    fontSize: 18,
    fontWeight: 'bold'
  },
  listContainer: {
    gap: 10,
    paddingBottom: 20
  },
  monsterCard: {
    backgroundColor: '#2a2a2a',
    padding: 15,
    borderRadius: 8,
    borderLeftWidth: 4,
    borderBottomWidth: 1,
    borderBottomColor: '#3a3a3a'
  },
  monsterHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8
  },
  monsterName: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
    flex: 1
  },
  rarity: {
    fontSize: 12,
    fontWeight: 'bold'
  },
  monsterInfo: {
    color: '#aaa',
    fontSize: 12
  },
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingBottom: 50
  },
  emptyText: {
    color: '#fff',
    fontSize: 18,
    marginBottom: 10
  },
  emptySubtext: {
    color: '#aaa',
    fontSize: 14
  },
  // Modal Styles
  modalContainer: {
    flex: 1,
    backgroundColor: 'rgba(0, 0, 0, 0.9)',
    justifyContent: 'flex-end'
  },
  modalContent: {
    backgroundColor: '#2a2a2a',
    borderTopLeftRadius: 20,
    borderTopRightRadius: 20,
    padding: 20,
    paddingBottom: 40
  },
  closeButton: {
    position: 'absolute',
    top: 15,
    right: 15,
    width: 30,
    height: 30,
    justifyContent: 'center',
    alignItems: 'center',
    zIndex: 10
  },
  closeButtonText: {
    color: '#fff',
    fontSize: 24
  },
  modalTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#fff',
    marginBottom: 20,
    marginTop: 10
  },
  modalStats: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 10,
    marginBottom: 20
  },
  modalStatItem: {
    flex: 1,
    minWidth: '45%',
    backgroundColor: '#1a1a1a',
    padding: 12,
    borderRadius: 8,
    alignItems: 'center'
  },
  modalStatLabel: {
    color: '#aaa',
    fontSize: 12,
    marginBottom: 5
  },
  modalStatValue: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#6366f1'
  },
  descriptionBox: {
    backgroundColor: '#1a1a1a',
    padding: 15,
    borderRadius: 8,
    marginBottom: 20
  },
  descriptionLabel: {
    color: '#aaa',
    fontSize: 12,
    marginBottom: 8
  },
  description: {
    color: '#fff',
    fontSize: 14,
    lineHeight: 20
  },
  modalCloseButton: {
    backgroundColor: '#6366f1',
    padding: 15,
    borderRadius: 8,
    alignItems: 'center'
  },
  modalCloseButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold'
  }
});
