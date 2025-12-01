# Life Simulation Game - Backend API 설계 (Expo 모바일 앱용)

## 개요
Flask 웹 앱을 Node.js/Express 기반의 REST API로 변환하기 위한 설계 문서입니다.
Expo React Native 모바일 앱에서 호출할 모든 엔드포인트를 정의합니다.

---

## 기본 정보

### API 기본 URL
- 개발: `http://localhost:3000/api`
- 배포: `https://api.life-simulation-game.com/api`

### 인증 방식
- JWT 토큰 기반 (Authorization: Bearer {token})
- 로컬 스토리지에 저장 (React Native: AsyncStorage)

### 응답 형식
모든 응답은 JSON 형식:
```json
{
  "success": true/false,
  "data": {},
  "message": "String",
  "error": "String (error only)"
}
```

---

## 1. 플레이어 관리 API

### 1.1 게임 시작 (새 게임)
```
POST /api/player/start
요청: 없음
응답:
{
  "success": true,
  "data": {
    "player": { /* 플레이어 데이터 전체 */ },
    "token": "JWT_TOKEN"
  }
}
```

### 1.2 게임 로드 (저장된 게임)
```
POST /api/player/load
요청: 없음
응답:
{
  "success": true,
  "data": {
    "player": { /* 저장된 플레이어 데이터 */ },
    "token": "JWT_TOKEN"
  }
}
```

### 1.3 게임 저장
```
POST /api/player/save
헤더: Authorization: Bearer {token}
요청:
{
  "player_data": { /* 플레이어 데이터 */ }
}
응답:
{
  "success": true,
  "message": "게임이 저장되었습니다."
}
```

### 1.4 플레이어 정보 조회
```
GET /api/player/info
헤더: Authorization: Bearer {token}
응답:
{
  "success": true,
  "data": {
    "레벨": 1,
    "경험치": 0,
    "돈": 0,
    "힘": 0,
    "지능": 0,
    "외모": 0,
    "체력스탯": 0,
    "운": 0,
    /* ... 모든 플레이어 통계 ... */
  }
}
```

### 1.5 플레이어 통계
```
GET /api/player/stats
헤더: Authorization: Bearer {token}
응답:
{
  "success": true,
  "data": {
    "stats": [10, 5, 8, 12, 3],
    "labels": ["힘", "지능", "외모", "체력", "운"],
    "level": 5,
    "exp": 250,
    "max_exp": 300
  }
}
```

---

## 2. 대시보드 API

### 2.1 대시보드 정보
```
GET /api/dashboard
헤더: Authorization: Bearer {token}
응답:
{
  "success": true,
  "data": {
    "player": { /* 플레이어 전체 데이터 */ },
    "stats": { /* 플레이어 통계 */ },
    "recent_events": [ /* 최근 이벤트 */ ],
    "achievements": [ /* 성취 데이터 */ ]
  }
}
```

### 2.2 잠자기
```
POST /api/player/sleep
헤더: Authorization: Bearer {token}
응답:
{
  "success": true,
  "data": {
    "player": { /* 업데이트된 플레이어 */ },
    "event": { "메시지": "String", "type": "String" } (선택사항)
  }
}
```

### 2.3 스탯 분배
```
POST /api/player/allocate-stats
헤더: Authorization: Bearer {token}
요청:
{
  "stat_type": "힘|지능|외모|체력|운",
  "points": 5
}
응답:
{
  "success": true,
  "data": {
    "player": { /* 업데이트된 플레이어 */ }
  }
}
```

---

## 3. 일일 표현 (Daily Expressions) API

### 3.1 표현 목록 조회
```
GET /api/expressions
헤더: Authorization: Bearer {token}
응답:
{
  "success": true,
  "data": {
    "expressions": [
      {
        "id": 0,
        "expression": "Good morning",
        "meaning": "좋은 아침",
        "category": "인사"
      },
      ...
    ],
    "total": 180,
    "progress": 45
  }
}
```

### 3.2 표현 학습 확인
```
POST /api/expressions/check
헤더: Authorization: Bearer {token}
요청:
{
  "index": 0,
  "user_input": "good morning"
}
응답:
{
  "success": true,
  "data": {
    "correct": true,
    "exp_gained": 10,
    "level_up": false,
    "current_level": 2,
    "progress": 46,
    "total": 180
  }
}
```

