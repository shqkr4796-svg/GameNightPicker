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
          <Text style={styles.statValue}>{totalPoints}P</Text>
        </View>
      </View>

      <Text style={styles.sectionTitle}>업적 목록</Text>
      {achievements.map((achievement, idx) => (
        <View
          key={idx}
          style={[styles.achievementCard, achievement.achieved && styles.achievedCard]}
        >
          <View style={styles.achievementContent}>
            <View style={styles.achievementIcon}>
              <Text style={achievement.achieved ? styles.achievedIcon : styles.unachievedIcon}>
                {achievement.achieved ? '✓' : '◯'}
              </Text>
            </View>
            <View style={styles.achievementInfo}>
              <Text style={[styles.achievementName, !achievement.achieved && styles.unachievedText]}>
                {achievement.name}
              </Text>
              <Text style={styles.achievementDesc}>{achievement.description || achievement.desc}</Text>
            </View>
            <View style={styles.achievementRight}>
              <Text style={[styles.pointsBadge, achievement.achieved && styles.earnedPoints]}>
                {achievement.points}P
              </Text>
            </View>
          </View>
          {achievement.achieved && !achievement.claimed && (
            <TouchableOpacity
              style={styles.claimButton}
              onPress={() => handleClaimAchievement(achievement.id)}
            >
              <Text style={styles.claimButtonText}>보상 수령</Text>
            </TouchableOpacity>
          )}
        </View>
      ))}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#1a1a1a', padding: 16 },
  title: { fontSize: 28, fontWeight: 'bold', color: '#fff', marginBottom: 5 },
  statsContainer: { flexDirection: 'row', gap: 12, marginBottom: 20 },
  statBox: { flex: 1, backgroundColor: '#2a2a2a', padding: 15, borderRadius: 8 },
  statLabel: { color: '#aaa', fontSize: 12, marginBottom: 5 },
  statValue: { color: '#fff', fontSize: 18, fontWeight: 'bold' },
  sectionTitle: { fontSize: 16, fontWeight: '600', color: '#6366f1', marginBottom: 12 },
  achievementCard: { backgroundColor: '#2a2a2a', padding: 12, borderRadius: 8, marginBottom: 10 },
  achievedCard: { borderLeftWidth: 4, borderLeftColor: '#22c55e' },
  achievementContent: { flexDirection: 'row', alignItems: 'center' },
  achievementIcon: { width: 40, height: 40, borderRadius: 20, backgroundColor: '#3a3a3a', alignItems: 'center', justifyContent: 'center', marginRight: 12 },
  achievedIcon: { color: '#22c55e', fontSize: 20, fontWeight: 'bold' },
  unachievedIcon: { color: '#aaa', fontSize: 16 },
  achievementInfo: { flex: 1 },
  achievementName: { color: '#fff', fontSize: 14, fontWeight: '600', marginBottom: 4 },
  unachievedText: { color: '#aaa' },
  achievementDesc: { color: '#999', fontSize: 12 },
  achievementRight: { alignItems: 'flex-end' },
  pointsBadge: { color: '#aaa', fontSize: 12, fontWeight: '600' },
  earnedPoints: { color: '#22c55e' },
  claimButton: { backgroundColor: '#6366f1', paddingVertical: 8, borderRadius: 6, alignItems: 'center', marginTop: 10 },
  claimButtonText: { color: '#fff', fontSize: 12, fontWeight: '600' }
});
