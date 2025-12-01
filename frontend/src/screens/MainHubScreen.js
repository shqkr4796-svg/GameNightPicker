import React, { useState, useEffect } from 'react';
import { View, Text, TouchableOpacity, StyleSheet, ScrollView, Alert } from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { playerAPI } from '../services/api';

export default function MainHubScreen({ navigation }) {
  const [playerData, setPlayerData] = useState(null);
  const [playerName, setPlayerName] = useState('');

  useEffect(() => {
    loadPlayerData();
  }, []);

  const loadPlayerData = async () => {
    try {
      const name = await AsyncStorage.getItem('player_name');
      setPlayerName(name || '플레이어');

      const response = await playerAPI.getInfo();
      if (response.data.success) {
        setPlayerData(response.data.data);
      }
    } catch (error) {
      Alert.alert('오류', '플레이어 데이터 로드 실패');
    }
  };

  const handleLogout = async () => {
    await AsyncStorage.removeItem('auth_token');
    await AsyncStorage.removeItem('player_id');
    await AsyncStorage.removeItem('player_name');
    navigation.replace('Login');
  };

  if (!playerData) {
    return (
      <View style={styles.container}>
        <Text style={styles.loadingText}>로딩 중...</Text>
      </View>
    );
  }

  return (
    <ScrollView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.playerName}>{playerName}</Text>
        <Text style={styles.level}>Lv. {playerData.level || 1}</Text>
      </View>

      <View style={styles.statsContainer}>
        <View style={styles.stat}>
          <Text style={styles.statLabel}>경험치</Text>
          <Text style={styles.statValue}>{playerData.경험치 || 0}</Text>
        </View>
        <View style={styles.stat}>
          <Text style={styles.statLabel}>돈</Text>
          <Text style={styles.statValue}>${playerData.돈 || 0}</Text>
        </View>
        <View style={styles.stat}>
          <Text style={styles.statLabel}>체력</Text>
          <Text style={styles.statValue}>{playerData.체력 || 100}</Text>
        </View>
      </View>

      <View style={styles.menuContainer}>
        <TouchableOpacity
          style={styles.menuButton}
          onPress={() => navigation.navigate('Adventure')}
        >
          <Text style={styles.menuTitle}>🗡️ 모험</Text>
          <Text style={styles.menuDesc}>스테이지를 진행하고 몬스터와 전투하세요</Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={styles.menuButton}
          onPress={() => navigation.navigate('Dungeon')}
        >
          <Text style={styles.menuTitle}>🏰 던전</Text>
          <Text style={styles.menuDesc}>퀴즈로 몬스터를 물리치세요</Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={styles.menuButton}
          onPress={() => navigation.navigate('Compendium')}
        >
          <Text style={styles.menuTitle}>📖 도감</Text>
          <Text style={styles.menuDesc}>포획한 몬스터를 확인하세요</Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={styles.menuButton}
          onPress={() => navigation.navigate('Shop')}
        >
          <Text style={styles.menuTitle}>🛍️ 상점</Text>
          <Text style={styles.menuDesc}>아이템을 구매하세요</Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={styles.menuButton}
          onPress={() => navigation.navigate('Dashboard')}
        >
          <Text style={styles.menuTitle}>📊 대시보드</Text>
          <Text style={styles.menuDesc}>플레이어 정보를 보세요</Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={styles.menuButton}
          onPress={() => navigation.navigate('Skills')}
        >
          <Text style={styles.menuTitle}>⚔️ 스킬</Text>
          <Text style={styles.menuDesc}>스킬을 관리하세요</Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={styles.menuButton}
          onPress={() => navigation.navigate('Inventory')}
        >
          <Text style={styles.menuTitle}>🎒 인벤토리</Text>
          <Text style={styles.menuDesc}>아이템을 관리하세요</Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={styles.menuButton}
          onPress={() => navigation.navigate('Achievements')}
        >
          <Text style={styles.menuTitle}>🏆 성취</Text>
          <Text style={styles.menuDesc}>성취를 확인하세요</Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={styles.menuButton}
          onPress={() => navigation.navigate('RealEstate')}
        >
          <Text style={styles.menuTitle}>🏠 부동산</Text>
          <Text style={styles.menuDesc}>부동산을 구매하세요</Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={styles.menuButton}
          onPress={() => navigation.navigate('Job')}
        >
          <Text style={styles.menuTitle}>💼 직업</Text>
          <Text style={styles.menuDesc}>직업을 선택하세요</Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={styles.menuButton}
          onPress={() => navigation.navigate('Quiz')}
        >
          <Text style={styles.menuTitle}>📚 단어 퀴즈</Text>
          <Text style={styles.menuDesc}>단어 학습 퀴즈를 풀어보세요</Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={styles.menuButton}
          onPress={() => navigation.navigate('DailyExpressions')}
        >
          <Text style={styles.menuTitle}>📝 일일 표현</Text>
          <Text style={styles.menuDesc}>영어 표현을 학습하세요</Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={styles.menuButton}
          onPress={() => navigation.navigate('WordManagement')}
        >
          <Text style={styles.menuTitle}>📋 단어 관리</Text>
          <Text style={styles.menuDesc}>나의 단어장을 관리하세요</Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={styles.menuButton}
          onPress={() => navigation.navigate('Fusion')}
        >
          <Text style={styles.menuTitle}>✨ 몬스터 합성</Text>
          <Text style={styles.menuDesc}>같은 등급 3마리를 합성하세요</Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={[styles.menuButton, styles.logoutButton]}
          onPress={handleLogout}
        >
          <Text style={styles.menuTitle}>🚪 로그아웃</Text>
          <Text style={styles.menuDesc}>게임을 종료합니다</Text>
        </TouchableOpacity>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#1a1a1a',
    padding: 20
  },
  header: {
    marginBottom: 30,
    alignItems: 'center'
  },
  playerName: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#fff',
    marginBottom: 5
  },
  level: {
    fontSize: 16,
    color: '#aaa'
  },
  statsContainer: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    marginBottom: 30,
    backgroundColor: '#2a2a2a',
    padding: 15,
    borderRadius: 8
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
  menuContainer: {
    gap: 10
  },
  menuButton: {
    backgroundColor: '#2a2a2a',
    padding: 15,
    borderRadius: 8,
    borderLeftWidth: 4,
    borderLeftColor: '#6366f1'
  },
  menuTitle: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
    marginBottom: 5
  },
  menuDesc: {
    color: '#aaa',
    fontSize: 12
  },
  logoutButton: {
    borderLeftColor: '#ef4444',
    marginTop: 10
  },
  loadingText: {
    color: '#fff',
    textAlign: 'center',
    marginTop: 20
  }
});
