# 생명 시뮬레이션 게임 - React Native 프론트엔드

Expo + React Native로 구축한 모바일 게임 프론트엔드입니다.

## 설치

```bash
cd frontend
npm install
```

## 실행

```bash
npm start          # Expo 시작
npm run android    # Android 에뮬레이터
npm run ios        # iOS 시뮬레이터
npm run web        # 웹 브라우저
```

## 프로젝트 구조

```
frontend/
├── src/
│   ├── screens/
│   │   ├── LoginScreen.js       # 로그인 화면
│   │   └── MainHubScreen.js     # 메인 허브
│   ├── components/              # 재사용 컴포넌트
│   └── services/
│       └── api.js              # API 클라이언트
├── App.js                       # 앱 진입점
├── app.json                     # Expo 설정
└── package.json
```

## 기능

- ✅ 플레이어 인증 (JWT)
- ✅ 게임 허브 네비게이션
- ✅ 캐릭터 통계 표시
- ✅ 메뉴 시스템

## 다음 단계

- [ ] 모험 화면 (Adventure)
- [ ] 던전 화면 (Dungeon)
- [ ] 도감 화면 (Compendium)
- [ ] 상점 화면 (Shop)
- [ ] 스킬 화면 (Skills)
- [ ] 게임 설정 화면
- [ ] 전투 애니메이션
- [ ] 사운드 효과

## API 연결

백엔드 서버와 통신합니다:
- Base URL: `http://localhost:3000` (개발)
- JWT 토큰: AsyncStorage에 자동 저장

## 빌드 및 배포

### iOS App Store
```bash
eas build --platform ios
eas submit --platform ios
```

### Google Play
```bash
eas build --platform android
eas submit --platform android
```