---

## 4. 단어 관리 API

### 4.1 사용자 단어 조회
```
GET /api/words?category=all
헤더: Authorization: Bearer {token}
응답:
{
  "success": true,
  "data": {
    "words": [
      {
        "단어": "apple",
        "뜻": "사과",
        "카테고리": "기본",
        "index": 0
      }
    ],
    "categories": ["기본", "TOEIC", "일상"],
    "total": 150
  }
}
```

### 4.2 단어 추가
```
POST /api/words/add
헤더: Authorization: Bearer {token}
요청:
{
  "word": "apple",
  "meaning": "사과",
  "category": "기본"
}
응답:
{
  "success": true,
  "message": "단어가 추가되었습니다."
}
```

### 4.3 단어 삭제
```
DELETE /api/words/{index}
헤더: Authorization: Bearer {token}
응답:
{
  "success": true,
  "message": "단어가 삭제되었습니다."
}
```

### 4.4 단어 수정
```
PUT /api/words/{index}
헤더: Authorization: Bearer {token}
요청:
{
  "word": "새로운_단어",
  "meaning": "새로운_뜻",
  "category": "새로운_카테고리"
}
응답:
{
  "success": true,
  "message": "단어가 수정되었습니다."
}
```

### 4.5 카테고리 일괄 변경
```
POST /api/words/batch-update-category
헤더: Authorization: Bearer {token}
요청:
{
  "word_indices": [0, 1, 2],
  "new_category": "TOEIC"
}
응답:
{
  "success": true,
  "message": "카테고리가 변경되었습니다."
}
```

---

## 5. 퀴즈 API

### 5.1 퀴즈 조회
```
GET /api/quiz?category=all&language=random
헤더: Authorization: Bearer {token}
응답:
{
  "success": true,
  "data": {
    "word_bank": [ /* 퀴즈에 사용할 단어들 */ ],
    "categories": ["기본", "TOEIC", ...],
    "completed_words": 10,
    "total_words": 50,
    "current_question": {
      "type": "뜻맞히기|단어맞히기",
      "word": "apple",
      "options": ["사과", "바나나", "딸기", "포도"],
      "correct_answer": "사과"
    }
  }
}
```

### 5.2 퀴즈 답변
```
POST /api/quiz/answer
헤더: Authorization: Bearer {token}
요청:
{
  "category": "all",
  "answer": "사과",
  "correct_answer": "사과",
  "question_type": "뜻맞히기",
  "quiz_word": "apple"
}
응답:
{
  "success": true,
  "data": {
    "correct": true,
    "exp_gained": 10,
    "message": "정답! 경험치 +10",
    "completed_words": 11,
    "total_words": 50,
    "all_completed": false,
    "next_question": { /* 다음 문제 */ }
  }
}
```

### 5.3 틀린 문제 조회
```
GET /api/quiz/wrong-questions?category=all
헤더: Authorization: Bearer {token}
응답:
{
  "success": true,
  "data": {
    "wrong_questions": [
      {
        "word": "apple",
        "meaning": "사과",
        "question_type": "뜻맞히기",
        "correct_answer": "사과",
        "player_answer": "바나나",
        "category": "기본"
      }
    ]
  }
}
```

### 5.4 퀴즈 세션 리셋
```
POST /api/quiz/reset
헤더: Authorization: Bearer {token}
요청:
{
  "category": "all"
}
응답:
{
  "success": true,
  "message": "퀴즈 세션이 초기화되었습니다."
}
```

---

## 6. 직업 시스템 API

### 6.1 직업 목록
```
GET /api/job/list
헤더: Authorization: Bearer {token}
응답:
{
  "success": true,
  "data": {
    "jobs": [
      {
        "id": 1,
        "이름": "편의점 알바",
        "급여": 5000,
        "요구스탯": "체력 >= 5",
        "회복율": 3
      }
    ]
  }
}
```

### 6.2 직업 신청
```
POST /api/job/apply
헤더: Authorization: Bearer {token}
요청:
{
  "job_id": 1
}
응답:
{
  "success": true,
  "data": {
    "player": { /* 업데이트된 플레이어 */ }
  }
}
```

