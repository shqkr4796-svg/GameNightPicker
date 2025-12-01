import React, { useState } from 'react';
import { View, Text, TouchableOpacity, StyleSheet, FlatList, Alert, Modal, TextInput, ScrollView, Vibration } from 'react-native';

export default function WordManagementScreen({ navigation }) {
  const [words, setWords] = useState([
    { id: 1, word: 'Algorithm', meaning: '알고리즘', category: 'AI' },
    { id: 2, word: 'Revenue', meaning: '수익', category: 'Business' },
    { id: 3, word: 'Portfolio', meaning: '포트폴리오', category: 'Finance' },
    { id: 4, word: 'API', meaning: '응용 프로그래밍 인터페이스', category: 'IT' },
    { id: 5, word: 'Brand', meaning: '브랜드', category: 'Marketing' },
    { id: 6, word: 'Variable', meaning: '변수', category: 'Programming' }
  ]);

  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [modalVisible, setModalVisible] = useState(false);
  const [editingWord, setEditingWord] = useState(null);
  const [newWord, setNewWord] = useState('');
  const [newMeaning, setNewMeaning] = useState('');
  const [newCategory, setNewCategory] = useState('AI');
  const [selectedWords, setSelectedWords] = useState(new Set());

  const categories = ['AI', 'Business', 'Finance', 'IT', 'Marketing', 'Programming'];

  const filteredWords = words.filter((word) => {
    const matchesSearch =
      word.word.toLowerCase().includes(searchTerm.toLowerCase()) ||
      word.meaning.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesCategory = selectedCategory === 'all' || word.category === selectedCategory;
    return matchesSearch && matchesCategory;
  });

  const handleAddWord = () => {
    if (!newWord.trim() || !newMeaning.trim()) {
      Alert.alert('알림', '단어와 뜻을 입력해주세요.');
      return;
    }

    if (editingWord) {
      // 수정
      setWords(
        words.map((w) =>
          w.id === editingWord.id
            ? { ...w, word: newWord, meaning: newMeaning, category: newCategory }
            : w
        )
      );
      Vibration.vibrate([0, 100, 50, 100]);
      Alert.alert('성공', '단어가 수정되었습니다.');
    } else {
      // 추가
      setWords([
        ...words,
        { id: Math.max(...words.map((w) => w.id), 0) + 1, word: newWord, meaning: newMeaning, category: newCategory }
      ]);
      Vibration.vibrate([0, 100, 50, 100]);
      Alert.alert('성공', '단어가 추가되었습니다.');
    }

    setNewWord('');
    setNewMeaning('');
    setNewCategory('AI');
    setEditingWord(null);
    setModalVisible(false);
  };

  const handleDeleteWord = (id) => {
    Alert.alert('삭제', '이 단어를 삭제하시겠습니까?', [
      { text: '취소', style: 'cancel' },
      {
        text: '삭제',
        onPress: () => {
          setWords(words.filter((w) => w.id !== id));
          Vibration.vibrate(200);
          Alert.alert('완료', '단어가 삭제되었습니다.');
        },
        style: 'destructive'
      }
    ]);
  };

  const handleEditWord = (word) => {
    setEditingWord(word);
    setNewWord(word.word);
    setNewMeaning(word.meaning);
    setNewCategory(word.category);
    setModalVisible(true);
  };

  const handleSelectWord = (id) => {
    const newSelected = new Set(selectedWords);
    if (newSelected.has(id)) {
      newSelected.delete(id);
    } else {
      newSelected.add(id);
    }
    setSelectedWords(newSelected);
  };

  const handleDeleteSelected = () => {
    if (selectedWords.size === 0) {
      Alert.alert('알림', '삭제할 단어를 선택해주세요.');
      return;
    }

    Alert.alert('삭제', `${selectedWords.size}개의 단어를 삭제하시겠습니까?`, [
      { text: '취소', style: 'cancel' },
      {
        text: '삭제',
        onPress: () => {
          setWords(words.filter((w) => !selectedWords.has(w.id)));
          setSelectedWords(new Set());
          Vibration.vibrate([100, 100, 100]);
          Alert.alert('완료', `${selectedWords.size}개의 단어가 삭제되었습니다.`);
        },
        style: 'destructive'
      }
    ]);
  };

  const handleChangeCategorySelected = (category) => {
    if (selectedWords.size === 0) {
      Alert.alert('알림', '카테고리를 변경할 단어를 선택해주세요.');
      return;
    }

    setWords(
      words.map((w) =>
        selectedWords.has(w.id) ? { ...w, category } : w
      )
    );
    setSelectedWords(new Set());
    Vibration.vibrate([0, 100, 50, 100]);
    Alert.alert('완료', `${selectedWords.size}개 단어의 카테고리가 변경되었습니다.`);
  };

  const renderWordItem = ({ item }) => (
    <View style={[styles.wordItem, selectedWords.has(item.id) && styles.selectedWordItem]}>
      <TouchableOpacity
        style={styles.selectCheckbox}
        onPress={() => handleSelectWord(item.id)}
      >
        <View
          style={[
            styles.checkbox,
            selectedWords.has(item.id) && styles.checkboxSelected
          ]}
        >
          {selectedWords.has(item.id) && <Text style={styles.checkmark}>✓</Text>}
        </View>
      </TouchableOpacity>

      <View style={styles.wordContent}>
        <Text style={styles.wordText}>{item.word}</Text>
        <Text style={styles.meaningText}>{item.meaning}</Text>
        <Text style={[styles.categoryBadge, { color: '#6366f1' }]}>{item.category}</Text>
      </View>

      <View style={styles.actionButtons}>
        <TouchableOpacity
          style={styles.editButton}
          onPress={() => handleEditWord(item)}
        >
          <Text style={styles.editButtonText}>✎</Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={styles.deleteButton}
          onPress={() => handleDeleteWord(item.id)}
        >
          <Text style={styles.deleteButtonText}>✕</Text>
        </TouchableOpacity>
      </View>
    </View>
  );

  return (
    <ScrollView style={styles.container}>
      <Text style={styles.title}>📝 단어 관리</Text>

      {/* 통계 */}
      <View style={styles.statsContainer}>
        <View style={styles.statBox}>
          <Text style={styles.statValue}>{words.length}</Text>
          <Text style={styles.statLabel}>총 단어</Text>
        </View>
        <View style={styles.statBox}>
          <Text style={styles.statValue}>{categories.length}</Text>
          <Text style={styles.statLabel}>카테고리</Text>
        </View>
        <View style={styles.statBox}>
          <Text style={styles.statValue}>{filteredWords.length}</Text>
          <Text style={styles.statLabel}>검색 결과</Text>
        </View>
      </View>

      {/* 검색 */}
      <View style={styles.searchContainer}>
        <TextInput
          style={styles.searchInput}
          placeholder="단어, 뜻 검색..."
          placeholderTextColor="#666"
          value={searchTerm}
          onChangeText={setSearchTerm}
        />
      </View>

      {/* 카테고리 필터 */}
      <ScrollView horizontal showsHorizontalScrollIndicator={false} style={styles.categoryFilter}>
        <TouchableOpacity
          style={[styles.categoryFilterButton, selectedCategory === 'all' && styles.activeFilterButton]}
          onPress={() => setSelectedCategory('all')}
        >
          <Text style={selectedCategory === 'all' ? styles.activeFilterText : styles.filterText}>전체</Text>
        </TouchableOpacity>
        {categories.map((cat) => (
          <TouchableOpacity
            key={cat}
            style={[styles.categoryFilterButton, selectedCategory === cat && styles.activeFilterButton]}
            onPress={() => setSelectedCategory(cat)}
          >
            <Text style={selectedCategory === cat ? styles.activeFilterText : styles.filterText}>{cat}</Text>
          </TouchableOpacity>
        ))}
      </ScrollView>

      {/* 액션 버튼 */}
      <View style={styles.actionBar}>
        <TouchableOpacity
          style={styles.addButton}
          onPress={() => {
            setEditingWord(null);
            setNewWord('');
            setNewMeaning('');
            setNewCategory('AI');
            setModalVisible(true);
          }}
        >
          <Text style={styles.addButtonText}>➕ 단어 추가</Text>
        </TouchableOpacity>

        {selectedWords.size > 0 && (
          <>
            <TouchableOpacity
              style={styles.changeCategoryButton}
              onPress={() => {
                Alert.alert('카테고리 변경', '변경할 카테고리를 선택하세요', [
                  ...categories.map((cat) => ({
                    text: cat,
                    onPress: () => handleChangeCategorySelected(cat)
                  })),
                  { text: '취소', style: 'cancel' }
                ]);
              }}
            >
              <Text style={styles.changeCategoryButtonText}>📁 카테고리 변경</Text>
            </TouchableOpacity>

            <TouchableOpacity
              style={styles.deleteAllButton}
              onPress={handleDeleteSelected}
            >
              <Text style={styles.deleteAllButtonText}>🗑️ 삭제 ({selectedWords.size})</Text>
            </TouchableOpacity>
          </>
        )}
      </View>

      {/* 단어 목록 */}
      <View style={styles.listContainer}>
        {filteredWords.length > 0 ? (
          <FlatList
            data={filteredWords}
            renderItem={renderWordItem}
            keyExtractor={(item) => item.id.toString()}
            scrollEnabled={false}
            ItemSeparatorComponent={() => <View style={styles.separator} />}
          />
        ) : (
          <View style={styles.emptyContainer}>
            <Text style={styles.emptyText}>단어가 없습니다.</Text>
          </View>
        )}
      </View>

      {/* 추가/수정 모달 */}
      <Modal visible={modalVisible} transparent={true} animationType="slide" onRequestClose={() => setModalVisible(false)}>
        <View style={styles.modalContainer}>
          <View style={styles.modalContent}>
            <View style={styles.modalHeader}>
              <Text style={styles.modalTitle}>{editingWord ? '단어 수정' : '단어 추가'}</Text>
              <TouchableOpacity onPress={() => setModalVisible(false)}>
                <Text style={styles.closeButton}>✕</Text>
              </TouchableOpacity>
            </View>

            <View style={styles.modalBody}>
              <Text style={styles.inputLabel}>단어</Text>
              <TextInput
                style={styles.textInput}
                placeholder="단어를 입력하세요"
                placeholderTextColor="#666"
                value={newWord}
                onChangeText={setNewWord}
              />

              <Text style={styles.inputLabel}>뜻</Text>
              <TextInput
                style={styles.textInput}
                placeholder="뜻을 입력하세요"
                placeholderTextColor="#666"
                value={newMeaning}
                onChangeText={setNewMeaning}
              />

              <Text style={styles.inputLabel}>카테고리</Text>
              <ScrollView horizontal showsHorizontalScrollIndicator={false} style={styles.categorySelection}>
                {categories.map((cat) => (
                  <TouchableOpacity
                    key={cat}
                    style={[styles.categoryOption, newCategory === cat && styles.selectedCategoryOption]}
                    onPress={() => setNewCategory(cat)}
                  >
                    <Text style={newCategory === cat ? styles.selectedCategoryText : styles.categoryOptionText}>{cat}</Text>
                  </TouchableOpacity>
                ))}
              </ScrollView>
            </View>

            <View style={styles.modalFooter}>
              <TouchableOpacity style={styles.cancelButton} onPress={() => setModalVisible(false)}>
                <Text style={styles.cancelButtonText}>취소</Text>
              </TouchableOpacity>

              <TouchableOpacity style={styles.confirmButton} onPress={handleAddWord}>
                <Text style={styles.confirmButtonText}>{editingWord ? '수정' : '추가'}</Text>
              </TouchableOpacity>
            </View>
          </View>
        </View>
      </Modal>
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
    marginBottom: 15
  },
  statsContainer: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    marginBottom: 20,
    gap: 8
  },
  statBox: {
    flex: 1,
    backgroundColor: '#2a2a2a',
    padding: 12,
    borderRadius: 8,
    alignItems: 'center'
  },
  statValue: {
    color: '#6366f1',
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 4
  },
  statLabel: {
    color: '#aaa',
    fontSize: 11
  },
  searchContainer: {
    marginBottom: 15
  },
  searchInput: {
    backgroundColor: '#2a2a2a',
    color: '#fff',
    borderRadius: 8,
    paddingHorizontal: 12,
    paddingVertical: 10,
    fontSize: 14,
    borderWidth: 1,
    borderColor: '#3a3a3a'
  },
  categoryFilter: {
    marginBottom: 15,
    marginHorizontal: -20,
    paddingHorizontal: 20
  },
  categoryFilterButton: {
    backgroundColor: '#2a2a2a',
    paddingHorizontal: 12,
    paddingVertical: 8,
    borderRadius: 6,
    marginRight: 8,
    borderWidth: 1,
    borderColor: '#3a3a3a'
  },
  activeFilterButton: {
    backgroundColor: '#6366f1',
    borderColor: '#6366f1'
  },
  filterText: {
    color: '#aaa',
    fontSize: 12,
    fontWeight: '600'
  },
  activeFilterText: {
    color: '#fff',
    fontSize: 12,
    fontWeight: '600'
  },
  actionBar: {
    gap: 8,
    marginBottom: 15
  },
  addButton: {
    backgroundColor: '#22c55e',
    padding: 12,
    borderRadius: 8,
    alignItems: 'center'
  },
  addButtonText: {
    color: '#fff',
    fontSize: 14,
    fontWeight: 'bold'
  },
  changeCategoryButton: {
    backgroundColor: '#f59e0b',
    padding: 12,
    borderRadius: 8,
    alignItems: 'center'
  },
  changeCategoryButtonText: {
    color: '#fff',
    fontSize: 14,
    fontWeight: 'bold'
  },
  deleteAllButton: {
    backgroundColor: '#ef4444',
    padding: 12,
    borderRadius: 8,
    alignItems: 'center'
  },
  deleteAllButtonText: {
    color: '#fff',
    fontSize: 14,
    fontWeight: 'bold'
  },
  listContainer: {
    marginBottom: 30
  },
  wordItem: {
    backgroundColor: '#2a2a2a',
    padding: 12,
    borderRadius: 8,
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8
  },
  selectedWordItem: {
    backgroundColor: '#1f3a1f',
    borderWidth: 2,
    borderColor: '#22c55e'
  },
  selectCheckbox: {
    padding: 8
  },
  checkbox: {
    width: 24,
    height: 24,
    borderRadius: 6,
    borderWidth: 2,
    borderColor: '#3a3a3a',
    justifyContent: 'center',
    alignItems: 'center'
  },
  checkboxSelected: {
    backgroundColor: '#22c55e',
    borderColor: '#22c55e'
  },
  checkmark: {
    color: '#fff',
    fontWeight: 'bold',
    fontSize: 14
  },
  wordContent: {
    flex: 1,
    marginLeft: 8
  },
  wordText: {
    color: '#fff',
    fontSize: 14,
    fontWeight: 'bold',
    marginBottom: 3
  },
  meaningText: {
    color: '#aaa',
    fontSize: 12,
    marginBottom: 4
  },
  categoryBadge: {
    fontSize: 10,
    fontWeight: '600'
  },
  actionButtons: {
    flexDirection: 'row',
    gap: 8
  },
  editButton: {
    width: 32,
    height: 32,
    borderRadius: 6,
    backgroundColor: '#3b82f6',
    justifyContent: 'center',
    alignItems: 'center'
  },
  editButtonText: {
    color: '#fff',
    fontSize: 16
  },
  deleteButton: {
    width: 32,
    height: 32,
    borderRadius: 6,
    backgroundColor: '#ef4444',
    justifyContent: 'center',
    alignItems: 'center'
  },
  deleteButtonText: {
    color: '#fff',
    fontSize: 16
  },
  separator: {
    height: 0
  },
  emptyContainer: {
    paddingVertical: 30,
    alignItems: 'center'
  },
  emptyText: {
    color: '#666',
    fontSize: 14
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
    paddingBottom: 40
  },
  modalHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 20
  },
  modalTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#fff'
  },
  closeButton: {
    color: '#fff',
    fontSize: 24,
    fontWeight: 'bold'
  },
  modalBody: {
    marginBottom: 20
  },
  inputLabel: {
    color: '#6366f1',
    fontSize: 12,
    fontWeight: 'bold',
    marginBottom: 8,
    marginTop: 12
  },
  textInput: {
    backgroundColor: '#1a1a1a',
    color: '#fff',
    borderRadius: 8,
    paddingHorizontal: 12,
    paddingVertical: 10,
    fontSize: 14,
    borderWidth: 1,
    borderColor: '#3a3a3a'
  },
  categorySelection: {
    marginBottom: 15,
    marginHorizontal: -20,
    paddingHorizontal: 20
  },
  categoryOption: {
    backgroundColor: '#1a1a1a',
    paddingHorizontal: 12,
    paddingVertical: 8,
    borderRadius: 6,
    marginRight: 8,
    borderWidth: 1,
    borderColor: '#3a3a3a'
  },
  selectedCategoryOption: {
    backgroundColor: '#6366f1',
    borderColor: '#6366f1'
  },
  categoryOptionText: {
    color: '#aaa',
    fontSize: 12
  },
  selectedCategoryText: {
    color: '#fff',
    fontSize: 12,
    fontWeight: 'bold'
  },
  modalFooter: {
    flexDirection: 'row',
    gap: 10
  },
  cancelButton: {
    flex: 1,
    backgroundColor: '#666',
    padding: 12,
    borderRadius: 8,
    alignItems: 'center'
  },
  cancelButtonText: {
    color: '#fff',
    fontSize: 14,
    fontWeight: 'bold'
  },
  confirmButton: {
    flex: 1,
    backgroundColor: '#6366f1',
    padding: 12,
    borderRadius: 8,
    alignItems: 'center'
  },
  confirmButtonText: {
    color: '#fff',
    fontSize: 14,
    fontWeight: 'bold'
  }
});
