import React, { useState, useEffect } from 'react';
import { View, Text, TouchableOpacity, StyleSheet, FlatList, Alert, ActivityIndicator, Modal, Vibration } from 'react-native';

export default function DungeonScreen({ navigation }) {
  const [dungeons, setDungeons] = useState([
    {
      id: 1,
      name: '초급 던전',
      difficulty: '쉬움',
      level_required: 1,
      monsters: 3,
      rewards: '100 경험치, 500 골드'
    },
    {
      id: 2,
      name: '중급 던전',
      difficulty: '보통',
      level_required: 10,
      monsters: 5,
      rewards: '300 경험치, 1500 골드'
    },
    {
      id: 3,
      name: '고급 던전',
      difficulty: '어려움',
      level_required: 20,
      monsters: 7,
      rewards: '500 경험치, 3000 골드'
    }
  ]);
  const [selectedDungeon, setSelectedDungeon] = useState(null);
  const [quizActive, setQuizActive] = useState(false);
  const [currentQuestion, setCurrentQuestion] = useState(null);
  const [score, setScore] = useState(0);
  const [loading, setLoading] = useState(false);

  const playQuizSound = (type) => {
    if (type === 'correct') {
      Vibration.vibrate([0, 100, 50, 100]); // 정답 효과
    } else if (type === 'wrong') {
      Vibration.vibrate([0, 200]); // 오답 효과
    } else if (type === 'complete') {
      Vibration.vibrate([0, 100, 50, 100, 50, 100, 50, 100]); // 완료 효과
    }
  };

  // 샘플 문제들
  const sampleQuestions = [
    {
      id: 1,
      text: '"Hello, how are you?" 는 무엇을 의미하나요?',
      options: ['안녕하세요, 어떻게 지내세요?', '잠깐, 어디가?', '나중에 만나요', '안녕히 가세요'],
      correct: 0
    },
    {
      id: 2,
      text: '"Thank you" 의 의미는?',
      options: ['미안해요', '감사합니다', '도와줘', '멋있어요'],
      correct: 1
    },
    {
      id: 3,
      text: '"Nice to meet you" 는?',
      options: ['만나서 반갑습니다', '또 만났네요', '이별은 슬퍼요', '처음 봐요'],
      correct: 0
    },
    {
      id: 4,
      text: '"I love you" 의 뜻은?',
      options: ['난 너를 봐', '나는 너를 사랑해', '난 혼자야', '우리 친구할까?'],
      correct: 1
    },
    {
      id: 5,
      text: '"Excuse me" 는?',
      options: ['미안해요', '저기요', '괜찮아요', '뭐해요?'],
      correct: 1
    }
  ];

  const handleStartDungeon = async (dungeon) => {
    setSelectedDungeon(dungeon);
    setQuizActive(true);
    setScore(0);
    setCurrentQuestion(sampleQuestions[0]);
  };

  const handleAnswerQuestion = (selectedIndex) => {
    if (selectedIndex === currentQuestion.correct) {
      setScore(score + 10);
      Alert.alert('정답!', '다음 문제로 진행합니다.');
    } else {
      Alert.alert('오답!', '정답을 다시 확인해주세요.');
    }

    const nextQuestionIndex = sampleQuestions.findIndex(q => q.id === currentQuestion.id) + 1;
    if (nextQuestionIndex < sampleQuestions.length) {
      setCurrentQuestion(sampleQuestions[nextQuestionIndex]);
    } else {
      // 던전 완료
      Alert.alert('던전 완료!', `최종 점수: ${score + 10}점\n보상을 획득했습니다!`);
      setQuizActive(false);
      setSelectedDungeon(null);
    }
  };

  const handleFleeQuiz = () => {
    Alert.alert('도망', '던전에서 도망쳤습니다.');
    setQuizActive(false);
    setSelectedDungeon(null);
    setCurrentQuestion(null);
  };

  const renderDungeonCard = ({ item }) => (
    <TouchableOpacity
      style={[
        styles.dungeonCard,
        {
          borderLeftColor:
            item.difficulty === '쉬움' ? '#3b82f6' : item.difficulty === '보통' ? '#f59e0b' : '#ef4444'
        }
      ]}
      onPress={() => handleStartDungeon(item)}
    >
      <View style={styles.dungeonHeader}>
        <Text style={styles.dungeonName}>{item.name}</Text>
        <Text
          style={[
            styles.difficulty,
            {
              color:
                item.difficulty === '쉬움' ? '#3b82f6' : item.difficulty === '보통' ? '#f59e0b' : '#ef4444'
            }
          ]}
        >
          {item.difficulty}
        </Text>
      </View>
      <Text style={styles.dungeonInfo}>필요 레벨: {item.level_required}</Text>
      <Text style={styles.dungeonInfo}>몬스터: {item.monsters}마리</Text>
      <Text style={styles.rewards}>보상: {item.rewards}</Text>
    </TouchableOpacity>
  );

  if (quizActive && currentQuestion) {
    return (
      <View style={styles.quizContainer}>
        {/* 진행도 */}
        <View style={styles.progressHeader}>
          <Text style={styles.dungeonTitle}>{selectedDungeon.name}</Text>
          <Text style={styles.score}>점수: {score}</Text>
        </View>

        {/* 문제 */}
        <View style={styles.questionBox}>
          <Text style={styles.questionText}>{currentQuestion.text}</Text>
        </View>

        {/* 선택지 */}
        <View style={styles.optionsContainer}>
          {currentQuestion.options.map((option, index) => (
            <TouchableOpacity
              key={index}
              style={styles.optionButton}
              onPress={() => handleAnswerQuestion(index)}
            >
              <Text style={styles.optionText}>{option}</Text>
            </TouchableOpacity>
          ))}
        </View>

        {/* 도망 버튼 */}
        <TouchableOpacity
          style={styles.fleeQuizButton}
          onPress={handleFleeQuiz}
        >
          <Text style={styles.fleeQuizButtonText}>던전 도망</Text>
        </TouchableOpacity>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <Text style={styles.title}>던전</Text>
      <Text style={styles.subtitle}>퀴즈를 풀어 몬스터를 물리치세요</Text>

      <FlatList
        data={dungeons}
        renderItem={renderDungeonCard}
        keyExtractor={(item) => item.id.toString()}
        contentContainerStyle={styles.listContainer}
        scrollEnabled={true}
      />

      <View style={styles.infoBox}>
        <Text style={styles.infoTitle}>📌 던전이란?</Text>
        <Text style={styles.infoText}>
          영어 단어 및 표현 퀴즈를 풀어서 던전의 몬스터를 물리치는 시스템입니다.
        </Text>
      </View>
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
    marginBottom: 5
  },
  subtitle: {
    fontSize: 14,
    color: '#aaa',
    marginBottom: 20
  },
  listContainer: {
    gap: 10,
    paddingBottom: 20
  },
  dungeonCard: {
    backgroundColor: '#2a2a2a',
    padding: 15,
    borderRadius: 8,
    borderLeftWidth: 4,
    marginBottom: 5
  },
  dungeonHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 10
  },
  dungeonName: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
    flex: 1
  },
  difficulty: {
    fontSize: 12,
    fontWeight: 'bold'
  },
  dungeonInfo: {
    color: '#aaa',
    fontSize: 12,
    marginBottom: 5
  },
  rewards: {
    color: '#6366f1',
    fontSize: 12,
    fontWeight: 'bold'
  },
  infoBox: {
    backgroundColor: '#2a2a2a',
    padding: 15,
    borderRadius: 8,
    borderLeftWidth: 4,
    borderLeftColor: '#6366f1'
  },
  infoTitle: {
    color: '#fff',
    fontSize: 14,
    fontWeight: 'bold',
    marginBottom: 8
  },
  infoText: {
    color: '#aaa',
    fontSize: 12,
    lineHeight: 18
  },
  // Quiz Styles
  quizContainer: {
    flex: 1,
    backgroundColor: '#1a1a1a',
    padding: 20,
    justifyContent: 'space-between'
  },
  progressHeader: {
    backgroundColor: '#2a2a2a',
    padding: 15,
    borderRadius: 8,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 20
  },
  dungeonTitle: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
    flex: 1
  },
  score: {
    color: '#6366f1',
    fontSize: 16,
    fontWeight: 'bold'
  },
  questionBox: {
    backgroundColor: '#2a2a2a',
    padding: 20,
    borderRadius: 8,
    marginBottom: 20,
    borderLeftWidth: 4,
    borderLeftColor: '#f59e0b'
  },
  questionText: {
    color: '#fff',
    fontSize: 16,
    lineHeight: 24,
    fontWeight: '500'
  },
  optionsContainer: {
    gap: 10,
    marginBottom: 20,
    flex: 1,
    justifyContent: 'center'
  },
  optionButton: {
    backgroundColor: '#6366f1',
    padding: 15,
    borderRadius: 8,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center'
  },
  optionText: {
    color: '#fff',
    fontSize: 14,
    fontWeight: '500'
  },
  fleeQuizButton: {
    backgroundColor: '#ef4444',
    padding: 15,
    borderRadius: 8,
    alignItems: 'center'
  },
  fleeQuizButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold'
  }
});
