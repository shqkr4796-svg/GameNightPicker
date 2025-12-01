import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, ScrollView, TouchableOpacity, ActivityIndicator, RefreshControl } from 'react-native';
import { dashboardAPI } from '../services/api';

export default function DashboardScreen({ navigation }) {
  const [playerStats, setPlayerStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [activeTab, setActiveTab] = useState('status');

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    setLoading(true);
    try {
      const [statsRes, levelRes, progressRes] = await Promise.all([
        dashboardAPI.getStats(),
        dashboardAPI.getLevelInfo(),
        dashboardAPI.getProgress()
      ]);

      if (statsRes.data.success) {
        const combinedStats = {
          ...statsRes.data.data,
          ...(levelRes.data.success && levelRes.data.data),
          ...(progressRes.data.success && progressRes.data.data)
        };
        setPlayerStats(combinedStats);
      }
    } catch (error) {
      console.log('대시보드 데이터 로드 실패');
    } finally {
      setLoading(false);
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    try {
      await loadDashboardData();
    } finally {
      setRefreshing(false);
    }
  };

  if (loading) {
    return (
      <View style={styles.container}>
        <ActivityIndicator color="#6366f1" size="large" />
      </View>
    );
  }

  if (!playerStats) {
    return (
      <View style={styles.container}>
        <Text style={styles.errorText}>데이터를 불러올 수 없습니다</Text>
      </View>
    );
  }

  const renderStatusTab = () => (
    <View style={styles.tabContent}>
      {/* 기본 정보 */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>📊 기본 정보</Text>
        <View style={styles.statsGrid}>
          <View style={styles.statBox}>
            <Text style={styles.statLabel}>레벨</Text>
            <Text style={styles.statValue}>{playerStats.level || 1}</Text>
          </View>
          <View style={styles.statBox}>
            <Text style={styles.statLabel}>경험치</Text>
            <Text style={styles.statValue}>{playerStats.exp || 0}/{playerStats.exp_max || 100}</Text>
          </View>
          <View style={styles.statBox}>
            <Text style={styles.statLabel}>날짜</Text>
            <Text style={styles.statValue}>{playerStats.date || 1}일</Text>
          </View>
          <View style={styles.statBox}>
            <Text style={styles.statLabel}>시간</Text>
            <Text style={styles.statValue}>{playerStats.time || 8}시</Text>
          </View>
          <View style={styles.statBox}>
            <Text style={styles.statLabel}>건강</Text>
            <Text style={styles.statValue}>{playerStats.health || 10}/10</Text>
          </View>
          <View style={styles.statBox}>
            <Text style={styles.statLabel}>기력</Text>
            <Text style={styles.statValue}>{playerStats.stamina || 0}/{playerStats.max_stamina || 100}</Text>
          </View>
        </View>
      </View>

      {/* 경험치 진행률 */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>⚡ 경험치 진행률</Text>
        <View style={styles.progressCard}>
          <View style={styles.progressBar}>
            <View
              style={[
                styles.progressFill,
                { width: `${((playerStats.exp || 0) / (playerStats.exp_max || 100)) * 100}%` }
              ]}
            />
          </View>
          <Text style={styles.progressText}>
            {playerStats.exp || 0} / {playerStats.exp_max || 100}
          </Text>
        </View>
      </View>

      {/* 자산 정보 */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>💰 자산</Text>
        <View style={styles.assetBox}>
          <View style={styles.assetItem}>
            <Text style={styles.assetLabel}>보유 금액</Text>
            <Text style={[styles.assetValue, { color: '#22c55e' }]}>
              ₩{(playerStats.money || 0).toLocaleString()}
            </Text>
          </View>
          <View style={styles.assetItem}>
            <Text style={styles.assetLabel}>스탯 포인트</Text>
            <Text style={[styles.assetValue, { color: '#f59e0b' }]}>
              {playerStats.stat_points || 0}
            </Text>
          </View>
        </View>

        {/* 스탯 분배 버튼 */}
        {(playerStats.stat_points || 0) > 0 && (
          <TouchableOpacity
            style={styles.allocateButton}
            onPress={() => navigation.navigate('AllocateStats')}
          >
            <Text style={styles.allocateButtonText}>📊 스탯 분배</Text>
          </TouchableOpacity>
        )}
      </View>
    </View>
  );

  const renderTierTab = () => (
    <View style={styles.tabContent}>
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>🏆 현재 티어</Text>
        <View style={styles.tierBox}>
          <Text style={styles.tierName}>{playerStats.tier || 'Bronze V'}</Text>
          <View style={styles.tierProgressBar}>
            <View
              style={[
                styles.tierProgressFill,
                { width: `${(playerStats.tier_progress || 0)}%` }
              ]}
            />
          </View>
          <Text style={styles.tierProgress}>{playerStats.tier_progress || 0}% 진행</Text>
        </View>

        <Text style={[styles.sectionTitle, { marginTop: 20 }]}>📈 티어 목록</Text>
        <View style={styles.tierList}>
          {playerStats.tier_list?.map((tier, idx) => (
            <View
              key={idx}
              style={[styles.tierItem, tier.current && styles.activeTierItem]}
            >
              <Text style={tier.current ? styles.activeTierText : styles.tierItemText}>
                {tier.current ? '▶ ' : '  '}{tier.name}
              </Text>
            </View>
          )) || (
            <Text style={styles.tierItemText}>티어 정보 없음</Text>
          )}
        </View>
      </View>
    </View>
  );

  const renderSituationTab = () => (
    <View style={styles.tabContent}>
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>💼 현재 상황</Text>

        <View style={styles.situationBox}>
          <Text style={styles.situationTitle}>직업</Text>
          <Text style={styles.situationValue}>{playerStats.job || '없음'}</Text>
          <Text style={styles.situationDesc}>
            월급: ₩{(playerStats.salary || 0).toLocaleString()}
          </Text>
        </View>

        <View style={styles.situationBox}>
          <Text style={styles.situationTitle}>부동산</Text>
          <Text style={styles.situationValue}>{playerStats.property || '없음'}</Text>
          {playerStats.rent && (
            <Text style={styles.situationDesc}>월세: ₩{playerStats.rent.toLocaleString()}</Text>
          )}
        </View>

        <View style={styles.situationBox}>
          <Text style={styles.situationTitle}>스킬</Text>
          <Text style={styles.situationValue}>{playerStats.skills_owned || 0}개 소유</Text>
        </View>
      </View>
    </View>
  );

  const renderStatsTab = () => (
    <View style={styles.tabContent}>
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>⚡ 능력치</Text>

        <View style={styles.abilitiesGrid}>
          {[
            { label: '💪 힘', value: playerStats.strength || 0 },
            { label: '🧠 지능', value: playerStats.intelligence || 0 },
            { label: '✨ 매력', value: playerStats.charm || 0 },
            { label: '❤️ 체력', value: playerStats.stamina_stat || 0 },
            { label: '🍀 운', value: playerStats.luck || 0 }
          ].map((ability, idx) => (
            <View key={idx} style={styles.abilityBox}>
              <Text style={styles.abilityLabel}>{ability.label}</Text>
              <Text style={styles.abilityValue}>{ability.value}</Text>
              <View style={styles.abilityBar}>
                <View
                  style={[
                    styles.abilityBarFill,
                    { width: `${(ability.value / 20) * 100}%` }
                  ]}
                />
              </View>
            </View>
          ))}
        </View>
      </View>
    </View>
  );

  return (
    <ScrollView
      style={styles.container}
      refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor="#6366f1" />}
    >
      <Text style={styles.title}>📊 대시보드</Text>

      {/* 탭 버튼 */}
      <View style={styles.tabButtons}>
        {['status', 'tier', 'situation', 'stats'].map((tab) => (
          <TouchableOpacity
            key={tab}
            style={[styles.tabButton, activeTab === tab && styles.activeTabButton]}
            onPress={() => setActiveTab(tab)}
          >
            <Text style={activeTab === tab ? styles.activeTabText : styles.tabText}>
              {tab === 'status' ? '상태' : tab === 'tier' ? '티어' : tab === 'situation' ? '상황' : '능력치'}
            </Text>
          </TouchableOpacity>
        ))}
      </View>

      {/* 탭 콘텐츠 */}
      {activeTab === 'status' && renderStatusTab()}
      {activeTab === 'tier' && renderTierTab()}
      {activeTab === 'situation' && renderSituationTab()}
      {activeTab === 'stats' && renderStatsTab()}
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
    marginBottom: 15
  },
  errorText: {
    color: '#ef4444',
    fontSize: 16,
    textAlign: 'center'
  },
  tabButtons: {
    flexDirection: 'row',
    marginBottom: 20,
    backgroundColor: '#2a2a2a',
    borderRadius: 8,
    padding: 4,
    gap: 4
  },
  tabButton: {
    flex: 1,
    paddingVertical: 10,
    borderRadius: 6,
    alignItems: 'center'
  },
  activeTabButton: {
    backgroundColor: '#6366f1'
  },
  tabText: {
    color: '#aaa',
    fontSize: 12,
    fontWeight: '600'
  },
  activeTabText: {
    color: '#fff',
    fontSize: 12,
    fontWeight: '600'
  },
  tabContent: {
    marginBottom: 30
  },
  section: {
    marginBottom: 20
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#fff',
    marginBottom: 12
  },
  statsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 8
  },
  statBox: {
    width: '48%',
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
    fontSize: 14,
    fontWeight: 'bold'
  },
  progressCard: {
    backgroundColor: '#2a2a2a',
    padding: 15,
    borderRadius: 8
  },
  progressBar: {
    height: 10,
    backgroundColor: '#1a1a1a',
    borderRadius: 5,
    overflow: 'hidden',
    marginBottom: 8
  },
  progressFill: {
    height: '100%',
    backgroundColor: '#6366f1'
  },
  progressText: {
    color: '#aaa',
    fontSize: 12
  },
  assetBox: {
    backgroundColor: '#2a2a2a',
    padding: 15,
    borderRadius: 8
  },
  assetItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingVertical: 8
  },
  assetLabel: {
    color: '#aaa',
    fontSize: 13
  },
  assetValue: {
    fontSize: 14,
    fontWeight: 'bold'
  },
  tierBox: {
    backgroundColor: '#2a2a2a',
    padding: 15,
    borderRadius: 8,
    marginBottom: 15
  },
  tierName: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
    marginBottom: 10
  },
  tierProgressBar: {
    height: 8,
    backgroundColor: '#1a1a1a',
    borderRadius: 4,
    overflow: 'hidden',
    marginBottom: 8
  },
  tierProgressFill: {
    height: '100%',
    backgroundColor: '#f59e0b'
  },
  tierProgress: {
    color: '#aaa',
    fontSize: 12
  },
  tierList: {
    gap: 6
  },
  tierItem: {
    backgroundColor: '#2a2a2a',
    padding: 10,
    borderRadius: 6
  },
  activeTierItem: {
    backgroundColor: '#1a4d7d',
    borderLeftWidth: 3,
    borderLeftColor: '#6366f1'
  },
  tierItemText: {
    color: '#aaa',
    fontSize: 12
  },
  activeTierText: {
    color: '#6366f1',
    fontSize: 12,
    fontWeight: 'bold'
  },
  situationBox: {
    backgroundColor: '#2a2a2a',
    padding: 15,
    borderRadius: 8,
    marginBottom: 12
  },
  situationTitle: {
    color: '#6366f1',
    fontSize: 13,
    fontWeight: 'bold',
    marginBottom: 5
  },
  situationValue: {
    color: '#fff',
    fontSize: 14,
    fontWeight: '600',
    marginBottom: 5
  },
  situationDesc: {
    color: '#999',
    fontSize: 12
  },
  abilitiesGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 10
  },
  abilityBox: {
    width: '48%',
    backgroundColor: '#2a2a2a',
    padding: 12,
    borderRadius: 8
  },
  abilityLabel: {
    color: '#aaa',
    fontSize: 12,
    marginBottom: 5
  },
  abilityValue: {
    color: '#fff',
    fontSize: 14,
    fontWeight: 'bold',
    marginBottom: 5
  },
  abilityBar: {
    height: 6,
    backgroundColor: '#1a1a1a',
    borderRadius: 3,
    overflow: 'hidden'
  },
  abilityBarFill: {
    height: '100%',
    backgroundColor: '#6366f1'
  },
  allocateButton: {
    marginTop: 15,
    backgroundColor: '#6366f1',
    paddingVertical: 12,
    borderRadius: 8,
    alignItems: 'center'
  },
  allocateButtonText: {
    color: '#fff',
    fontSize: 14,
    fontWeight: '600'
  }
});
