import React, { useState, useEffect } from 'react';
import { View, Text, TouchableOpacity, StyleSheet, FlatList, Alert, ActivityIndicator, Modal, Vibration } from 'react-native';

export default function JobScreen({ navigation }) {
  const [jobs, setJobs] = useState([
    {
      id: 1,
      name: '편의점 직원',
      difficulty: '초급',
      salary: 5000,
      requirements: { strength: 1, intelligence: 1, charm: 1, stamina: 1, luck: 1 }
    },
    {
      id: 2,
      name: '식당 종업원',
      difficulty: '초급',
      salary: 6000,
      requirements: { strength: 2, intelligence: 1, charm: 2, stamina: 2, luck: 1 }
    },
    {
      id: 3,
      name: '사무직 직원',
      difficulty: '중급',
      salary: 15000,
      requirements: { strength: 2, intelligence: 5, charm: 2, stamina: 3, luck: 2 }
    },
    {
      id: 4,
      name: '개발자',
      difficulty: '중급',
      salary: 20000,
      requirements: { strength: 2, intelligence: 8, charm: 1, stamina: 3, luck: 3 }
    },
    {
      id: 5,
      name: '마케터',
      difficulty: '중급',
      salary: 18000,
      requirements: { strength: 2, intelligence: 5, charm: 6, stamina: 3, luck: 2 }
    },
    {
      id: 6,
      name: '의사',
      difficulty: '고급',
      salary: 40000,
      requirements: { strength: 3, intelligence: 10, charm: 5, stamina: 5, luck: 4 }
    },
    {
      id: 7,
      name: 'CEO',
      difficulty: '전문직',
      salary: 100000,
      requirements: { strength: 5, intelligence: 10, charm: 10, stamina: 8, luck: 10 }
    }
  ]);
  const [currentJob, setCurrentJob] = useState(null);
  const [playerStats, setPlayerStats] = useState({
    strength: 5,
    intelligence: 5,
    charm: 3,
    stamina: 4,
    luck: 2,
    money: 50000
  });
  const [selectedJob, setSelectedJob] = useState(null);
  const [modalVisible, setModalVisible] = useState(false);

  const canApplyForJob = (job) => {
    return (
      playerStats.strength >= job.requirements.strength &&
      playerStats.intelligence >= job.requirements.intelligence &&
      playerStats.charm >= job.requirements.charm &&
      playerStats.stamina >= job.requirements.stamina &&
      playerStats.luck >= job.requirements.luck
    );
  };

  const handleApplyJob = (job) => {
    if (!canApplyForJob(job)) {
      Alert.alert('불가능', '스탯이 부족합니다.');
      Vibration.vibrate(200);
      return;
    }

    Vibration.vibrate([0, 100, 50, 100]);
    setCurrentJob(job);
    Alert.alert('성공', `${job.name}에 취업했습니다!\n월급: ${job.salary}원`);
    setModalVisible(false);
  };

  const handleWork = () => {
    if (!currentJob) {
      Alert.alert('알림', '먼저 직업을 선택해주세요.');
      return;
    }

    Vibration.vibrate([0, 100, 50, 100, 50, 100]);
    const newMoney = playerStats.money + currentJob.salary;
    setPlayerStats({ ...playerStats, money: newMoney });
    Alert.alert('성공', `${currentJob.salary}원을 벌었습니다!`);
  };

  const getDifficultyColor = (difficulty) => {
    const colors = {
      '초급': '#3b82f6',
      '중급': '#f59e0b',
      '고급': '#ef4444',
      '전문직': '#8b5cf6'
    };
    return colors[difficulty] || '#666';
  };

  const renderJobCard = ({ item }) => (
    <TouchableOpacity
      style={[
        styles.jobCard,
        { borderLeftColor: getDifficultyColor(item.difficulty) },
        currentJob?.id === item.id && styles.activeJob
      ]}
      onPress={() => {
        setSelectedJob(item);
        setModalVisible(true);
      }}
    >
      <View style={styles.jobHeader}>
        <View style={{ flex: 1 }}>
          <Text style={styles.jobName}>{item.name}</Text>
          <Text style={styles.jobDifficulty}>{item.difficulty}</Text>
        </View>
        <Text style={styles.jobSalary}>${item.salary}</Text>
      </View>

      {currentJob?.id === item.id && (
        <Text style={styles.currentBadge}>✓ 현재 직업</Text>
      )}

      {canApplyForJob(item) ? (
        <Text style={styles.canApply}>지원 가능</Text>
      ) : (
        <Text style={styles.cannotApply}>스탯 부족</Text>
      )}
    </TouchableOpacity>
  );

  return (
    <View style={styles.container}>
      <Text style={styles.title}>💼 직업</Text>

      {/* 현재 직업 & 돈 */}
      <View style={styles.statusBox}>
        <View>
          <Text style={styles.statusLabel}>현재 직업</Text>
          <Text style={styles.statusValue}>{currentJob?.name || '없음'}</Text>
        </View>
        <View>
          <Text style={styles.statusLabel}>보유 금액</Text>
          <Text style={[styles.statusValue, { color: '#22c55e' }]}>${playerStats.money}</Text>
        </View>
      </View>

      {/* 근무하기 버튼 */}
      {currentJob && (
        <TouchableOpacity style={styles.workButton} onPress={handleWork}>
          <Text style={styles.workButtonText}>
            💰 근무하기 (+${currentJob.salary})
          </Text>
        </TouchableOpacity>
      )}

      {/* 직업 목록 */}
      <FlatList
        data={jobs}
        renderItem={renderJobCard}
        keyExtractor={(item) => item.id.toString()}
        contentContainerStyle={styles.listContainer}
        scrollEnabled={true}
      />

      {/* 직업 상세 모달 */}
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

            {selectedJob && (
              <>
                <Text style={styles.modalTitle}>{selectedJob.name}</Text>

                <View style={styles.detailBox}>
                  <View style={styles.detailRow}>
                    <Text style={styles.detailLabel}>난이도</Text>
                    <Text
                      style={[
                        styles.detailValue,
                        { color: getDifficultyColor(selectedJob.difficulty) }
                      ]}
                    >
                      {selectedJob.difficulty}
                    </Text>
                  </View>

                  <View style={styles.detailRow}>
                    <Text style={styles.detailLabel}>월급</Text>
                    <Text style={[styles.detailValue, { color: '#22c55e' }]}>
                      ${selectedJob.salary}
                    </Text>
                  </View>

                  <View style={styles.divider} />

                  <Text style={styles.requirementTitle}>📊 필요 스탯</Text>
                  <View style={styles.requirementList}>
                    <Text style={styles.requirementItem}>
                      💪 힘: {selectedJob.requirements.strength} (현재: {playerStats.strength})
                    </Text>
                    <Text style={styles.requirementItem}>
                      🧠 지능: {selectedJob.requirements.intelligence} (현재: {playerStats.intelligence})
                    </Text>
                    <Text style={styles.requirementItem}>
                      ✨ 매력: {selectedJob.requirements.charm} (현재: {playerStats.charm})
                    </Text>
                    <Text style={styles.requirementItem}>
                      ❤️ 체력: {selectedJob.requirements.stamina} (현재: {playerStats.stamina})
                    </Text>
                    <Text style={styles.requirementItem}>
                      🍀 운: {selectedJob.requirements.luck} (현재: {playerStats.luck})
                    </Text>
                  </View>
                </View>

                <TouchableOpacity
                  style={[
                    styles.applyButton,
                    !canApplyForJob(selectedJob) && styles.disabledButton
                  ]}
                  onPress={() => handleApplyJob(selectedJob)}
                  disabled={!canApplyForJob(selectedJob)}
                >
                  <Text style={styles.applyButtonText}>지원하기</Text>
                </TouchableOpacity>

                <TouchableOpacity
                  style={styles.closeModalButton}
                  onPress={() => setModalVisible(false)}
                >
                  <Text style={styles.closeModalButtonText}>닫기</Text>
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
    marginBottom: 15
  },
  statusBox: {
    backgroundColor: '#2a2a2a',
    padding: 15,
    borderRadius: 8,
    marginBottom: 15,
    flexDirection: 'row',
    justifyContent: 'space-between'
  },
  statusLabel: {
    color: '#aaa',
    fontSize: 12,
    marginBottom: 5
  },
  statusValue: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold'
  },
  workButton: {
    backgroundColor: '#22c55e',
    padding: 15,
    borderRadius: 8,
    marginBottom: 15,
    alignItems: 'center'
  },
  workButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold'
  },
  listContainer: {
    gap: 10
  },
  jobCard: {
    backgroundColor: '#2a2a2a',
    padding: 15,
    borderRadius: 8,
    borderLeftWidth: 4
  },
  activeJob: {
    backgroundColor: '#1f3a1f',
    borderLeftColor: '#22c55e'
  },
  jobHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 10
  },
  jobName: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold'
  },
  jobDifficulty: {
    color: '#aaa',
    fontSize: 12,
    marginTop: 5
  },
  jobSalary: {
    color: '#22c55e',
    fontSize: 14,
    fontWeight: 'bold'
  },
  currentBadge: {
    color: '#22c55e',
    fontSize: 12,
    fontWeight: 'bold',
    marginBottom: 5
  },
  canApply: {
    color: '#22c55e',
    fontSize: 12
  },
  cannotApply: {
    color: '#ef4444',
    fontSize: 12
  },
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
    paddingBottom: 40
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
  detailBox: {
    backgroundColor: '#1a1a1a',
    padding: 15,
    borderRadius: 8,
    marginBottom: 20
  },
  detailRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#3a3a3a'
  },
  detailLabel: {
    color: '#aaa',
    fontSize: 12
  },
  detailValue: {
    color: '#fff',
    fontSize: 14,
    fontWeight: 'bold'
  },
  divider: {
    height: 1,
    backgroundColor: '#3a3a3a',
    marginVertical: 10
  },
  requirementTitle: {
    color: '#fff',
    fontSize: 13,
    fontWeight: 'bold',
    marginBottom: 10
  },
  requirementList: {
    gap: 8
  },
  requirementItem: {
    color: '#bbb',
    fontSize: 12
  },
  applyButton: {
    backgroundColor: '#6366f1',
    padding: 15,
    borderRadius: 8,
    alignItems: 'center',
    marginBottom: 10
  },
  disabledButton: {
    backgroundColor: '#666'
  },
  applyButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold'
  },
  closeModalButton: {
    backgroundColor: '#ef4444',
    padding: 12,
    borderRadius: 8,
    alignItems: 'center'
  },
  closeModalButtonText: {
    color: '#fff',
    fontSize: 14,
    fontWeight: 'bold'
  }
});
