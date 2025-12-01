import React, { useState } from 'react';
import { View, Text, StyleSheet, FlatList, ScrollView } from 'react-native';

export default function AchievementsScreen({ navigation }) {
  const [achievements] = useState([
    { id: 1, name: '첫 걸음', desc: '게임 시작', difficulty: '쉬움', points: 10, achieved: true },
    { id: 2, name: '레벨 10 도달', desc: '10레벨에 도달하기', difficulty: '쉬움', points: 20, achieved: true },
    { id: 3, name: '전투 승리 10회', desc: '모험에서 10번 승리', difficulty: '보통', points: 30, achieved: true },
    { id: 4, name: '몬스터 포획 5개', desc: '5개 이상의 몬스터 포획', difficulty: '보통', points: 40, achieved: false },
    { id: 5, name: '부자 되기', desc: '100,000원 보유', difficulty: '보통', points: 50, achieved: true },
    { id: 6, name: 'CEO 취업', desc: 'CEO 직업 획득', difficulty: '어려움', points: 100, achieved: false },
    { id: 7, name: '모든 표현 학습', desc: '180개 표현 모두 학습', difficulty: '어려움', points: 150, achieved: false },
    { id: 8, name: '던전 완주', desc: '모든 던전 클리어', difficulty: '어려움', points: 200, achieved: false },
    { id: 9, name: '레벨 50 달성', desc: '최고 레벨 도달', difficulty: '극어려움', points: 500, achieved: false },
    { id: 10, name: '완벽한 수집가', desc: '모든 몬스터 포획', difficulty: '극어려움', points: 1000, achieved: false },
  ]);

  const totalPoints = achievements.reduce((sum, ach) => ach.achieved ? sum + ach.points : sum, 0);
  const totalPointsMax = achievements.reduce((sum, ach) => sum + ach.points, 0);

  const getDifficultyColor = (difficulty) => {
    const colors = {
      '쉬움': '#22c55e',
      '보통': '#3b82f6',
      '어려움': '#f59e0b',
      '극어려움': '#ef4444'
    };
    return colors[difficulty] || '#666';
  };

  const achievedCount = achievements.filter(a => a.achieved).length;

  const renderAchievement = ({ item }) => (
    <View style={[styles.achievementCard, item.achieved && styles.achievedCard]}>
      <View style={styles.achievementContent}>
        <View style={styles.achievementIcon}>
          {item.achieved ? (
            <Text style={styles.achievedIcon}>✓</Text>
          ) : (
            <Text style={styles.unachievedIcon}>◯</Text>
          )}
        </View>

        <View style={styles.achievementInfo}>
          <Text style={[styles.achievementName, !item.achieved && styles.unachievedText]}>
            {item.name}
          </Text>
          <Text style={styles.achievementDesc}>{item.desc}</Text>
        </View>

        <View style={styles.achievementRight}>
          <Text
            style={[
              styles.difficultyBadge,
              { color: getDifficultyColor(item.difficulty) }
            ]}
          >
            {item.difficulty}
          </Text>
          <Text style={[styles.pointsBadge, item.achieved && styles.earnedPoints]}>
            {item.points}P
          </Text>
        </View>
      </View>
    </View>
  );

  return (
    <View style={styles.container}>
      <Text style={styles.title}>🏆 성취</Text>

      {/* 상단 정보 */}
      <View style={styles.statsContainer}>
        <View style={styles.statBox}>
          <Text style={styles.statLabel}>달성한 성취</Text>
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