### 6.3 근무
```
POST /api/job/work
헤더: Authorization: Bearer {token}
응답:
{
  "success": true,
  "data": {
    "player": { /* 업데이트된 플레이어 */ },
    "money_earned": 5000,
    "message": "근무를 완료했습니다!"
  }
}
```

---

## 7. 부동산 API

### 7.1 부동산 목록
```
GET /api/real-estate/list
헤더: Authorization: Bearer {token}
응답:
{
  "success": true,
  "data": {
    "properties": [
      {
        "id": 1,
        "이름": "원룸",
        "가격": 50000,
        "월세": 3000,
        "기력회복": 10
      }
    ]
  }
}
```

### 7.2 부동산 구매
```
POST /api/real-estate/buy
헤더: Authorization: Bearer {token}
요청:
{
  "property_id": 1
}
응답:
{
  "success": true,
  "data": {
    "player": { /* 업데이트된 플레이어 */ }
  }
}
```

### 7.3 부동산 판매
```
POST /api/real-estate/sell
헤더: Authorization: Bearer {token}
응답:
{
  "success": true,
  "data": {
    "player": { /* 업데이트된 플레이어 */ }
  }
}
```

### 7.4 거주지 변경
```
POST /api/real-estate/change-residence
헤더: Authorization: Bearer {token}
요청:
{
  "property_name": "원룸"
}
응답:
{
  "success": true,
  "data": {
    "player": { /* 업데이트된 플레이어 */ }
  }
}
```

---

## 8. 상점 API

### 8.1 상점 아이템 목록
```
GET /api/shop/items
헤더: Authorization: Bearer {token}
응답:
{
  "success": true,
  "data": {
    "items": [
      {
        "id": 1,
        "이름": "목검",
        "타입": "무기",
        "가격": 1000,
        "공격력": 10
      }
    ]
  }
}
```

### 8.2 아이템 구매
```
POST /api/shop/buy
헤더: Authorization: Bearer {token}
요청:
{
  "item_id": 1
}
응답:
{
  "success": true,
  "data": {
    "player": { /* 업데이트된 플레이어 */ }
  }
}
```

---

## 9. 인벤토리 API

### 9.1 인벤토리 조회
```
GET /api/inventory
헤더: Authorization: Bearer {token}
응답:
{
  "success": true,
  "data": {
    "weapons": [
      {
        "이름": "목검",
        "공격력": 10
      }
    ],
    "equipped_weapon": "목검",
    "items": []
  }
}
```

### 9.2 무기 장착
```
POST /api/inventory/equip-weapon
헤더: Authorization: Bearer {token}
요청:
{
  "weapon_name": "목검"
}
응답:
{
  "success": true,
  "message": "무기를 장착했습니다."
}
```

### 9.3 무기 해제
```
POST /api/inventory/unequip-weapon
헤더: Authorization: Bearer {token}
응답:
{
  "success": true,
  "message": "무기를 해제했습니다."
}
```

---

## 10. 던전 API

### 10.1 던전 목록
```
GET /api/dungeon/list
헤더: Authorization: Bearer {token}
응답:
{
  "success": true,
  "data": {
    "dungeons": [
      {
        "id": "toeic_1",
        "이름": "TOEIC 던전",
        "난이도": "보통",
        "word_count": 30,
        "reward_info": "1,000~2,000원 + 경험치 10~20"
      }
    ]
  }
}
```

### 10.2 던전 미리보기
```
GET /api/dungeon/{dungeon_id}/preview
헤더: Authorization: Bearer {token}
응답:
{
  "success": true,
  "data": {
    "dungeon": { /* 던전 정보 */ },
    "all_words": [ /* 모든 단어 */ ],
    "total_words": 30
  }
}
```

### 10.3 던전 시작
```
POST /api/dungeon/start
헤더: Authorization: Bearer {token}
요청:
{
  "dungeon_id": "toeic_1"
}
응답:
{
  "success": true,
  "data": {
    "dungeon_run": {
      "dungeon_id": "toeic_1",
      "current_monster": { /* 현재 몬스터 */ },
      "current_question": { /* 현재 문제 */ },
      "monster_progress": 0,
      "monster_hp": 5
    }
  }
}
```

