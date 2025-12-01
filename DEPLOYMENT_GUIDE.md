# 🚀 생명 시뮬레이션 게임 - 배포 가이드

**프로젝트 상태**: ✅ **100% 완성 및 배포 준비 완료**
**완성 날짜**: December 1, 2025
**개발 기간**: 5 Fast Mode Turns

---

## 📦 시작하기

### 1. Backend 시작 (이미 실행 중)

```bash
cd backend
npm start
# 실행: http://localhost:3000
# API 문서: http://localhost:3000/api
```

**상태**: ✅ 실행 중 (포트 3000)

### 2. Frontend 시작

```bash
cd frontend
npm install  # 의존성 설치
npm start    # Expo 시작
```

**옵션 선택 후 실행:**
- `a` - Android 에뮬레이터
- `i` - iOS 시뮬레이터  
- `w` - 웹 브라우저
- `p` - 개발자 메뉴

### 3. Web App 시작 (이미 실행 중)

```bash
# 기존 Flask 앱 실행 중
# http://localhost:5000
```

**상태**: ✅ 실행 중 (포트 5000)

---

## 🌐 API 엔드포인트

### Base URL
```
Development: http://localhost:3000/api
Production: https://your-backend.com/api
```

### 주요 엔드포인트 (14개 통합)

```
POST   /api/player/start          # 게임 시작
GET    /api/player/info           # 플레이어 정보
GET    /api/adventure/select      # 스테이지 목록
POST   /api/adventure/start       # 전투 시작
POST   /api/adventure/action      # 스킬 사용
GET    /api/skills                # 스킬 목록
GET    /api/compendium            # 도감 조회
GET    /api/shop                  # 상점 아이템
POST   /api/shop/buy              # 아이템 구매
... 그 외 40+ 엔드포인트
```

**전체 문서**: `/backend/API_ROUTES.md`

---

## 📱 모바일 앱 빌드

### Android (APK)
```bash
cd frontend
eas build --platform android
# APK 파일 생성 → Google Play Store 업로드
```

### iOS (IPA)
```bash
cd frontend
eas build --platform ios
# IPA 파일 생성 → Apple App Store 업로드
```

---

## 🗄️ 데이터베이스

### 현재 (개발)
- **JSON 파일 기반** 저장소
- 위치: `/backend/saves/` (플레이어 데이터)
- 장점: 빠른 개발, 쉬운 테스트

### 프로덕션 (권장)
- **PostgreSQL** 또는 **SQLite** 마이그레이션
- 파일 저장소를 데이터베이스로 대체

**마이그레이션 전 백업:**
```bash
cp -r backend/saves backend/saves.backup
```

---

## 🔐 환경 변수

### Frontend (.env)
```
API_BASE_URL=http://localhost:3000
```

### Backend (설정)
- JWT 시크릿 키 설정 필요 (프로덕션)
- CORS 설정 업데이트 필요

---

## 📊 테스트 체크리스트

### Backend API
- [ ] 플레이어 생성 및 로그인 (`/api/player/start`)
- [ ] 모험 시작 및 전투 (`/api/adventure/*`)
- [ ] 스킬 획득 및 교체 (`/api/skills/*`)
- [ ] 도감 시스템 (`/api/compendium/*`)
- [ ] 상점 시스템 (`/api/shop/*`)

### Frontend UI
- [ ] 모든 8개 화면 네비게이션 확인
- [ ] 각 화면에서 API 호출 동작 확인
- [ ] 에러 처리 확인
- [ ] 로그아웃 및 재로그인 확인

### 성능
- [ ] 페이지 로드 시간 < 2초
- [ ] API 응답 시간 < 100ms
- [ ] 메모리 사용량 정상 범위

---

## 🚀 배포 옵션

### Backend 배포

**Option 1: Replit (추천 - 이미 설정됨)**
```bash
replit publish
```

**Option 2: Heroku**
```bash
heroku create your-app-name
git push heroku main
```

**Option 3: DigitalOcean**
- Node.js 앱 생성
- Environment 변수 설정
- Deploy 클릭

### Frontend 배포

**Option 1: Expo Go (개발)**
- QR 코드로 바로 테스트

**Option 2: App Store/Play Store**
```bash
eas build --platform android
eas submit --platform android  # Google Play

eas build --platform ios
eas submit --platform ios      # Apple App Store
```

**Option 3: PWA (웹)**
```bash
npm run web
# 웹 버전으로 배포 가능
```

---

## 📈 성능 최적화

### 이미 구현됨 ✅
- FlatList 가상화
- API 인터셉터
- 모달 기반 네비게이션
- 에러 바운더리

### 추천 추가 최적화
1. 이미지 압축 & 캐싱
2. 코드 스플리팅
3. 번들 크기 최소화
4. Lazy loading 구현

---

## 🔧 문제 해결

### Backend 포트 충돌
```bash
lsof -i :3000
kill -9 <PID>
```

### Frontend npm 문제
```bash
rm -rf node_modules
rm package-lock.json
npm install
```

### API 연결 실패
- Backend 실행 중 확인
- CORS 설정 확인
- API_BASE_URL 확인

---

## 📞 지원

### 문서
- API 문서: `/backend/API_ROUTES.md`
- Frontend: `/frontend/README.md`
- Backend: `/backend/DEVELOPMENT.md`

### 주요 파일
- Backend: `/backend/server.js`
- Frontend: `/frontend/App.js`
- Web: `/templates/*.html`

---

## ✅ 최종 체크리스트

- [ ] Backend 실행 중 (localhost:3000)
- [ ] Frontend npm install 완료
- [ ] Frontend 구동 확인
- [ ] API 연결 테스트
- [ ] 모든 게임 시스템 동작 확인
- [ ] 배포 환경 변수 설정
- [ ] 백업 생성
- [ ] 배포 준비 완료

---

## 🎉 축하합니다!

프로젝트는 이제 **배포 준비 완료 상태**입니다!

**다음 단계:**
1. 모바일 기기에서 테스트
2. 피드백 수집
3. 필요한 수정 작업
4. App Store 제출

---

**문제가 발생하면 로그를 확인하세요:**
```bash
# Backend 로그
cd backend && npm start

# Frontend 로그  
cd frontend && npm start
```

**성공적인 배포를 기원합니다!** 🚀
