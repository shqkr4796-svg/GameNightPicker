import React, { useState } from 'react';
import { View, Text, StyleSheet, ScrollView, TouchableOpacity } from 'react-native';

export default function DashboardScreen({ navigation }) {
  const [playerStats] = useState({
    level: 15,
    exp: 450,
    expMax: 1000,
    date: 42,
    time: 14,
    health: 8.5,
    stamina: 35,
    maxStamina: 100,
    money: 150000,
    statPoints: 5,
    strength: 8,
    intelligence: 12,
    charm: 6,
    staminaStat: 10,
    luck: 5,
    tier: 'Bronze I',
    tierProgress: 65,
    job: 'Developer',
    salary: 20000,
    property: '아파트 (월세: 5,000원)',
    skills: 4
  });

  const [activeTab, setActiveTab] = useState('status');

  const renderStatusTab = () => (
    <View style={styles.tabContent}>
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>📊 기본 정보</Text>
        <View style={styles.statsGrid}>
          <View style={styles.statBox}>
            <Text style={styles.statLabel}>레벨</Text>
            <Text style={styles.statValue}>{playerStats.level}</Text>
          </View>
          <View style={styles.statBox}>
            <Text style={styles.statLabel}>경험치</Text>
            <Text style={styles.statValue}>{playerStats.exp}/{playerStats.expMax}</Text>
          </View>
          <View style={styles.statBox}>
            <Text style={styles.statLabel}>날짜</Text>
            <Text style={styles.statValue}>{playerStats.date}일</Text>
          </View>
          <View style={styles.statBox}>
            <Text style={styles.statLabel}>시간</Text>
            <Text style={styles.statValue}>{playerStats.time}시</Text>
          </View>
          <View style={styles.statBox}>
            <Text style={styles.statLabel}>건강</Text>
            <Text style={styles.statValue}>{playerStats.health}/10</Text>
          </View>
          <View style={styles.statBox}>
            <Text style={styles.statLabel}>기력</Text>
            <Text style={styles.statValue}>{playerStats.stamina}/{playerStats.maxStamina}</Text>
          </View>
        </View>
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>💰 자산</Text>
        <View style={styles.assetBox}>
          <View style={styles.assetItem}>
            <Text style={styles.assetLabel}>보유 금액</Text>
            <Text style={[styles.assetValue, { color: '#22c55e' }]}>₩{playerStats.money.toLocaleString()}</Text>
          </View>
          <View style={styles.assetItem}>
            <Text style={styles.assetLabel}>스탯 포인트</Text>
            <Text style={[styles.assetValue, { color: '#f59e0b' }]}>{playerStats.statPoints}</Text>
          </View>
        </View>
      </View>
    </View>
  );

  const renderTierTab = () => (
    <View style={styles.tabContent}>
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>🏆 현재 티어</Text>
        <View style={styles.tierBox}>
          <Text style={styles.tierName}>{playerStats.tier}</Text>
          <View style={styles.tierProgressBar}>
            <View
              style={[
                styles.tierProgressFill,
                { width: `${playerStats.tierProgress}%` }
              ]}
            />
          </View>
          <Text style={styles.tierProgress}>{playerStats.tierProgress}% 진행</Text>
        </View>

        <Text style={[styles.sectionTitle, { marginTop: 20 }]}>📈 티어 순서</Text>
        <View style={styles.tierList}>
          {['Bronze V', 'Bronze IV', 'Bronze III', 'Bronze II', 'Bronze I', 'Silver V'].map((tier, idx) => (
            <View
              key={idx}
              style={[styles.tierItem, tier === playerStats.tier && styles.activeTierItem]}
            >
              <Text style={tier === playerStats.tier ? styles.activeTierText : styles.tierItemText}>
                {tier === playerStats.tier ? '▶ ' : '  '}{tier}
              </Text>
            </View>
          ))}
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
          <Text style={styles.situationValue}>{playerStats.job}</Text>
          <Text style={styles.situationDesc}>월급: ₩{playerStats.salary.toLocaleString()}</Text>
        </View>

        <View style={styles.situationBox}>
          <Text style={styles.situationTitle}>부동산</Text>
          <Text style={styles.situationValue}>{playerStats.property}</Text>
        </View>

        <View style={styles.situationBox}>
          <Text style={styles.situationTitle}>스킬</Text>
          <Text style={styles.situationValue}>{playerStats.skills}개 소유</Text>
        </View>
      </View>
    </View>
  );

  const renderStatsTab = () => (
    <View style={styles.tabContent}>
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>⚡ 능력치</Text>

        <View style={styles.abilitiesGrid}>
          <View style={styles.abilityBox}>
            <Text style={styles.abilityLabel}>💪 힘</Text>
            <Text style={styles.abilityValue}>{playerStats.strength}</Text>
            <View style={styles.abilityBar}>
              <View
                style={[styles.abilityBarFill, { width: `${(playerStats.strength / 20) * 100}%` }]}
              />
            </View>
          </View>

          <View style={styles.abilityBox}>
            <Text style={styles.abilityLabel}>🧠 지능</Text>
            <Text style={styles.abilityValue}>{playerStats.intelligence}</Text>
            <View style={styles.abilityBar}>
              <View
                style={[styles.abilityBarFill, { width: `${(playerStats.intelligence / 20) * 100}%` }]}
              />
            </View>
          </View>

          <View style={styles.abilityBox}>
            <Text style={styles.abilityLabel}>✨ 매력</Text>
            <Text style={styles.abilityValue}>{playerStats.charm}</Text>
            <View style={styles.abilityBar}>
              <View
                style={[styles.abilityBarFill, { width: `${(playerStats.charm / 20) * 100}%` }]}
              />
            </View>
          </View>

          <View style={styles.abilityBox}>
            <Text style={styles.abilityLabel}>❤️ 체력</Text>
            <Text style={styles.abilityValue}>{playerStats.staminaStat}</Text>
            <View style={styles.abilityBar}>
              <View
                style={[styles.abilityBarFill, { width: `${(playerStats.staminaStat / 20) * 100}%` }]}
              />
            </View>
          </View>

          <View style={styles.abilityBox}>
            <Text style={styles.abilityLabel}>🍀 운</Text>
            <Text style={styles.abilityValue}>{playerStats.luck}</Text>
            <View style={styles.abilityBar}>
              <View
                style={[styles.abilityBarFill, { width: `${(playerStats.luck / 20) * 100}%` }]}
              />
            </View>
          </View>
        </View>
      </View>
    </View>
  );

  return (
    <ScrollView style={styles.container}>
      <Text style={styles.title}>📊 대시보드</Text>

      {/* 탭 버튼 */}
      <View style={styles.tabButtons}>
        <TouchableOpacity
          style={[styles.tabButton, activeTab === 'status' && styles.activeTabButton]}
          onPress={() => setActiveTab('status')}
        >
          <Text style={activeTab === 'status' ? styles.activeTabText : styles.tabText}>상태</Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={[styles.tabButton, activeTab === 'tier' && styles.activeTabButton]}
          onPress={() => setActiveTab('tier')}
        >
          <Text style={activeTab === 'tier' ? styles.activeTabText : styles.tabText}>티어</Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={[styles.tabButton, activeTab === 'situation' && styles.activeTabButton]}
          onPress={() => setActiveTab('situation')}
        >
          <Text style={activeTab === 'situation' ? styles.activeTabText : styles.tabText}>상황</Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={[styles.tabButton, activeTab === 'stats' && styles.activeTabButton]}
          onPress={() => setActiveTab('stats')}
        >
          <Text style={activeTab === 'stats' ? styles.activeTabText : styles.tabText}>능력치</Text>
        </TouchableOpacity>
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
    padding: 20
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#fff',
    marginBottom: 15
  },
  tabButtons: {
    flexDirection: 'row',
    marginBottom: 20,
    backgroundColor: '#2a2a2a',
    borderRadius: 8,
    padding: 4
  },
  tabButton: {
    flex: 1,
    paddingVertical: 10,
    paddingHorizontal: 8,
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
    fontWeight: 'bold',
    color: '#fff',
    marginBottom: 12
  },
  statsGrid: {
    display: 'flex',
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
  assetBox: {
    backgroundColor: '#2a2a2a',
    padding: 15,
    borderRadius: 8
  },
  assetItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginVertical: 8
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
    alignItems: 'center'
  },
  tierName: {
    color: '#6366f1',
    fontSize: 20,
    fontWeight: 'bold',
    marginBottom: 10
  },
  tierProgressBar: {
    width: '100%',
    height: 12,
    backgroundColor: '#3a3a3a',
    borderRadius: 6,
    marginBottom: 8,
    overflow: 'hidden'
  },
  tierProgressFill: {
    height: '100%',
    backgroundColor: '#6366f1'
  },
  tierProgress: {
    color: '#aaa',
    fontSize: 12
  },
  tierList: {
    marginTop: 10
  },
  tierItem: {
    paddingVertical: 8,
    paddingHorizontal: 12,
    backgroundColor: '#2a2a2a',
    marginVertical: 4,
    borderRadius: 6,
    borderLeftWidth: 3,
    borderLeftColor: '#3a3a3a'
  },
  activeTierItem: {
    borderLeftColor: '#6366f1',
    backgroundColor: '#1f2a4a'
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
    padding: 12,
    borderRadius: 8,
    marginBottom: 10
  },
  situationTitle: {
    color: '#6366f1',
    fontSize: 12,
    fontWeight: 'bold',
    marginBottom: 5
  },
  situationValue: {
    color: '#fff',
    fontSize: 14,
    fontWeight: 'bold',
    marginBottom: 5
  },
  situationDesc: {
    color: '#aaa',
    fontSize: 11
  },
  abilitiesGrid: {
    gap: 8
  },
  abilityBox: {
    backgroundColor: '#2a2a2a',
    padding: 12,
    borderRadius: 8,
    marginBottom: 8
  },
  abilityLabel: {
    color: '#aaa',
    fontSize: 12,
    marginBottom: 5
  },
  abilityValue: {
    color: '#6366f1',
    fontSize: 16,
    fontWeight: 'bold',
    marginBottom: 8
  },
  abilityBar: {
    height: 8,
    backgroundColor: '#3a3a3a',
    borderRadius: 4,
    overflow: 'hidden'
  },
  abilityBarFill: {
    height: '100%',
    backgroundColor: '#6366f1'
  }
});
