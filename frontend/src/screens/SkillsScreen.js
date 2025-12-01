import React, { useState, useEffect } from 'react';
import { View, Text, TouchableOpacity, StyleSheet, FlatList, Alert, ActivityIndicator, Modal } from 'react-native';
import { skillsAPI } from '../services/api';

export default function SkillsScreen({ navigation }) {
  const [currentSkills, setCurrentSkills] = useState([]);
  const [acquiredSkills, setAcquiredSkills] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedSkill, setSelectedSkill] = useState(null);
  const [replaceMode, setReplaceMode] = useState(false);
  const [replaceTarget, setReplaceTarget] = useState(null);
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
      const response = await skillsAPI.replace(oldSkill.이름, newSkill.이름);
      if (response.data.success) {
        Alert.alert('성공', response.data.data.message);
        loadSkills();
        setModalVisible(false);
        setReplaceMode(false);
      }
    } catch (error) {
      Alert.alert('오류', '스킬 교체 실패');
    }
  };

  const renderSkillCard = ({ item, index }) => (
    <TouchableOpacity
      style={styles.skillCard}
      onPress={() => {
        setSelectedSkill(item);
        setReplaceTarget({ skill: item, type: 'current', index });
        setModalVisible(true);
      }}
    >
      <View style={styles.skillHeader}>
        <Text style={styles.skillName}>{item.이름}</Text>
        <Text style={styles.skillSlot}>슬롯 {index + 1}/4</Text>
      </View>
      <View style={styles.skillStats}>
        <Text style={styles.skillStat}>
          데미지: {item.데미지_최소}-{item.데미지_최대}
        </Text>
        <Text style={styles.skillStat}>
          횟수: {item.사용_횟수}
        </Text>
      </View>
    </TouchableOpacity>
  );

  const renderAcquiredSkill = ({ item }) => (
    <TouchableOpacity
      style={styles.acquiredSkillCard}
      onPress={() => {
        setSelectedSkill(item);
        setReplaceTarget({ skill: item, type: 'acquired' });
        setReplaceMode(true);
        setModalVisible(true);
      }}
    >
      <Text style={styles.acquiredSkillName}>{item.이름}</Text>
      <Text style={styles.acquiredSkillInfo}>
        데미지: {item.데미지_최소}-{item.데미지_최대}
      </Text>
    </TouchableOpacity>
  );

  if (loading) {
    return (
      <View style={styles.container}>
        <ActivityIndicator color="#6366f1" size="large" />
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <Text style={styles.title}>스킬</Text>

      {/* 현재 스킬 */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>
          현재 스킬 ({currentSkills.length}/{4})
        </Text>
        <FlatList
          data={currentSkills}
          renderItem={renderSkillCard}
          keyExtractor={(item, idx) => `current-${idx}`}
          scrollEnabled={false}
          contentContainerStyle={styles.skillList}
        />
      </View>

      {/* 획득한 스킬 */}
      {acquiredSkills.length > 0 && (
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>
            획득한 스킬 ({acquiredSkills.length})
          </Text>
          <Text style={styles.acquiredSubtext}>
            현재 스킬과 교체하려면 선택하세요
          </Text>
          <FlatList
            data={acquiredSkills}
            renderItem={renderAcquiredSkill}
            keyExtractor={(item, idx) => `acquired-${idx}`}
            scrollEnabled={false}
            contentContainerStyle={styles.acquiredList}
            numColumns={2}
          />
        </View>
      )}

      {/* 스킬 상세 & 교체 모달 */}
      <Modal
        visible={modalVisible}
        transparent={true}
        animationType="slide"
        onRequestClose={() => setModalVisible(false)}
      >
        <View style={styles.modalContainer}>
          <View style={styles.modalContent}>
            <TouchableOpacity
              style={styles.closeButton}
              onPress={() => setModalVisible(false)}
            >
              <Text style={styles.closeButtonText}>✕</Text>
            </TouchableOpacity>

            {selectedSkill && (
              <>
                <Text style={styles.modalTitle}>{selectedSkill.이름}</Text>

                <View style={styles.modalStats}>
                  <View style={styles.modalStatItem}>
                    <Text style={styles.modalStatLabel}>최소 데미지</Text>
                    <Text style={styles.modalStatValue}>
                      {selectedSkill.데미지_최소}
                    </Text>
                  </View>
                  <View style={styles.modalStatItem}>
                    <Text style={styles.modalStatLabel}>최대 데미지</Text>
                    <Text style={styles.modalStatValue}>
                      {selectedSkill.데미지_최대}
                    </Text>
                  </View>
                </View>

                <View style={styles.modalStats}>
                  <View style={styles.modalStatItem}>
                    <Text style={styles.modalStatLabel}>사용 횟수</Text>
                    <Text style={styles.modalStatValue}>
                      {selectedSkill.사용_횟수}
                    </Text>
                  </View>
                  <View style={styles.modalStatItem}>
                    <Text style={styles.modalStatLabel}>타입</Text>
                    <Text style={styles.modalStatValue}>
                      {selectedSkill.타입 || '일반'}
                    </Text>
                  </View>
                </View>

                {replaceMode && replaceTarget?.type === 'acquired' && currentSkills.length > 0 && (
                  <>
                    <Text style={styles.replaceText}>
                      교체할 현재 스킬을 선택하세요
                    </Text>
                    <FlatList
                      data={currentSkills}
                      renderItem={({ item, index }) => (
                        <TouchableOpacity
                          style={styles.replaceOption}
                          onPress={() =>
                            handleReplaceSkill(item, selectedSkill)
                          }
                        >
                          <Text style={styles.replaceOptionText}>
                            {item.이름} (슬롯 {index + 1})
                          </Text>
                          <Text style={styles.replaceOptionArrow}>→</Text>
                        </TouchableOpacity>
                      )}
                      keyExtractor={(item, idx) => `replace-${idx}`}
                      scrollEnabled={false}
                    />
                  </>
                )}

                <TouchableOpacity
                  style={styles.modalCloseButton}
                  onPress={() => setModalVisible(false)}
                >
                  <Text style={styles.modalCloseButtonText}>닫기</Text>
                </TouchableOpacity>
              </>
            )}
          </View>
        </View>
      </Modal>
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
    marginBottom: 20
  },
  section: {
    marginBottom: 30
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#6366f1',
    marginBottom: 10
  },
  acquiredSubtext: {
    fontSize: 12,
    color: '#aaa',
    marginBottom: 10
  },
  skillList: {
    gap: 10
  },
  skillCard: {
    backgroundColor: '#2a2a2a',
    padding: 15,
    borderRadius: 8,
    borderLeftWidth: 4,
    borderLeftColor: '#6366f1',
    marginBottom: 5
  },
  skillHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 10
  },
  skillName: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
    flex: 1
  },
  skillSlot: {
    color: '#aaa',
    fontSize: 12
  },
  skillStats: {
    gap: 5
  },
  skillStat: {
    color: '#aaa',
    fontSize: 12
  },
  acquiredList: {
    gap: 10
  },
  acquiredSkillCard: {
    flex: 1,
    backgroundColor: '#2a2a2a',
    padding: 12,
    borderRadius: 8,
    borderWidth: 2,
    borderColor: '#44aa00',
    marginHorizontal: 5,
    marginBottom: 10
  },
  acquiredSkillName: {
    color: '#fff',
    fontSize: 14,
    fontWeight: 'bold',
    marginBottom: 5
  },
  acquiredSkillInfo: {
    color: '#aaa',
    fontSize: 11
  },
  // Modal
  modalContainer: {
    flex: 1,
    backgroundColor: 'rgba(0, 0, 0, 0.9)',
    justifyContent: 'flex-end'
  },
  modalContent: {
    backgroundColor: '#2a2a2a',
    borderTopLeftRadius: 20,
    borderTopRightRadius: 20,
    padding: 20,
    paddingBottom: 40,
    maxHeight: '80%'
  },
  closeButton: {
    position: 'absolute',
    top: 15,
    right: 15,
    width: 30,
    height: 30,
    justifyContent: 'center',
    alignItems: 'center'
  },
  closeButtonText: {
    color: '#fff',
    fontSize: 24
  },
  modalTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#fff',
    marginBottom: 20,
    marginTop: 10
  },
  modalStats: {
    flexDirection: 'row',
    gap: 10,
    marginBottom: 15
  },
  modalStatItem: {
    flex: 1,
    backgroundColor: '#1a1a1a',
    padding: 12,
    borderRadius: 8,
    alignItems: 'center'
  },
  modalStatLabel: {
    color: '#aaa',
    fontSize: 12,
    marginBottom: 5
  },
  modalStatValue: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#6366f1'
  },
  replaceText: {
    color: '#fff',
    fontSize: 14,
    marginBottom: 10,
    fontWeight: 'bold'
  },
  replaceOption: {
    backgroundColor: '#1a1a1a',
    padding: 12,
    borderRadius: 8,
    marginBottom: 8,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center'
  },
  replaceOptionText: {
    color: '#fff',
    fontSize: 14,
    flex: 1
  },
  replaceOptionArrow: {
    color: '#6366f1',
    fontSize: 16,
    fontWeight: 'bold'
  },
  modalCloseButton: {
    backgroundColor: '#6366f1',
    padding: 15,
    borderRadius: 8,
    alignItems: 'center',
    marginTop: 20
  },
  modalCloseButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold'
  }
});
