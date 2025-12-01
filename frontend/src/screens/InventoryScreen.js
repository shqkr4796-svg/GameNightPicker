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

  const handleUnequipWeapon = async (itemId) => {
    Vibration.vibrate([0, 100, 50, 100]);
    try {
      const response = await inventoryAPI.unequip(itemId);
      if (response.data.success) {
        Alert.alert('성공', '무기가 제거되었습니다!');
        loadInventory();
      }
    } catch (error) {
      Alert.alert('오류', '무기 제거 실패');
    }
  };

  if (loading) {
    return <View style={styles.container}><ActivityIndicator color="#6366f1" size="large" /></View>;
  }

  const tabs = ['weapons', 'armor', 'items'];
  const tabLabels = { weapons: '무기', armor: '갑옷', items: '아이템' };
  const currentItems = inventory[selectedTab] || [];

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
            <Text style={[styles.tabText, selectedTab === tab && styles.tabTextActive]}>
              {tabLabels[tab]} ({inventory[tab]?.length || 0})
            </Text>
          </TouchableOpacity>
        ))}
      </View>

      <View style={styles.itemList}>
        {currentItems.map((item, idx) => (
          <View key={idx} style={[styles.itemCard, item.equipped && styles.equippedItem]}>
            <View style={styles.itemHeader}>
              <View>
                <Text style={styles.itemName}>{item.name}</Text>
                {item.attack && <Text style={styles.itemStat}>⚔️ {item.attack}</Text>}
                {item.defense && <Text style={styles.itemStat}>🛡️ {item.defense}</Text>}
              </View>
              {item.equipped && <Text style={styles.equippedBadge}>장착 중</Text>}
            </View>
            {selectedTab !== 'items' && (
              <View style={styles.buttonRow}>
                <TouchableOpacity
                  style={[styles.actionButton, styles.flex1]}
                  onPress={() => handleEquip(item.id)}
                >
                  <Text style={styles.actionText}>{item.equipped ? '장착' : '장착'}</Text>
                </TouchableOpacity>
                {item.equipped && (
                  <TouchableOpacity
                    style={[styles.actionButton, styles.deleteButton, styles.flex1]}
                    onPress={() => handleUnequipWeapon(item.id)}
                  >
                    <Text style={styles.actionText}>해제</Text>
                  </TouchableOpacity>
                )}
              </View>
            )}
          </View>
        ))}
        {currentItems.length === 0 && (
          <View style={styles.emptyState}>
            <Text style={styles.emptyText}>아이템이 없습니다</Text>
          </View>
        )}
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#1a1a1a', padding: 16 },
  title: { fontSize: 28, fontWeight: 'bold', color: '#fff', marginBottom: 5 },
  subtitle: { fontSize: 14, color: '#aaa', marginBottom: 20 },
  tabButtons: { flexDirection: 'row', gap: 8, marginBottom: 20 },
  tabButton: { flex: 1, backgroundColor: '#2a2a2a', paddingVertical: 10, borderRadius: 6, alignItems: 'center' },
  tabButtonActive: { backgroundColor: '#6366f1' },
  tabText: { color: '#aaa', fontSize: 12, fontWeight: '600' },
  tabTextActive: { color: '#fff' },
  itemList: { gap: 10, marginBottom: 30 },
  itemCard: { backgroundColor: '#2a2a2a', padding: 12, borderRadius: 8 },
  equippedItem: { borderLeftWidth: 4, borderLeftColor: '#6366f1' },
  itemHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 },
  itemName: { color: '#fff', fontSize: 14, fontWeight: '600', marginBottom: 4 },
  itemStat: { color: '#aaa', fontSize: 12 },
  equippedBadge: { backgroundColor: '#6366f1', color: '#fff', paddingHorizontal: 8, paddingVertical: 4, borderRadius: 4, fontSize: 11, fontWeight: '600' },
  buttonRow: { flexDirection: 'row', gap: 8 },
  flex1: { flex: 1 },
  actionButton: { backgroundColor: '#3a3a3a', paddingVertical: 8, borderRadius: 6, alignItems: 'center' },
  deleteButton: { backgroundColor: '#ef4444' },
  actionText: { color: '#fff', fontSize: 12, fontWeight: '600' },
  emptyState: { alignItems: 'center', paddingVertical: 30 },
  emptyText: { color: '#aaa', fontSize: 14 }
});
