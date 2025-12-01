import React, { useState } from 'react';
import { View, Text, TouchableOpacity, StyleSheet, Alert, Vibration, ScrollView } from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { playerAPI } from '../services/api';

export default function SleepScreen({ navigation }) {
  const [loading, setLoading] = useState(false);
  const [sleepResult, setSleepResult] = useState(null);

  const handleSleep = async () => {
    setLoading(true);
    Vibration.vibrate([0, 100, 50, 100]);

    try {
      // 백엔드 API 호출
      const response = await playerAPI.sleep();
      
      if (response.data.success) {
        const playerData = response.data.data.player;
        
        // 플레이어 데이터 업데이트
        await AsyncStorage.setItem('player_data', JSON.stringify(playerData));
        
        // 월세 수입 메시지 파싱
        const rentIncome = response.data.data.rent_income;
        
        setSleepResult({
          message: response.data.data.message,
          currentEnergy: response.data.data.current_energy,
          currentTime: response.data.data.current_time,
          totalMoney: response.data.data.total_money,
          rentIncome: rentIncome
        });

        setTimeout(() => {
          navigation.goBack();
        }, 2500);
      }
    } catch (error) {
      Alert.alert('오류', error.response?.data?.error || '수면 중 오류가 발생했습니다.');
    } finally {
      setLoading(false);
    }
  };

  if (sleepResult) {
    return (
      <View style={styles.container}>
        <View style={styles.resultCard}>
          <Text style={styles.resultIcon}>😴</Text>
          <Text style={styles.resultMessage}>{sleepResult.message}</Text>
          
          <View style={styles.statsContainer}>
            <View style={styles.statItem}>
              <Text style={styles.statLabel}>시간</Text>
              <Text style={styles.statValue}>{sleepResult.currentTime}</Text>
            </View>
            <View style={styles.statItem}>
              <Text style={styles.statLabel}>기력</Text>
              <Text style={styles.statValue}>{sleepResult.currentEnergy}</Text>
            </View>
            <View style={styles.statItem}>
              <Text style={styles.statLabel}>총 자산</Text>
              <Text style={styles.statValue}>₩{(sleepResult.totalMoney || 0).toLocaleString()}</Text>
            </View>
          </View>

          {sleepResult.rentIncome && sleepResult.rentIncome.length > 0 && (
            <View style={styles.rentContainer}>
              <Text style={styles.rentTitle}>💰 월세 수입</Text>
              {sleepResult.rentIncome.map((rent, idx) => (
                <Text key={idx} style={styles.rentItem}>{rent}</Text>
              ))}
            </View>
          )}

          <Text style={styles.autoCloseText}>자동으로 돌아갑니다...</Text>
        </View>
      </View>
    );
  }

  return (
    <ScrollView style={styles.container}>
      <Text style={styles.title}>💤 수면</Text>

      <View style={styles.card}>
        <Text style={styles.cardTitle}>편히 쉬어보세요</Text>
        <Text style={styles.cardDescription}>
          충분한 수면은 체력을 회복하고 하루를 새로 시작하는 데 도움이 됩니다.
        </Text>
      </View>

      <View style={styles.benefitsCard}>
        <Text style={styles.benefitsTitle}>✨ 수면 효과</Text>
        <Text style={styles.benefitItem}>• 체력 50 회복</Text>
        <Text style={styles.benefitItem}>• 경험치 10 획득</Text>
        <Text style={styles.benefitItem}>• 하루의 활동 초기화</Text>
      </View>

      <TouchableOpacity
        style={[styles.sleepButton, loading && styles.sleepButtonDisabled]}
        onPress={handleSleep}
        disabled={loading}
      >
        <Text style={styles.sleepButtonText}>
          {loading ? '잠자는 중...' : '💤 자러 가기'}
        </Text>
      </TouchableOpacity>

      <TouchableOpacity
        style={styles.cancelButton}
        onPress={() => navigation.goBack()}
      >
        <Text style={styles.cancelButtonText}>돌아가기</Text>
      </TouchableOpacity>

      <View style={styles.infoCard}>
        <Text style={styles.infoText}>
          💡 팁: 매일 수면을 취하면 꾸준히 성장할 수 있습니다!
        </Text>
      </View>
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
    marginBottom: 20
  },
  card: {
    backgroundColor: '#2a2a2a',
    padding: 20,
    borderRadius: 8,
    marginBottom: 15,
    borderLeftWidth: 4,
    borderLeftColor: '#6366f1'
  },
  cardTitle: {
    color: '#fff',
    fontSize: 18,
    fontWeight: '600',
    marginBottom: 10
  },
  cardDescription: {
    color: '#aaa',
    fontSize: 14,
    lineHeight: 20
  },
  benefitsCard: {
    backgroundColor: '#2a2a2a',
    padding: 20,
    borderRadius: 8,
    marginBottom: 20,
    borderLeftWidth: 4,
    borderLeftColor: '#22c55e'
  },
  benefitsTitle: {
    color: '#22c55e',
    fontSize: 14,
    fontWeight: '600',
    marginBottom: 12
  },
  benefitItem: {
    color: '#aaa',
    fontSize: 12,
    marginBottom: 6,
    lineHeight: 18
  },
  sleepButton: {
    backgroundColor: '#6366f1',
    paddingVertical: 15,
    borderRadius: 8,
    alignItems: 'center',
    marginBottom: 10
  },
  sleepButtonDisabled: {
    backgroundColor: '#3a3a3a'
  },
  sleepButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold'
  },
  cancelButton: {
    backgroundColor: '#3a3a3a',
    paddingVertical: 12,
    borderRadius: 8,
    alignItems: 'center',
    marginBottom: 20
  },
  cancelButtonText: {
    color: '#aaa',
    fontSize: 14,
    fontWeight: '600'
  },
  infoCard: {
    backgroundColor: '#2a2a2a',
    padding: 12,
    borderRadius: 8,
    marginBottom: 30
  },
  infoText: {
    color: '#aaa',
    fontSize: 12,
    textAlign: 'center',
    lineHeight: 18
  },
  resultCard: {
    backgroundColor: '#2a2a2a',
    padding: 30,
    borderRadius: 12,
    alignItems: 'center',
    marginTop: 80,
    borderWidth: 2,
    borderColor: '#22c55e'
  },
  resultIcon: {
    fontSize: 64,
    marginBottom: 15
  },
  resultMessage: {
    color: '#fff',
    fontSize: 20,
    fontWeight: 'bold',
    marginBottom: 25
  },
  statsContainer: {
    width: '100%',
    marginBottom: 20
  },
  statItem: {
    backgroundColor: '#1a1a1a',
    paddingVertical: 12,
    paddingHorizontal: 15,
    borderRadius: 6,
    marginBottom: 8,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center'
  },
  statLabel: {
    color: '#aaa',
    fontSize: 12
  },
  statValue: {
    color: '#22c55e',
    fontSize: 16,
    fontWeight: 'bold'
  },
  autoCloseText: {
    color: '#666',
    fontSize: 12,
    marginTop: 15
  },
  rentContainer: {
    backgroundColor: '#1a1a1a',
    padding: 15,
    borderRadius: 8,
    marginVertical: 15,
    borderLeftWidth: 3,
    borderLeftColor: '#fbbf24'
  },
  rentTitle: {
    color: '#fbbf24',
    fontSize: 14,
    fontWeight: '600',
    marginBottom: 8
  },
  rentItem: {
    color: '#aaa',
    fontSize: 12,
    marginBottom: 4,
    paddingLeft: 8
  }
});
