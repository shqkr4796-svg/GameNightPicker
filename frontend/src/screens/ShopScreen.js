import React, { useState, useEffect } from 'react';
import { View, Text, TouchableOpacity, StyleSheet, ScrollView, Alert, ActivityIndicator, Modal, Vibration } from 'react-native';
import { shopAPI } from '../services/api';

export default function ShopScreen({ navigation }) {
  const [items, setItems] = useState([]);
  const [inventory, setInventory] = useState({});
  const [playerMoney, setPlayerMoney] = useState(0);
  const [loading, setLoading] = useState(true);
  const [selectedItem, setSelectedItem] = useState(null);
  const [modalVisible, setModalVisible] = useState(false);
  const [buyAmount, setBuyAmount] = useState(1);
  const [selectedCategory, setSelectedCategory] = useState('all');

  useEffect(() => {
    loadShop();
  }, []);

  const loadShop = async () => {
    setLoading(true);
    try {
      const response = await shopAPI.list();
      if (response.data.success) {
        setItems(response.data.data.shop_items || []);
        setInventory(response.data.data.inventory || {});
        setPlayerMoney(response.data.data.player_money || 0);
      }
    } catch (error) {
      Alert.alert('오류', '상점 데이터 로드 실패');
    } finally {
      setLoading(false);
    }
  };

  const handleBuyItem = async () => {
    if (!selectedItem) return;

    const totalCost = selectedItem.price * buyAmount;
    if (totalCost > playerMoney) {
      Alert.alert('오류', '돈이 부족합니다.');
      Vibration.vibrate(200);
      return;
    }

    Vibration.vibrate([0, 100, 50, 100, 50, 100]);

    try {
      const response = await shopAPI.buy(selectedItem.item_id, buyAmount);
      if (response.data.success) {
        Alert.alert('성공', `${selectedItem.name}을(를) ${buyAmount}개 구매했습니다!`);
        loadShop();
        setModalVisible(false);
        setBuyAmount(1);
      }
    } catch (error) {
      Alert.alert('오류', '구매 실패');
    }
  };

  const handleUseItem = async (itemId) => {
    try {
      const response = await shopAPI.useItem(itemId);
      if (response.data.success) {
        Vibration.vibrate([0, 100, 50, 100]);
        Alert.alert('성공', response.data.data.message);
        loadShop();
      }
    } catch (error) {
      Alert.alert('오류', '아이템 사용 실패');
    }
  };

  const getItemColor = (category) => {
    const colors = { potion: '#ef4444', buff: '#6366f1', equipment: '#f59e0b', quest: '#3b82f6' };
    return colors[category] || '#666';
  };

  const categories = ['all', 'potion', 'buff', 'equipment', 'quest'];
  const filteredItems = selectedCategory === 'all' ? items : items.filter(i => i.category === selectedCategory);

  if (loading) {
    return <View style={styles.container}><ActivityIndicator color="#6366f1" size="large" /></View>;
  }

  return (
    <ScrollView style={styles.container}>
      <Text style={styles.title}>상점</Text>
      <Text style={styles.subtitle}>아이템을 구매하여 모험을 도와주세요</Text>

      <View style={styles.moneyCard}>
        <Text style={styles.moneyLabel}>보유 금액</Text>
        <Text style={styles.moneyValue}>₩{playerMoney.toLocaleString()}</Text>
      </View>

      <Text style={styles.sectionTitle}>카테고리</Text>
      <ScrollView horizontal showsHorizontalScrollIndicator={false} style={styles.categoryScroll}>
        {categories.map(cat => (
          <TouchableOpacity
            key={cat}
            style={[styles.categoryTag, selectedCategory === cat && styles.categoryTagActive]}
            onPress={() => setSelectedCategory(cat)}
          >
            <Text style={[styles.categoryTagText, selectedCategory === cat && styles.categoryTagTextActive]}>
              {cat === 'all' ? '전체' : cat === 'potion' ? '포션' : cat === 'buff' ? '버프' : cat === 'equipment' ? '장비' : '퀘스트'}
            </Text>
          </TouchableOpacity>
        ))}
      </ScrollView>

      <Text style={styles.sectionTitle}>상품</Text>
      <View style={styles.itemGrid}>
        {filteredItems.map((item, idx) => {
          const owned = inventory[item.item_id] || 0;
          return (
            <TouchableOpacity
              key={idx}
              style={[styles.itemCard, { borderLeftColor: getItemColor(item.category) }]}
              onPress={() => {
                setSelectedItem(item);
                setBuyAmount(1);
                setModalVisible(true);
              }}
            >
              <Text style={styles.itemName}>{item.name}</Text>
              <Text style={[styles.itemPrice, { color: getItemColor(item.category) }]}>₩{item.price}</Text>
              {owned > 0 && <Text style={styles.ownedBadge}>보유: {owned}</Text>}
            </TouchableOpacity>
          );
        })}
      </View>

      <Modal visible={modalVisible} transparent animationType="slide">
        <View style={styles.modal}>
          <View style={styles.modalContent}>
            <Text style={styles.modalTitle}>{selectedItem?.name}</Text>
            <Text style={styles.modalDesc}>{selectedItem?.description}</Text>
            <View style={styles.modalActions}>
              <TouchableOpacity style={[styles.button, styles.buttonSecondary]} onPress={() => {
                setBuyAmount(Math.max(1, buyAmount - 1));
              }}>
                <Text style={styles.buttonText}>−</Text>
              </TouchableOpacity>
              <Text style={styles.amountText}>{buyAmount}개</Text>
              <TouchableOpacity style={[styles.button, styles.buttonSecondary]} onPress={() => {
                setBuyAmount(buyAmount + 1);
              }}>
                <Text style={styles.buttonText}>+</Text>
              </TouchableOpacity>
            </View>
            <Text style={styles.totalPrice}>
              총액: ₩{((selectedItem?.price || 0) * buyAmount).toLocaleString()}
            </Text>
            <TouchableOpacity style={[styles.button, styles.buttonPrimary]} onPress={handleBuyItem}>
              <Text style={styles.buttonText}>구매</Text>
            </TouchableOpacity>
            <TouchableOpacity style={[styles.button, styles.buttonSecondary]} onPress={() => setModalVisible(false)}>
              <Text style={styles.buttonText}>취소</Text>
            </TouchableOpacity>
          </View>
        </View>
      </Modal>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#1a1a1a', padding: 16 },
  title: { fontSize: 28, fontWeight: 'bold', color: '#fff', marginBottom: 5 },
  subtitle: { fontSize: 14, color: '#aaa', marginBottom: 20 },
  moneyCard: { backgroundColor: '#2a2a2a', padding: 15, borderRadius: 8, marginBottom: 20 },
  moneyLabel: { color: '#aaa', fontSize: 12, marginBottom: 5 },
  moneyValue: { color: '#22c55e', fontSize: 20, fontWeight: 'bold' },
  sectionTitle: { fontSize: 16, fontWeight: '600', color: '#6366f1', marginBottom: 12 },
  categoryScroll: { marginBottom: 20 },
  categoryTag: { backgroundColor: '#2a2a2a', paddingHorizontal: 12, paddingVertical: 6, borderRadius: 6, marginRight: 8 },
  categoryTagActive: { backgroundColor: '#6366f1' },
  categoryTagText: { color: '#aaa', fontSize: 12, fontWeight: '600' },
  categoryTagTextActive: { color: '#fff' },
  itemGrid: { flexDirection: 'row', flexWrap: 'wrap', gap: 10, marginBottom: 30 },
  itemCard: { width: '48%', backgroundColor: '#2a2a2a', padding: 12, borderRadius: 8, borderLeftWidth: 4 },
  itemName: { color: '#fff', fontSize: 13, fontWeight: '600', marginBottom: 5 },
  itemPrice: { fontSize: 14, fontWeight: 'bold', marginBottom: 5 },
  ownedBadge: { color: '#aaa', fontSize: 11 },
  modal: { flex: 1, backgroundColor: 'rgba(0,0,0,0.7)', justifyContent: 'flex-end' },
  modalContent: { backgroundColor: '#2a2a2a', padding: 20, borderTopLeftRadius: 16, borderTopRightRadius: 16 },
  modalTitle: { color: '#fff', fontSize: 18, fontWeight: 'bold', marginBottom: 8 },
  modalDesc: { color: '#aaa', fontSize: 12, marginBottom: 20 },
  modalActions: { flexDirection: 'row', justifyContent: 'center', gap: 10, marginBottom: 15 },
  button: { paddingVertical: 10, paddingHorizontal: 15, borderRadius: 6, alignItems: 'center' },
  buttonPrimary: { backgroundColor: '#6366f1', flex: 1 },
  buttonSecondary: { backgroundColor: '#3a3a3a', flex: 0.3 },
  buttonText: { color: '#fff', fontWeight: 'bold' },
  amountText: { color: '#fff', fontSize: 14, fontWeight: '600', minWidth: 40, textAlign: 'center' },
  totalPrice: { color: '#22c55e', fontSize: 14, fontWeight: 'bold', marginBottom: 15, textAlign: 'center' }
});
