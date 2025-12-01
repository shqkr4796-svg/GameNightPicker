import React, { useState, useEffect } from 'react';
import { View, Text, TouchableOpacity, StyleSheet, ScrollView, Alert, ActivityIndicator, Vibration } from 'react-native';
import { dungeonAPI } from '../services/api';

export default function DungeonScreen({ navigation }) {
  const [dungeons, setDungeons] = useState([]);
  const [selectedDungeon, setSelectedDungeon] = useState(null);
  const [quizActive, setQuizActive] = useState(false);
  const [currentQuestion, setCurrentQuestion] = useState(null);
  const [score, setScore] = useState(0);
  const [loading, setLoading] = useState(true);
  const [questionIndex, setQuestionIndex] = useState(0);

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
      const response = await dungeonAPI.start(dungeon.id);
      if (response.data.success) {
        setQuizActive(true);
        setScore(0);
        setQuestionIndex(0);
        setCurrentQuestion(response.data.data.first_question);
      }
    } catch (error) {
      Alert.alert('오류', '던전 시작 실패');
    }
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
    return (
      <ScrollView style={styles.container}>
        <View style={styles.quizHeader}>
          <Text style={styles.dungeonName}>{selectedDungeon?.name}</Text>
          <Text style={styles.scoreText}>점수: {score}점</Text>
        </View>

        <View style={styles.questionContainer}>
          <Text style={styles.questionNumber}>문제 {questionIndex + 1}</Text>
          <Text style={styles.question}>{currentQuestion.text}</Text>
        </View>

        <View style={styles.optionsContainer}>
          {currentQuestion.options?.map((option, idx) => (
            <TouchableOpacity
              key={idx}
              style={styles.optionButton}
              onPress={() => handleAnswerQuestion(option)}
            >
              <Text style={styles.optionText}>{option}</Text>
            </TouchableOpacity>
          ))}
        </View>
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
  emptyState: {
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 40
  },
  emptyText: {
    color: '#aaa',
    fontSize: 14
  }
});
