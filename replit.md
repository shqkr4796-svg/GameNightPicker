# Life Simulation Game

## Overview

A text-based life simulation game built with Flask where players can create characters, develop skills through English vocabulary quizzes, pursue careers, buy real estate, and track achievements. The game features a progression system with levels, stats, various life activities, and a comprehensive monster collection system with Word Dungeon.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Template Engine**: Jinja2 templates with Bootstrap 5 dark theme
- **UI Framework**: Bootstrap 5 with custom CSS animations and responsive design
- **JavaScript**: Vanilla JavaScript with Web Audio API for monster sound effects, Feather icons for interactive elements
- **Static Assets**: CSS animations, progress bars, monster images (planned), sound effects
- **Audio System**: 
  - Rarity-based monster appearance sound effects (Rare, Epic, Unique, Legendary)
  - RPG battle background music with single-minor-key progression (Am-G-C-F), drum beats, synth

### Backend Architecture
- **Web Framework**: Flask with session-based state management
- **Game Logic**: Modular Python functions handling player progression, dungeon mechanics, and monster system
- **Data Storage**: JSON file-based persistence + monsters.py for monster database
- **Route Structure**: RESTful endpoints for dungeons, monsters, compendium, and trading

### Data Management
- **Save System**: JSON file storage for player progress with automatic save/load functionality
- **Monster System**: Fixed monster database (42 unique monsters) with individual stat ranges
- **Compendium**: Player monster collection with captured monsters stored by monster ID
- **Game Data**: Vocabulary words, jobs, real estate, monsters, dungeons

### Game Mechanics
- **Word Dungeon**: Quiz-based dungeon with:
  - 42 unique pre-defined monsters (Rare: 10, Epic: 10, Unique: 10, Legendary: 12)
  - Rarity-based random spawning
  - Monster-specific stat generation with randomization
  - Multiple choice vocabulary questions per monster
  - Capture probability based on rarity (Rare: 50%, Epic: 10%, Unique: 5%, Legendary: 1%)
  - Compendium tracking of captured monsters

- **Adventure System**: 
  - 200 stages in general difficulty + unlockable 200 stages in hard (심화) difficulty
  - 3-monster team battles with turn-based combat
  - Hard difficulty (심화): Enemies have 2x attack and 2x HP, skill card drop rate 2x higher
  - Automatic stage reset to 1 when clearing stage 200 (can unlock hard difficulty or replay hard)
  - Text-to-Speech enabled for vocabulary practice

- **Monster System**: 
  - Fixed monster roster with individual names and stat ranges
  - Rarity-based appearance rates in dungeons
  - Combat: Answer questions to deal damage, lose HP on wrong answers
  - Capture on monster defeat (with probability check)

- **Audio Effects**: Distinct sound signatures per rarity tier using Web Audio API
  - Rare: Simple sine wave tone
  - Epic: Square wave with ascending pitch
  - Unique: Multi-harmonic blend with pulsing effect
  - Legendary: Drum-like kick + high-frequency effect combo
  - Background Music: RPG battle theme with Am-G-C-F chord progression, drum beats, syncopation

- **Progression**: Level-based system with experience, stat allocation, and tier ranks

## Monster Database

**Location**: `data/monsters.py`
**Total Monsters**: 42
- Rare (10): Slime, Goblin, Vampire Bat, Golem, Skeleton, Orc, Werewolf, Tooth Ghost, Fire Spider, Ice Elemental
- Epic (10): Necromancer, Black Knight, Frost Wizard, Dragon Hunter, Dark Priest, Legendary Warrior, Fire Wizard, Poison Archer, Kraken, Sky God
- Unique (10): Shepherd of Tartarus, Azure Dragon, Ancient Vampire, Spirit of Infinity, Shadow of Despair, Heavenly Knight, Last Emperor, Guardian of Time, Resurrected King, Pope of Darkness
- Legendary (12): Yama Raja, Creator of Heaven and Earth, Eternal Demon, King of Abyss, Azure Dragon, Fury of Flame, The Absolute, Infinite Judge, God of Annihilation, Keeper of Eternal Night, Avatar of Chaos, Last Dragon

## Monster Images

Status: **Images placeholder (empty strings)**
- Monster images will be added later
- Current system supports white background monster images
- Images directory ready at: `/static/monsters/`

## Expo Mobile App Development Progress (Dec 1, 2025)

### Phase 2: Node.js/Express Backend (100% Basic APIs Complete)
**Status**: All 9 core API systems implemented! Ready for advanced logic phase.

