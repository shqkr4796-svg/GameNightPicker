import React, { useState, useEffect } from 'react';
import { View, Text, TouchableOpacity, StyleSheet, ScrollView, TextInput, Alert, ActivityIndicator, Vibration } from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';

export default function WrongQuizRetryScreen({ navigation, route }) {
  const [wrongQuestions, setWrongQuestions] = useState([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [loading, setLoading] = useState(true);
  const [userAnswer, setUserAnswer] = useState('');
  const [answered, setAnswered] = useState(false);
  const [isCorrect, setIsCorrect] = useState(null);
  const [playerData, setPlayerData] = useState(null);

  const category = route?.params?.category || 'all';
  const language = route?.params?.language || 'random';

  useEffect(() => {
    loadWrongQuestions();
  }, [category]);

  const loadWrongQuestions = async () => {
    setLoading(true);
    try {
      // 틀린 문제 로드
      const wrongKey = `wrong_questions_${category}`;
      const saved = await AsyncStorage.getItem(wrongKey);
      if (saved) {
        const questions = JSON.parse(saved);
        setWrongQuestions(questions);
        setCurrentIndex(0);
        setAnswered(false);
        setUserAnswer('');
        setIsCorrect(null);
      } else {
        Alert.alert('알림', '틀린 문제가 없습니다.', [
          { text: '확인', onPress: () => navigation.goBack() }
        ]);
      }

      // 플레이어 데이터 로드
      const playerStr = await AsyncStorage.getItem('player_data');
      if (playerStr) {
        setPlayerData(JSON.parse(playerStr));
      }
    } catch (error) {
      console.log('틀린 문제 로드 실패');
      Alert.alert('오류', '데이터 로드 실패');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <View style={styles.container}><ActivityIndicator color="#6366f1" size="large" /></View>;
  }

  if (wrongQuestions.length === 0) {
    return (
      <View style={styles.container}>
        <View style={styles.emptyState}>
          <Text style={styles.emptyIcon}>✨</Text>
          <Text style={styles.emptyText}>틀린 문제가 없습니다!</Text>
          <TouchableOpacity
            style={styles.backButton}
            onPress={() => navigation.goBack()}
          >
            <Text style={styles.backButtonText}>돌아가기</Text>
          </TouchableOpacity>
        </View>
      </View>
    );
  }

  const currentQuestion = wrongQuestions[currentIndex];

  const handleAnswer = async () => {
    if (!userAnswer.trim()) {
      Alert.alert('알림', '답을 입력해주세요.');
      return;
    }

    const correctAnswer = currentQuestion.correct_answer.toLowerCase();
    const inputAnswer = userAnswer.toLowerCase().trim();
    const correct =
      correctAnswer === inputAnswer ||
      inputAnswer.includes(correctAnswer) ||
      correctAnswer.includes(inputAnswer);

    Vibration.vibrate(correct ? [0, 100, 50, 100] : [200, 100, 200]);
    setIsCorrect(correct);
    setAnswered(true);

    if (correct) {
      // 경험치 획득
      if (playerData) {
        const updatedPlayer = {
          ...playerData,
          exp: (playerData.exp || 0) + 10
        };
        await AsyncStorage.setItem('player_data', JSON.stringify(updatedPlayer));
        setPlayerData(updatedPlayer);
      }
    }
  };

  const handleNext = async () => {
    if (isCorrect) {
      // 맞춘 문제 제거
      const updated = wrongQuestions.filter((_, idx) => idx !== currentIndex);
      
      if (updated.length === 0) {
        // 모든 문제 완료
        Vibration.vibrate([0, 100, 50, 100, 50, 100]);
        await AsyncStorage.removeItem(`wrong_questions_${category}`);
        Alert.alert('축하합니다! 🎉', '모든 틀린 문제를 완료했습니다!', [
          { text: '확인', onPress: () => navigation.goBack() }
        ]);
      } else {
        // 다음 문제로
        await AsyncStorage.setItem(
          `wrong_questions_${category}`,
          JSON.stringify(updated)
        );
        setWrongQuestions(updated);
        setCurrentIndex(0);
        setUserAnswer('');
        setAnswered(false);
        setIsCorrect(null);
      }
    } else {
      // 틀렸으면 다음 문제로
      if (currentIndex + 1 >= wrongQuestions.length) {
        // 모든 문제 완료 (재도전 완료)
        Alert.alert('완료', '틀린 문제 재도전을 마쳤습니다.', [
          { text: '확인', onPress: () => navigation.goBack() }
        ]);
      } else {
        setCurrentIndex(currentIndex + 1);
        setUserAnswer('');
        setAnswered(false);
        setIsCorrect(null);
      }
    }
  };

  const progressPercent = Math.round(
    ((wrongQuestions.length - wrongQuestions.length + currentIndex + 1) /
      wrongQuestions.length) *
      100
  );

  return (
    <ScrollView style={styles.container}>
      <Text style={styles.title}>❌ 틀린 문제 재도전</Text>

      {/* 진행률 */}
      <View style={styles.progressContainer}>
        <View style={styles.progressBar}>
          <View
            style={[styles.progressFill, { width: `${progressPercent}%` }]}
          />
        </View>
        <Text style={styles.progressText}>
          {currentIndex + 1} / {wrongQuestions.length}
        </Text>
      </View>

      {/* 문제 카드 */}
      <View style={styles.questionCard}>
        <View style={styles.questionHeader}>
          <Text style={styles.questionType}>
            {currentQuestion.question_type === '뜻맞히기'
              ? '🎯 뜻 맞히기'
              : '🎯 단어 맞히기'}
          </Text>
          <Text style={styles.categoryTag}>{currentQuestion.category}</Text>
        </View>

        {/* 문제 내용 */}
        {currentQuestion.question_type === '뜻맞히기' ? (
          <>
            <Text style={styles.questionLabel}>뜻을 읽고 단어를 맞히세요</Text>
            <Text style={styles.questionContent}>{currentQuestion.correct_answer}</Text>
            <Text style={styles.hintText}>정답: {currentQuestion.word || '단어'}</Text>
          </>
        ) : (
          <>
            <Text style={styles.questionLabel}>단어의 뜻을 맞히세요</Text>
            <Text style={styles.questionContent}>{currentQuestion.word || '단어'}</Text>
            <Text style={styles.hintText}>정답: {currentQuestion.correct_answer}</Text>
          </>
        )}
      </View>

      {!answered ? (
        <>
          {/* 답변 입력 */}
          <TextInput
            style={styles.answerInput}
            placeholder="답을 입력하세요..."
            placeholderTextColor="#666"
            value={userAnswer}
            onChangeText={setUserAnswer}
            editable={!answered}
          />

          {/* 제출 버튼 */}
          <TouchableOpacity
            style={[styles.button, styles.buttonPrimary]}
            onPress={handleAnswer}
          >
            <Text style={styles.buttonText}>답변 제출</Text>
          </TouchableOpacity>
        </>
      ) : (
        <>
          {/* 결과 표시 */}
          <View
            style={[
              styles.resultCard,
              isCorrect ? styles.resultCorrect : styles.resultWrong
            ]}
          >
            <Text style={styles.resultIcon}>{isCorrect ? '✅' : '❌'}</Text>
            <Text style={styles.resultText}>
              {isCorrect ? '정답입니다!' : '틀렸습니다.'}
            </Text>
            {isCorrect ? (
              <>
                <Text style={styles.resultExp}>경험치 +10</Text>
              </>
            ) : (
              <>
                <Text style={styles.resultCorrectAnswer}>
                  정답: {currentQuestion.correct_answer}
                </Text>
                <Text style={styles.resultYourAnswer}>
                  당신의 답: {userAnswer}
                </Text>
              </>
            )}
          </View>

          {/* 다음 버튼 */}
          <TouchableOpacity
            style={[styles.button, styles.buttonSecondary]}
            onPress={handleNext}
          >
            <Text style={styles.buttonText}>
              {isCorrect
                ? currentIndex + 1 >= wrongQuestions.length
                  ? '완료'
                  : '다음 문제'
                : currentIndex + 1 >= wrongQuestions.length
                ? '재도전 완료'
                : '다음 문제'}
            </Text>
          </TouchableOpacity>
        </>
      )}

      {/* 정보 카드 */}
      <View style={styles.infoCard}>
        <Text style={styles.infoTitle}>💡 팁</Text>
        <Text style={styles.infoText}>• 맞힌 문제는 목록에서 제거됩니다</Text>
        <Text style={styles.infoText}>• 정답할 때마다 경험치 +10을 획득합니다</Text>
        <Text style={styles.infoText}>• 부분 일치도 정답으로 인정됩니다</Text>
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
    fontSize: 24,
    fontWeight: 'bold',
    color: '#fff',
    marginBottom: 15
  },
  progressContainer: {
    marginBottom: 20
  },
  progressBar: {
    height: 8,
    backgroundColor: '#2a2a2a',
    borderRadius: 4,
    overflow: 'hidden',
    marginBottom: 8
  },
  progressFill: {
    height: '100%',
    backgroundColor: '#6366f1'
  },
  progressText: {
    color: '#aaa',
    fontSize: 12,
    textAlign: 'right'
  },
  questionCard: {
    backgroundColor: '#2a2a2a',
    padding: 20,
    borderRadius: 8,
    marginBottom: 20,
    borderLeftWidth: 4,
    borderLeftColor: '#6366f1'
  },
  questionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 15
  },
  questionType: {
    color: '#fff',
    fontSize: 14,
    fontWeight: '600'
  },
  categoryTag: {
    backgroundColor: '#6366f1',
    color: '#fff',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 4,
    fontSize: 11,
    fontWeight: '600'
  },
  questionLabel: {
    color: '#aaa',
    fontSize: 12,
    marginBottom: 10
  },
  questionContent: {
    color: '#fff',
    fontSize: 18,
    fontWeight: 'bold',
    paddingVertical: 10,
    paddingHorizontal: 12,
    backgroundColor: '#1a1a1a',
    borderRadius: 6,
    marginBottom: 10
  },
  hintText: {
    color: '#999',
    fontSize: 12,
    fontStyle: 'italic'
  },
  answerInput: {
    backgroundColor: '#2a2a2a',
    color: '#fff',
    paddingHorizontal: 15,
    paddingVertical: 12,
    borderRadius: 8,
    fontSize: 16,
    marginBottom: 12
  },
  resultCard: {
    padding: 20,
    borderRadius: 8,
    alignItems: 'center',
    marginBottom: 15
  },
  resultCorrect: {
    backgroundColor: '#1a3a2a',
    borderLeftWidth: 4,
    borderLeftColor: '#22c55e'
  },
  resultWrong: {
    backgroundColor: '#3a1a1a',
    borderLeftWidth: 4,
    borderLeftColor: '#ef4444'
  },
  resultIcon: {
    fontSize: 40,
    marginBottom: 10
  },
  resultText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
    marginBottom: 10
  },
  resultExp: {
    color: '#22c55e',
    fontSize: 14,
    fontWeight: '600'
  },
  resultCorrectAnswer: {
    color: '#22c55e',
    fontSize: 13,
    marginBottom: 5
  },
  resultYourAnswer: {
    color: '#ef4444',
    fontSize: 13
  },
  button: {
    paddingVertical: 12,
    borderRadius: 8,
    alignItems: 'center',
    marginBottom: 12
  },
  buttonPrimary: {
    backgroundColor: '#6366f1'
  },
  buttonSecondary: {
    backgroundColor: '#3a3a3a'
  },
  buttonText: {
    color: '#fff',
    fontSize: 14,
    fontWeight: 'bold'
  },
  emptyState: {
    alignItems: 'center',
    paddingVertical: 60
  },
  emptyIcon: {
    fontSize: 48,
    marginBottom: 15
  },
  emptyText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
    marginBottom: 20
  },
  backButton: {
    backgroundColor: '#3a3a3a',
    paddingVertical: 10,
    paddingHorizontal: 20,
    borderRadius: 6
  },
  backButtonText: {
    color: '#fff',
    fontWeight: 'bold'
  },
  infoCard: {
    backgroundColor: '#2a2a2a',
    padding: 15,
    borderRadius: 8,
    marginBottom: 30,
    borderLeftWidth: 4,
    borderLeftColor: '#22c55e'
  },
  infoTitle: {
    color: '#fff',
    fontSize: 13,
    fontWeight: '600',
    marginBottom: 10
  },
  infoText: {
    color: '#aaa',
    fontSize: 11,
    marginBottom: 6,
    lineHeight: 16
  }
});
