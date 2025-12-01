import React, { useState, useEffect } from 'react';
import { View, Text, TouchableOpacity, StyleSheet, Alert, Vibration, ScrollView } from 'react-native';

export default function QuizScreen({ navigation }) {
  const [quizData] = useState({
    ai: [
      { word: 'Algorithm', meaning: '알고리즘', example: 'An algorithm is a step-by-step procedure' },
      { word: 'Neural Network', meaning: '신경망', example: 'Neural networks mimic the brain' },
      { word: 'Machine Learning', meaning: '머신러닝', example: 'Machine learning enables computers to learn' }
    ],
    business: [
      { word: 'Revenue', meaning: '수익', example: 'The company increased its revenue by 20%' },
      { word: 'Market Share', meaning: '시장 점유율', example: 'Apple has a large market share' },
      { word: 'Stakeholder', meaning: '이해관계자', example: 'All stakeholders must agree' }
    ],
    finance: [
      { word: 'Portfolio', meaning: '포트폴리오', example: 'Diversify your investment portfolio' },
      { word: 'Dividend', meaning: '배당금', example: 'Shareholders receive annual dividends' },
      { word: 'Liquidity', meaning: '유동성', example: 'The company has good liquidity' }
    ],
    it: [
      { word: 'API', meaning: '응용 프로그래밍 인터페이스', example: 'Use the API to integrate services' },
      { word: 'Framework', meaning: '프레임워크', example: 'React is a popular JavaScript framework' },
      { word: 'Database', meaning: '데이터베이스', example: 'Store data in a SQL database' }
    ],
    marketing: [
      { word: 'Brand', meaning: '브랜드', example: 'Apple is a strong brand' },
      { word: 'Campaign', meaning: '캠페인', example: 'Launch a marketing campaign' },
      { word: 'Demographic', meaning: '인구통계', example: 'Target your demographic audience' }
    ],
    programming: [
      { word: 'Variable', meaning: '변수', example: 'Declare a variable in JavaScript' },
      { word: 'Function', meaning: '함수', example: 'Define a function to reuse code' },
      { word: 'Loop', meaning: '반복문', example: 'Use a loop to iterate through data' }
    ]
  });

  const categories = ['AI', 'Business', 'Finance', 'IT', 'Marketing', 'Programming'];
  
  const [selectedCategory, setSelectedCategory] = useState(null);
  const [quizMode, setQuizMode] = useState(false);
  const [currentQuestion, setCurrentQuestion] = useState(null);
  const [options, setOptions] = useState([]);
  const [score, setScore] = useState(0);
  const [totalQuestions, setTotalQuestions] = useState(0);
  const [answered, setAnswered] = useState(0);
  const [wrongQuestions, setWrongQuestions] = useState([]);
  const [showingWrongMode, setShowingWrongMode] = useState(false);

  const startQuiz = (category) => {
    const categoryKey = category.toLowerCase();
    const words = quizData[categoryKey] || [];
    
    if (words.length === 0) {
      Alert.alert('알림', '이 카테고리에 단어가 없습니다.');
      return;
    }

    setSelectedCategory(category);
    setQuizMode(true);
    setScore(0);
    setAnswered(0);
    setTotalQuestions(words.length * 3);
    setWrongQuestions([]);
    setShowingWrongMode(false);
    
    generateNewQuestion(words);
  };

  const generateNewQuestion = (words) => {
    const randomWord = words[Math.floor(Math.random() * words.length)];
    const questionType = Math.random() > 0.5 ? 'meaning' : 'word';
    
    let question, correctAnswer, incorrectAnswers;

    if (questionType === 'meaning') {
      question = `다음 뜻의 단어는?`;
      correctAnswer = randomWord.word;
      incorrectAnswers = words
        .filter(w => w.word !== randomWord.word)
        .map(w => w.word)
        .slice(0, 3);
    } else {
      question = `다음 단어의 뜻은?`;
      correctAnswer = randomWord.meaning;
      incorrectAnswers = words
        .filter(w => w.meaning !== randomWord.meaning)
        .map(w => w.meaning)
        .slice(0, 3);
    }

    const allOptions = [correctAnswer, ...incorrectAnswers].sort(() => Math.random() - 0.5);

    setCurrentQuestion({
      question,
      questionContent: questionType === 'meaning' ? randomWord.meaning : randomWord.word,
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

  const nextQuestion = () => {
    if (answered + 1 >= totalQuestions) {
      Alert.alert('완료!', `퀴즈 종료!\n정답: ${score/10}/${totalQuestions/3}\n정확도: ${Math.round((score/(totalQuestions)) * 100)}%`, [
        { text: '확인', onPress: () => endQuiz() }
      ]);
    } else {
      const categoryKey = selectedCategory.toLowerCase();
      const words = quizData[categoryKey];
      generateNewQuestion(words);
    }
  };

  const endQuiz = () => {
    setQuizMode(false);
    setSelectedCategory(null);
    setCurrentQuestion(null);
  };

  if (quizMode && currentQuestion) {
    return (
      <ScrollView style={styles.container}>
        <View style={styles.quizHeader}>
          <Text style={styles.title}>📚 {selectedCategory} 단어 퀴즈</Text>
          <View style={styles.stats}>
            <Text style={styles.stat}>진행: {answered}/{totalQuestions}</Text>
            <Text style={styles.stat}>점수: {score}pt</Text>
          </View>
        </View>

        <View style={styles.progressBar}>
          <View
            style={[
              styles.progressFill,
              { width: `${(answered / totalQuestions) * 100}%` }
            ]}
          />
        </View>

        {/* 질문 */}
        <View style={styles.questionCard}>
          <Text style={styles.questionLabel}>{currentQuestion.question}</Text>
          <View style={styles.questionContent}>
            <Text style={styles.questionText}>{currentQuestion.questionContent}</Text>
          </View>

          {currentQuestion.type === 'word' && (
            <View style={styles.exampleBox}>
              <Text style={styles.exampleLabel}>예시:</Text>
              <Text style={styles.exampleText}>{currentQuestion.word.example}</Text>
            </View>
          )}
        </View>

        {/* 선택지 */}
        <View style={styles.optionsContainer}>
          {options.map((option, idx) => (
            <TouchableOpacity
              key={idx}
              style={styles.optionButton}
              onPress={() => handleAnswer(option)}
            >
              <View style={styles.optionBox}>
                <View style={styles.optionNumber}>
                  <Text style={styles.optionNumberText}>{String.fromCharCode(65 + idx)}</Text>
                </View>
                <Text style={styles.optionText}>{option}</Text>
              </View>
            </TouchableOpacity>
          ))}
        </View>

        <TouchableOpacity
          style={styles.exitButton}
          onPress={endQuiz}
        >
          <Text style={styles.exitButtonText}>퀴즈 종료</Text>
        </TouchableOpacity>
      </ScrollView>
    );
  }

  return (
    <ScrollView style={styles.container}>
      <Text style={styles.title}>📚 단어 퀴즈</Text>

      {wrongQuestions.length > 0 && (
        <TouchableOpacity
          style={styles.wrongQuestionsButton}
          onPress={() => {
            setShowingWrongMode(true);
            setQuizMode(true);
            setAnswered(0);
            setScore(0);
            const categoryKey = selectedCategory?.toLowerCase() || 'ai';
            const words = quizData[categoryKey];
            generateNewQuestion(words);
          }}
        >
          <Text style={styles.wrongQuestionsText}>
            ⚠️ 틀린 문제 {wrongQuestions.length}개 재도전
          </Text>
        </TouchableOpacity>
      )}

      <View style={styles.categoryGrid}>
        {categories.map((category) => (
          <TouchableOpacity
            key={category}
            style={styles.categoryCard}
            onPress={() => startQuiz(category)}
          >
            <View style={styles.categoryContent}>
              <Text style={styles.categoryIcon}>📖</Text>
              <Text style={styles.categoryName}>{category}</Text>
              <Text style={styles.categoryDesc}>단어 퀴즈</Text>
            </View>
          </TouchableOpacity>
        ))}
      </View>

      <View style={styles.infoBox}>
        <Text style={styles.infoTitle}>ℹ️ 퀴즈 방법</Text>
        <Text style={styles.infoText}>• 4개 선택지 중 정답을 고르세요</Text>
        <Text style={styles.infoText}>• 정답마다 경험치 +10 획득</Text>
        <Text style={styles.infoText}>• 카테고리별로 단어를 학습하세요</Text>
        <Text style={styles.infoText}>• 틀린 문제는 따로 복습할 수 있습니다</Text>
      </View>
    </ScrollView>
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
  wrongQuestionsButton: {
    backgroundColor: '#ef4444',
    padding: 15,
    borderRadius: 8,
    marginBottom: 20,
    alignItems: 'center'
  },
  wrongQuestionsText: {
    color: '#fff',
    fontSize: 14,
    fontWeight: 'bold'
  },
  quizHeader: {
    marginBottom: 20
  },
  stats: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginTop: 10
  },
  stat: {
    color: '#aaa',
    fontSize: 12
  },
  progressBar: {
    height: 12,
    backgroundColor: '#3a3a3a',
    borderRadius: 6,
    marginBottom: 20,
    overflow: 'hidden'
  },
  progressFill: {
    height: '100%',
    backgroundColor: '#6366f1'
  },
  questionCard: {
    backgroundColor: '#2a2a2a',
    padding: 20,
    borderRadius: 8,
    marginBottom: 20,
    borderLeftWidth: 4,
    borderLeftColor: '#6366f1'
  },
  questionLabel: {
    color: '#aaa',
    fontSize: 12,
    marginBottom: 10,
    fontWeight: 'bold'
  },
  questionContent: {
    backgroundColor: '#1a1a1a',
    padding: 20,
    borderRadius: 8,
    marginBottom: 15,
    borderWidth: 2,
    borderColor: '#6366f1'
  },
  questionText: {
    color: '#6366f1',
    fontSize: 18,
    fontWeight: 'bold',
    textAlign: 'center'
  },
  exampleBox: {
    backgroundColor: '#1a1a1a',
    padding: 12,
    borderRadius: 6,
    borderLeftWidth: 3,
    borderLeftColor: '#f59e0b'
  },
  exampleLabel: {
    color: '#f59e0b',
    fontSize: 11,
    fontWeight: 'bold',
    marginBottom: 5
  },
  exampleText: {
    color: '#bbb',
    fontSize: 12,
    lineHeight: 18
  },
  optionsContainer: {
    marginBottom: 20,
    gap: 10
  },
  optionButton: {
    marginVertical: 4
  },
  optionBox: {
    backgroundColor: '#2a2a2a',
    padding: 15,
    borderRadius: 8,
    flexDirection: 'row',
    alignItems: 'center',
    borderWidth: 2,
    borderColor: '#3a3a3a'
  },
  optionNumber: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: '#6366f1',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 15
  },
  optionNumberText: {
    color: '#fff',
    fontWeight: 'bold',
    fontSize: 14
  },
  optionText: {
    color: '#fff',
    fontSize: 14,
    flex: 1
  },
  exitButton: {
    backgroundColor: '#ef4444',
    padding: 12,
    borderRadius: 8,
    alignItems: 'center',
    marginBottom: 20
  },
  exitButtonText: {
    color: '#fff',
    fontSize: 14,
    fontWeight: 'bold'
  },
  categoryGrid: {
    display: 'flex',
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 10,
    marginBottom: 30
  },
  categoryCard: {
    width: '48%',
    backgroundColor: '#2a2a2a',
    padding: 20,
    borderRadius: 8,
    borderLeftWidth: 4,
    borderLeftColor: '#6366f1'
  },
  categoryContent: {
    alignItems: 'center'
  },
  categoryIcon: {
    fontSize: 32,
    marginBottom: 8
  },
  categoryName: {
    color: '#fff',
    fontSize: 14,
    fontWeight: 'bold',
    marginBottom: 4
  },
  categoryDesc: {
    color: '#aaa',
    fontSize: 11
  },
  infoBox: {
    backgroundColor: '#2a2a2a',
    padding: 15,
    borderRadius: 8,
    marginBottom: 30
  },
  infoTitle: {
    color: '#fff',
    fontSize: 13,
    fontWeight: 'bold',
    marginBottom: 10
  },
  infoText: {
    color: '#aaa',
    fontSize: 12,
    marginVertical: 4,
    lineHeight: 18
  }
});
