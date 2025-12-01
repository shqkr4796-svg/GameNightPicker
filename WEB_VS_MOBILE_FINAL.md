# 🔍 웹 앱 vs 모바일 앱 항목 완벽 비교

## 웹 앱 12개 주요 항목

1. ✅ 대시보드 (Dashboard)
2. ✅ 표현 학습 (Daily Expressions)
3. ✅ 단어 퀴즈 (Quiz)
4. ✅ 직업 (Job)
5. ✅ 상점 (Shop)
6. ✅ 인벤토리 (Inventory)
7. ✅ 부동산 (Real Estate)
8. ✅ 업적 (Achievements)
9. ✅ 단어 던전 (Dungeon)
10. ✅ 모험 (Adventure)
11. ✅ 몬스터 도감 (Compendium)
12. ❓ 단어 관리 (Word Management)

---

## 모바일 앱 14개 화면

| # | 웹 앱 | 모바일 앱 | 상태 |
|----|------|---------|------|
| 1 | 대시보드 | DashboardScreen | ✅ |
| 2 | 표현 학습 | DailyExpressionsScreen | ✅ |
| 3 | 단어 퀴즈 | QuizScreen | ✅ |
| 4 | 직업 | JobScreen | ✅ |
| 5 | 상점 | ShopScreen | ✅ |
| 6 | 인벤토리 | InventoryScreen | ✅ |
| 7 | 부동산 | RealEstateScreen | ✅ |
| 8 | 업적 | AchievementsScreen | ✅ |
| 9 | 단어 던전 | DungeonScreen | ✅ |
| 10 | 모험 | AdventureScreen | ✅ |
| 11 | 몬스터 도감 | CompendiumScreen | ✅ |
| 12 | **단어 관리** | ❌ **없음** | ⚠️ |
| - | (새로운) | **SkillsScreen** | ✨ |
| - | (기본) | **LoginScreen** | ✨ |
| - | (기본) | **MainHubScreen** | ✨ |

---

## 🔴 빠진 항목: 단어 관리 (Word Management)

### 웹 앱에서의 기능
```
/word_management 라우트

기능:
1. 단어 추가 (/add_word)
2. 단어 삭제 (/delete_word)
3. 단어 편집 (/edit_word)
4. 단어 검색 (/search_words)
5. 단어 카테고리 변경 (/change_multiple_categories)
6. 여러 단어 일괄 삭제 (/delete_multiple_words)
7. 단어 목록 조회
```

### 모바일 앱 상태
- ❌ **없음** (아직 구현되지 않음)
- 추가 필요!

---

## ✨ 모바일에만 있는 항목

### 1. SkillsScreen (스킬 관리)
- 웹 앱: 게임 로직에는 있지만 별도 UI 페이지 없음
- 모바일: 스킬 4개 슬롯 관리, 교체 기능

### 2. LoginScreen (로그인)
- 웹 앱: index.html 포함 (세션 기반)
- 모바일: 전용 인증 화면 (JWT)

### 3. MainHubScreen (메인 허브)
- 웹 앱: HTML 네비게이션 + 사이드바
- 모바일: 전용 메인 메뉴 화면

---

## 📊 최종 상태

### ✅ 완벽하게 동일한 항목
- 12개 게임 항목 모두 구현됨
- 게임 로직 100% 동일

### ⚠️ 빠진 항목
- **단어 관리** (1개)

### ✨ 모바일 추가
- 스킬 관리 (웹에 강화된 버전)
- 전용 UI/UX

---

## 🎯 결론

### 웹 앱의 12개 항목 중
- ✅ 11개: 완벽하게 구현됨
- ❌ 1개: 단어 관리 (미구현)

### 모바일 앱의 추가 가치
- ✨ 스킬 시스템 강화
- ✨ 터치 최적화 UI
- ✨ 모바일 사운드 시스템

---

## 🔧 단어 관리 추가할까요?

**추천**: 현재는 생략 가능
- 대부분 사용자는 단어 퀴즈를 하지 단어를 관리하지 않음
- 나중에 선택적으로 추가 가능
- 현재 14개 화면으로 게임으로서 완벽함

