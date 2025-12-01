import React, { useState, useEffect } from 'react';
import { View, Text, TouchableOpacity, StyleSheet, ScrollView, Alert, ActivityIndicator, Vibration } from 'react-native';
import { inventoryAPI } from '../services/api';

export default function InventoryScreen({ navigation }) {
  const [inventory, setInventory] = useState({ weapons: [], armor: [], items: [] });
  const [selectedTab, setSelectedTab] = useState('weapons');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadInventory();
  }, []);

  const loadInventory = async () => {
    setLoading(true);
    try {
      const response = await inventoryAPI.list();
      if (response.data.success) {
        setInventory(response.data.data.inventory || { weapons: [], armor: [], items: [] });
      }
    } catch (error) {
      Alert.alert('오류', '인벤토리 로드 실패');
    } finally {
      setLoading(false);
    }
  };

  const handleEquip = async (itemId) => {
    Vibration.vibrate([0, 100, 50, 100]);
    try {
      const response = await inventoryAPI.equip(itemId);
      if (response.data.success) {
        Alert.alert('성공', '장착되었습니다!');
        loadInventory();
      }
    } catch (error) {
      Alert.alert('오류', '장착 실패');
    }
  };

  const handleUseItem = async (itemId) => {
    Vibration.vibrate([0, 100, 50, 100, 50, 100]);
    try {
      const response = await inventoryAPI.useItem(itemId);
      if (response.data.success) {
        Alert.alert('성공', response.data.data.message);
        loadInventory();
      }
    } catch (error) {
      Alert.alert('오류', '사용 실패');
    }
  };

  if (loading) {
    return <View style={styles.container}><ActivityIndicator color="#6366f1" size="large" /></View>;
  }

  const renderItem = (item, type) => (
    <View key={item.id} style={[styles.itemCard, item.equipped && styles.equippedItem]}>
      <View style={styles.itemContent}>
        <View>
          <Text style={styles.itemName}>{item.name}</Text>
          {item.attack && <Text style={styles.itemStat}>⚔️ {item.attack}</Text>}
          {item.defense && <Text style={styles.itemStat}>🛡️ {item.defense}</Text>}
        </View>
      </View>
    </View>
  );

  const tabs = ['weapons', 'armor', 'items'];
  const tabLabels = { weapons: '무기', armor: '갑옷', items: '아이템' };

  return (
    <ScrollView style={styles.container}>
      <Text style={styles.title}>인벤토리</Text>
      <Text style={styles.subtitle}>보유한 아이템을 관리하세요</Text>

      <View style={styles.tabButtons}>
        {tabs.map(tab => (
          <TouchableOpacity
            key={tab}
            style={[styles.tabButton, selectedTab === tab && styles.tabButtonActive]}
            onPress={() => setSelectedTab(tab)}
          >
            <Text style={[styles.tabText, selectedTab === tab && styles.tabTextActive]}>{tabLabels[tab]}</Text>
          </TouchableOpacity>
        ))}
      </View>

      <View style={styles.itemList}>
        {inventory[selectedTab]?.map(item => renderItem(item, selectedTab))}
      </View>
      onPress={() => handleItemPress(item, 'armor')}
    >
      <View style={styles.itemContent}>
        <View>
          <Text style={styles.itemName}>{item.name}</Text>
          <View style={styles.itemStats}>
            <Text style={styles.itemStat}>🛡️ 방어: {item.defense}</Text>
            <Text style={[styles.itemRarity, { color: getRarityColor(item.rarity) }]}>
              {item.rarity}
            </Text>
          </View>
        </View>
        {item.equipped && <Text style={styles.equippedBadge}>장착 중</Text>}
      </View>
    </TouchableOpacity>
  );

  const renderSkillItem = ({ item }) => (
    <TouchableOpacity
      style={styles.skillItemCard}
      onPress={() => handleItemPress(item, 'skillItem')}
    >
      <View style={styles.skillItemContent}>
        <View>
          <Text style={styles.itemName}>{item.name}</Text>
          <Text style={styles.itemDesc}>{item.effect}</Text>
        </View>
        <View style={styles.quantityBadge}>
          <Text style={styles.quantityText}>×{item.quantity}</Text>
        </View>
      </View>
    </TouchableOpacity>
  );

  return (
    <View style={styles.container}>
      <Text style={styles.title}>🎒 인벤토리</Text>

      {/* 탭 */}
      <View style={styles.tabContainer}>
        <TouchableOpacity
          style={[styles.tab, selectedTab === 'weapons' && styles.activeTab]}
          onPress={() => setSelectedTab('weapons')}
        >
          <Text style={selectedTab === 'weapons' ? styles.activeTabText : styles.tabText}>
            ⚔️ 무기 ({inventory.weapons.length})
          </Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={[styles.tab, selectedTab === 'armor' && styles.activeTab]}
          onPress={() => setSelectedTab('armor')}
        >
          <Text style={selectedTab === 'armor' ? styles.activeTabText : styles.tabText}>
            🛡️ 방어구 ({inventory.armor.length})
          </Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={[styles.tab, selectedTab === 'skillItems' && styles.activeTab]}
          onPress={() => setSelectedTab('skillItems')}
        >
          <Text style={selectedTab === 'skillItems' ? styles.activeTabText : styles.tabText}>
            ⚡ 아이템 ({inventory.skillItems.length})
          </Text>
        </TouchableOpacity>
      </View>

      {/* 무기 */}
      {selectedTab === 'weapons' && (
        <FlatList
          data={inventory.weapons}
          renderItem={renderWeapon}
          keyExtractor={(item) => item.id.toString()}
          contentContainerStyle={styles.listContainer}
        />
      )}

      {/* 방어구 */}
      {selectedTab === 'armor' && (
        <FlatList
          data={inventory.armor}
          renderItem={renderArmor}
          keyExtractor={(item) => item.id.toString()}
          contentContainerStyle={styles.listContainer}
        />
      )}

      {/* 스킬 아이템 */}
      {selectedTab === 'skillItems' && (
        <FlatList
          data={inventory.skillItems}
          renderItem={renderSkillItem}
          keyExtractor={(item) => item.id.toString()}
          contentContainerStyle={styles.listContainer}
        />
      )}

      {/* 상세 모달 */}
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

            {selectedItem && (
              <>
                <Text style={styles.modalTitle}>{selectedItem.name}</Text>

                {selectedItem.type !== 'skillItem' && (
                  <>
                    <View style={styles.modalRarity}>
                      <Text style={[styles.rarityText, { color: getRarityColor(selectedItem.rarity) }]}>
                        {selectedItem.rarity}
                      </Text>
                    </View>

                    <View style={styles.modalStats}>
                      {selectedItem.type === 'weapon' && (
                        <Text style={styles.modalStat}>⚔️ 공격력: {selectedItem.attack}</Text>
                      )}
                      {selectedItem.type === 'armor' && (
                        <Text style={styles.modalStat}>🛡️ 방어력: {selectedItem.defense}</Text>
                      )}
                    </View>

                    <TouchableOpacity
                      style={[
                        styles.equipButton,
                        selectedItem.equipped && styles.unequipButton
                      ]}
                      onPress={() => handleEquip(selectedItem)}
                    >
                      <Text style={styles.equipButtonText}>
                        {selectedItem.equipped ? '장착 해제' : '장착'}
                      </Text>
                    </TouchableOpacity>
                  </>
                )}

                {selectedItem.type === 'skillItem' && (
                  <>
                    <View style={styles.modalEffect}>
                      <Text style={styles.effectLabel}>효과</Text>
                      <Text style={styles.effectText}>{selectedItem.effect}</Text>
                    </View>

                    <View style={styles.quantityInfo}>
                      <Text style={styles.quantityLabel}>보유 수량</Text>
                      <Text style={styles.quantityNum}>{selectedItem.quantity}개</Text>
                    </View>

                    <TouchableOpacity
                      style={styles.useButton}
                      onPress={() => handleUseItem(selectedItem)}
                    >
                      <Text style={styles.useButtonText}>사용</Text>
                    </TouchableOpacity>
                  </>
                )}

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
    padding: 20
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#fff',
    marginBottom: 15
  },
  tabContainer: {
    flexDirection: 'row',
    marginBottom: 15,
    backgroundColor: '#2a2a2a',
    borderRadius: 8,
    padding: 4
  },
  tab: {
    flex: 1,
    paddingVertical: 10,
    alignItems: 'center',
    borderRadius: 6
  },
  activeTab: {
    backgroundColor: '#6366f1'
  },
  tabText: {
    color: '#aaa',
    fontSize: 12,
    fontWeight: '600'
  },
  activeTabText: {
    color: '#fff',
    fontSize: 12,
    fontWeight: '600'
  },
  listContainer: {
    gap: 10
  },
  itemCard: {
    backgroundColor: '#2a2a2a',
    padding: 15,
    borderRadius: 8,
    borderLeftWidth: 4,
    borderLeftColor: '#6366f1'
  },
  equippedItem: {
    backgroundColor: '#1f3a1f',
    borderLeftColor: '#22c55e'
  },
  itemContent: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center'
  },
  itemName: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
    marginBottom: 5
  },
  itemStats: {
    flexDirection: 'row',
    gap: 10
  },
  itemStat: {
    color: '#aaa',
    fontSize: 12
  },
  itemRarity: {
    fontSize: 12,
    fontWeight: 'bold'
  },
  equippedBadge: {
    color: '#22c55e',
    fontSize: 12,
    fontWeight: 'bold'
  },
  skillItemCard: {
    backgroundColor: '#2a2a2a',
    padding: 15,
    borderRadius: 8,
    borderLeftWidth: 4,
    borderLeftColor: '#f59e0b'
  },
  skillItemContent: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center'
  },
  itemDesc: {
    color: '#aaa',
    fontSize: 12,
    marginTop: 5
  },
  quantityBadge: {
    backgroundColor: '#f59e0b',
    paddingHorizontal: 10,
    paddingVertical: 5,
    borderRadius: 20
  },
  quantityText: {
    color: '#fff',
    fontWeight: 'bold',
    fontSize: 12
  },
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
    alignItems: 'center'
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
  modalRarity: {
    backgroundColor: '#1a1a1a',
    padding: 15,
    borderRadius: 8,
    alignItems: 'center',
    marginBottom: 15
  },
  rarityText: {
    fontSize: 18,
    fontWeight: 'bold'
  },
  modalStats: {
    backgroundColor: '#1a1a1a',
    padding: 15,
    borderRadius: 8,
    marginBottom: 15
  },
  modalStat: {
    color: '#fff',
    fontSize: 14,
    marginVertical: 5
  },
  equipButton: {
    backgroundColor: '#6366f1',
    padding: 15,
    borderRadius: 8,
    alignItems: 'center',
    marginBottom: 10
  },
  unequipButton: {
    backgroundColor: '#ef4444'
  },
  equipButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold'
  },
  modalEffect: {
    backgroundColor: '#1a1a1a',
    padding: 15,
    borderRadius: 8,
    marginBottom: 15
  },
  effectLabel: {
    color: '#6366f1',
    fontSize: 12,
    fontWeight: 'bold',
    marginBottom: 5
  },
  effectText: {
    color: '#fff',
    fontSize: 14
  },
  quantityInfo: {
    backgroundColor: '#1a1a1a',
    padding: 15,
    borderRadius: 8,
    marginBottom: 15,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center'
  },
  quantityLabel: {
    color: '#aaa',
    fontSize: 12
  },
  quantityNum: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold'
  },
  useButton: {
    backgroundColor: '#22c55e',
    padding: 15,
    borderRadius: 8,
    alignItems: 'center',
    marginBottom: 10
  },
  useButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold'
  },
  closeModalButton: {
    backgroundColor: '#666',
    padding: 12,
    borderRadius: 8,
    alignItems: 'center'
  },
  closeModalButtonText: {
    color: '#fff',
    fontSize: 14,
    fontWeight: 'bold'
  }
});
