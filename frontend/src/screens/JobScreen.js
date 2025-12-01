import React, { useState, useEffect } from 'react';
import { View, Text, TouchableOpacity, StyleSheet, ScrollView, Alert, ActivityIndicator, Vibration } from 'react-native';
import { jobAPI } from '../services/api';

export default function JobScreen({ navigation }) {
  const [jobs, setJobs] = useState([]);
  const [currentJob, setCurrentJob] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadJobs();
  }, []);

  const loadJobs = async () => {
    setLoading(true);
    try {
      const response = await jobAPI.list();
      if (response.data.success) {
        setJobs(response.data.data.jobs || []);
        setCurrentJob(response.data.data.current_job);
      }
    } catch (error) {
      Alert.alert('오류', '직업 데이터 로드 실패');
    } finally {
      setLoading(false);
    }
  };

  const handleApplyJob = async (jobId) => {
    Vibration.vibrate([0, 100, 50, 100]);
    try {
      const response = await jobAPI.apply(jobId);
      if (response.data.success) {
        Alert.alert('성공', '직업에 지원했습니다!');
        loadJobs();
      }
    } catch (error) {
      Alert.alert('오류', '지원 실패');
    }
  };

  const handleWork = async () => {
    if (!currentJob) {
      Alert.alert('알림', '먼저 직업을 선택해주세요');
      return;
    }
    try {
      const response = await jobAPI.work();
      if (response.data.success) {
        Vibration.vibrate([0, 100, 50, 100, 50, 100]);
        Alert.alert('성공', `${response.data.data.earned || 0}원을 획득했습니다!`);
        loadJobs();
      }
    } catch (error) {
      Alert.alert('오류', '업무 수행 실패');
    }
  };

  const handleQuit = async () => {
    try {
      const response = await jobAPI.quit();
      if (response.data.success) {
        Alert.alert('성공', '직업을 그만두었습니다');
        loadJobs();
      }
    } catch (error) {
      Alert.alert('오류', '사직 실패');
    }
  };

  if (loading) {
    return <View style={styles.container}><ActivityIndicator color="#6366f1" size="large" /></View>;
  }

  return (
    <ScrollView style={styles.container}>
      <Text style={styles.title}>직업</Text>
      <Text style={styles.subtitle}>직업을 선택하여 돈을 벌어보세요</Text>

      {currentJob && (
        <View style={styles.currentJobCard}>
          <Text style={styles.currentJobTitle}>현재 직업</Text>
          <Text style={styles.jobName}>{currentJob.name}</Text>
          <Text style={styles.jobSalary}>월급: ₩{(currentJob.salary || 0).toLocaleString()}</Text>
          <View style={styles.jobActions}>
            <TouchableOpacity style={[styles.button, styles.buttonPrimary]} onPress={handleWork}>
              <Text style={styles.buttonText}>업무 수행</Text>
            </TouchableOpacity>
            <TouchableOpacity style={[styles.button, styles.buttonDanger]} onPress={handleQuit}>
              <Text style={styles.buttonText}>사직</Text>
            </TouchableOpacity>
          </View>
        </View>
      )}

      <Text style={styles.sectionTitle}>직업 목록</Text>
      <View style={styles.jobList}>
        {jobs.map((job, idx) => (
          <View key={idx} style={styles.jobCard}>
            <View style={styles.jobHeader}>
              <Text style={styles.jobName}>{job.name || `직업 ${idx + 1}`}</Text>
              <Text style={styles.jobLevel}>Lv. {job.required_level || 1}+</Text>
            </View>
            <Text style={styles.jobDesc}>{job.description || '돈을 버는 직업입니다'}</Text>
            <Text style={styles.jobSalary}>월급: ₩{(job.salary || 0).toLocaleString()}</Text>
            {currentJob?.id !== job.id && (
              <TouchableOpacity
                style={[styles.button, styles.buttonSecondary]}
                onPress={() => handleApplyJob(job.id)}
              >
                <Text style={styles.buttonText}>지원하기</Text>
              </TouchableOpacity>
            )}
          </View>
        ))}
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#1a1a1a', padding: 16 },
  title: { fontSize: 28, fontWeight: 'bold', color: '#fff', marginBottom: 5 },
  subtitle: { fontSize: 14, color: '#aaa', marginBottom: 20 },
  currentJobCard: { backgroundColor: '#2a2a2a', padding: 15, borderRadius: 8, marginBottom: 20, borderLeftWidth: 4, borderLeftColor: '#22c55e' },
  currentJobTitle: { color: '#aaa', fontSize: 11, marginBottom: 5 },
  jobName: { color: '#fff', fontSize: 16, fontWeight: 'bold', marginBottom: 5 },
  jobDesc: { color: '#aaa', fontSize: 12, marginBottom: 10 },
  jobSalary: { color: '#22c55e', fontSize: 13, fontWeight: '600', marginBottom: 10 },
  jobLevel: { backgroundColor: '#6366f1', color: '#fff', paddingHorizontal: 8, paddingVertical: 4, borderRadius: 4, fontSize: 11, fontWeight: '600' },
  jobActions: { flexDirection: 'row', gap: 8 },
  sectionTitle: { fontSize: 16, fontWeight: '600', color: '#6366f1', marginBottom: 12 },
  jobList: { gap: 12, marginBottom: 30 },
  jobCard: { backgroundColor: '#2a2a2a', padding: 15, borderRadius: 8 },
  jobHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 8 },
  button: { paddingVertical: 10, borderRadius: 6, alignItems: 'center', flex: 1 },
  buttonPrimary: { backgroundColor: '#6366f1' },
  buttonSecondary: { backgroundColor: '#3a3a3a' },
  buttonDanger: { backgroundColor: '#ef4444' },
  buttonText: { color: '#fff', fontWeight: 'bold', fontSize: 13 }
});
