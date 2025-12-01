import React, { useState, useEffect } from 'react';
import { View, Text, TouchableOpacity, StyleSheet, ScrollView, Alert, ActivityIndicator, Vibration } from 'react-native';
import { expressionsAPI } from '../services/api';

export default function DailyExpressionsScreen({ navigation }) {
  const [expressions, setExpressions] = useState([]);
  const [dailyTask, setDailyTask] = useState(null);
  const [selectedExpression, setSelectedExpression] = useState(null);
  const [quizMode, setQuizMode] = useState(false);
  const [score, setScore] = useState(0);
  const [answered, setAnswered] = useState(0);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadExpressionData();
  }, []);

  const loadExpressionData = async () => {
    setLoading(true);
    try {
      const [expRes, dailyRes] = await Promise.all([
        expressionsAPI.list(),
        expressionsAPI.getDailyTask()
      ]);

      if (expRes.data.success) {
        setExpressions(expRes.data.data.expressions || []);
      }
      if (dailyRes.data.success) {
        setDailyTask(dailyRes.data.data);
      }
    } catch (error) {
      Alert.alert('오류', '표현 데이터 로드 실패');
    } finally {
      setLoading(false);
    }
  };

  const startQuiz = () => {
    if (expressions.length === 0) {
      Alert.alert('알림', '표현이 없습니다.');
      return;
    }

    setQuizMode(true);
    setScore(0);
    setAnswered(0);
    setSelectedExpression(expressions[0]);
  };

  const handleAnswerQuestion = async (answer) => {
    if (!selectedExpression) return;

    Vibration.vibrate([0, 100, 50, 100]);

    try {
      const response = await expressionsAPI.submit(selectedExpression.id, answer);

      if (response.data.correct) {
        setScore(score + 10);
        Alert.alert('정답!', '좋습니다!', [
          { text: '다음', onPress: () => nextExpression() }
        ]);
      } else {
        Alert.alert('오답', `정답: ${selectedExpression.meaning}`, [
          { text: '다음', onPress: () => nextExpression() }
        ]);
      }
      setAnswered(answered + 1);
    } catch (error) {
      Alert.alert('오류', '답변 처리 실패');
    }
  };

  const nextExpression = () => {
    if (answered + 1 >= expressions.length) {
      Alert.alert('완료', `최종 점수: ${score + 10}점`, [
        {
          text: '확인',
          onPress: () => {
            setQuizMode(false);
            setSelectedExpression(null);
          }
        }
      ]);
    } else {
      setSelectedExpression(expressions[answered + 1]);
    }
  };

  if (loading) {
    return (
      <View style={styles.container}>
        <ActivityIndicator color="#6366f1" size="large" />
      </View>
    );
  }

  if (quizMode && selectedExpression) {
    return (
      <ScrollView style={styles.container}>
        <Text style={styles.title}>표현 학습 - 퀴즈</Text>

        <View style={styles.progressCard}>
          <Text style={styles.progressText}>
            {answered + 1} / {expressions.length}
          </Text>
          <Text style={styles.scoreText}>점수: {score}점</Text>
        </View>

        <View style={styles.questionCard}>
          <Text style={styles.questionLabel}>다음 표현의 뜻은?</Text>
          <Text style={styles.expressionText}>{selectedExpression.expression}</Text>
        </View>

        <View style={styles.optionsContainer}>
          {expressions.slice(0, 4).map((exp, idx) => (
            <TouchableOpacity
              key={idx}
              style={styles.optionButton}
              onPress={() => handleAnswerQuestion(exp.meaning)}
            >
              <Text style={styles.optionText}>{exp.meaning}</Text>
            </TouchableOpacity>
          ))}
        </View>
      </ScrollView>
    );
  }

  return (
    <ScrollView style={styles.container}>
      <Text style={styles.title}>표현 학습</Text>
      <Text style={styles.subtitle}>일상 영어 표현을 배워보세요</Text>

      {dailyTask && (
        <View style={styles.dailyTaskCard}>
          <Text style={styles.dailyLabel}>오늘의 미션</Text>
          <Text style={styles.dailyTitle}>{dailyTask.title || '10개 표현 학습'}</Text>
          <Text style={styles.dailyReward}>보상: {dailyTask.reward || '100 EXP'}</Text>
        </View>
      )}

      <Text style={styles.sectionTitle}>표현 목록</Text>
      <View style={styles.expressionList}>
        {expressions.map((expr, idx) => (
          <View key={idx} style={styles.expressionCard}>
            <View style={styles.expressionHeader}>
              <Text style={styles.expressionText}>{expr.expression}</Text>
            </View>
            <Text style={styles.meaningText}>{expr.meaning}</Text>
            {expr.examples && expr.examples[0] && (
              <Text style={styles.exampleText}>예: {expr.examples[0]}</Text>
            )}
          </View>
        ))}
      </View>

      <TouchableOpacity
        style={styles.startButton}
        onPress={startQuiz}
      >
        <Text style={styles.startButtonText}>퀴즈 시작</Text>
      </TouchableOpacity>
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
  sectionTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#6366f1',
    marginBottom: 12,
    marginTop: 16
  },
  dailyTaskCard: {
    backgroundColor: '#2a2a2a',
    padding: 16,
    borderRadius: 8,
    marginBottom: 20,
    borderLeftWidth: 4,
    borderLeftColor: '#22c55e'
  },
  dailyLabel: {
    color: '#aaa',
    fontSize: 12,
    marginBottom: 5
  },
  dailyTitle: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
    marginBottom: 8
  },
  dailyReward: {
    color: '#22c55e',
    fontSize: 12,
    fontWeight: '600'
  },
  expressionList: {
    gap: 10,
    marginBottom: 20
  },
  expressionCard: {
    backgroundColor: '#2a2a2a',
    padding: 12,
    borderRadius: 8
  },
  expressionHeader: {
    marginBottom: 8
  },
  expressionText: {
    color: '#fff',
    fontSize: 14,
    fontWeight: '600'
  },
  meaningText: {
    color: '#6366f1',
    fontSize: 12,
    marginBottom: 5
  },
  exampleText: {
    color: '#999',
    fontSize: 11,
    fontStyle: 'italic'
  },
  startButton: {
    backgroundColor: '#6366f1',
    padding: 15,
    borderRadius: 8,
    alignItems: 'center',
    marginBottom: 30
  },
  startButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold'
  },
  progressCard: {
    backgroundColor: '#2a2a2a',
    padding: 16,
    borderRadius: 8,
    marginBottom: 20,
    flexDirection: 'row',
    justifyContent: 'space-between'
  },
  progressText: {
    color: '#aaa',
    fontSize: 14
  },
  scoreText: {
    color: '#6366f1',
    fontSize: 14,
    fontWeight: 'bold'
  },
  questionCard: {
    backgroundColor: '#2a2a2a',
    padding: 20,
    borderRadius: 8,
    marginBottom: 20,
    alignItems: 'center'
  },
  questionLabel: {
    color: '#aaa',
    fontSize: 12,
    marginBottom: 10
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
  }
});