### 10.4 던전 답변
```
POST /api/dungeon/answer
헤더: Authorization: Bearer {token}
요청:
{
  "choice": 0
}
응답:
{
  "success": true,
  "data": {
    "correct": true,
    "message": "정답!",
    "monster_defeated": false,
    "captured": false,
    "dungeon_run": { /* 업데이트된 던전 상태 */ },
    "game_over": false
  }
}
```

### 10.5 던전 나가기
```
POST /api/dungeon/leave
헤더: Authorization: Bearer {token}
응답:
{
  "success": true,
  "message": "던전에서 나갔습니다."
}
```

---

## 11. 몬스터/도감 API

### 11.1 도감 조회
```
GET /api/compendium?rarity=all
헤더: Authorization: Bearer {token}
응답:
{
  "success": true,
  "data": {
    "compendium": [
      {
        "compendium_index": 0,
        "id": "slime_1",
        "이름": "Slime",
        "등급": "레어",
        "공격력": 5,
        "체력": 10,
        "포획날짜": "2025-01-01T10:00:00"
      }
    ],
    "total_monsters": 42,
    "captured_count": 5
  }
}
```

### 11.2 모든 몬스터 정보
```
GET /api/monsters/all?rarity=all
헤더: Authorization: Bearer {token}
응답:
{
  "success": true,
  "data": {
    "monsters": {
      "slime_1": {
        "id": "slime_1",
        "이름": "Slime",
        "등급": "레어",
        "설명": "기본 몬스터",
        "이미지": "" (미포획시)
      }
    }
  }
}
```

### 11.3 몬스터 삭제
```
DELETE /api/compendium/{monster_id}
헤더: Authorization: Bearer {token}
응답:
{
  "success": true,
  "message": "몬스터가 삭제되었습니다."
}
```

---

## 12. 몬스터 합성 API

### 12.1 합성 페이지 데이터
```
GET /api/fusion
헤더: Authorization: Bearer {token}
응답:
{
  "success": true,
  "data": {
    "compendium": [ /* 플레이어 도감 */ ],
    "monsters_by_rarity": {
      "레어": [ /* 레어 몬스터들 */ ],
      "에픽": [ /* 에픽 몬스터들 */ ]
    }
  }
}
```

### 12.2 몬스터 합성
```
POST /api/fusion/merge
헤더: Authorization: Bearer {token}
요청:
{
  "selected_monsters": [0, 1, 2]
}
응답:
{
  "success": true,
  "data": {
    "player": { /* 업데이트된 플레이어 */ },
    "result_monster": { /* 합성 결과 몬스터 */ },
    "is_upgraded": true,
    "is_mythic": false
  }
}
```

---

## 13. 모험 (Adventure) 시스템 API

### 13.1 모험 선택 페이지
```
GET /api/adventure/select
헤더: Authorization: Bearer {token}
응답:
{
  "success": true,
  "data": {
    "available_monsters": [ /* 캡처한 몬스터들 */ ],
    "stages": [
      {
        "stage_id": 1,
        "name": "Stage 1",
        "difficulty": "일반",
        "enemy_level": 1,
        "reward": { "exp": 50, "money": 100 }
      }
    ],
    "current_stage": 1,
    "cleared_stage": 0,
    "adventure_energy": 100
  }
}
```

### 13.2 모험 시작
```
POST /api/adventure/start
헤더: Authorization: Bearer {token}
요청:
{
  "stage_id": 1,
  "monster_ids": ["slime_1", "goblin_1", "spider_1"]
}
응답:
{
  "success": true,
  "data": {
    "battle_state": {
      "player_turn": true,
      "player_hp": 100,
      "player_mp": 50,
      "enemy_hp": 80,
      "current_skills": ["박치기", "날카로운이빨"],
      "enemy_skills": ["기본공격"]
    },
    "battle_id": "UUID"
  }
}
```

### 13.3 모험 액션
```
POST /api/adventure/action
헤더: Authorization: Bearer {token}
요청:
{
  "battle_id": "UUID",
  "action_type": "skill",
  "skill_name": "박치기"
}
응답:
{
  "success": true,
  "data": {
    "battle_state": { /* 업데이트된 전투 상태 */ },
    "game_over": false,
    "winner": null,
    "skill_usage": {
      "박치기": 1,
      "날카로운이빨": 0
    }
  }
}
```

