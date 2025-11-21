import json
import random
import os
import hashlib
from datetime import datetime
from data.game_data import *

SAVE_FILE = 'savegame.json'
EVENTS_FILE = 'events.json'
WORD_BANK_FILE = 'word_bank.json'
TOEIC_WORDS_FILE = 'data/toeic_words.json'

# 단어장 캐시
_word_bank_cache = None

def create_new_player():
    """새 플레이어 생성"""
    return {
        '레벨': 1, '경험치': 0, '경험치최대': 100, '스탯포인트': 0,
        '힘': 0, '지능': 0, '외모': 0, '체력스탯': 0, '운': 0,
        '체력': 10, '기력': 10, '최대기력': 10, '직장': None, '직장정보': None,
        '돈': 0, '거주지': None, '날짜': 1, '시간': 8, '질병': None,
        '인벤토리': [], '성취': [], '총_퀴즈': 0, '정답_퀴즈': 0,
        '도감': {},  # 몬스터 도감
        '던전클리어횟수': 0,  # 던전 클리어 횟수
        '무기_인벤토리': {},  # 무기 인벤토리
        '장착된_무기': None,  # 장착된 무기
        '던전_인벤토리': {},  # 던전 아이템 인벤토리
        '일일표현_완료': False,  # 오늘 일일 표현 완료 여부
        '일일표현_마지막날짜': 0,  # 마지막 완료한 날짜
        '일일표현_진도': 0  # 오늘의 표현 진도 (0-5)
    }

def save_game(player_data):
    """게임 저장"""
    try:
        with open(SAVE_FILE, 'w', encoding='utf-8') as f:
            json.dump(player_data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"저장 실패: {e}")
        return False

def load_game():
    """게임 불러오기"""
    try:
        if os.path.exists(SAVE_FILE):
            with open(SAVE_FILE, 'r', encoding='utf-8') as f:
                player = json.load(f)
                
                # 기존 플레이어 호환성 처리
                if '최대기력' not in player:
                    player['최대기력'] = 10  # 기본값
                    # 기존 거주지가 있다면 해당 부동산의 기력회복만큼 최대기력 증가
                    if player['거주지']:
                        for prop in real_estate:
                            if prop['이름'] == player['거주지']:
                                player['최대기력'] += prop['기력회복']
                                break
                
                # 던전 클리어 횟수 필드 추가 (기존 플레이어 호환성)
                if '던전클리어횟수' not in player:
                    player['던전클리어횟수'] = 0
                
                # 부동산 30일 월세 시스템 마이그레이션
                if player['거주지'] and '부동산구매날짜' not in player:
                    # 기존 플레이어는 즉시 월세를 받을 수 있도록 설정
                    player['부동산구매날짜'] = player['날짜'] - 30
                    player['마지막월세날짜'] = player['날짜'] - 30
                
                # 무기 시스템 마이그레이션 (기존 플레이어 호환성)
                if '무기_인벤토리' not in player:
                    player['무기_인벤토리'] = {}
                if '장착된_무기' not in player:
                    player['장착된_무기'] = None