**Completed APIs (9 systems):**
- ✅ 플레이어 관리 (시작, 로드, 저장, 정보, 잠자기, 스탯 분배)
- ✅ 던전 시스템 (목록, 미리보기, 시작, 답변, 나가기)
- ✅ 퀴즈 시스템 (조회, 답변)
- ✅ 모험 시스템 (선택, 시작, 액션)
- ✅ 도감 시스템 (조회, 상세, 포획)
- ✅ 상점 시스템 (조회, 구매, 아이템 사용)
- ✅ 부동산 시스템 (조회, 구매, 월세 수금)
- ✅ 직업 시스템 (목록, 선택, 일하기)
- ✅ 일일 표현 시스템 (조회, 연습)

**Infrastructure:**
- ✅ Express 프로젝트 초기화 + JWT 인증
- ✅ 파일 저장 시스템 (JSON 기반)
- ✅ 게임 데이터 JSON 파일 (monsters, skills, adventures)
- ✅ API 문서 작성

**Location**: `/home/runner/workspace/backend/`

### Phase 2.3: 고급 게임 로직 (완료 100%)
- ✅ **복잡한 전투 엔진** (battleEngine.js)
  - 턴 기반 전투 시스템
  - 스킬 데미지 계산 (보정치 범위 내 랜덤)
  - 적의 기본 공격
  - 승리/패배 처리
  - 기술 카드 드롭 시스템 (난이도별 확률)
- ✅ **스킬 획득 및 교체** (skills.js)
  - 새 스킬 획득 처리
  - 최대 4개 스킬 슬롯 관리
  - 스킬 교체 시스템
- ✅ **기술 아이템 시스템** (skillItems.js)
  - 기술 충전제 (횟수 부분 회복)
  - 기술 초기화제 (완전 리셋)

### Phase 3: React Native 프론트엔드 (85% 완료)
- ✅ Expo 프로젝트 구조
- ✅ 인증 화면 (LoginScreen) 
- ✅ 메인 게임 허브 (MainHubScreen)
- ✅ API 클라이언트 (axios + interceptors)
- ✅ 네비게이션 설정
- ✅ 모험 화면 (AdventureScreen) - 스테이지 선택 & 실시간 전투
- ✅ 도감 화면 (CompendiumScreen) - 몬스터 갤러리
- ✅ 스킬 화면 (SkillsScreen) - 스킬 관리 & 교체
- ✅ 던전 화면 (DungeonScreen) - 퀴즈 시스템
- ✅ 상점 화면 (ShopScreen) - 상품 구매
- ⏳ 부동산/설정 화면 (최종 단계)

---

## Recent Changes (Dec 1, 2025 - Turn 3-4)

### 게임 화면 대량 개발 완료
1. ✅ **AdventureScreen.js** - 스테이지 선택 & 실시간 전투
   - 스테이지 목록 표시
   - HP 바 애니메이션
   - 스킬 선택 인터페이스
   - 전투 로그 시스템
   - 승리/패배 처리

2. ✅ **CompendiumScreen.js** - 몬스터 갤러리
   - 포획한 몬스터 목록
   - 레어도 색상 구분
   - 완성도 통계
   - 몬스터 상세 정보 모달

3. ✅ **SkillsScreen.js** - 스킬 관리
   - 현재 스킬 표시 (4개 슬롯)
   - 획득한 스킬 리스트
   - 스킬 교체 시스템
   - 스킬 상세 정보

4. ✅ **DungeonScreen.js** - 퀴즈 시스템
   - 던전 레벨 선택
   - 영어 퀴즈 문제
   - 객관식 선택지
   - 점수 시스템
   - 도망 기능

**결과**: 6개 화면 완성 (70% 완료)

---

## Recent Changes (Dec 1, 2025 - Turn 3)

### React Native 프론트엔드 초기화 완료
1. ✅ **Expo 프로젝트 구조**
   - React Native + Expo 기본 설정
   - React Navigation 스택 네비게이션
   - 환경 변수 설정

2. ✅ **API 클라이언트** (api.js)
   - Axios 인터셉터 (토큰 자동 추가)
   - 모든 게임 API 메서드
   - 에러 처리

3. ✅ **인증 시스템**
   - LoginScreen: 플레이어 이름 입력 → 게임 시작
   - JWT 토큰 저장 (AsyncStorage)
   - 자동 인증 체크

4. ✅ **게임 허브**
   - MainHubScreen: 플레이어 통계 표시
   - 게임 시스템 메뉴
   - 로그아웃 기능

---

## Recent Changes (Dec 1, 2025 - Turn 2)

### 스킬 시스템 및 기술 아이템 완성
1. ✅ **skills.js** - 스킬 관리
   - 스킬 목록 조회
   - 스킬 획득 처리
   - 스킬 교체 시스템 (최대 4개 슬롯)
   - 획득한 스킬 보유 목록

