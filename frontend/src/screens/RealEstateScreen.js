import React, { useState, useEffect } from 'react';
import { View, Text, TouchableOpacity, StyleSheet, ScrollView, Alert, ActivityIndicator, Vibration } from 'react-native';
import { realEstateAPI } from '../services/api';

export default function RealEstateScreen({ navigation }) {
  const [properties, setProperties] = useState([]);
  const [playerMoney, setPlayerMoney] = useState(0);
  const [currentProperty, setCurrentProperty] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadRealEstate();
  }, []);

  const loadRealEstate = async () => {
    setLoading(true);
    try {
      const response = await realEstateAPI.list();
      if (response.data.success) {
        setProperties(response.data.data.properties || []);
        setPlayerMoney(response.data.data.player_money || 0);
        setCurrentProperty(response.data.data.current_property);
      }
    } catch (error) {
      Alert.alert('오류', '부동산 데이터 로드 실패');
    } finally {
      setLoading(false);
    }
  };

  const handleBuyProperty = async (propertyId) => {
    Vibration.vibrate([0, 100, 50, 100]);
    try {
      const response = await realEstateAPI.buy(propertyId);
      if (response.data.success) {
        Alert.alert('성공', '부동산을 구매했습니다!');
        loadRealEstate();
      }
    } catch (error) {
      Alert.alert('오류', '구매 실패');
    }
  };

  const handleChangeResidence = async (propertyId) => {
    try {
      const response = await realEstateAPI.changeResidence(propertyId);
      if (response.data.success) {
        Vibration.vibrate([0, 100, 50, 100]);
        Alert.alert('성공', '거주지를 변경했습니다!');
        loadRealEstate();
      }
    } catch (error) {
      Alert.alert('오류', '변경 실패');
    }
  };

  if (loading) {
    return <View style={styles.container}><ActivityIndicator color="#6366f1" size="large" /></View>;
  }

  return (
    <ScrollView style={styles.container}>
      <Text style={styles.title}>부동산</Text>
      <Text style={styles.subtitle}>부동산을 구매하여 자산을 늘려보세요</Text>

      <View style={styles.moneyCard}>
        <Text style={styles.moneyLabel}>보유 금액</Text>
        <Text style={styles.moneyValue}>₩{playerMoney.toLocaleString()}</Text>
      </View>

      {currentProperty && (
        <View style={styles.currentCard}>
          <Text style={styles.currentLabel}>현재 거주지</Text>
          <Text style={styles.propertyName}>{currentProperty.name}</Text>
          <Text style={styles.propertyInfo}>월세: ₩{(currentProperty.monthly_rent || 0).toLocaleString()}</Text>
        </View>
      )}

      <Text style={styles.sectionTitle}>매물</Text>
      {properties.map((property, idx) => (
        <TouchableOpacity
          key={idx}
          style={[styles.propertyCard, property.owned && styles.ownedProperty]}
      ]}
      onPress={() => {
        setSelectedProperty(item);
        setModalVisible(true);
      }}
    >
      <View style={styles.propertyHeader}>
        <Text style={styles.propertyName}>{item.name}</Text>
        {item.owned && <Text style={styles.ownedBadge}>✓ 소유중</Text>}
      </View>

      <View style={styles.propertyInfo}>
        <Text style={styles.infoText}>📍 {item.location}</Text>
        <Text style={styles.infoText}>가격: ${item.price}</Text>
        <Text style={styles.rentText}>월세: ${item.monthly_rent}</Text>
        <Text style={styles.levelText}>필요 레벨: {item.level_required}</Text>
      </View>

      {item.owned && (
        <TouchableOpacity
          style={styles.collectButton}
          onPress={() => handleCollectRent(item.id)}
        >
          <Text style={styles.collectButtonText}>월세 수령</Text>
        </TouchableOpacity>
      )}
    </TouchableOpacity>
  );

  return (
    <View style={styles.container}>
      <Text style={styles.title}>부동산</Text>

      {/* 돈 표시 */}
      <View style={styles.moneyBox}>
        <Text style={styles.moneyLabel}>보유 자산</Text>
        <Text style={styles.moneyValue}>${playerMoney}</Text>
      </View>

      {/* 부동산 목록 */}
      <FlatList
        data={properties}
        renderItem={renderPropertyCard}
        keyExtractor={(item) => item.id.toString()}
        contentContainerStyle={styles.listContainer}
        scrollEnabled={true}
      />

      {/* 부동산 상세 모달 */}
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

            {selectedProperty && (
              <>
                <Text style={styles.modalTitle}>{selectedProperty.name}</Text>

                <View style={styles.detailBox}>
                  <View style={styles.detailRow}>
                    <Text style={styles.detailLabel}>위치</Text>
                    <Text style={styles.detailValue}>{selectedProperty.location}</Text>
                  </View>

                  <View style={styles.detailRow}>
                    <Text style={styles.detailLabel}>구매 가격</Text>
                    <Text style={styles.detailValue}>${selectedProperty.price}</Text>
                  </View>

                  <View style={styles.detailRow}>
                    <Text style={styles.detailLabel}>월세 수익</Text>
                    <Text style={[styles.detailValue, { color: '#22c55e' }]}>
                      ${selectedProperty.monthly_rent}/월
                    </Text>
                  </View>

                  <View style={styles.detailRow}>
                    <Text style={styles.detailLabel}>필요 레벨</Text>
                    <Text style={styles.detailValue}>{selectedProperty.level_required}</Text>
                  </View>
                </View>

                {selectedProperty.owned ? (
                  <View style={styles.ownedSection}>
                    <Text style={styles.ownedText}>✓ 소유 중인 부동산</Text>
                    <TouchableOpacity
                      style={styles.rentButton}
                      onPress={() => {
                        handleCollectRent(selectedProperty.id);
                        setModalVisible(false);
                      }}
                    >
                      <Text style={styles.rentButtonText}>월세 ${selectedProperty.monthly_rent} 수령</Text>
                    </TouchableOpacity>
                  </View>
                ) : (
                  <>
                    <View style={styles.affordabilityBox}>
                      {playerMoney >= selectedProperty.price ? (
                        <Text style={styles.affordableText}>✓ 구매 가능합니다!</Text>
                      ) : (
                        <Text style={styles.unaffordableText}>
                          ✗ 돈이 부족합니다 (${selectedProperty.price - playerMoney} 더 필요)
                        </Text>
                      )}
                    </View>

                    <TouchableOpacity
                      style={[
                        styles.buyButton,
                        playerMoney < selectedProperty.price && styles.disabledButton
                      ]}
                      onPress={() => {
                        handleBuyProperty(selectedProperty.id);
                      }}
                      disabled={playerMoney < selectedProperty.price}
                    >
                      <Text style={styles.buyButtonText}>구매하기</Text>
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
  propertyCard: {
    backgroundColor: '#2a2a2a',
    padding: 15,
    borderRadius: 8,
    borderLeftWidth: 4,
    borderLeftColor: '#f59e0b'
  },
  ownedProperty: {
    borderLeftColor: '#22c55e'
  },
  propertyHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 10
  },
  propertyName: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
    flex: 1
  },
  ownedBadge: {
    color: '#22c55e',
    fontSize: 12,
    fontWeight: 'bold',
    backgroundColor: '#1a1a1a',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 4
  },
  propertyInfo: {
    gap: 5,
    marginBottom: 10
  },
  infoText: {
    color: '#aaa',
    fontSize: 12
  },
  rentText: {
    color: '#6366f1',
    fontSize: 12,
    fontWeight: 'bold'
  },
  levelText: {
    color: '#f59e0b',
    fontSize: 11
  },
  collectButton: {
    backgroundColor: '#22c55e',
    padding: 10,
    borderRadius: 6,
    alignItems: 'center'
  },
  collectButtonText: {
    color: '#fff',
    fontSize: 12,
    fontWeight: 'bold'
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
    padding: 15,
    borderRadius: 8,
    marginBottom: 20
  },
  detailRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 10,
    borderBottomWidth: 1,
    borderBottomColor: '#3a3a3a'
  },
  detailLabel: {
    color: '#aaa',
    fontSize: 12
  },
  detailValue: {
    color: '#fff',
    fontSize: 14,
    fontWeight: 'bold'
  },
  affordabilityBox: {
    padding: 12,
    borderRadius: 8,
    marginBottom: 15,
    backgroundColor: '#1a1a1a',
    borderWidth: 2,
    borderColor: '#6366f1'
  },
  affordableText: {
    color: '#22c55e',
    fontSize: 14,
    fontWeight: 'bold',
    textAlign: 'center'
  },
  unaffordableText: {
    color: '#ef4444',
    fontSize: 14,
    fontWeight: 'bold',
    textAlign: 'center'
  },
  ownedSection: {
    marginBottom: 15
  },
  ownedText: {
    color: '#22c55e',
    fontSize: 14,
    fontWeight: 'bold',
    marginBottom: 10,
    textAlign: 'center'
  },
  rentButton: {
    backgroundColor: '#22c55e',
    padding: 15,
    borderRadius: 8,
    alignItems: 'center'
  },
  rentButtonText: {
    color: '#fff',
    fontSize: 14,
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
  closeModalButton: {
    backgroundColor: '#ef4444',
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
