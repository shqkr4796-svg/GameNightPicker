# Life Simulation Game - Backend API

Expo React Native 모바일 앱을 위한 Node.js/Express 백엔드 API

## 설명

Flask 웹 앱에서 마이그레이션한 REST API 백엔드입니다.
모든 게임 로직을 Node.js로 재구현하고 있습니다.

## 설치

```bash
npm install
```

## 환경 설정

`.env` 파일 생성:
```
PORT=3000
NODE_ENV=development
JWT_SECRET=your_secret_key
SAVE_DIR=./saves
DATA_DIR=./data
```

## 실행

### 개발 모드 (자동 재시작)
```bash
npm run dev
```

### 프로덕션 모드
```bash
npm start
```

## 프로젝트 구조

```
backend/
├── server.js              # Express 서버 진입점
├── .env                   # 환경 설정
├── package.json           # 의존성
├── routes/                # API 라우트 (추가 예정)
│   ├── player.js
│   ├── dungeon.js
│   ├── adventure.js
│   └── quiz.js
├── controllers/           # 비즈니스 로직 (추가 예정)
├── utils/                 # 유틸리티 함수 (추가 예정)
│   ├── gameLogic.js
│   ├── auth.js
│   └── validation.js
├── data/                  # 게임 데이터 (추가 예정)
│   ├── monsters.json
│   ├── skills.json
│   └── adventures.json
└── saves/                 # 플레이어 저장 데이터
```

## API 문서

자세한 API 문서는 `../API_DESIGN.md` 참고

## 개발 진행 상황

### Phase 2: Node.js 백엔드 구현
- [x] 프로젝트 초기화
- [x] Express 기본 설정
- [x] JWT 인증 구현
- [x] 플레이어 관리 API (기본)
- [x] 던전 API (기본)
- [x] 모험 시스템 API (기본)
- [x] 퀴즈 API (기본)
- [x] 게임 로직 유틸리티 (부분 완료)
- [ ] 고급 게임 로직 포팅
- [ ] 몬스터 시스템 API
- [ ] 데이터베이스 통합 (선택사항)

## 라이선스

ISC