2. ✅ **skillItems.js** - 기술 아이템 시스템
   - 기술 충전제 (횟수 부분 회복 - 50%)
   - 기술 초기화제 (완전 리셋)
   - 아이템 인벤토리 관리
   - 아이템 사용 처리

3. ✅ **Phase 2.3 완료** - 고급 게임 로직 100%
   - 턴 기반 전투 엔진
   - 스킬 관리 시스템
   - 기술 아이템 시스템

---

## Previous Changes (Dec 1, 2025 - Turn 1)

### 복잡한 전투 엔진 구현
1. ✅ **battleEngine.js** - 턴 기반 전투 시스템
   - 스킬 데미지 계산 (보정치 범위 내 랜덤)
   - 적의 기본 공격
   - 승리/패배 처리
   - 기술 카드 드롭 (확률 기반)
   - 난이도별 보상 배증

2. ✅ **adventure.js 개선**
   - /start: 실제 전투 시작
   - /action: 스킬 사용 처리
   - /flee: 전투 도망 (NEW)

3. ✅ **문서화**
   - BACKEND_SUMMARY.md 작성
   - API_ROUTES.md 업데이트

---

## Previous Changes (Nov 28, 2025)

### Skill Item System (Nov 28 - Latest)
1. ✅ **기술 충전제 시스템** - 기술 횟수 부분 회복
   - 드롭 확률: 기술 카드와 동일 (스테이지 1: 0.02%, 심화: 0.04%)
   - 효과: 최대 제한 횟수의 1/2 회복 (최대치 초과 불가)
   - 팝업: 초록색 테마로 획득 시 알림
   - 데이터: 모험_아이템에 '기술충전제' 추가

2. ✅ **기술 초기화제 시스템** - 모든 기술 횟수 리셋
   - 드롭 확률: 기술 카드의 1/2 (스테이지 1: 0.01%, 심화: 0.02%)
   - 효과: 모든 기술 사용 횟수 완전 리셋
   - 팝업: 파란색 테마로 획득 시 알림
   - 데이터: 모험_아이템에 '기술초기화제' 추가

3. ✅ **Backend 구현**
   - /adventure/use_skill_item: 아이템 사용 엔드포인트 추가
   - 기술 충전제 사용 시 회복량 계산 (최대치 이상 불가)
   - 기술 초기화제 사용 시 즉시 리셋 처리

4. ✅ **Frontend UI 업그레이드**
   - showItemAcquireModal(): 아이템 획득 팝업 함수 추가
   - 기술 획득/교체 팝업과 동일한 패턴의 디자인
   - 아이템 획득 후 기술 팝업 순서대로 표시

### Skill Acquisition & Replacement UI (Nov 28 - Previous)
1. ✅ **기술 획득 팝업** - 새 기술 획득 시 표시
2. ✅ **기술 교체 UI** - 4개 이상 기술일 때 선택 가능  
3. ✅ **Backend 처리** - complete_adventure_battle, replace_skill 엔드포인트

### Previous Updates (Nov 27)
1. ✅ **Hard Difficulty (심화) System** - Complete implementation
   - Players unlock hard difficulty after clearing stage 200 in normal mode
   - Hard difficulty: Same 200 stages but enemies have 2x attack and 2x HP
   - Skill card acquisition rate 2x higher in hard difficulty (0.02% → 0.04% at stage 1, up to 25.6% at stage 200)
   - Stage select shows current difficulty indicator: "(일반)" for normal, "🔥 심화" for hard
   - Auto-reset to stage 1 when clearing stage 200 for infinite replayability

2. ✅ **Background Music System** - Enhanced RPG battle theme
   - Replaced with new single-minor-key battle music (Am-G-C-F chord progression)
   - Features: Strong drum kick beats, bass line following Am-G-C-F, repeating catchy melody hooks
   - Syncopation and 16th note patterns for dynamic feel
   - Dissonant tones (diminished) for tension
   - Modern synth-like high-frequency lead lines
   - 8-second loop for continuous battle atmosphere
   - ON/OFF button with immediate state reflection (no flickering)

3. ✅ **Audio UI Improvements**
   - Background music toggle button loads with no visual flicker
   - Button state reflects localStorage immediately on page load
   - Music state syncs between adventure selection and battle pages

## External Dependencies

- **Flask**: Web framework for routing and session management
- **Bootstrap 5**: Frontend UI framework with dark theme support
- **Chart.js**: Data visualization for player statistics
- **Feather Icons**: Scalable vector icons
- **Web Audio API**: Browser-native sound effects and background music (no external audio files)

The application uses a self-contained architecture perfect for local deployment and development.
