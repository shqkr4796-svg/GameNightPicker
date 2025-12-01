import React, { useState, useEffect } from 'react';
import { View, Text, TouchableOpacity, StyleSheet, ScrollView, Alert, ActivityIndicator, Vibration, Modal } from 'react-native';
import { dungeonAPI } from '../services/api';
import AsyncStorage from '@react-native-async-storage/async-storage';

export default function DungeonScreen({ navigation }) {
  const [dungeons, setDungeons] = useState([]);
  const [selectedDungeon, setSelectedDungeon] = useState(null);
  const [quizActive, setQuizActive] = useState(false);
  const [currentQuestion, setCurrentQuestion] = useState(null);
  const [score, setScore] = useState(0);
  const [loading, setLoading] = useState(true);
  const [questionIndex, setQuestionIndex] = useState(0);
  const [hintUsed, setHintUsed] = useState(false);
  const [hintOptions, setHintOptions] = useState(null);
  const [dungeonInventory, setDungeonInventory] = useState({});
  const [showItemModal, setShowItemModal] = useState(false);

  useEffect(() => {
    loadDungeonData();
  }, []);

  const loadDungeonData = async () => {
    setLoading(true);
    try {
      const response = await dungeonAPI.list();
      if (response.data.success) {
        setDungeons(response.data.data.dungeons || []);
      }
    } catch (error) {
      Alert.alert('오류', '던전 데이터 로드 실패');
    } finally {
      setLoading(false);
    }
  };

  const handleStartDungeon = async (dungeon) => {
    setSelectedDungeon(dungeon);
    Vibration.vibrate([0, 100, 50, 100]);

    try {
      // 던전 인벤토리 로드
      const playerStr = await AsyncStorage.getItem('player_data');
      if (playerStr) {
        const player = JSON.parse(playerStr);
        setDungeonInventory(player.dungeonInventory || {});
      }

      const response = await dungeonAPI.start(dungeon.id);
      if (response.data.success) {
        setQuizActive(true);
        setScore(0);
        setQuestionIndex(0);
        setHintUsed(false);
        setHintOptions(null);
        setCurrentQuestion(response.data.data.first_question);
      }
    } catch (error) {
      Alert.alert('오류', '던전 시작 실패');
    }
  };

  const handleUseItem = (itemName) => {
    Alert.alert(
      `🎁 ${itemName} 사용`,
      `이 아이템을 사용할까요?`,
      [
        { text: '취소', style: 'cancel' },
        {
          text: '사용',
          onPress: async () => {
            try {
              const playerStr = await AsyncStorage.getItem('player_data');
              if (playerStr) {
                const player = JSON.parse(playerStr);
                
                // 아이템 사용 - 인벤토리에서 제거
                if (player.dungeonInventory && player.dungeonInventory[itemName]) {
                  player.dungeonInventory[itemName]--;
                  if (player.dungeonInventory[itemName] === 0) {
                    delete player.dungeonInventory[itemName];
                  }
                  
                  await AsyncStorage.setItem('player_data', JSON.stringify(player));
                  setDungeonInventory(player.dungeonInventory || {});
                  
                  Vibration.vibrate([0, 100, 50, 100]);
                  Alert.alert('✨ 아이템 사용됨', `${itemName}의 효과가 적용되었습니다!`);
                  setShowItemModal(false);
                }
              }
            } catch (error) {
              Alert.alert('오류', '아이템 사용 실패');
            }
          }
        }
      ]
    );
  };

  const handleUseHint = () => {
    if (!currentQuestion || hintUsed) return;
    
    // 4개 선택지 중 정답 1개 + 오답 1개만 남기기
    const correctAnswer = currentQuestion.options[0];
    const wrongAnswers = currentQuestion.options.slice(1);
    const selectedWrong = wrongAnswers[Math.floor(Math.random() * wrongAnswers.length)];
    
    const reduced = [correctAnswer, selectedWrong].sort(() => Math.random() - 0.5);
    
    setHintUsed(true);
    setHintOptions(reduced);
    Alert.alert('💡 힌트 사용됨', '선택지가 2개로 줄어들었습니다!');
    Vibration.vibrate([0, 100, 50, 100]);
  };

  const handleSkipQuestion = () => {
    if (!currentQuestion) return;
    
    Alert.alert(
      '⏭️ 문제 스킵',
      '이 문제를 넘어갈까요?\n(경험치를 받지 못합니다)',
      [
        { text: '취소', style: 'cancel' },
        {
          text: '넘어가기',
          onPress: async () => {
            try {
              const response = await dungeonAPI.answer(selectedDungeon.id, '스킵');
              if (response.data.next_question) {
                setCurrentQuestion(response.data.next_question);
                setQuestionIndex(questionIndex + 1);
                setHintUsed(false);
                setHintOptions(null);
              } else {
                await completeDungeon();
              }
            } catch (error) {
              Alert.alert('오류', '스킵 처리 실패');
            }
          }
        }
      ]
    );
  };

  const handleAnswerQuestion = async (answer) => {
    if (!currentQuestion) return;

    try {
      const response = await dungeonAPI.answer(selectedDungeon.id, answer);

      if (response.data.correct) {
        Vibration.vibrate([0, 100, 50, 100]);
        setScore(score + 10);

        if (response.data.next_question) {
          setCurrentQuestion(response.data.next_question);
          setQuestionIndex(questionIndex + 1);
        } else {
          // 던전 완료
          await completeDungeon();
        }
      } else {
        Vibration.vibrate([0, 200]);
        Alert.alert('오답', `정답: ${response.data.correct_answer}`);
        
        if (response.data.next_question) {
          setCurrentQuestion(response.data.next_question);
          setQuestionIndex(questionIndex + 1);
        }
      }
    } catch (error) {
      Alert.alert('오류', '답변 처리 실패');
    }
  };

  const completeDungeon = async () => {
    try {
      const response = await dungeonAPI.complete(selectedDungeon.id);
      if (response.data.success) {
        Alert.alert(
          '던전 완료!',
          `점수: ${score}점\n보상: ${response.data.rewards || '경험치 +100'}`,
          [
            {
              text: '확인',
              onPress: () => {
                setQuizActive(false);
                setSelectedDungeon(null);
                loadDungeonData();
              }
            }
          ]
        );
      }
    } catch (error) {
      Alert.alert('오류', '던전 완료 처리 실패');
    }
  };

  if (loading) {
    return (
      <View style={styles.container}>
        <ActivityIndicator color="#6366f1" size="large" />
      </View>
    );
  }

  if (quizActive && currentQuestion) {
    const displayOptions = hintOptions || currentQuestion.options;
    
    return (
      <ScrollView style={styles.container}>
        <View style={styles.quizHeader}>
          <Text style={styles.dungeonName}>{selectedDungeon?.name}</Text>
          <Text style={styles.scoreText}>점수: {score}점</Text>
        </View>

        <View style={styles.questionContainer}>
          <Text style={styles.questionNumber}>문제 {questionIndex + 1}</Text>
          <Text style={styles.question}>{currentQuestion.text}</Text>
          {hintUsed && <Text style={styles.hintBadge}>💡 힌트 사용됨</Text>}
        </View>

        <View style={styles.optionsContainer}>
          {displayOptions?.map((option, idx) => (
            <TouchableOpacity
              key={idx}
              style={styles.optionButton}
              onPress={() => handleAnswerQuestion(option)}
            >
              <Text style={styles.optionText}>{option}</Text>
            </TouchableOpacity>
          ))}
        </View>

        <View style={styles.actionButtons}>
          <TouchableOpacity
            style={[styles.actionButton, hintUsed && styles.actionButtonDisabled]}
            onPress={handleUseHint}
            disabled={hintUsed}
          >
            <Text style={styles.actionButtonText}>💡 힌트</Text>
          </TouchableOpacity>
          <TouchableOpacity
            style={styles.actionButton}
            onPress={handleSkipQuestion}
          >
            <Text style={styles.actionButtonText}>⏭️ 스킵</Text>
          </TouchableOpacity>
          {Object.keys(dungeonInventory).length > 0 && (
            <TouchableOpacity
              style={styles.actionButton}
              onPress={() => setShowItemModal(true)}
            >
              <Text style={styles.actionButtonText}>🎁 아이템</Text>
            </TouchableOpacity>
          )}
        </View>

        {/* 아이템 선택 모달 */}
        <Modal
          visible={showItemModal}
          transparent
          animationType="slide"
          onRequestClose={() => setShowItemModal(false)}
        >
          <View style={styles.modalOverlay}>
            <View style={styles.modalContent}>
              <Text style={styles.modalTitle}>🎁 던전 아이템 사용</Text>
              
              <ScrollView style={styles.itemList}>
                {Object.entries(dungeonInventory).map(([itemName, count]) => (
                  <TouchableOpacity
                    key={itemName}
                    style={styles.itemButton}
                    onPress={() => handleUseItem(itemName)}
                  >
                    <View>
                      <Text style={styles.itemName}>{itemName}</Text>
                      <Text style={styles.itemCount}>보유: {count}개</Text>
                    </View>
                    <Text style={styles.useButtonText}>사용</Text>
                  </TouchableOpacity>
                ))}
              </ScrollView>

              <TouchableOpacity
                style={styles.modalCloseButton}
                onPress={() => setShowItemModal(false)}
              >
                <Text style={styles.modalCloseButtonText}>닫기</Text>
              </TouchableOpacity>
            </View>
          </View>
        </Modal>
      </ScrollView>
    );
  }

  return (
    <ScrollView style={styles.container}>
      <Text style={styles.title}>단어 던전</Text>
      <Text style={styles.subtitle}>던전을 선택하여 어려운 단어들을 정복하세요</Text>

      <View style={styles.dungeonList}>
        {dungeons.map((dungeon, idx) => (
          <TouchableOpacity
            key={idx}
            style={styles.dungeonCard}
            onPress={() => handleStartDungeon(dungeon)}
          >
            <View style={styles.dungeonHeader}>
              <Text style={styles.dungeonName}>{dungeon.name || `던전 ${dungeon.id}`}</Text>
              <Text style={styles.difficultyBadge}>{dungeon.difficulty}</Text>
            </View>
            <Text style={styles.dungeonInfo}>
              문제: {dungeon.questions || 5}개 | 보상: {dungeon.rewards || '100 EXP'}
            </Text>
            <Text style={styles.dungeonDesc}>{dungeon.description || '지혜의 문제들'}</Text>
          </TouchableOpacity>
        ))}
      </View>

      {dungeons.length === 0 && (
        <View style={styles.emptyState}>
          <Text style={styles.emptyText}>던전 데이터를 로드할 수 없습니다</Text>
        </View>
      )}
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
  dungeonList: {
    gap: 12,
    marginBottom: 20
  },
  dungeonCard: {
    backgroundColor: '#2a2a2a',
    padding: 16,
    borderRadius: 8,
    borderLeftWidth: 4,
    borderLeftColor: '#6366f1'
  },
  dungeonHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8
  },
  dungeonName: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600'
  },
  difficultyBadge: {
    backgroundColor: '#6366f1',
    color: '#fff',
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 4,
    fontSize: 12,
    fontWeight: '600'
  },
  dungeonInfo: {
    color: '#aaa',
    fontSize: 12,
    marginBottom: 5
  },
  dungeonDesc: {
    color: '#999',
    fontSize: 12
  },
  quizHeader: {
    backgroundColor: '#2a2a2a',
    padding: 16,
    borderRadius: 8,
    marginBottom: 20,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center'
  },
  scoreText: {
    color: '#6366f1',
    fontSize: 16,
    fontWeight: 'bold'
  },
  questionContainer: {
    backgroundColor: '#2a2a2a',
    padding: 20,
    borderRadius: 8,
    marginBottom: 20
  },
  questionNumber: {
    color: '#aaa',
    fontSize: 12,
    marginBottom: 8
  },
  question: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
    lineHeight: 24
  },
  optionsContainer: {
    gap: 10,
    marginBottom: 20
  },
  optionButton: {
    backgroundColor: '#2a2a2a',
    padding: 15,
    borderRadius: 8,
    borderWidth: 2,
    borderColor: 'transparent'
  },
  optionText: {
    color: '#fff',
    fontSize: 14,
    fontWeight: '500'
  },
  hintBadge: {
    color: '#fbbf24',
    fontSize: 12,
    marginTop: 8,
    fontWeight: '600'
  },
  actionButtons: {
    flexDirection: 'row',
    gap: 10,
    marginTop: 20,
    marginBottom: 20
  },
  actionButton: {
    flex: 1,
    backgroundColor: '#6366f1',
    paddingVertical: 12,
    borderRadius: 8,
    alignItems: 'center'
  },
  actionButtonDisabled: {
    backgroundColor: '#3a3a3a',
    opacity: 0.5
  },
  actionButtonText: {
    color: '#fff',
    fontSize: 14,
    fontWeight: '600'
  },
  emptyState: {
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 40
  },
  emptyText: {
    color: '#aaa',
    fontSize: 14
  },
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0, 0, 0, 0.8)',
    justifyContent: 'flex-end'
  },
  modalContent: {
    backgroundColor: '#2a2a2a',
    borderTopLeftRadius: 16,
    borderTopRightRadius: 16,
    padding: 20,
    maxHeight: '70%'
  },
  modalTitle: {
    color: '#fff',
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 16
  },
  itemList: {
    marginBottom: 16,
    maxHeight: 300
  },
  itemButton: {
    backgroundColor: '#1a1a1a',
    padding: 12,
    borderRadius: 8,
    marginBottom: 10,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    borderLeftWidth: 3,
    borderLeftColor: '#6366f1'
  },
  itemName: {
    color: '#fff',
    fontSize: 14,
    fontWeight: '600',
    marginBottom: 4
  },
  itemCount: {
    color: '#888',
    fontSize: 12
  },
  useButtonText: {
    color: '#6366f1',
    fontSize: 12,
    fontWeight: 'bold'
  },
  modalCloseButton: {
    backgroundColor: '#3a3a3a',
    paddingVertical: 12,
    borderRadius: 8,
    alignItems: 'center'
  },
  modalCloseButtonText: {
    color: '#aaa',
    fontSize: 14,
    fontWeight: '600'
  }
});