### 13.4 기술 아이템 사용
```
POST /api/adventure/use-skill-item
헤더: Authorization: Bearer {token}
요청:
{
  "battle_id": "UUID",
  "item_type": "기술충전제|기술초기화제",
  "skill_name": "박치기" (충전제일 때만)
}
응답:
{
  "success": true,
  "data": {
    "recovery_amount": 2,
    "adventure_items": {
      "기술충전제": 3
    },
    "message": "기술 횟수를 회복했습니다."
  }
}
```

### 13.5 모험 결과
```
GET /api/adventure/result/{battle_id}
헤더: Authorization: Bearer {token}
응답:
{
  "success": true,
  "data": {
    "winner": "player",
    "rewards": {
      "exp": 100,
      "money": 500,
      "skills": ["기술카드"],
      "items": ["기술충전제"]
    },
    "level_up": false
  }
}
```

---

## 14. 성취 API

### 14.1 모든 성취 조회
```
GET /api/achievements/all
헤더: Authorization: Bearer {token}
응답:
{
  "success": true,
  "data": {
    "achievements": [
      {
        "id": "first_level",
        "title": "첫 레벨업",
        "description": "첫 레벨업을 달성하세요.",
        "points": 10,
        "unlocked": true
      }
    ]
  }
}
```

### 14.2 플레이어 성취 조회
```
GET /api/achievements/player
헤더: Authorization: Bearer {token}
응답:
{
  "success": true,
  "data": {
    "player_achievements": [ /* 달성한 성취 ID들 */ ],
    "achievement_points": 100
  }
}
```

---

## 15. 기타 API

### 15.1 플레이어 경험치 추가 (음성 연습)
```
POST /api/player/add-exp
헤더: Authorization: Bearer {token}
요청:
{
  "exp": 10
}
응답:
{
  "success": true,
  "data": {
    "exp": 10,
    "current_level": 2,
    "level_up": false
  }
}
```

---

## 데이터 구조

### 플레이어 데이터
```json
{
  "레벨": 1,
  "경험치": 0,
  "경험치최대": 100,
  "스탯포인트": 0,
  "힘": 0,
  "지능": 0,
  "외모": 0,
  "체력스탯": 0,
  "운": 0,
  "체력": 10,
  "기력": 10,
  "최대기력": 10,
  "직장": null,
  "돈": 0,
  "거주지": null,
  "날짜": 1,
  "시간": 8,
  "도감": [],
  "모험_현재스테이지": 1,
  "모험_클리어스테이지": 0,
  "모험_기술": ["박치기"],
  "모험_기력": 100,
  "모험_기력최대": 100,
  "모험_난이도": "일반"
}
```

### 몬스터 도감 항목
```json
{
  "compendium_index": 0,
  "id": "slime_1",
  "이름": "Slime",
  "등급": "레어",
  "공격력": 5,
  "체력": 10,
  "포획날짜": "2025-01-01T10:00:00"
}
```

---

## 에러 코드

| 코드 | 의미 |
|------|------|
| 200 | 성공 |
| 400 | 잘못된 요청 |
| 401 | 인증 실패 (토큰 없음/만료됨) |
| 403 | 권한 없음 |
| 404 | 리소스 없음 |
| 500 | 서버 에러 |

---

## 마이그레이션 체크리스트

### Phase 1: API 설계 ✅ (완료)
- [x] 모든 엔드포인트 정의
- [x] 요청/응답 형식 정의
- [x] 데이터 구조 정의

### Phase 2: Node.js/Express 백엔드 구현 (다음)
- [ ] Express 프로젝트 초기화
- [ ] MongoDB/PostgreSQL 스키마 정의
- [ ] JWT 인증 구현
- [ ] 모든 라우트 구현
- [ ] 게임 로직 포팅

### Phase 3: Expo React Native 프론트엔드 (그 다음)
- [ ] Expo 프로젝트 초기화
- [ ] 화면 구성 (Navigation)
- [ ] API 호출 로직
- [ ] UI 구현

### Phase 4: 테스트 및 배포
- [ ] 통합 테스트
- [ ] 성능 최적화
- [ ] iOS/Android 빌드
- [ ] App Store/Google Play 배포
