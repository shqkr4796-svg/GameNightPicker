import React, { useState, useEffect } from 'react';
import { View, Text, TouchableOpacity, StyleSheet, ScrollView, Alert, ActivityIndicator, Vibration } from 'react-native';
import { achievementsAPI } from '../services/api';

export default function AchievementsScreen({ navigation }) {
  const [achievements, setAchievements] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadAchievements();
  }, []);

  const loadAchievements = async () => {
    setLoading(true);
    try {
      const [listRes, progressRes] = await Promise.all([
        achievementsAPI.list(),
        achievementsAPI.progress()
      ]);

      if (listRes.data.success) {
        setAchievements(listRes.data.data.achievements || []);
      }
      if (progressRes.data.success) {
        setStats(progressRes.data.data);
      }
    } catch (error) {
      Alert.alert('오류', '업적 데이터 로드 실패');
    } finally {
      setLoading(false);
    }
  };

  const handleClaimAchievement = async (achievementId) => {
    Vibration.vibrate([0, 100, 50, 100, 50, 100]);
    try {
      const response = await achievementsAPI.claim(achievementId);
      if (response.data.success) {
        Alert.alert('성공', response.data.data.message);
        loadAchievements();
      }
    } catch (error) {
      Alert.alert('오류', '보상 수령 실패');
    }
  };

  const getDifficultyColor = (difficulty) => ({
    '쉬움': '#22c55e',
    '보통': '#3b82f6',
    '어려움': '#f59e0b',
    '극어려움': '#ef4444'
  }[difficulty] || '#666');

  if (loading) {
    return <View style={styles.container}><ActivityIndicator color="#6366f1" size="large" /></View>;
  }

  const totalPoints = achievements.reduce((sum, a) => a.achieved ? sum + (a.points || 0) : sum, 0);
  const achievedCount = achievements.filter(a => a.achieved).length;

  return (
    <ScrollView style={styles.container}>
      <Text style={styles.title}>🏆 업적</Text>

      <View style={styles.statsContainer}>
        <View style={styles.statBox}>
          <Text style={styles.statLabel}>달성한 업적</Text>
          <Text style={styles.statValue}>{achievedCount}/{achievements.length}</Text>
        </View>
        <View style={styles.statBox}>
          <Text style={styles.statLabel}>획득 포인트</Text>
          <Text style={[styles.statValue, { color: '#f59e0b' }]}>
            {totalPoints}/{totalPointsMax}
          </Text>
        </View>
        <View style={styles.statBox}>
          <Text style={styles.statLabel}>완성도</Text>
          <Text style={[styles.statValue, { color: '#22c55e' }]}>
            {Math.round((achievedCount / achievements.length) * 100)}%
          </Text>
        </View>
      </View>

      {/* 진행 막대 */}
      <View style={styles.progressContainer}>
        <View style={styles.progressBar}>
          <View
            style={[
              styles.progressFill,
              { width: `${(achievedCount / achievements.length) * 100}%` }
            ]}
          />
        </View>
      </View>

      {/* 성취 목록 */}
      <FlatList
        data={achievements}
        renderItem={renderAchievement}
        keyExtractor={(item) => item.id.toString()}
        contentContainerStyle={styles.listContainer}
        scrollEnabled={true}
      />
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
  statsContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 20,
    gap: 8
  },
  statBox: {
    flex: 1,
    backgroundColor: '#2a2a2a',
    padding: 12,
    borderRadius: 8,
    alignItems: 'center'
  },
  statLabel: {
    color: '#aaa',
    fontSize: 11,
    marginBottom: 5
  },
  statValue: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold'
  },
  progressContainer: {
    marginBottom: 20
  },
  progressBar: {
    height: 12,
    backgroundColor: '#3a3a3a',
    borderRadius: 6,
    overflow: 'hidden'
  },
  progressFill: {
    height: '100%',
    backgroundColor: '#6366f1'
  },
  listContainer: {
    gap: 10,
    paddingBottom: 20
  },
  achievementCard: {
    backgroundColor: '#2a2a2a',
    padding: 12,
    borderRadius: 8,
    borderLeftWidth: 4,
    borderLeftColor: '#3a3a3a',
    opacity: 0.6
  },
  achievedCard: {
    backgroundColor: '#1f3a1f',
    borderLeftColor: '#22c55e',
    opacity: 1
  },
  achievementContent: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 10
  },
  achievementIcon: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: '#1a1a1a',
    justifyContent: 'center',
    alignItems: 'center'
  },
  achievedIcon: {
    color: '#22c55e',
    fontSize: 20,
    fontWeight: 'bold'
  },
  unachievedIcon: {
    color: '#666',
    fontSize: 20
  },
  achievementInfo: {
    flex: 1
  },
  achievementName: {
    color: '#fff',
    fontSize: 13,
    fontWeight: 'bold',
    marginBottom: 3
  },
  unachievedText: {
    color: '#aaa'
  },
  achievementDesc: {
    color: '#888',
    fontSize: 11
  },
  achievementRight: {
    alignItems: 'flex-end',
    gap: 4
  },
  difficultyBadge: {
    fontSize: 11,
    fontWeight: 'bold'
  },
  pointsBadge: {
    color: '#666',
    fontSize: 12,
    fontWeight: 'bold'
  },
  earnedPoints: {
    color: '#f59e0b'
  }
});
