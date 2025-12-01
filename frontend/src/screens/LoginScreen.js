import React, { useState } from 'react';
import { View, Text, TextInput, TouchableOpacity, StyleSheet, Alert, ActivityIndicator } from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { playerAPI } from '../services/api';

export default function LoginScreen({ navigation }) {
  const [loading, setLoading] = useState(false);
  const [playerName, setPlayerName] = useState('');

  const handleStartGame = async () => {
    if (!playerName.trim()) {
      Alert.alert('오류', '플레이어 이름을 입력해주세요.');
      return;
    }

    setLoading(true);
    try {
      const response = await playerAPI.start();
      
      if (response.data.success) {
        // 토큰 저장
        await AsyncStorage.setItem('auth_token', response.data.data.token);
        await AsyncStorage.setItem('player_id', response.data.data.player_id);
        await AsyncStorage.setItem('player_name', playerName);

        Alert.alert('환영합니다!', `${playerName}님, 게임에 입장했습니다!`);
        navigation.replace('MainHub');
      } else {
        Alert.alert('오류', response.data.error || '게임 시작 실패');
      }
    } catch (error) {
      Alert.alert('오류', error.message || '서버 연결 실패');
    } finally {
      setLoading(false);
    }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>생명 시뮬레이션 게임</Text>
      <Text style={styles.subtitle}>플레이어 이름을 입력하세요</Text>

      <TextInput
        style={styles.input}
        placeholder="플레이어 이름"
        placeholderTextColor="#999"
        value={playerName}
        onChangeText={setPlayerName}
        editable={!loading}
      />

      <TouchableOpacity
        style={[styles.button, loading && styles.buttonDisabled]}
        onPress={handleStartGame}
        disabled={loading}
      >
        {loading ? (
          <ActivityIndicator color="#fff" />
        ) : (
          <Text style={styles.buttonText}>게임 시작</Text>
        )}
      </TouchableOpacity>

      <Text style={styles.info}>
        게임을 시작하면 새로운 캐릭터가 생성됩니다.
      </Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#1a1a1a',
    padding: 20
  },
  title: {
    fontSize: 32,
    fontWeight: 'bold',
    color: '#fff',
    marginBottom: 10,
    textAlign: 'center'
  },
  subtitle: {
    fontSize: 16,
    color: '#aaa',
    marginBottom: 30,
    textAlign: 'center'
  },
  input: {
    width: '100%',
    padding: 15,
    marginBottom: 20,
    backgroundColor: '#2a2a2a',
    color: '#fff',
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#444',
    fontSize: 16
  },
  button: {
    width: '100%',
    padding: 15,
    backgroundColor: '#6366f1',
    borderRadius: 8,
    alignItems: 'center',
    marginBottom: 20
  },
  buttonDisabled: {
    opacity: 0.6
  },
  buttonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold'
  },
  info: {
    color: '#666',
    fontSize: 12,
    textAlign: 'center',
    marginTop: 20
  }
});
