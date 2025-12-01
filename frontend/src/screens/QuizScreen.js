import React, { useState, useEffect } from 'react';
import { View, Text, TouchableOpacity, StyleSheet, Alert, Vibration, ScrollView, ActivityIndicator } from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { quizAPI } from '../services/api';

export default function QuizScreen({ navigation }) {
  const [categories, setCategories] = useState(['AI', 'Business', 'Finance', 'IT', 'Marketing', 'Programming']);
  const [selectedCategory, setSelectedCategory] = useState(null);
  const [selectedLanguage, setSelectedLanguage] = useState('all');
  const [quizMode, setQuizMode] = useState(false);
  const [currentQuestion, setCurrentQuestion] = useState(null);
  const [options, setOptions] = useState([]);
  const [score, setScore] = useState(0);
  const [totalQuestions, setTotalQuestions] = useState(0);
  const [answered, setAnswered] = useState(0);
  const [wrongQuestions, setWrongQuestions] = useState([]);
  const [showingWrongMode, setShowingWrongMode] = useState(false);
  const [loading, setLoading] = useState(false);
  const [words, setWords] = useState([]);

  const languages = [
    { label: '전체', value: 'all' },
    { label: '한글 뜻', value: 'korean' },
    { label: '영어', value: 'english' }
  ];

  const startQuiz = async (category) => {
    setLoading(true);
    try {
      const response = await quizAPI.getCategory(category.toLowerCase());
      if (response.data.success) {
        const categoryWords = response.data.data.words || [];
        setWords(categoryWords);
        setSelectedCategory(category);
        setQuizMode(true);
        setScore(0);
        setAnswered(0);
        setTotalQuestions(categoryWords.length * 2);
        setWrongQuestions([]);
        setShowingWrongMode(false);
        generateNewQuestion(categoryWords);
      }
    } catch (error) {
      Alert.alert('오류', '퀴즈 데이터 로드 실패');
    } finally {
      setLoading(false);
    }
  };

  const generateNewQuestion = (wordList) => {
    if (!wordList || wordList.length === 0) {
      Alert.alert('알림', '출제할 단어가 없습니다.');
      return;
    }

    const randomWord = wordList[Math.floor(Math.random() * wordList.length)];
    const questionType = selectedLanguage === 'all' 
      ? (Math.random() > 0.5 ? 'meaning' : 'word')
      : (selectedLanguage === 'korean' ? 'meaning' : 'word');

    let question, correctAnswer, incorrectAnswers;

    if (questionType === 'meaning') {
      question = `다음 뜻의 단어는?`;
      correctAnswer = randomWord.단어 || randomWord.word;
      incorrectAnswers = wordList
        .filter(w => (w.단어 || w.word) !== correctAnswer)
        .map(w => w.단어 || w.word)
        .slice(0, 3);
    } else {
      question = `다음 단어의 뜻은?`;
      correctAnswer = randomWord.뜻 || randomWord.meaning;
      incorrectAnswers = wordList
        .filter(w => (w.뜻 || w.meaning) !== correctAnswer)
        .map(w => w.뜻 || w.meaning)
        .slice(0, 3);
    }

    const allOptions = [correctAnswer, ...incorrectAnswers].sort(() => Math.random() - 0.5);

    setCurrentQuestion({
      question,
      questionContent: questionType === 'meaning' ? (randomWord.뜻 || randomWord.meaning) : (randomWord.단어 || randomWord.word),
      correctAnswer,
      type: questionType,
      word: randomWord
    });
    setOptions(allOptions);
  };

  const handleAnswer = (answer) => {
    const isCorrect = answer === currentQuestion.correctAnswer;

    if (isCorrect) {
      Vibration.vibrate([0, 100, 50, 100]);
      setScore(score + 10);
      Alert.alert('정답!', '경험치 +10 획득!', [
        { text: '다음', onPress: () => nextQuestion() }
      ]);
    } else {
      Vibration.vibrate(200);
      setWrongQuestions([...wrongQuestions, currentQuestion]);
      Alert.alert('오답', `정답: ${currentQuestion.correctAnswer}`, [
        { text: '다음', onPress: () => nextQuestion() }
      ]);
    }

    setAnswered(answered + 1);
  };

  const nextQuestion = async () => {
    if (answered + 1 >= totalQuestions) {
      await endQuiz();
    } else {
      generateNewQuestion(words);
    }
  };

  const endQuiz = async () => {
    // 틀린 문제 AsyncStorage에 저장
    if (wrongQuestions.length > 0) {
      try {
        await AsyncStorage.setItem(
          `wrong_questions_${selectedCategory}`,
          JSON.stringify(wrongQuestions)
        );
      } catch (error) {
        console.log('틀린 문제 저장 실패');
      }
    }

    const buttons = [
      {
        text: '계속',
        onPress: () => {
          setQuizMode(false);
          setSelectedCategory(null);
          setScore(0);
          setAnswered(0);
        }
      }
    ];

    // 틀린 문제가 있으면 재도전 버튼 추가
    if (wrongQuestions.length > 0) {
      buttons.unshift({
        text: '틀린 문제 재도전',
        onPress: () => {
          navigation.navigate('WrongQuizRetry', {
            category: selectedCategory,
            language: selectedLanguage
          });
        }
      });
    }

    Alert.alert(
      '퀴즈 완료',
      `점수: ${score}점\n정답률: ${Math.round((score / totalQuestions) * 100)}%\n틀린 문제: ${wrongQuestions.length}개`,
      buttons
    );
  };

  const retryWrongQuestions = () => {
    if (wrongQuestions.length === 0) {
      Alert.alert('알림', '틀린 문제가 없습니다.');
      return;
    }
    setShowingWrongMode(true);
    setScore(0);
    setAnswered(0);
    setTotalQuestions(wrongQuestions.length);
    setCurrentQuestion(wrongQuestions[0]);
    setOptions([wrongQuestions[0].correctAnswer, ...wrongQuestions.slice(1, 4).map(q => q.correctAnswer)].sort(() => Math.random() - 0.5));
  };

  if (loading) {
    return (
      <View style={styles.container}>
        <ActivityIndicator color="#6366f1" size="large" />
      </View>
    );
  }

  // 퀴즈 진행 중
  if (quizMode && currentQuestion) {
    const progressPercent = (answered / totalQuestions) * 100;

    return (
      <ScrollView style={styles.container}>
        {/* 진행률 표시 */}
        <View style={styles.progressSection}>
          <Text style={styles.progressText}>
            {answered} / {totalQuestions}
          </Text>
          <View style={styles.progressBar}>
            <View
              style={[
                styles.progressFill,
                { width: `${progressPercent}%` }
              ]}
            />
          </View>
          <Text style={styles.scoreText}>점수: {score}점</Text>
        </View>

        {/* 카테고리 & 언어 표시 */}
        <View style={styles.quizInfo}>
          <Text style={styles.categoryTag}>카테고리: {selectedCategory}</Text>
          <Text style={styles.languageTag}>
            언어: {languages.find(l => l.value === selectedLanguage)?.label}
          </Text>
        </View>

        {/* 질문 */}
        <View style={styles.questionSection}>
          <Text style={styles.question}>{currentQuestion.question}</Text>
          <View style={styles.questionContent}>
            <Text style={styles.questionText}>{currentQuestion.questionContent}</Text>
          </View>
        </View>

        {/* 선택지 */}
        <View style={styles.optionsContainer}>
          {options.map((option, idx) => (
            <TouchableOpacity
              key={idx}
              style={styles.optionButton}
              onPress={() => handleAnswer(option)}
            >
              <Text style={styles.optionText}>{option}</Text>
            </TouchableOpacity>
          ))}
        </View>

        {/* 틀린 문제 카운트 */}
        {wrongQuestions.length > 0 && (
          <View style={styles.wrongCountBadge}>
            <Text style={styles.wrongCountText}>
              ⚠️ 틀린 문제: {wrongQuestions.length}개
            </Text>
          </View>
        )}
      </ScrollView>
    );
  }

  // 카테고리 선택 화면
  return (
    <ScrollView style={styles.container}>
      <Text style={styles.title}>단어 퀴즈</Text>
      <Text style={styles.subtitle}>카테고리를 선택하여 시작하세요</Text>

      {/* 언어 선택 */}
      <Text style={styles.sectionTitle}>학습 언어</Text>
      <View style={styles.languageButtons}>
        {languages.map((lang) => (
          <TouchableOpacity
            key={lang.value}
            style={[
              styles.langButton,
              selectedLanguage === lang.value && styles.langButtonActive
            ]}
            onPress={() => setSelectedLanguage(lang.value)}
          >
            <Text
              style={[
                styles.langButtonText,
                selectedLanguage === lang.value && styles.langButtonTextActive
              ]}
            >
              {lang.label}
            </Text>
          </TouchableOpacity>
        ))}
      </View>

      {/* 틀린 문제 재도전 버튼 */}
      {wrongQuestions.length > 0 && (
        <TouchableOpacity
          style={styles.retryButtonContainer}
          onPress={() => navigation.navigate('WrongQuizRetry', { category: selectedCategory })}
        >
          <Text style={styles.retryButtonEmoji}>❌</Text>
          <View style={styles.retryButtonContent}>
            <Text style={styles.retryButtonTitle}>틀린 문제 재도전</Text>
            <Text style={styles.retryButtonCount}>{wrongQuestions.length}개 문제 남음</Text>
          </View>
          <Text style={styles.retryButtonArrow}>→</Text>
        </TouchableOpacity>
      )}

      {/* 카테고리 그리드 */}
      <Text style={styles.sectionTitle}>카테고리</Text>
      <View style={styles.categoryGrid}>
        {categories.map((category, idx) => (
          <TouchableOpacity
            key={idx}
            style={styles.categoryCard}
            onPress={() => startQuiz(category)}
          >
            <Text style={styles.categoryEmoji}>📚</Text>
            <Text style={styles.categoryName}>{category}</Text>
            <Text style={styles.categoryHint}>탭하여 시작</Text>
          </TouchableOpacity>
        ))}
      </View>

      {/* 통계 */}
      <View style={styles.statsCard}>
        <Text style={styles.statsTitle}>📊 학습 통계</Text>
        <Text style={styles.statItem}>카테고리: {categories.length}개</Text>
        <Text style={styles.statItem}>학습 준비 완료!</Text>
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
  sectionTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#6366f1',
    marginBottom: 12,
    marginTop: 16
  },
  // Language Selection
  languageButtons: {
    flexDirection: 'row',
    gap: 8,
    marginBottom: 20
  },
  langButton: {
    flex: 1,
    paddingVertical: 10,
    paddingHorizontal: 12,
    borderRadius: 6,
    backgroundColor: '#2a2a2a',
    borderWidth: 2,
    borderColor: 'transparent',
    alignItems: 'center'
  },
  langButtonActive: {
    backgroundColor: '#6366f1',
    borderColor: '#6366f1'
  },
  langButtonText: {
    color: '#aaa',
    fontSize: 12,
    fontWeight: '600'
  },
  langButtonTextActive: {
    color: '#fff'
  },
  // Category Grid
  categoryGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 12,
    marginBottom: 20
  },
  categoryCard: {
    width: '48%',
    backgroundColor: '#2a2a2a',
    padding: 20,
    borderRadius: 8,
    alignItems: 'center',
    borderWidth: 2,
    borderColor: 'transparent'
  },
  categoryEmoji: {
    fontSize: 32,
    marginBottom: 8
  },
  categoryName: {
    color: '#fff',
    fontSize: 14,
    fontWeight: '600',
    marginBottom: 5,
    textAlign: 'center'
  },
  categoryHint: {
    color: '#6366f1',
    fontSize: 10
  },
  // Stats
  statsCard: {
    backgroundColor: '#2a2a2a',
    padding: 15,
    borderRadius: 8,
    marginBottom: 30,
    borderLeftWidth: 4,
    borderLeftColor: '#6366f1'
  },
  statsTitle: {
    color: '#fff',
    fontSize: 14,
    fontWeight: '600',
    marginBottom: 10
  },
  statItem: {
    color: '#aaa',
    fontSize: 12,
    marginBottom: 5
  },
  // Quiz Mode
  progressSection: {
    backgroundColor: '#2a2a2a',
    padding: 15,
    borderRadius: 8,
    marginBottom: 20
  },
  progressText: {
    color: '#aaa',
    fontSize: 12,
    marginBottom: 8
  },
  progressBar: {
    height: 6,
    backgroundColor: '#1a1a1a',
    borderRadius: 3,
    overflow: 'hidden',
    marginBottom: 8
  },
  progressFill: {
    height: '100%',
    backgroundColor: '#6366f1'
  },
  scoreText: {
    color: '#6366f1',
    fontSize: 14,
    fontWeight: '600'
  },
  quizInfo: {
    flexDirection: 'row',
    gap: 10,
    marginBottom: 20
  },
  categoryTag: {
    backgroundColor: '#2a2a2a',
    color: '#6366f1',
    paddingHorizontal: 10,
    paddingVertical: 6,
    borderRadius: 6,
    fontSize: 12,
    fontWeight: '600'
  },
  languageTag: {
    backgroundColor: '#2a2a2a',
    color: '#22c55e',
    paddingHorizontal: 10,
    paddingVertical: 6,
    borderRadius: 6,
    fontSize: 12,
    fontWeight: '600'
  },
  questionSection: {
    backgroundColor: '#2a2a2a',
    padding: 20,
    borderRadius: 8,
    marginBottom: 20
  },
  question: {
    color: '#aaa',
    fontSize: 14,
    marginBottom: 15
  },
  questionContent: {
    backgroundColor: '#1a1a1a',
    padding: 15,
    borderRadius: 8
  },
  questionText: {
    color: '#fff',
    fontSize: 18,
    fontWeight: '600',
    textAlign: 'center'
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
  wrongCountBadge: {
    backgroundColor: '#4d3333',
    padding: 12,
    borderRadius: 8,
    alignItems: 'center',
    marginBottom: 20,
    borderLeftWidth: 4,
    borderLeftColor: '#ef4444'
  },
  wrongCountText: {
    color: '#ff9999',
    fontSize: 14,
    fontWeight: '600'
  },
  // Retry Button
  retryButtonContainer: {
    backgroundColor: '#3a1a1a',
    borderLeftWidth: 4,
    borderLeftColor: '#ef4444',
    padding: 15,
    borderRadius: 8,
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 20
  },
  retryButtonEmoji: {
    fontSize: 24,
    marginRight: 12
  },
  retryButtonContent: {
    flex: 1
  },
  retryButtonTitle: {
    color: '#fff',
    fontSize: 14,
    fontWeight: '600',
    marginBottom: 4
  },
  retryButtonCount: {
    color: '#aaa',
    fontSize: 11
  },
  retryButtonArrow: {
    color: '#ef4444',
    fontSize: 16,
    fontWeight: 'bold'
  }
});
