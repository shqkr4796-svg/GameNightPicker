import React, { useState, useEffect } from 'react';
import { View, Text, TouchableOpacity, StyleSheet, ScrollView, Alert, ActivityIndicator, Modal, Vibration } from 'react-native';
import { skillsAPI } from '../services/api';

export default function SkillsScreen({ navigation }) {
  const [currentSkills, setCurrentSkills] = useState([]);
  const [acquiredSkills, setAcquiredSkills] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedSkill, setSelectedSkill] = useState(null);
  const [replaceMode, setReplaceMode] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);

  useEffect(() => {
    loadSkills();
  }, []);

  const loadSkills = async () => {
    setLoading(true);
    try {
      const response = await skillsAPI.list();
      if (response.data.success) {
        setCurrentSkills(response.data.data.current_skills || []);
        setAcquiredSkills(response.data.data.acquired_skills || []);
      }
    } catch (error) {
      Alert.alert('오류', '스킬 데이터 로드 실패');
    } finally {
      setLoading(false);
    }
  };

  const handleReplaceSkill = async (oldSkill, newSkill) => {
    try {
      const response = await skillsAPI.replace(oldSkill.이름 || oldSkill.name, newSkill.이름 || newSkill.name);
      if (response.data.success) {
        Vibration.vibrate([0, 100, 50, 100]);
        Alert.alert('성공', '스킬이 교체되었습니다!');
        loadSkills();
        setModalVisible(false);
        setReplaceMode(false);
      }
    } catch (error) {
      Alert.alert('오류', '스킬 교체 실패');
    }
  };

  const handleAcquireSkill = async (skillName) => {
    try {
      const response = await skillsAPI.acquire(skillName);
      if (response.data.success) {
        Vibration.vibrate([0, 100, 50, 100]);
        Alert.alert('성공', '스킬을 획득했습니다!');
        loadSkills();
      }
    } catch (error) {
      Alert.alert('오류', '스킬 획득 실패');
    }
  };

  if (loading) {
    return (
      <View style={styles.container}>
        <ActivityIndicator color="#6366f1" size="large" />
      </View>
    );
  }

  const maxSlots = 4;
  const emptySlots = maxSlots - currentSkills.length;

  return (
    <ScrollView style={styles.container}>
      <Text style={styles.title}>스킬</Text>
      <Text style={styles.subtitle}>현재 장착한 스킬을 관리하세요</Text>

      {/* 현재 스킬 */}
      <View style={styles.section}>
        <View style={styles.sectionHeader}>
          <Text style={styles.sectionTitle}>⚔️ 현재 스킬</Text>
          <Text style={styles.sectionBadge}>{currentSkills.length}/{maxSlots}</Text>
        </View>

        {currentSkills.length > 0 ? (
          <View style={styles.skillList}>
            {currentSkills.map((skill, idx) => (
              <TouchableOpacity
                key={idx}
                style={styles.skillCard}
                onPress={() => {
                  setSelectedSkill(skill);
                  setReplaceMode(true);
                  setModalVisible(true);
                }}
              >
                <View style={styles.skillCardHeader}>
                  <View>
                    <Text style={styles.skillName}>{skill.이름 || skill.name}</Text>
                    <Text style={styles.slotNumber}>슬롯 {idx + 1}</Text>
                  </View>
                  <Text style={styles.skillBadge}>⚡</Text>
                </View>
                <View style={styles.skillStats}>
                  <Text style={styles.skillStat}>
                    데미지: {skill.데미지_최소 || skill.min_damage}-{skill.데미지_최대 || skill.max_damage}
                  </Text>
                  <Text style={styles.skillStat}>
                    사용: {skill.사용_횟수 || skill.uses} / {skill.최대_사용 || skill.max_uses}
                  </Text>
                </View>
              </TouchableOpacity>
            ))}
          </View>
        ) : (
          <View style={styles.emptyState}>
            <Text style={styles.emptyText}>장착된 스킬이 없습니다</Text>
          </View>
        )}

        {emptySlots > 0 && (
          <View style={styles.emptySlots}>
            <Text style={styles.emptySlotLabel}>빈 슬롯: {emptySlots}개</Text>
          </View>
        )}
      </View>

      {/* 획득한 스킬 */}
      {acquiredSkills.length > 0 && (
        <View style={styles.section}>
          <View style={styles.sectionHeader}>
            <Text style={styles.sectionTitle}>📚 획득한 스킬</Text>
            <Text style={styles.sectionBadge}>{acquiredSkills.length}</Text>
          </View>
          <Text style={styles.sectionDesc}>현재 스킬과 교체하려면 선택하세요</Text>

          <View style={styles.acquiredSkillList}>
            {acquiredSkills.map((skill, idx) => (
              <TouchableOpacity
                key={idx}
                style={styles.acquiredSkillCard}
                onPress={() => {
                  if (currentSkills.length < maxSlots) {
                    handleAcquireSkill(skill.이름 || skill.name);
                  } else {
                    setSelectedSkill(skill);
                    setReplaceMode(true);
                    setModalVisible(true);
                  }
                }}
              >
                <View style={styles.acquiredSkillHeader}>
                  <Text style={styles.acquiredSkillName}>{skill.이름 || skill.name}</Text>
                  <Text style={styles.acquiredSkillDamage}>
                    {skill.데미지_최소 || skill.min_damage}-{skill.데미지_최대 || skill.max_damage}
                  </Text>
                </View>
              </TouchableOpacity>
            ))}
          </View>
        </View>
      )}

      {/* 스킬 팁 */}
      <View style={styles.tipsCard}>
        <Text style={styles.tipsTitle}>💡 스킬 팁</Text>
        <Text style={styles.tipsText}>• 최대 {maxSlots}개의 스킬을 장착할 수 있습니다</Text>
        <Text style={styles.tipsText}>• 새로운 스킬 획득 시 기존 스킬과 교체할 수 있습니다</Text>
        <Text style={styles.tipsText}>• 각 스킬은 정해진 횟수만큼 사용할 수 있습니다</Text>
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
    marginBottom: 5
  },
  subtitle: {
    fontSize: 14,
    color: '#aaa',
    marginBottom: 20
  },
  section: {
    marginBottom: 24
  },
  sectionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#fff'
  },
  sectionBadge: {
    backgroundColor: '#6366f1',
    color: '#fff',
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 4,
    fontSize: 12,
    fontWeight: '600'
  },
  sectionDesc: {
    color: '#aaa',
    fontSize: 12,
    marginBottom: 12
  },
  skillList: {
    gap: 12
  },
  skillCard: {
    backgroundColor: '#2a2a2a',
    padding: 15,
    borderRadius: 8,
    borderLeftWidth: 4,
    borderLeftColor: '#6366f1'
  },
  skillCardHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: 10
  },
  skillName: {
    color: '#fff',
    fontSize: 15,
    fontWeight: '600',
    marginBottom: 4
  },
  slotNumber: {
    color: '#aaa',
    fontSize: 11
  },
  skillBadge: {
    fontSize: 18
  },
  skillStats: {
    gap: 4
  },
  skillStat: {
    color: '#aaa',
    fontSize: 12
  },
  emptyState: {
    backgroundColor: '#2a2a2a',
    padding: 20,
    borderRadius: 8,
    alignItems: 'center'
  },
  emptyText: {
    color: '#aaa',
    fontSize: 14
  },
  emptySlots: {
    backgroundColor: '#1a4d7d',
    padding: 12,
    borderRadius: 8,
    marginTop: 12,
    borderLeftWidth: 3,
    borderLeftColor: '#6366f1'
  },
  emptySlotLabel: {
    color: '#6366f1',
    fontSize: 12,
    fontWeight: '600'
  },
  acquiredSkillList: {
    gap: 10
  },
  acquiredSkillCard: {
    backgroundColor: '#2a2a2a',
    padding: 12,
    borderRadius: 8,
    borderWidth: 2,
    borderColor: '#3a3a3a'
  },
  acquiredSkillHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center'
  },
  acquiredSkillName: {
    color: '#fff',
    fontSize: 14,
    fontWeight: '600'
  },
  acquiredSkillDamage: {
    color: '#6366f1',
    fontSize: 12,
    fontWeight: '600'
  },
  tipsCard: {
    backgroundColor: '#2a2a2a',
    padding: 15,
    borderRadius: 8,
    marginBottom: 30,
    borderLeftWidth: 4,
    borderLeftColor: '#22c55e'
  },
  tipsTitle: {
    color: '#fff',
    fontSize: 14,
    fontWeight: '600',
    marginBottom: 8
  },
  tipsText: {
    color: '#aaa',
    fontSize: 12,
    marginBottom: 4
  }
});
