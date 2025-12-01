import React, { useState, useEffect } from 'react';
import { View, Text, TouchableOpacity, StyleSheet, ScrollView, Alert, ActivityIndicator, AsyncStorage, Image } from 'react-native';

export default function HomeScreen({ navigation }) {
  const [hasLoadableGame, setHasLoadableGame] = useState(false);
  const [loading, setLoading] = useState(true);
  const [playerName, setPlayerName] = useState('');
  const [playerLevel, setPlayerLevel] = useState(0);

  useEffect(() => {
    checkForSavedGame();
  }, []);

  const checkForSavedGame = async () => {
    try {
      const savedGame = await AsyncStorage.getItem('player_data');
      if (savedGame) {
        const data = JSON.parse(savedGame);
        setHasLoadableGame(true);
        setPlayerName(data.name || '플레이어');
        setPlayerLevel(data.level || 1);
      }
    } catch (error) {
      console.log('저장된 게임 확인 실패');
    } finally {
      setLoading(false);
    }
  };

  const handleStartNewGame = async () => {
    Alert.alert(
      '새 게임 시작',
      '새 게임을 시작하면 기존 게임 데이터가 삭제됩니다.',
      [
        { text: '취소', onPress: () => {} },
        {
          text: '확인',
          onPress: async () => {
            try {
              // 새 게임 데이터 생성
              const newPlayer = {
                id: new Date().getTime(),
                name: '새로운 플레이어',
                level: 1,
                exp: 0,
                health: 10,
                stamina: 100,
                money: 10000,
                date: 1,
                time: 8,
                strength: 5,
                intelligence: 5,
                charm: 5,
                stamina_stat: 5,
                luck: 5,
                tier: 'Bronze V',
                tier_progress: 0,
                skills: [],
                monsters: [],
                properties: [],
                job: null,
                createdAt: new Date().toISOString()
              };

              await AsyncStorage.setItem('player_data', JSON.stringify(newPlayer));
              Alert.alert('성공', '새 게임을 시작했습니다!', [
                { text: '확인', onPress: () => navigation.navigate('Dashboard') }
              ]);
            } catch (error) {
              Alert.alert('오류', '게임 저장 실패');
            }
          }
        }
      ]
    );
  };

  const handleLoadGame = async () => {
    try {
      const savedGame = await AsyncStorage.getItem('player_data');
      if (savedGame) {
        Alert.alert('성공', `${playerName} (Lv. ${playerLevel})의 게임을 불러왔습니다!`, [
          { text: '확인', onPress: () => navigation.navigate('Dashboard') }
        ]);
      } else {
        Alert.alert('알림', '저장된 게임이 없습니다.');
      }
    } catch (error) {
      Alert.alert('오류', '게임 불러오기 실패');
    }
  };

  const handleDeleteGame = async () => {
    Alert.alert(
      '게임 삭제',
      `${playerName}의 데이터가 완전히 삭제됩니다.\n정말로 삭제하시겠습니까?`,
      [
        { text: '취소', onPress: () => {} },
        {
          text: '삭제',
          onPress: async () => {
            try {
              await AsyncStorage.removeItem('player_data');
              setHasLoadableGame(false);
              setPlayerName('');
              setPlayerLevel(0);
              Alert.alert('완료', '게임 데이터가 삭제되었습니다.');
            } catch (error) {
              Alert.alert('오류', '삭제 실패');
            }
          },
          style: 'destructive'
        }
      ]
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
    <ScrollView style={styles.container}>
      {/* 헤더 */}
      <View style={styles.header}>
        <Text style={styles.gameTitle}>🎮 인생 시뮬레이션</Text>
        <Text style={styles.gameSubtitle}>당신의 인생을 플레이하세요</Text>
      </View>

      {/* 메인 이미지 */}
      <View style={styles.bannerContainer}>
        <View style={styles.bannerContent}>
          <Text style={styles.bannerText}>📖 새로운 인생의 시작</Text>
        </View>
      </View>

      {/* 게임 상태 */}
      {hasLoadableGame ? (
        <View style={styles.gameStatusCard}>
          <View style={styles.statusHeader}>
            <Text style={styles.statusTitle}>진행 중인 게임</Text>
            <Text style={styles.statusBadge}>저장됨</Text>
          </View>
          <View style={styles.playerInfo}>
            <Text style={styles.playerName}>{playerName}</Text>
            <Text style={styles.playerLevel}>Lv. {playerLevel}</Text>
          </View>
          <Text style={styles.statusDesc}>이전 게임을 계속하거나 새 게임을 시작할 수 있습니다.</Text>
        </View>
      ) : (
        <View style={styles.noGameCard}>
          <Text style={styles.noGameIcon}>✨</Text>
          <Text style={styles.noGameText}>저장된 게임이 없습니다</Text>
          <Text style={styles.noGameDesc}>새 게임을 시작하여 당신의 인생을 만들어보세요!</Text>
        </View>
      )}

      {/* 버튼 영역 */}
      <View style={styles.buttonSection}>
        {/* 새 게임 시작 */}
        <TouchableOpacity
          style={[styles.button, styles.buttonPrimary]}
          onPress={handleStartNewGame}
        >
          <Text style={styles.buttonText}>✨ 새 게임 시작</Text>
        </TouchableOpacity>

        {/* 게임 불러오기 */}
        {hasLoadableGame && (
          <>
            <TouchableOpacity
              style={[styles.button, styles.buttonSecondary]}
              onPress={handleLoadGame}
            >
              <Text style={styles.buttonText}>📂 게임 불러오기</Text>
            </TouchableOpacity>

            {/* 게임 삭제 */}
            <TouchableOpacity
              style={[styles.button, styles.buttonDanger]}
              onPress={handleDeleteGame}
            >
              <Text style={styles.buttonText}>🗑️ 게임 삭제</Text>
            </TouchableOpacity>
          </>
        )}
      </View>

      {/* 게임 정보 */}
      <View style={styles.infoSection}>
        <Text style={styles.infoTitle}>📚 게임 소개</Text>
        
        <View style={styles.infoCard}>
          <Text style={styles.infoCardTitle}>🎯 주요 기능</Text>
          <Text style={styles.infoItem}>• 영어 학습을 통한 능력치 상승</Text>
          <Text style={styles.infoItem}>• 던전 탐험 및 몬스터 포획</Text>
          <Text style={styles.infoItem}>• 직업 선택 및 부동산 투자</Text>
          <Text style={styles.infoItem}>• 스킬 습득 및 장비 장착</Text>
          <Text style={styles.infoItem}>• 업적 달성 및 보상 획득</Text>
        </View>

        <View style={styles.infoCard}>
          <Text style={styles.infoCardTitle}>⚡ 게임 팁</Text>
          <Text style={styles.infoItem}>• 매일 표현 학습으로 경험치 획득</Text>
          <Text style={styles.infoItem}>• 퀴즈를 풀어 모험 기력 충전</Text>
          <Text style={styles.infoItem}>• 다양한 직업으로 돈 벌기</Text>
          <Text style={styles.infoItem}>• 모험에서 몬스터 포획하기</Text>
        </View>
      </View>

      {/* 버전 정보 */}
      <View style={styles.footer}>
        <Text style={styles.versionText}>v1.0.0</Text>
        <Text style={styles.copyrightText}>© 2024 Life Simulation Game</Text>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#1a1a1a'
  },
  header: {
    paddingHorizontal: 16,
    paddingTop: 40,
    paddingBottom: 20,
    backgroundColor: '#2a2a2a'
  },
  gameTitle: {
    fontSize: 32,
    fontWeight: 'bold',
    color: '#6366f1',
    marginBottom: 5
  },
  gameSubtitle: {
    fontSize: 14,
    color: '#aaa'
  },
  bannerContainer: {
    margin: 16,
    borderRadius: 12,
    overflow: 'hidden',
    backgroundColor: '#2a2a2a'
  },
  bannerContent: {
    paddingVertical: 60,
    paddingHorizontal: 20,
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: 'linear-gradient(135deg, #6366f1 0%, #3b82f6 100%)'
  },
  bannerText: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#fff'
  },
  gameStatusCard: {
    marginHorizontal: 16,
    marginBottom: 20,
    backgroundColor: '#2a2a2a',
    padding: 15,
    borderRadius: 8,
    borderLeftWidth: 4,
    borderLeftColor: '#22c55e'
  },
  statusHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12
  },
  statusTitle: {
    color: '#fff',
    fontSize: 14,
    fontWeight: '600'
  },
  statusBadge: {
    backgroundColor: '#22c55e',
    color: '#fff',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 4,
    fontSize: 11,
    fontWeight: '600'
  },
  playerInfo: {
    marginBottom: 10
  },
  playerName: {
    color: '#fff',
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 4
  },
  playerLevel: {
    color: '#aaa',
    fontSize: 12
  },
  statusDesc: {
    color: '#aaa',
    fontSize: 12,
    lineHeight: 18
  },
  noGameCard: {
    marginHorizontal: 16,
    marginBottom: 20,
    backgroundColor: '#2a2a2a',
    padding: 30,
    borderRadius: 8,
    alignItems: 'center'
  },
  noGameIcon: {
    fontSize: 48,
    marginBottom: 12
  },
  noGameText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
    marginBottom: 5
  },
  noGameDesc: {
    color: '#aaa',
    fontSize: 12,
    textAlign: 'center'
  },
  buttonSection: {
    marginHorizontal: 16,
    marginBottom: 30,
    gap: 10
  },
  button: {
    paddingVertical: 15,
    paddingHorizontal: 20,
    borderRadius: 8,
    alignItems: 'center'
  },
  buttonPrimary: {
    backgroundColor: '#6366f1'
  },
  buttonSecondary: {
    backgroundColor: '#3a3a3a'
  },
  buttonDanger: {
    backgroundColor: '#ef4444'
  },
  buttonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold'
  },
  infoSection: {
    marginHorizontal: 16,
    marginBottom: 20
  },
  infoTitle: {
    color: '#6366f1',
    fontSize: 16,
    fontWeight: '600',
    marginBottom: 12
  },
  infoCard: {
    backgroundColor: '#2a2a2a',
    padding: 15,
    borderRadius: 8,
    marginBottom: 10
  },
  infoCardTitle: {
    color: '#fff',
    fontSize: 14,
    fontWeight: '600',
    marginBottom: 10
  },
  infoItem: {
    color: '#aaa',
    fontSize: 12,
    marginBottom: 6,
    lineHeight: 16
  },
  footer: {
    alignItems: 'center',
    paddingVertical: 20,
    borderTopWidth: 1,
    borderTopColor: '#2a2a2a'
  },
  versionText: {
    color: '#666',
    fontSize: 12,
    marginBottom: 5
  },
  copyrightText: {
    color: '#555',
    fontSize: 11
  }
});
