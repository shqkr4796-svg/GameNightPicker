import React, { useState } from 'react';
import { View, Text, TouchableOpacity, StyleSheet, FlatList, Modal, Alert, Vibration } from 'react-native';

export default function InventoryScreen({ navigation }) {
  const [inventory] = useState({
    weapons: [
      { id: 1, name: 'Iron Sword', attack: 5, equipped: true, rarity: 'Common' },
      { id: 2, name: 'Steel Sword', attack: 8, equipped: false, rarity: 'Uncommon' }
    ],
    armor: [
      { id: 1, name: 'Iron Armor', defense: 3, equipped: true, rarity: 'Common' },
      { id: 2, name: 'Mithril Armor', defense: 7, equipped: false, rarity: 'Rare' }
    ],
    skillItems: [
      { id: 1, name: 'Skill Recharger', quantity: 2, effect: '스킬 기력 회복' },
      { id: 2, name: 'Skill Resetter', quantity: 1, effect: '스킬 초기화' },
      { id: 3, name: 'Stat Booster', quantity: 3, effect: '능력치 +1' }
    ]
  });

  const [selectedTab, setSelectedTab] = useState('weapons');
  const [selectedItem, setSelectedItem] = useState(null);
  const [modalVisible, setModalVisible] = useState(false);

  const getRarityColor = (rarity) => {
    const colors = {
      'Common': '#95a5a6',
      'Uncommon': '#27ae60',
      'Rare': '#3498db',
      'Epic': '#8e44ad',
      'Legendary': '#f39c12'
    };
    return colors[rarity] || '#95a5a6';
  };

  const handleItemPress = (item, type) => {
    setSelectedItem({ ...item, type });
    setModalVisible(true);
  };

  const handleEquip = (item) => {
    Vibration.vibrate([0, 100, 50, 100]);
    Alert.alert('장착', `${item.name}을(를) 장착했습니다!`);
    setModalVisible(false);
  };

  const handleUseItem = (item) => {
    Vibration.vibrate([0, 100, 50, 100, 50, 100]);
    Alert.alert('사용', `${item.name}을(를) 사용했습니다!\n효과: ${item.effect}`);
    setModalVisible(false);
  };

  const renderWeapon = ({ item }) => (
    <TouchableOpacity
      style={[styles.itemCard, item.equipped && styles.equippedItem]}
      onPress={() => handleItemPress(item, 'weapon')}
    >
      <View style={styles.itemContent}>
        <View>
          <Text style={styles.itemName}>{item.name}</Text>
          <View style={styles.itemStats}>
            <Text style={styles.itemStat}>⚔️ 공격: {item.attack}</Text>
            <Text style={[styles.itemRarity, { color: getRarityColor(item.rarity) }]}>
              {item.rarity}
            </Text>
          </View>
        </View>
        {item.equipped && <Text style={styles.equippedBadge}>장착 중</Text>}
      </View>
    </TouchableOpacity>
  );

  const renderArmor = ({ item }) => (
    <TouchableOpacity
      style={[styles.itemCard, item.equipped && styles.equippedItem]}
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
