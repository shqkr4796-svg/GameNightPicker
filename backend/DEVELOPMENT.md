# Backend 개발 진행 상황

## 완료된 항목 ✅

### Phase 2.1: 기본 구조 (100% 완료)
- Express 프로젝트 초기화
- JWT 인증 시스템
- 파일 저장 시스템 (JSON 기반)
- 게임 로직 유틸리티

### Phase 2.2: 기본 API 라우트 (80% 완료)
- ✅ 플레이어 관리 (시작, 로드, 저장, 정보, 잠자기, 스탯 분배)
- ✅ 던전 시스템 (목록, 미리보기, 시작, 답변, 나가기)
- ✅ 퀴즈 시스템 (조회, 답변)
- ✅ 모험 시스템 (선택, 시작, 액션)

## 다음 단계 🔄

### Phase 2.3: 고급 게임 로직 (0% 완료)
- 복잡한 전투 로직 구현
- 몬스터 포획 시스템
- 스킬 획득 및 교체
- 기술 아이템 시스템

### Phase 2.4: 추가 API (0% 완료)
- 몬스터/도감 시스템
- 부동산 시스템
- 상점 시스템
- 직업 시스템
- 일일 표현 시스템

### Phase 2.5: 데이터 통합 (0% 완료)
- 게임 데이터 파일 생성 (monsters.json, skills.json 등)
- 초기 데이터 설정

## 아키텍처 메모

### 저장 시스템
- 플레이어 데이터: `saves/player_{id}.json` (개별 파일)
- 게임 데이터: `data/{name}.json` (읽기 전용)

### 인증
- JWT 토큰 기반
- Authorization 헤더: `Bearer {token}`

### 응답 형식
```json
{
  "success": true/false,
  "data": {},
  "message": "string",
  "error": "string"
}
```

## 테스트 방법

1. 서버 실행:
```bash
npm start
```

2. 새 게임 시작:
```bash
curl -X POST http://localhost:3000/api/player/start
```

3. 토큰과 함께 요청:
```bash
curl -X GET http://localhost:3000/api/player/info \
  -H "Authorization: Bearer {token}"
```

## 다음 우선순위
1. 게임 데이터 파일 생성 및 로드
2. 복잡한 전투 로직 구현
3. 몬스터 포획 시스템
4. 나머지 API 완성
