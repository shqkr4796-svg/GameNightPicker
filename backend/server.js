import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

// 환경 설정
dotenv.config();

// ES6 module에서 __dirname 사용
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Express 앱 생성
const app = express();
const PORT = process.env.PORT || 3000;

// 미들웨어 설정
app.use(cors());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// 저장 디렉토리 초기화
const saveDir = process.env.SAVE_DIR || './saves';
const dataDir = process.env.DATA_DIR || './data';

if (!fs.existsSync(saveDir)) {
  fs.mkdirSync(saveDir, { recursive: true });
  console.log(`✓ 저장 디렉토리 생성: ${saveDir}`);
}

if (!fs.existsSync(dataDir)) {
  fs.mkdirSync(dataDir, { recursive: true });
  console.log(`✓ 데이터 디렉토리 생성: ${dataDir}`);
}

// 헬스 체크 라우트
app.get('/health', (req, res) => {
  res.json({
    success: true,
    message: 'Backend API is running',
    timestamp: new Date().toISOString()
  });
});

// API 라우트 임포트
import playerRoutes from './routes/player.js';
import dungeonRoutes from './routes/dungeon.js';
import quizRoutes from './routes/quiz.js';
import adventureRoutes from './routes/adventure.js';
import compendiumRoutes from './routes/compendium.js';
import shopRoutes from './routes/shop.js';
import realEstateRoutes from './routes/realEstate.js';

app.use('/api/player', playerRoutes);
app.use('/api/dungeon', dungeonRoutes);
app.use('/api/quiz', quizRoutes);
app.use('/api/adventure', adventureRoutes);
app.use('/api/compendium', compendiumRoutes);
app.use('/api/shop', shopRoutes);
app.use('/api/realestate', realEstateRoutes);

// 기본 API 정보 라우트
app.get('/api', (req, res) => {
  res.json({
    success: true,
    message: 'Life Simulation Game Backend API v1.0.0',
    endpoints: {
      health: 'GET /health',
      player: 'GET/POST /api/player/*',
      dungeon: 'GET/POST /api/dungeon/*',
      adventure: 'GET/POST /api/adventure/*',
      quiz: 'GET/POST /api/quiz/*'
    }
  });
});

// 에러 핸들러
app.use((err, req, res, next) => {
  console.error('Error:', err);
  res.status(err.status || 500).json({
    success: false,
    error: err.message || 'Internal Server Error'
  });
});

// 404 핸들러
app.use((req, res) => {
  res.status(404).json({
    success: false,
    error: 'Route not found'
  });
});

// 서버 시작
app.listen(PORT, () => {
  console.log(`\n🚀 Backend Server Running on http://localhost:${PORT}`);
  console.log(`📚 API Documentation: http://localhost:${PORT}/api`);
  console.log(`💚 Health Check: http://localhost:${PORT}/health\n`);
});
