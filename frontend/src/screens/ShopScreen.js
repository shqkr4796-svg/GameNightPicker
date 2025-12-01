import React, { useState, useEffect } from 'react';
import { View, Text, TouchableOpacity, StyleSheet, FlatList, Alert, ActivityIndicator, Modal } from 'react-native';
import { shopAPI } from '../services/api';

export default function ShopScreen({ navigation }) {
  const [items, setItems] = useState([]);
  const [inventory, setInventory] = useState({});
  const [playerMoney, setPlayerMoney] = useState(0);
  const [loading, setLoading] = useState(true);
  const [selectedItem, setSelectedItem] = useState(null);
  const [modalVisible, setModalVisible] = useState(false);
  const [buyAmount, setBuyAmount] = useState(1);

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
      return;
    }

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
        Alert.alert('성공', response.data.data.message);
        loadShop();
      }
    } catch (error) {
      Alert.alert('오류', '아이템 사용 실패');
    }
  };

  const getItemColor = (category) => {
    const colors = {
      'potion': '#ef4444',
      'buff': '#6366f1',
      'equipment': '#f59e0b',
      'quest': '#3b82f6'
    };
    return colors[category] || '#666';
  };

  const renderItemCard = ({ item }) => {
    const inventoryCount = inventory[item.item_id] || 0;

    return (
      <TouchableOpacity
        style={[
          styles.itemCard,
          { borderLeftColor: getItemColor(item.category) }
        ]}
        onPress={() => {
          setSelectedItem(item);
          setBuyAmount(1);
          setModalVisible(true);
        }}
      >
        <View style={styles.itemHeader}>
          <Text style={styles.itemName}>{item.name}</Text>
          <Text style={[styles.price, { color: getItemColor(item.category) }]}>
            ${item.price}
          </Text>
        </View>
        <Text style={styles.itemDescription}>{item.description}</Text>
        <View style={styles.itemFooter}>
          <Text style={styles.category}>{item.category}</Text>
          {inventoryCount > 0 && (
            <Text style={styles.inventoryCount}>보유: {inventoryCount}개</Text>
          )}
        </View>
      </TouchableOpacity>
    );
  };

  if (loading) {
    return (
      <View style={styles.container}>
        <ActivityIndicator color="#6366f1" size="large" />
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <Text style={styles.title}>상점</Text>

      {/* 돈 표시 */}
      <View style={styles.moneyBox}>
        <Text style={styles.moneyLabel}>보유 금액</Text>
        <Text style={styles.moneyValue}>${playerMoney}</Text>
      </View>

      {/* 아이템 목록 */}
      {items.length === 0 ? (
        <View style={styles.emptyContainer}>
          <Text style={styles.emptyText}>판매 중인 아이템이 없습니다.</Text>
        </View>
      ) : (
        <FlatList
          data={items}
          renderItem={renderItemCard}
          keyExtractor={(item) => item.item_id.toString()}
          contentContainerStyle={styles.listContainer}
          scrollEnabled={true}
        />
      )}

      {/* 구매 모달 */}
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

                <View style={styles.detailBox}>
                  <Text style={styles.detailLabel}>설명</Text>
                  <Text style={styles.detailText}>{selectedItem.description}</Text>
                </View>

                <View style={styles.priceBox}>
                  <Text style={styles.priceLabel}>가격</Text>
                  <Text style={styles.priceValue}>${selectedItem.price}</Text>
                </View>

                <View style={styles.quantityBox}>
                  <Text style={styles.quantityLabel}>수량 선택</Text>
                  <View style={styles.quantityControls}>
                    <TouchableOpacity
                      style={styles.quantityButton}
                      onPress={() => setBuyAmount(Math.max(1, buyAmount - 1))}
                    >
                      <Text style={styles.quantityButtonText}>−</Text>
                    </TouchableOpacity>
                    <Text style={styles.quantityDisplay}>{buyAmount}</Text>
                    <TouchableOpacity
                      style={styles.quantityButton}
                      onPress={() => {
                        const maxBuy = Math.floor(playerMoney / selectedItem.price);
                        setBuyAmount(Math.min(maxBuy, buyAmount + 1));
                      }}
                    >
                      <Text style={styles.quantityButtonText}>+</Text>
                    </TouchableOpacity>
                  </View>
                </View>

                <View style={styles.totalBox}>
                  <Text style={styles.totalLabel}>총 가격</Text>
                  <Text style={styles.totalValue}>
                    ${selectedItem.price * buyAmount}
                  </Text>
                </View>

                {playerMoney < selectedItem.price * buyAmount ? (
                  <View style={[styles.buyButton, styles.disabledButton]}>
                    <Text style={styles.buyButtonText}>돈이 부족합니다</Text>
                  </View>
                ) : (
                  <TouchableOpacity
                    style={styles.buyButton}
                    onPress={handleBuyItem}
                  >
                    <Text style={styles.buyButtonText}>구매</Text>
                  </TouchableOpacity>
                )}

                <TouchableOpacity
                  style={styles.cancelButton}
                  onPress={() => setModalVisible(false)}
                >
                  <Text style={styles.cancelButtonText}>취소</Text>
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
  moneyBox: {
    backgroundColor: '#2a2a2a',
    padding: 15,
    borderRadius: 8,
    marginBottom: 20,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center'
  },
  moneyLabel: {
    color: '#aaa',
    fontSize: 14
  },
  moneyValue: {
    color: '#22c55e',
    fontSize: 20,
    fontWeight: 'bold'
  },
  listContainer: {
    gap: 10,
    paddingBottom: 20
  },
  itemCard: {
    backgroundColor: '#2a2a2a',
    padding: 15,
    borderRadius: 8,
    borderLeftWidth: 4
  },
  itemHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8
  },
  itemName: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
    flex: 1
  },
  price: {
    fontSize: 14,
    fontWeight: 'bold'
  },
  itemDescription: {
    color: '#aaa',
    fontSize: 12,
    marginBottom: 10,
    lineHeight: 16
  },
  itemFooter: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center'
  },
  category: {
    backgroundColor: '#1a1a1a',
    color: '#aaa',
    fontSize: 11,
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 4
  },
  inventoryCount: {
    color: '#6366f1',
    fontSize: 12,
    fontWeight: 'bold'
  },
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center'
  },
  emptyText: {
    color: '#aaa',
    fontSize: 16
  },
  // Modal
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
  detailBox: {
    backgroundColor: '#1a1a1a',
    padding: 12,
    borderRadius: 8,
    marginBottom: 15
  },
  detailLabel: {
    color: '#aaa',
    fontSize: 12,
    marginBottom: 5
  },
  detailText: {
    color: '#fff',
    fontSize: 14,
    lineHeight: 20
  },
  priceBox: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    backgroundColor: '#1a1a1a',
    padding: 12,
    borderRadius: 8,
    marginBottom: 15
  },
  priceLabel: {
    color: '#aaa',
    fontSize: 12
  },
  priceValue: {
    color: '#22c55e',
    fontSize: 16,
    fontWeight: 'bold'
  },
  quantityBox: {
    backgroundColor: '#1a1a1a',
    padding: 12,
    borderRadius: 8,
    marginBottom: 15
  },
  quantityLabel: {
    color: '#aaa',
    fontSize: 12,
    marginBottom: 10
  },
  quantityControls: {
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
    gap: 15
  },
  quantityButton: {
    width: 40,
    height: 40,
    backgroundColor: '#6366f1',
    borderRadius: 8,
    justifyContent: 'center',
    alignItems: 'center'
  },
  quantityButtonText: {
    color: '#fff',
    fontSize: 20,
    fontWeight: 'bold'
  },
  quantityDisplay: {
    color: '#fff',
    fontSize: 18,
    fontWeight: 'bold',
    minWidth: 40,
    textAlign: 'center'
  },
  totalBox: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    backgroundColor: '#0a0a0a',
    padding: 12,
    borderRadius: 8,
    marginBottom: 15,
    borderWidth: 2,
    borderColor: '#6366f1'
  },
  totalLabel: {
    color: '#aaa',
    fontSize: 12
  },
  totalValue: {
    color: '#6366f1',
    fontSize: 16,
    fontWeight: 'bold'
  },
  buyButton: {
    backgroundColor: '#6366f1',
    padding: 15,
    borderRadius: 8,
    alignItems: 'center',
    marginBottom: 10
  },
  disabledButton: {
    backgroundColor: '#666'
  },
  buyButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold'
  },
  cancelButton: {
    backgroundColor: '#ef4444',
    padding: 12,
    borderRadius: 8,
    alignItems: 'center'
  },
  cancelButtonText: {
    color: '#fff',
    fontSize: 14,
    fontWeight: 'bold'
  }
});
