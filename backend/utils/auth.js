import jwt from 'jsonwebtoken';

const JWT_SECRET = process.env.JWT_SECRET || 'life_simulation_game_secret_key_2025';

/**
 * JWT 토큰 생성
 */
export function generateToken(playerData) {
  return jwt.sign(
    { playerId: playerData.id || 'default' },
    JWT_SECRET,
    { expiresIn: '7d' }
  );
}

/**
 * JWT 토큰 검증
 */
export function verifyToken(token) {
  try {
    return jwt.verify(token, JWT_SECRET);
  } catch (error) {
    return null;
  }
}

/**
 * 인증 미들웨어
 */
export function authMiddleware(req, res, next) {
  const authHeader = req.headers.authorization;
  
  if (!authHeader || !authHeader.startsWith('Bearer ')) {
    return res.status(401).json({
      success: false,
      error: '인증이 필요합니다. 토큰을 제공해주세요.'
    });
  }

  const token = authHeader.substring(7);
  const decoded = verifyToken(token);

  if (!decoded) {
    return res.status(401).json({
      success: false,
      error: '유효하지 않은 토큰입니다.'
    });
  }

  req.playerId = decoded.playerId;
  next();
}

export default {
  generateToken,
  verifyToken,
  authMiddleware
};
