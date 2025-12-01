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

  const handleSellProperty = async (propertyId) => {
    Alert.alert(
      '⚠️ 부동산 판매',
      '이 부동산을 판매할까요?',
      [
        { text: '취소', style: 'cancel' },
        {
          text: '판매',
          style: 'destructive',
          onPress: async () => {
            try {
              const response = await realEstateAPI.sell(propertyId);
              if (response.data.success) {
                Vibration.vibrate([0, 100, 200]);
                Alert.alert('판매 완료', response.data.data.message);
                loadRealEstate();
              }
            } catch (error) {
              Alert.alert('오류', '판매 실패');
            }
          }
        }
      ]
    );
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
        <View key={idx} style={[styles.propertyCard, property.owned && styles.ownedProperty]}>
          <View style={styles.propertyHeader}>
            <Text style={styles.propertyName}>{property.name}</Text>
            {property.owned && <Text style={styles.ownedBadge}>✓ 소유중</Text>}
          </View>
          <Text style={styles.propertyInfo}>
            가격: ₩{property.price.toLocaleString()} | 월세: ₩{property.monthly_rent.toLocaleString()}
          </Text>
          {!property.owned ? (
            <TouchableOpacity style={[styles.button, styles.buttonPrimary]} onPress={() => handleBuyProperty(property.id)}>
              <Text style={styles.buttonText}>구매하기</Text>
            </TouchableOpacity>
          ) : (
            <View style={styles.buttonRow}>
              <TouchableOpacity style={[styles.button, styles.buttonSecondary, styles.flex1]} onPress={() => handleChangeResidence(property.id)}>
                <Text style={styles.buttonText}>거주</Text>
              </TouchableOpacity>
              <TouchableOpacity style={[styles.button, styles.buttonDanger, styles.flex1]} onPress={() => handleSellProperty(property.id)}>
                <Text style={styles.buttonText}>판매</Text>
              </TouchableOpacity>
            </View>
          )}
        </View>
      ))}
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
  currentCard: { backgroundColor: '#2a2a2a', padding: 15, borderRadius: 8, marginBottom: 20, borderLeftWidth: 4, borderLeftColor: '#6366f1' },
  currentLabel: { color: '#aaa', fontSize: 11, marginBottom: 5 },
  sectionTitle: { fontSize: 16, fontWeight: '600', color: '#6366f1', marginBottom: 12 },
  propertyCard: { backgroundColor: '#2a2a2a', padding: 15, borderRadius: 8, marginBottom: 10 },
  ownedProperty: { borderLeftWidth: 4, borderLeftColor: '#22c55e' },
  propertyHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 },
  propertyName: { color: '#fff', fontSize: 16, fontWeight: 'bold' },
  propertyInfo: { color: '#aaa', fontSize: 12, marginBottom: 10 },
  ownedBadge: { backgroundColor: '#22c55e', color: '#fff', paddingHorizontal: 8, paddingVertical: 4, borderRadius: 4, fontSize: 11, fontWeight: '600' },
  button: { paddingVertical: 10, borderRadius: 6, alignItems: 'center' },
  buttonPrimary: { backgroundColor: '#6366f1' },
  buttonSecondary: { backgroundColor: '#3a3a3a' },
  buttonDanger: { backgroundColor: '#ef4444' },
  buttonText: { color: '#fff', fontWeight: 'bold' },
  buttonRow: { flexDirection: 'row', gap: 8 },
  flex1: { flex: 1 }
});
