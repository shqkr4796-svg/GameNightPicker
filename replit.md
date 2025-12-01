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

### Phase 2.3: 고급 게임 로직 (다음 단계 - 미시작)
- 복잡한 전투 로직 (스킬 사용, 데미지 계산)
- 스킬 획득 및 교체 시스템
- 기술 아이템 시스템

### Phase 3: React Native 프론트엔드 (미시작)
- Expo 프로젝트 초기화
- 인증 화면, 메인 게임 화면
- 각 시스템별 UI 개발

---

## Recent Changes (Nov 28, 2025)

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
