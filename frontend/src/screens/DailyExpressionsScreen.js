import React, { useState, useEffect } from 'react';
import { View, Text, TouchableOpacity, StyleSheet, FlatList, Alert, ActivityIndicator, Modal, Vibration, ScrollView } from 'react-native';

export default function DailyExpressionsScreen({ navigation }) {
  const [expressions, setExpressions] = useState([
    {
      id: 1,
      expression: 'Hello, how are you?',
      meaning: '안녕하세요, 어떻게 지내세요?',
      examples: [
        'Hello, how are you? I\'m fine, thank you.',
        'How are you doing today?'
      ],
      situation: '처음 만난 사람이나 친구에게 인사할 때',
      tip: '가장 기본적인 인사 표현입니다.'
    },
    {
      id: 2,
      expression: 'Thank you',
      meaning: '감사합니다',
      examples: [
        'Thank you for your help.',
        'Thank you so much!'
      ],
      situation: '도움을 받았을 때 감사를 표할 때',
      tip: '고마움을 표현하는 가장 기본적인 표현입니다.'
    },
    {
      id: 3,
      expression: 'Nice to meet you',
      meaning: '만나서 반갑습니다',
      examples: [
        'Nice to meet you! What\'s your name?',
        'Nice to meet you too!'
      ],
      situation: '처음 만나는 사람에게 인사할 때',
      tip: '첫 만남에서 좋은 인상을 줄 수 있는 표현입니다.'
    },
    {
      id: 4,
      expression: 'How\'s the weather?',
      meaning: '날씨가 어떻게 되나요?',
      examples: [
        'How\'s the weather today?',
        'How\'s the weather where you are?'
      ],
      situation: '날씨에 대해 물어볼 때',
      tip: '일상적인 화제로 자주 사용되는 표현입니다.'
    },
    {
      id: 5,
      expression: 'I\'m sorry',
      meaning: '죄송합니다',
      examples: [
        'I\'m sorry, I didn\'t hear you.',
        'I\'m sorry for being late.'
      ],
      situation: '실수를 했을 때 사과할 때',
      tip: '상대방에게 예의를 표시하는 중요한 표현입니다.'
    },
    {
      id: 6,
      expression: 'What time is it?',
      meaning: '지금 몇 시예요?',
      examples: [
        'What time is it now?',
        'Could you tell me what time is it?'
      ],
      situation: '시간을 물어볼 때',
      tip: '일상 생활에서 자주 사용하는 표현입니다.'
    }
  ]);

  const [learnedCount, setLearnedCount] = useState(0);
  const [selectedExpression, setSelectedExpression] = useState(null);
  const [modalVisible, setModalVisible] = useState(false);
  const [quizActive, setQuizActive] = useState(false);
  const [currentQuizExpression, setCurrentQuizExpression] = useState(null);
  const [userAnswer, setUserAnswer] = useState('');
  const [score, setScore] = useState(0);

  const startQuiz = () => {
    const randomExp = expressions[Math.floor(Math.random() * expressions.length)];
    setCurrentQuizExpression(randomExp);
    setUserAnswer('');
    setQuizActive(true);
  };

  const submitAnswer = () => {
    if (!userAnswer.trim()) {
      Alert.alert('알림', '답을 입력해주세요.');
      return;
    }

    const isCorrect = userAnswer.toLowerCase().includes(currentQuizExpression.expression.toLowerCase());

    if (isCorrect) {
      Vibration.vibrate([0, 100, 50, 100]);
      const newScore = score + 10;
      setScore(newScore);
      setLearnedCount(learnedCount + 1);
      Alert.alert('정답!', '경험치 +10 획득!', [
        {
          text: '계속',
          onPress: () => {
            setUserAnswer('');
            startQuiz();
          }
        }
      ]);
    } else {
      Vibration.vibrate(200);
      Alert.alert('오답', `정답: ${currentQuizExpression.expression}`, [
        {
          text: '다시',
          onPress: () => {
            setUserAnswer('');
            startQuiz();
          }
        }
      ]);
    }
  };

  const handleExpressionPress = (expression) => {
    setSelectedExpression(expression);
    setModalVisible(true);
  };

  const renderExpressionCard = ({ item }) => (
    <TouchableOpacity
      style={styles.expressionCard}
      onPress={() => handleExpressionPress(item)}
    >
      <View style={styles.expressionHeader}>
        <Text style={styles.expressionText}>{item.expression}</Text>
        <Text style={styles.meaningText}>{item.meaning}</Text>
      </View>
      <Text style={styles.situationText}>{item.situation}</Text>
    </TouchableOpacity>
  );

  if (quizActive && currentQuizExpression) {
    return (
      <View style={styles.container}>
        <Text style={styles.title}>📝 일일 표현 - 퀴즈</Text>

        <View style={styles.scoreBox}>
          <View>
            <Text style={styles.scoreLabel}>학습한 표현</Text>
            <Text style={styles.scoreValue}>{learnedCount}</Text>
          </View>
          <View>
            <Text style={styles.scoreLabel}>획득 경험치</Text>
            <Text style={[styles.scoreValue, { color: '#6366f1' }]}>{score}</Text>
          </View>
        </View>

        <View style={styles.quizBox}>
          <Text style={styles.quizLabel}>📖 다음 뜻에 맞는 표현을 입력하세요</Text>
          <View style={styles.meaningBox}>
            <Text style={styles.meaningTextLarge}>{currentQuizExpression.meaning}</Text>
          </View>

          <Text style={styles.exampleLabel}>예시:</Text>
          {currentQuizExpression.examples.map((ex, idx) => (
            <Text key={idx} style={styles.exampleText}>
              • {ex}
            </Text>
          ))}

          <View style={styles.inputContainer}>
            <Text style={styles.inputLabel}>답 입력:</Text>
            <View style={styles.inputBox}>
              <Text style={styles.inputPlaceholder}>{userAnswer || '표현을 입력하세요'}</Text>
            </View>
          </View>

          <View style={styles.keyboardSimulation}>
            {currentQuizExpression.expression.split('').map((char, idx) => (
              <TouchableOpacity
                key={idx}
                style={styles.charButton}
                onPress={() => setUserAnswer(userAnswer + char)}
              >
                <Text style={styles.charButtonText}>{char}</Text>
              </TouchableOpacity>
            ))}
          </View>

          <TouchableOpacity style={styles.clearButton} onPress={() => setUserAnswer('')}>
            <Text style={styles.clearButtonText}>지우기</Text>
          </TouchableOpacity>

          <TouchableOpacity style={styles.submitButton} onPress={submitAnswer}>
            <Text style={styles.submitButtonText}>제출 (경험치 +10)</Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={styles.exitButton}
            onPress={() => setQuizActive(false)}
          >
            <Text style={styles.exitButtonText}>나가기</Text>
          </TouchableOpacity>
        </View>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <Text style={styles.title}>📝 일일 표현</Text>

      <View style={styles.statsBox}>
        <View style={styles.statItem}>
          <Text style={styles.statLabel}>학습한 표현</Text>
          <Text style={styles.statValue}>{learnedCount}</Text>
        </View>
        <View style={styles.statItem}>
          <Text style={styles.statLabel}>총 표현 수</Text>
          <Text style={styles.statValue}>{expressions.length}</Text>
        </View>
        <View style={styles.statItem}>
          <Text style={styles.statLabel}>획득 경험치</Text>
          <Text style={[styles.statValue, { color: '#6366f1' }]}>{score}</Text>
        </View>
      </View>

      <TouchableOpacity style={styles.quizButton} onPress={startQuiz}>
        <Text style={styles.quizButtonText}>🎯 퀴즈 시작하기</Text>
      </TouchableOpacity>

      <FlatList
        data={expressions}
        renderItem={renderExpressionCard}
        keyExtractor={(item) => item.id.toString()}
        contentContainerStyle={styles.listContainer}
        scrollEnabled={true}
      />

      {/* 표현 상세 모달 */}
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

            {selectedExpression && (
              <ScrollView>
                <Text style={styles.modalTitle}>{selectedExpression.expression}</Text>

                <View style={styles.detailBox}>
                  <Text style={styles.sectionTitle}>의미</Text>
                  <Text style={styles.contentText}>{selectedExpression.meaning}</Text>

                  <Text style={[styles.sectionTitle, { marginTop: 15 }]}>상황</Text>
                  <Text style={styles.contentText}>{selectedExpression.situation}</Text>

                  <Text style={[styles.sectionTitle, { marginTop: 15 }]}>팁</Text>
                  <Text style={styles.contentText}>{selectedExpression.tip}</Text>

                  <Text style={[styles.sectionTitle, { marginTop: 15 }]}>예시</Text>
                  {selectedExpression.examples.map((ex, idx) => (
                    <Text key={idx} style={styles.exampleItemText}>
                      {idx + 1}. {ex}
                    </Text>
                  ))}
                </View>

                <TouchableOpacity
                  style={styles.closeModalButton}
                  onPress={() => setModalVisible(false)}
                >
                  <Text style={styles.closeModalButtonText}>닫기</Text>
                </TouchableOpacity>
              </ScrollView>
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
  statsBox: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    backgroundColor: '#2a2a2a',
    padding: 15,
    borderRadius: 8,
    marginBottom: 15
  },
  statItem: {
    alignItems: 'center'
  },
  statLabel: {
    color: '#aaa',
    fontSize: 12,
    marginBottom: 5
  },
  statValue: {
    color: '#fff',
    fontSize: 18,
    fontWeight: 'bold'
  },
  scoreBox: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    backgroundColor: '#2a2a2a',
    padding: 15,
    borderRadius: 8,
    marginBottom: 15
  },
  scoreLabel: {
    color: '#aaa',
    fontSize: 12,
    marginBottom: 5
  },
  scoreValue: {
    color: '#fff',
    fontSize: 18,
    fontWeight: 'bold'
  },
  quizButton: {
    backgroundColor: '#6366f1',
    padding: 15,
    borderRadius: 8,
    marginBottom: 15,
    alignItems: 'center'
  },
  quizButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold'
  },
  listContainer: {
    gap: 10
  },
  expressionCard: {
    backgroundColor: '#2a2a2a',
    padding: 15,
    borderRadius: 8,
    borderLeftWidth: 4,
    borderLeftColor: '#6366f1',
    marginBottom: 5
  },
  expressionHeader: {
    marginBottom: 10
  },
  expressionText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
    marginBottom: 5
  },
  meaningText: {
    color: '#6366f1',
    fontSize: 14
  },
  situationText: {
    color: '#aaa',
    fontSize: 12
  },
  quizBox: {
    backgroundColor: '#2a2a2a',
    padding: 20,
    borderRadius: 8,
    marginBottom: 20
  },
  quizLabel: {
    color: '#fff',
    fontSize: 14,
    fontWeight: 'bold',
    marginBottom: 15
  },
  meaningBox: {
    backgroundColor: '#1a1a1a',
    padding: 15,
    borderRadius: 8,
    marginBottom: 15,
    borderWidth: 2,
    borderColor: '#6366f1'
  },
  meaningTextLarge: {
    color: '#6366f1',
    fontSize: 16,
    fontWeight: 'bold',
    textAlign: 'center'
  },
  exampleLabel: {
    color: '#fff',
    fontSize: 12,
    fontWeight: 'bold',
    marginBottom: 8
  },
  exampleText: {
    color: '#bbb',
    fontSize: 12,
    marginBottom: 5
  },
  inputContainer: {
    marginVertical: 15
  },
  inputLabel: {
    color: '#fff',
    fontSize: 12,
    fontWeight: 'bold',
    marginBottom: 8
  },
  inputBox: {
    backgroundColor: '#1a1a1a',
    padding: 12,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#3a3a3a',
    minHeight: 50,
    justifyContent: 'center'
  },
  inputPlaceholder: {
    color: '#666',
    fontSize: 14
  },
  keyboardSimulation: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 5,
    marginBottom: 15
  },
  charButton: {
    backgroundColor: '#3a3a3a',
    paddingHorizontal: 8,
    paddingVertical: 6,
    borderRadius: 4
  },
  charButtonText: {
    color: '#fff',
    fontSize: 12
  },
  clearButton: {
    backgroundColor: '#ef4444',
    padding: 10,
    borderRadius: 8,
    alignItems: 'center',
    marginBottom: 10
  },
  clearButtonText: {
    color: '#fff',
    fontSize: 12,
    fontWeight: 'bold'
  },
  submitButton: {
    backgroundColor: '#22c55e',
    padding: 15,
    borderRadius: 8,
    alignItems: 'center',
    marginBottom: 10
  },
  submitButtonText: {
    color: '#fff',
    fontSize: 14,
    fontWeight: 'bold'
  },
  exitButton: {
    backgroundColor: '#666',
    padding: 12,
    borderRadius: 8,
    alignItems: 'center'
  },
  exitButtonText: {
    color: '#fff',
    fontSize: 12,
    fontWeight: 'bold'
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
    maxHeight: '90%'
  },
  closeButton: {
    position: 'absolute',
    top: 15,
    right: 15,
    width: 30,
    height: 30,
    justifyContent: 'center',
    alignItems: 'center',
    zIndex: 10
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
    marginBottom: 15
  },
  sectionTitle: {
    color: '#6366f1',
    fontSize: 14,
    fontWeight: 'bold',
    marginBottom: 8
  },
  contentText: {
    color: '#bbb',
    fontSize: 13,
    lineHeight: 20
  },
  exampleItemText: {
    color: '#aaa',
    fontSize: 12,
    marginVertical: 5,
    lineHeight: 18
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
