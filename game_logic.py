import json
import random
import os
import hashlib
from datetime import datetime
from data.game_data import *
from data.monsters import get_monster_by_id, get_monsters_by_rarity
from data.skills import SKILL_INFO

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
        '일일표현_진도': 0,  # 오늘의 표현 진도 (0-5)
        '학습한_표현_인덱스': [],  # 학습한 표현의 인덱스 리스트
        '모험_현재스테이지': 1,  # 현재 스테이지
        '모험_클리어스테이지': 0,  # 클리어한 최대 스테이지
        '모험_기술': ['박치기'],  # 보유한 기술 목록
        '모험_대표몬스터': None,  # 대표 몬스터 ID
        '모험_아이템': {},  # 모험 아이템 인벤토리
        '모험_기력': 1,  # 모험 기력
        '모험_기력최대': 100,  # 모험 기력 최대값
        '모험_정답_퀴즈': 0,  # 모험 기력 증가를 위한 퀴즈 정답 횟수
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
                if '던전_인벤토리' not in player:
                    player['던전_인벤토리'] = {}
                
                # 일일 표현 필드 추가 (기존 플레이어 호환성)
                if '일일표현_완료' not in player:
                    player['일일표현_완료'] = False
                if '일일표현_마지막날짜' not in player:
                    player['일일표현_마지막날짜'] = 0
                if '일일표현_진도' not in player:
                    player['일일표현_진도'] = 0
                if '학습한_표현_인덱스' not in player:
                    player['학습한_표현_인덱스'] = []
                
                # 모험 시스템 필드 추가 (기존 플레이어 호환성)
                if '모험_현재스테이지' not in player:
                    player['모험_현재스테이지'] = 1
                if '모험_클리어스테이지' not in player:
                    player['모험_클리어스테이지'] = 0
                if '모험_기술' not in player:
                    player['모험_기술'] = ['박치기']
                if '모험_대표몬스터' not in player:
                    player['모험_대표몬스터'] = None
                if '모험_아이템' not in player:
                    player['모험_아이템'] = {}
                if '모험_기력' not in player:
                    player['모험_기력'] = 1
                if '모험_기력최대' not in player:
                    player['모험_기력최대'] = 100
                if '모험_정답_퀴즈' not in player:
                    player['모험_정답_퀴즈'] = 0
                
                return player
    except Exception as e:
        print(f"불러오기 실패: {e}")
    return None

def check_level_up(player):
    """레벨업 확인"""
    level_ups = 0
    while player['경험치'] >= player['경험치최대']:
        player['레벨'] += 1
        player['스탯포인트'] += 1
        player['경험치'] -= player['경험치최대']
        player['경험치최대'] = int(player['경험치최대'] * 1.1)
        level_ups += 1
    return level_ups

def get_all_monster_images():
    """게임에 존재하는 모든 몬스터 이미지 반환"""
    from data.monsters import monsters_data
    
    all_monsters = {}
    for monster_id, monster_data in monsters_data.items():
        rarity = monster_data['등급']
        attack_range = monster_data['공격력']
        hp_range = monster_data['체력']
        
        all_monsters[monster_id] = {
            '이름': monster_data['이름'],
            '등급': rarity,
            '이미지': monster_data.get('이미지', ''),
            '공격력범위': f"{attack_range[0]}~{attack_range[1]}",
            '체력범위': f"{hp_range[0]}~{hp_range[1]}"
        }
    
    return all_monsters

def get_random_monster_image(rarity):
    """등급별 몬스터 이미지 - 무작위 선택"""
    import random
    
    monster_images = {
        '레어': [
            '/static/monsters/rare_1.png',
            '/static/monsters/rare_2.png',
            '/static/monsters/rare_3.png',
            '/static/monsters/rare_4.png',
            '/static/monsters/rare_5.png',
            '/static/monsters/rare_6.png',
            '/static/monsters/rare_7.png',
            '/static/monsters/rare_8.png',
            '/static/monsters/rare_9.png',
            '/static/monsters/rare_10.png'
        ],
        '에픽': [
            '/static/monsters/epic_1.png',
            '/static/monsters/epic_2.png',
            '/static/monsters/epic_3.png',
            '/static/monsters/epic_4.png',
            '/static/monsters/epic_5.png',
            '/static/monsters/epic_6.png',
            '/static/monsters/epic_7.png',
            '/static/monsters/epic_8.png',
            '/static/monsters/epic_9.png',
            '/static/monsters/epic_10.png'
        ],
        '유니크': [
            '/static/monsters/unique_1.png',
            '/static/monsters/unique_2.png',
            '/static/monsters/unique_3.png',
            '/static/monsters/unique_4.png',
            '/static/monsters/unique_5.png',
            '/static/monsters/unique_6.png',
            '/static/monsters/unique_7.png',
            '/static/monsters/unique_8.png',
            '/static/monsters/unique_9.png',
            '/static/monsters/unique_10.png'
        ],
        '레전드리': [
            '/static/monsters/legendary_1.png',
            '/static/monsters/legendary_2.png',
            '/static/monsters/legendary_3.png',
            '/static/monsters/legendary_4.png',
            '/static/monsters/legendary_5.png',
            '/static/monsters/legendary_6.png',
            '/static/monsters/legendary_7.png',
            '/static/monsters/legendary_8.png',
            '/static/monsters/legendary_9.png',
            '/static/monsters/legendary_10.png',
            '/static/monsters/legendary_11.png',
            '/static/monsters/legendary_12.png'
        ]
    }
    
    # 등급이 없으면 레어로 처리
    if rarity not in monster_images:
        rarity = '레어'
    
    return random.choice(monster_images[rarity])

def get_tier_conditions():
    """티어별 조건 반환 (업적 포인트 기준 + 몬스터 등급)"""
    return [
        {'name': '언랭크', 'image': '/static/tier_unranked.png', 'color': 'secondary', 'conditions': {'dungeon': 0, 'real_estate': 0, 'level': 0, 'achievement_points': 0, 'rare': 0, 'epic': 0, 'unique': 0, 'legendary': 0}},
        {'name': '브론즈', 'image': '/static/tier_bronze.png', 'color': 'warning', 'conditions': {'dungeon': 1, 'real_estate': 1, 'level': 15, 'achievement_points': 5, 'rare': 1, 'epic': 0, 'unique': 0, 'legendary': 0}},
        {'name': '실버', 'image': '/static/tier_silver.png', 'color': 'light', 'conditions': {'dungeon': 6, 'real_estate': 2, 'level': 40, 'achievement_points': 20, 'rare': 3, 'epic': 1, 'unique': 0, 'legendary': 0}},
        {'name': '골드', 'image': '/static/tier_gold.png', 'color': 'warning', 'conditions': {'dungeon': 16, 'real_estate': 3, 'level': 70, 'achievement_points': 40, 'rare': 5, 'epic': 3, 'unique': 1, 'legendary': 0}},
        {'name': '다이아', 'image': '/static/tier_diamond.png', 'color': 'info', 'conditions': {'dungeon': 31, 'real_estate': 5, 'level': 110, 'achievement_points': 70, 'rare': 8, 'epic': 5, 'unique': 3, 'legendary': 0}},
        {'name': '마스터', 'image': '/static/tier_master.png', 'color': 'primary', 'conditions': {'dungeon': 101, 'real_estate': 7, 'level': 160, 'achievement_points': 120, 'rare': 15, 'epic': 10, 'unique': 5, 'legendary': 1}},
        {'name': '챌린저', 'image': '/static/tier_challenger.png', 'color': 'danger', 'conditions': {'dungeon': 501, 'real_estate': 10, 'level': 200, 'achievement_points': 161, 'rare': 25, 'epic': 15, 'unique': 10, 'legendary': 3}}
    ]

def get_player_tier(player):
    """플레이어 통계에 따른 티어 계산 (업적 포인트 + 몬스터 등급)"""
    dungeon_clears = player.get('던전클리어횟수', 0)
    # 여러 부동산 소유 지원
    if isinstance(player.get('부동산들'), list):
        real_estate_count = len(player['부동산들'])
    elif player.get('거주지'):
        real_estate_count = 1
    else:
        real_estate_count = 0
    level = player['레벨']
    achievement_points = get_achievement_points(player)
    
    # 몬스터 등급별 개수 계산
    monster_counts = {'rare': 0, 'epic': 0, 'unique': 0, 'legendary': 0}
    compendium = player.get('도감', {})
    
    for monster_id in compendium:
        if monster_id:
            monster = get_monster_by_id(monster_id)
            if monster:
                rarity = monster.get('등급', '레어').lower()
                if rarity == '레어':
                    monster_counts['rare'] += 1
                elif rarity == '에픽':
                    monster_counts['epic'] += 1
                elif rarity == '유니크':
                    monster_counts['unique'] += 1
                elif rarity == '레전더리':
                    monster_counts['legendary'] += 1
    
    conditions = get_tier_conditions()
    
    # 가장 높은 달성 가능한 티어 찾기
    current_tier = conditions[0]  # 언랭크부터 시작
    
    for tier in conditions[1:]:  # 언랭크 제외
        req = tier['conditions']
        if (dungeon_clears >= req['dungeon'] and 
            real_estate_count >= req['real_estate'] and 
            level >= req['level'] and
            achievement_points >= req['achievement_points'] and
            monster_counts['rare'] >= req['rare'] and
            monster_counts['epic'] >= req['epic'] and
            monster_counts['unique'] >= req['unique'] and
            monster_counts['legendary'] >= req['legendary']):
            current_tier = tier
        else:
            break
    
    return current_tier

def get_player_stats(player):
    """플레이어 통계 정보"""
    total_stats = player['힘'] + player['지능'] + player['외모'] + player['체력스탯'] + player['운']
    quiz_accuracy = 0
    if player['총_퀴즈'] > 0:
        quiz_accuracy = (player['정답_퀴즈'] / player['총_퀴즈']) * 100
    
    dungeon_clears = player.get('던전클리어횟수', 0)
    tier_info = get_player_tier(player)
    tier_conditions = get_tier_conditions()
    
    # 부동산 갯수 계산
    real_estate_count = 1 if player.get('거주지') else 0
    
    return {
        'total_stats': total_stats,
        'quiz_accuracy': quiz_accuracy,
        'wealth_rank': get_wealth_rank(player['돈']),
        'days_played': player['날짜'],
        'dungeon_clears': dungeon_clears,
        'real_estate_count': real_estate_count,
        'achievements_count': len(player.get('성취', [])),
        'achievement_points': get_achievement_points(player),
        'level': player['레벨'],
        'tier': tier_info,
        'tier_conditions': tier_conditions
    }

def get_wealth_rank(money):
    """재산 등급 계산"""
    if money < 100000:
        return "거지"
    elif money < 1000000:
        return "서민"
    elif money < 10000000:
        return "중산층"
    elif money < 100000000:
        return "부유층"
    else:
        return "재벌"

def load_word_bank():
    """단어장 파일에서 로드"""
    try:
        if os.path.exists(WORD_BANK_FILE):
            with open(WORD_BANK_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            # 파일이 없으면 기본 단어장으로 초기화
            save_word_bank(word_bank)
            return word_bank
    except Exception as e:
        print(f"단어장 로드 실패: {e}")
        return word_bank

def save_word_bank(word_data):
    """단어장을 파일에 저장"""
    global _word_bank_cache
    try:
        with open(WORD_BANK_FILE, 'w', encoding='utf-8') as f:
            json.dump(word_data, f, ensure_ascii=False, indent=2)
        _word_bank_cache = word_data.copy()  # 캐시 업데이트 (깊은 복사)
        return True
    except Exception as e:
        print(f"단어장 저장 실패: {e}")
        return False

def get_word_bank():
    """단어장 가져오기 - 기본 단어와 사용자 단어 병합"""
    global _word_bank_cache
    
    # 기본 단어들 (data/game_data.py에서)
    base_words = word_bank.copy()
    
    # 사용자 추가 단어들 (word_bank.json에서) - 기본 단어와 중복되지 않는 것만
    user_words = get_user_words()
    
    # 두 단어집을 병합 (기본 단어 + 사용자 단어)
    _word_bank_cache = base_words + user_words
    
    return _word_bank_cache.copy()  # 복사본 반환으로 원본 보호

def get_user_words():
    """사용자가 추가한 단어들만 가져오기 (기본 단어와 중복 제거)"""
    if not os.path.exists(WORD_BANK_FILE):
        return []
    
    user_words = load_word_bank()
    base_words = word_bank.copy()
    
    # 기본 단어 리스트에서 단어 추출 (중복 확인용)
    base_word_texts = {word['단어'].lower() for word in base_words}
    
    # 기본 단어와 중복되지 않는 사용자 단어만 반환
    filtered_user_words = []
    for word in user_words:
        if word.get('단어', '').lower() not in base_word_texts:
            filtered_user_words.append(word)
    
    # 중복이 발견되었다면 정리된 목록을 저장
    if len(filtered_user_words) != len(user_words):
        save_user_words(filtered_user_words)
    
    return filtered_user_words

def save_user_words(user_words):
    """사용자 단어만 저장 (기본 단어는 제외)"""
    try:
        with open(WORD_BANK_FILE, 'w', encoding='utf-8') as f:
            json.dump(user_words, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"사용자 단어장 저장 실패: {e}")
        return False

def get_word_categories():
    """단어 카테고리 목록"""
    current_word_bank = get_word_bank()
    categories = set()
    for word in current_word_bank:
        categories.add(word.get('카테고리', '기본'))
    return list(categories)

def is_valid_word_entry(word, meaning):
    """단어 항목 유효성 검사"""
    if not word or not meaning:
        return False
    
    word = word.strip()
    meaning = meaning.strip()
    
    # 빈 문자열이거나 공백만 있는 경우
    if not word or not meaning:
        return False
    
    # 숫자만 있는 경우
    if word.isdigit() or meaning.isdigit():
        return False
    
    # 의미없는 반복 문자 (예: "aaa", "111")
    if len(set(word)) == 1 and len(word) > 2:
        return False
    if len(set(meaning)) == 1 and len(meaning) > 2:
        return False
    
    # 단어와 뜻이 동일한 경우
    if word.lower() == meaning.lower():
        return False
    
    return True

def add_word_to_bank(word, meaning, category='기본'):
    """단어장에 단어 추가 (중복 허용)"""
    # 유효성 검사
    if not is_valid_word_entry(word, meaning):
        return False
    
    # 사용자 단어에 바로 추가
    user_words = get_user_words()
    new_word = {
        '단어': word,
        '뜻': meaning,
        '카테고리': category
    }
    user_words.append(new_word)
    return save_user_words(user_words)

def save_category_words_to_bank(dungeon_id, category_name):
    """던전 카테고리의 모든 단어를 사용자 단어장에 저장"""
    try:
        # 던전 정보 가져오기
        dungeon = get_dungeon_by_id(dungeon_id)
        if not dungeon:
            return {'success': False, 'message': '존재하지 않는 던전입니다.'}
        
        # 던전의 단어 소스에서 모든 단어 로드 (던전에서 실제로 표시되는 단어들)
        word_source = dungeon.get('word_source', 'toeic')
        category_words = load_words_by_source(word_source)
        
        if not category_words:
            return {'success': False, 'message': '해당 카테고리에 단어가 없습니다.'}
        
        # 기본 단어와 사용자 단어장 가져오기
        base_words = word_bank.copy()
        user_words = get_user_words()
        
        # 중복 확인용 세트 (기본 단어 + 사용자 단어)
        base_word_texts = {base_word['단어'].lower() for base_word in base_words}
        user_word_texts = {user_word['단어'].lower() for user_word in user_words}
        existing_word_texts = base_word_texts | user_word_texts
        
        # 새로 추가할 단어들
        new_words = []
        duplicate_count = 0
        
        for word_data in category_words:
            word = word_data['단어']
            meaning = word_data['뜻']
            
            # 유효성 검사
            if not is_valid_word_entry(word, meaning):
                continue
            
            # 중복 확인 (기본 단어 + 사용자 단어 모두 확인)
            if word.lower() not in existing_word_texts:
                new_word = {
                    '단어': word,
                    '뜻': meaning,
                    '카테고리': category_name
                }
                new_words.append(new_word)
                existing_word_texts.add(word.lower())  # 같은 요청 내에서 중복 방지
            else:
                duplicate_count += 1
        
        if new_words:
            # 기존 사용자 단어에 새 단어들 추가
            user_words.extend(new_words)
            success = save_user_words(user_words)
            
            if success:
                total_words = len(category_words)
                added_count = len(new_words)
                message = f'"{category_name}" 카테고리에 {added_count}개의 단어가 저장되었습니다!'
                if duplicate_count > 0:
                    message += f' ({duplicate_count}개는 이미 존재하여 제외됨)'
                
                return {
                    'success': True, 
                    'message': message,
                    'added_count': added_count,
                    'total_words': total_words,
                    'duplicate_count': duplicate_count
                }
            else:
                return {'success': False, 'message': '단어 저장 중 오류가 발생했습니다.'}
        else:
            return {
                'success': False, 
                'message': f'추가할 수 있는 새로운 단어가 없습니다. ({duplicate_count}개 모두 이미 존재함)'
            }
    
    except Exception as e:
        print(f"Error in save_category_words_to_bank: {e}")
        return {'success': False, 'message': '카테고리 단어 저장 중 오류가 발생했습니다.'}

def add_words_to_bank(words, meanings, category, player):
    """여러 단어를 단어장에 추가 (중복 허용)"""
    user_words = get_user_words()
    
    added_count = 0
    
    for word, meaning in zip(words, meanings):
        # 유효성 검사 먼저
        if not is_valid_word_entry(word, meaning):
            continue
            
        # 중복 체크 없이 바로 추가
        user_words.append({
            '단어': word,
            '뜻': meaning,
            '카테고리': category
        })
        added_count += 1
    
    # 사용자 단어만 저장
    save_user_words(user_words)
    
    return added_count

def delete_word_from_bank(word_index):
    """단어장에서 단어 삭제 (사용자 단어만)"""
    current_word_bank = get_word_bank()  # 전체 단어장 로드
    base_words = word_bank.copy()  # 기본 단어들
    user_words = get_user_words()  # 사용자 단어들
    
    try:
        if 0 <= word_index < len(current_word_bank):
            target_word = current_word_bank[word_index]
            
            # 기본 단어는 삭제할 수 없음
            if word_index < len(base_words):
                return {'success': False, 'message': '기본 단어는 삭제할 수 없습니다. 사용자가 추가한 단어만 삭제 가능합니다.'}
            
            # 사용자 단어에서 이 단어를 찾아서 삭제
            target_word_text = target_word['단어']
            for i, user_word in enumerate(user_words):
                if user_word['단어'] == target_word_text and user_word['뜻'] == target_word['뜻']:
                    deleted_word = user_words.pop(i)
                    save_user_words(user_words)  # 사용자 단어만 저장
                    return {'success': True, 'message': f'단어 "{deleted_word["단어"]}"가 삭제되었습니다.'}
            
            return {'success': False, 'message': '사용자 단어장에서 해당 단어를 찾을 수 없습니다.'}
        else:
            return {'success': False, 'message': '잘못된 단어 번호입니다.'}
    except Exception as e:
        print(f"Error in delete_word_from_bank: {e}")
        return {'success': False, 'message': '단어 삭제 중 오류가 발생했습니다.'}

def delete_multiple_words_from_bank(word_indices):
    """단어장에서 여러 단어 삭제 (사용자 단어만)"""
    current_word_bank = get_word_bank()  # 전체 단어장 로드
    base_words = word_bank.copy()  # 기본 단어들
    user_words = get_user_words()  # 사용자 단어들
    
    try:
        word_indices = [int(idx) for idx in word_indices]
        deleted_words = []
        
        # 삭제할 단어들 수집 (사용자 단어만)
        words_to_delete = []
        for index in word_indices:
            if index >= len(base_words) and index < len(current_word_bank):  # 사용자 단어 범위
                target_word = current_word_bank[index]
                words_to_delete.append((target_word['단어'], target_word['뜻']))
        
        # 사용자 단어에서 일치하는 단어들 삭제
        for word_text, meaning in words_to_delete:
            for i in range(len(user_words) - 1, -1, -1):  # 뒤에서부터 삭제
                if user_words[i]['단어'] == word_text and user_words[i]['뜻'] == meaning:
                    deleted_word = user_words.pop(i)
                    deleted_words.append(deleted_word['단어'])
                    break  # 같은 단어라도 한 번만 삭제
        
        if deleted_words:
            save_user_words(user_words)  # 사용자 단어만 저장
            return {'success': True, 'message': f'{len(deleted_words)}개의 단어가 삭제되었습니다.'}
        else:
            return {'success': False, 'message': '삭제할 수 있는 사용자 단어가 없습니다. 기본 단어는 삭제할 수 없습니다.'}
    except Exception as e:
        print(f"Error in delete_multiple_words_from_bank: {e}")
        return {'success': False, 'message': '단어 삭제 중 오류가 발생했습니다.'}

def edit_word_in_bank(word_index, new_word, new_meaning, new_category):
    """단어장의 단어 수정 (사용자 단어만)"""
    current_word_bank = get_word_bank()  # 전체 단어장 로드
    base_words = word_bank.copy()  # 기본 단어들
    user_words = get_user_words()  # 사용자 단어들
    
    try:
        if 0 <= word_index < len(current_word_bank):
            # 기본 단어는 수정할 수 없음
            if word_index < len(base_words):
                return {'success': False, 'message': '기본 단어는 수정할 수 없습니다. 사용자가 추가한 단어만 수정 가능합니다.'}
            
            # 사용자 단어에서 이 단어를 찾아서 수정
            target_word = current_word_bank[word_index]
            target_word_text = target_word['단어']
            for i, user_word in enumerate(user_words):
                if user_word['단어'] == target_word_text and user_word['뜻'] == target_word['뜻']:
                    user_words[i] = {
                        '단어': new_word,
                        '뜻': new_meaning,
                        '카테고리': new_category
                    }
                    save_user_words(user_words)  # 사용자 단어만 저장
                    return {'success': True, 'message': f'단어 "{new_word}"가 수정되었습니다.'}
            
            return {'success': False, 'message': '사용자 단어장에서 해당 단어를 찾을 수 없습니다.'}
        else:
            return {'success': False, 'message': '잘못된 단어 번호입니다.'}
    except Exception as e:
        print(f"Error in edit_word_in_bank: {e}")
        return {'success': False, 'message': '단어 수정 중 오류가 발생했습니다.'}

def change_multiple_categories(word_indices, new_category):
    """여러 단어의 카테고리를 일괄 변경 (사용자 단어만)"""
    user_words = get_user_words()
    
    try:
        word_indices = [int(idx) for idx in word_indices]
        changed_count = 0
        
        # 각 인덱스에 해당하는 단어의 카테고리 변경
        for index in word_indices:
            if 0 <= index < len(user_words):
                user_words[index]['카테고리'] = new_category
                changed_count += 1
        
        if changed_count > 0:
            save_user_words(user_words)
            return {'success': True, 'message': f'{changed_count}개 단어의 카테고리가 "{new_category}"로 변경되었습니다.'}
        else:
            return {'success': False, 'message': '변경할 수 있는 단어가 없습니다.'}
    except Exception as e:
        print(f"Error in change_multiple_categories: {e}")
        return {'success': False, 'message': '카테고리 변경 중 오류가 발생했습니다.'}

def get_word_by_category(category='all'):
    """카테고리별 단어 조회"""
    current_word_bank = get_word_bank()
    if category == 'all':
        return current_word_bank
    else:
        return [word for word in current_word_bank if word.get('카테고리', '기본') == category]

def search_words(search_term):
    """단어 검색"""
    current_word_bank = get_word_bank()
    search_term = search_term.lower()
    results = []
    for i, word in enumerate(current_word_bank):
        if (search_term in word['단어'].lower() or 
            search_term in word['뜻'].lower() or 
            search_term in word.get('카테고리', '기본').lower()):
            word_with_index = word.copy()
            word_with_index['인덱스'] = str(i)
            results.append(word_with_index)
    return results

def process_quiz_answer(player, answer, correct_answer, question_type):
    """퀴즈 답안 처리"""
    player['총_퀴즈'] += 1
    player['기력'] = max(0, player['기력'] - 1)
    
    is_correct = answer.lower() == correct_answer.lower()
    
    if is_correct:
        exp_gain = random.randint(3, 7)
        player['경험치'] += exp_gain
        player['정답_퀴즈'] += 1
        level_ups = check_level_up(player)
        
        return {
            'correct': True,
            'exp_gained': exp_gain,
            'level_ups': level_ups,
            'correct_answer': correct_answer
        }
    else:
        return {
            'correct': False,
            'exp_gained': 0,
            'level_ups': 0,
            'correct_answer': correct_answer
        }

def get_jobs():
    """직업 목록 가져오기"""
    return jobs

def apply_for_job(player, job_id):
    """취업 신청"""
    if job_id < 0 or job_id >= len(jobs):
        return {'success': False, 'message': '잘못된 직업 선택입니다.'}
    
    job = jobs[job_id]
    
    # 각 스탯별 개별 요구사항 확인
    stat_names = ['힘', '지능', '외모', '체력스탯', '운']
    insufficient_stats = []
    
    for stat in stat_names:
        if player[stat] < job[stat]:
            insufficient_stats.append(f"{stat}: {player[stat]}/{job[stat]}")
    
    if insufficient_stats:
        return {
            'success': False, 
            'message': f'스탯이 부족합니다. 부족한 스탯: {", ".join(insufficient_stats)}'
        }
    else:
        player['직장'] = job['이름']
        player['직장정보'] = job
        return {'success': True, 'message': f"{job['이름']}에 취업했습니다!"}

def work(player):
    """근무하기"""
    if player['직장'] is None:
        return {'success': False, 'message': '직장이 없습니다.'}
    
    if player['기력'] <= 0:
        return {'success': False, 'message': '기력이 부족하여 근무할 수 없습니다.'}
    
    job_info = player['직장정보']
    salary = job_info['월급'] + random.randint(-500, 500)  # 급여 변동
    
    player['돈'] += salary
    player['기력'] = max(0, player['기력'] - 3)
    player['경험치'] += random.randint(5, 15)
    
    # 근무 시 시간 흐름 (1시간 근무)
    player['시간'] += 1
    if player['시간'] >= 24:
        player['시간'] -= 24
        player['날짜'] += 1
    
    # 스탯 증가 (직업에 따라)
    if random.random() < 0.3:  # 30% 확률로 스탯 증가
        stat_gains = []
        if job_info['힘'] > 0 and random.random() < 0.5:
            player['힘'] += 1
            stat_gains.append('힘')
        if job_info['지능'] > 0 and random.random() < 0.5:
            player['지능'] += 1
            stat_gains.append('지능')
        if job_info['외모'] > 0 and random.random() < 0.5:
            player['외모'] += 1
            stat_gains.append('외모')
    
    # 업적용 통계 업데이트
    if '일한_횟수' not in player:
        player['일한_횟수'] = 0
    player['일한_횟수'] += 1
    
    level_ups = check_level_up(player)
    
    message = f"{salary}원을 벌었습니다. 기력 -3, 경험치 획득, 시간 +1시간"
    if level_ups > 0:
        message += f" 레벨업! ({level_ups}회)"
    
    return {'success': True, 'message': message}

def get_real_estate():
    """부동산 목록 가져오기"""
    return real_estate

def buy_property(player, property_id):
    """부동산 구매 (여러 개 소유 가능)"""
    if property_id < 0 or property_id >= len(real_estate):
        return {'success': False, 'message': '잘못된 부동산 선택입니다.'}
    
    property_info = real_estate[property_id]
    
    if player['돈'] < property_info['매매']:
        return {'success': False, 'message': '돈이 부족합니다.'}
    
    # 부동산들 리스트 초기화 (기존 거주지 마이그레이션)
    if '부동산들' not in player:
        player['부동산들'] = []
        if player.get('거주지'):
            player['부동산들'].append({
                'name': player['거주지'],
                'buy_date': player.get('부동산구매날짜', player['날짜']),
                'last_rent_date': player.get('마지막월세날짜', player.get('부동산구매날짜', player['날짜']))
            })
    
    # 같은 부동산 중복 구매 방지
    for prop in player['부동산들']:
        if prop['name'] == property_info['이름']:
            return {'success': False, 'message': '이미 소유한 부동산입니다.'}
    
    player['돈'] -= property_info['매매']
    player['부동산들'].append({
        'name': property_info['이름'],
        'buy_date': player['날짜'],
        'last_rent_date': player['날짜']
    })
    player['최대기력'] += property_info['기력회복']
    player['기력'] = min(player['최대기력'], player['기력'])
    
    # 첫 거주지는 거주지로 설정
    if len(player['부동산들']) == 1:
        player['거주지'] = property_info['이름']
    
    return {'success': True, 'message': f"{property_info['이름']}을(를) 구매했습니다! 최대 기력이 {property_info['기력회복']}만큼 증가했습니다. (총 {len(player['부동산들'])}개 소유)"}

def sell_property(player, property_name=None):
    """부동산 판매 (현재 거주지 기본값)"""
    if '부동산들' not in player or len(player['부동산들']) == 0:
        return {'success': False, 'message': '소유한 부동산이 없습니다.'}
    
    sell_target = property_name or player.get('거주지')
    if not sell_target:
        return {'success': False, 'message': '판매할 부동산이 없습니다.'}
    
    for prop in real_estate:
        if prop['이름'] == sell_target:
            sell_price = int(prop['매매'] * 0.8)
            player['돈'] += sell_price
            player['최대기력'] -= prop['기력회복']
            player['기력'] = min(player['최대기력'], player['기력'])
            
            player['부동산들'] = [p for p in player['부동산들'] if p['name'] != sell_target]
            
            if player['부동산들']:
                player['거주지'] = player['부동산들'][0]['name']
            else:
                player['거주지'] = None
            
            return {'success': True, 'message': f"{sell_target}을(를) {sell_price}원에 판매했습니다."}
    
    return {'success': False, 'message': '판매 오류가 발생했습니다.'}

def change_residence(player, property_name):
    """거주지 변경 (소유한 부동산 중에서만)"""
    if '부동산들' not in player or len(player['부동산들']) == 0:
        return {'success': False, 'message': '소유한 부동산이 없습니다.'}
    
    # 소유하고 있는 부동산인지 확인
    owned = False
    for prop in player['부동산들']:
        if prop['name'] == property_name:
            owned = True
            break
    
    if not owned:
        return {'success': False, 'message': '소유하지 않은 부동산입니다.'}
    
    # 이미 거주중인지 확인
    if player.get('거주지') == property_name:
        return {'success': False, 'message': '이미 거주중인 부동산입니다.'}
    
    player['거주지'] = property_name
    
    # 기력 회복량 정보 찾기
    recovery = 0
    for prop in real_estate:
        if prop['이름'] == property_name:
            recovery = prop['기력회복']
            break
    
    return {'success': True, 'message': f"{property_name}로 이사했습니다! (추가 기력 회복량: +{recovery})"}

def get_shop_items():
    """상점 아이템 목록"""
    return shop_items

def buy_item(player, item_id):
    """아이템 구매 (던전 특화 버전)"""
    shop_items = get_shop_items()
    
    if item_id < 0 or item_id >= len(shop_items):
        return {'success': False, 'message': '잘못된 아이템 선택입니다.'}
    
    item = shop_items[item_id]
    
    if player['돈'] < item['가격']:
        return {'success': False, 'message': '돈이 부족합니다.'}
    
    player['돈'] -= item['가격']
    
    # 던전 아이템은 인벤토리에 저장
    if item.get('타입') == '던전':
        if '던전_인벤토리' not in player:
            player['던전_인벤토리'] = {}
        
        item_name = item['이름']
        if item_name not in player['던전_인벤토리']:
            player['던전_인벤토리'][item_name] = 0
        player['던전_인벤토리'][item_name] += 1
        
        return {'success': True, 'message': f'{item["이름"]}을(를) 구매하여 던전 인벤토리에 저장했습니다!'}
    
    # 무기는 장착 시스템으로 관리
    elif item.get('타입') == '무기':
        # 레벨 제한 확인
        required_level = item.get('레벨_제한', 0)
        if player['레벨'] < required_level:
            return {'success': False, 'message': f'레벨 {required_level} 이상이어야 구매할 수 있습니다. (현재 레벨: {player["레벨"]})'}
        
        if '무기_인벤토리' not in player:
            player['무기_인벤토리'] = {}
        
        item_name = item['이름']
        if item_name not in player['무기_인벤토리']:
            player['무기_인벤토리'][item_name] = 0
        player['무기_인벤토리'][item_name] += 1
        
        # 첫 번째 무기는 자동으로 장착 (장착된 무기가 없을 때만)
        if '장착된_무기' not in player or player['장착된_무기'] is None:
            player['장착된_무기'] = item_name
            return {'success': True, 'message': f'{item["이름"]}을(를) 구매하고 장착했습니다!'}
        else:
            return {'success': True, 'message': f'{item["이름"]}을(를) 구매했습니다! 인벤토리에서 장착할 수 있습니다.'}
    
    else:
        # 일반 아이템은 즉시 효과 적용
        for stat, value in item['효과'].items():
            if stat in player:
                if stat == '기력':
                    # 기력은 최대치 제한
                    player[stat] = min(player[stat] + value, player['최대기력'])
                elif stat == '체력':
                    # 체력은 최대치 제한 
                    player[stat] = min(player[stat] + value, player['최대체력'])
                else:
                    # 기타 스탯은 단순 증가
                    player[stat] += value
        
        return {'success': True, 'message': f'{item["이름"]}의 효과가 적용되었습니다!'}

def get_weapon_damage(player):
    """장착된 무기의 추가 피해 계산"""
    if '장착된_무기' not in player or not player['장착된_무기']:
        return 0
    
    weapon_name = player['장착된_무기']
    shop_items = get_shop_items()
    
    # 상점 아이템에서 무기 정보 찾기
    for item in shop_items:
        if item.get('이름') == weapon_name and item.get('타입') == '무기':
            return item['효과'].get('무기 피해', 0)
    
    return 0

def equip_weapon(player, weapon_name):
    """무기 장착"""
    if '무기_인벤토리' not in player:
        return {'success': False, 'message': '무기 인벤토리가 없습니다.'}
    
    if weapon_name not in player['무기_인벤토리'] or player['무기_인벤토리'][weapon_name] <= 0:
        return {'success': False, 'message': '보유하지 않은 무기입니다.'}
    
    # 레벨 제한 확인
    shop_items = get_shop_items()
    for item in shop_items:
        if item.get('이름') == weapon_name and item.get('타입') == '무기':
            required_level = item.get('레벨_제한', 0)
            if player['레벨'] < required_level:
                return {'success': False, 'message': f'레벨 {required_level} 이상이어야 장착할 수 있습니다. (현재 레벨: {player["레벨"]})'}
            break
    
    player['장착된_무기'] = weapon_name
    return {'success': True, 'message': f'{weapon_name}을(를) 장착했습니다!'}

def unequip_weapon(player):
    """무기 해제"""
    if '장착된_무기' in player:
        weapon_name = player['장착된_무기']
        player['장착된_무기'] = None
        return {'success': True, 'message': f'{weapon_name}을(를) 해제했습니다.'}
    else:
        return {'success': False, 'message': '장착된 무기가 없습니다.'}

def allocate_stat_points(player, stat_type, points):
    """스탯 포인트 분배"""
    if points <= 0 or points > player['스탯포인트']:
        return {'success': False, 'message': '잘못된 포인트 수입니다.'}
    
    stat_map = {
        '힘': '힘', '지능': '지능', '외모': '외모', 
        '체력': '체력스탯', '운': '운'
    }
    
    if stat_type not in stat_map:
        return {'success': False, 'message': '잘못된 스탯 유형입니다.'}
    
    player[stat_map[stat_type]] += points
    player['스탯포인트'] -= points
    
    return {'success': True, 'message': f'{stat_type}에 {points} 포인트를 분배했습니다.'}

def sleep(player):
    """잠자기"""
    # 기본 회복량 4 + 집의 퀄리티에 따른 추가 회복
    base_recovery = 4
    bonus_recovery = 0
    
    if player['거주지']:
        for prop in real_estate:
            if prop['이름'] == player['거주지']:
                bonus_recovery = prop['기력회복']
                break
    
    total_recovery = base_recovery + bonus_recovery
    player['기력'] = min(player['최대기력'], player['기력'] + total_recovery)
    player['체력'] = 10
    player['시간'] += 8
    
    # 월세 메시지 초기화
    rent_messages = []
    
    if player['시간'] >= 24:
        player['시간'] -= 24
        player['날짜'] += 1
        
        # 여러 부동산에서 월세 수입
        if '부동산들' in player and len(player['부동산들']) > 0:
            for i, prop_dict in enumerate(player['부동산들']):
                prop_name = prop_dict['name']
                last_rent_day = prop_dict.get('last_rent_date', prop_dict.get('buy_date', player['날짜']))
                days_since_last_rent = player['날짜'] - last_rent_day
                
                # 30일마다 월세 지급
                if days_since_last_rent >= 30:
                    for prop in real_estate:
                        if prop['이름'] == prop_name:
                            player['돈'] += prop['월세']
                            player['부동산들'][i]['last_rent_date'] = player['날짜']
                            rent_cycles = days_since_last_rent // 30
                            if rent_cycles > 1:
                                rent_messages.append(f'{prop_name} 월세 {prop["월세"]:,}원 ({rent_cycles}개월분)')
                                player['돈'] += prop['월세'] * (rent_cycles - 1)
                            else:
                                rent_messages.append(f'{prop_name} 월세 {prop["월세"]:,}원')
                            break
        # 하위호환성: 거주지만 있는 경우
        elif player['거주지'] and '부동산구매날짜' in player:
            days_since_purchase = player['날짜'] - player.get('부동산구매날짜', 0)
            last_rent_day = player.get('마지막월세날짜', player.get('부동산구매날짜', 0))
            days_since_last_rent = player['날짜'] - last_rent_day
            
            if days_since_last_rent >= 30:
                for prop in real_estate:
                    if prop['이름'] == player['거주지']:
                        player['돈'] += prop['월세']
                        player['마지막월세날짜'] = player['날짜']
                        rent_cycles = days_since_last_rent // 30
                        if rent_cycles > 1:
                            rent_messages.append(f'부동산 월세 수입 {prop["월세"]:,}원 ({rent_cycles}개월분)')
                            player['돈'] += prop['월세'] * (rent_cycles - 1)
                        else:
                            rent_messages.append(f'부동산 월세 수입 {prop["월세"]:,}원')
                        break
    
    # 업적용 통계 업데이트
    if '잠잔_횟수' not in player:
        player['잠잔_횟수'] = 0
    player['잠잔_횟수'] += 1
    
    # 월세 수입 메시지 추가
    base_message = f'충분히 잠을 잤습니다. 기력 +{total_recovery} (기본 4 + 집 보너스 {bonus_recovery}), 체력이 회복되었습니다.'
    if rent_messages:
        rent_text = ', '.join(rent_messages)
        return {'message': f'{base_message} {rent_text}'}
    else:
        return {'message': base_message}

def check_random_event(player):
    """랜덤 이벤트 확인"""
    if random.random() < 0.01:  # 1% 확률
        event = random.choice(random_events)
        
        # 이벤트 효과 적용
        for effect, value in event['효과'].items():
            if effect in player:
                try:
                    # 숫자 타입만 더함
                    if isinstance(player[effect], (int, float)) and isinstance(value, (int, float)):
                        player[effect] += value
                        player[effect] = max(0, player[effect])  # 음수 방지
                except (TypeError, ValueError):
                    pass  # 타입 오류 무시
        
        # 이벤트 기록
        save_event(event['이름'])
        
        return event
    
    return None

def save_event(event_name):
    """이벤트 기록 저장"""
    try:
        events = []
        if os.path.exists(EVENTS_FILE):
            with open(EVENTS_FILE, 'r', encoding='utf-8') as f:
                events = json.load(f)
        
        events.append({
            'event': event_name,
            'timestamp': datetime.now().isoformat()
        })
        
        # 최근 10개만 유지
        events = events[-10:]
        
        with open(EVENTS_FILE, 'w', encoding='utf-8') as f:
            json.dump(events, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"이벤트 저장 실패: {e}")

def get_recent_events():
    """최근 이벤트 가져오기"""
    try:
        if os.path.exists(EVENTS_FILE):
            with open(EVENTS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        print(f"이벤트 불러오기 실패: {e}")
    return []

def get_achievements(player):
    """성취 확인 - 플레이어가 달성한 성취 이름 반환"""
    achieved_conditions = get_player_achievements(player)
    achievements_list = get_all_achievements()
    
    # 조건 이름을 성취 이름으로 변환
    achievement_names = []
    for achievement in achievements_list:
        if achievement['조건'] in achieved_conditions:
            achievement_names.append(achievement['이름'])
    
    return achievement_names

def get_all_achievements():
    """모든 성취 목록 - 완전한 30개 업적과 난이도별 포인트"""
    return [
        # 쉬운 업적 (1-2점)
        {'이름': '첫 걸음', '설명': '게임 시작하기', '조건': 'game_start', '난이도': '쉬움', '포인트': 1},
        {'이름': '열정적인 학습자', '설명': '첫 퀴즈 정답', '조건': 'first_quiz', '난이도': '쉬움', '포인트': 1},
        {'이름': '사회초년생', '설명': '첫 직장 얻기', '조건': 'first_job', '난이도': '쉬움', '포인트': 1},
        {'이름': '독립', '설명': '첫 거주지 구입', '조건': 'first_home', '난이도': '쉬움', '포인트': 2},
        {'이름': '야심차', '설명': '레벨 5 달성', '조건': 'level_5', '난이도': '쉬움', '포인트': 2},
        {'이름': '저축왕', '설명': '10만원 이상 보유', '조건': 'money_100k', '난이도': '쉬움', '포인트': 2},
        
        # 보통 업적 (3-5점)
        {'이름': '레벨 마스터', '설명': '레벨 10 달성', '조건': 'level_10', '난이도': '보통', '포인트': 3},
        {'이름': '퀴즈 초보자', '설명': '퀴즈 20문제 정답', '조건': 'quiz_20', '난이도': '보통', '포인트': 3},
        {'이름': '성실한 근로자', '설명': '일하기 50번', '조건': 'work_50', '난이도': '보통', '포인트': 3},
        {'이름': '건강한 생활', '설명': '잠자기 30번', '조건': 'sleep_30', '난이도': '보통', '포인트': 3},
        {'이름': '백만장자', '설명': '100만원 이상 보유', '조건': 'money_1m', '난이도': '보통', '포인트': 4},
        {'이름': '퀴즈왕', '설명': '퀴즈 100문제 정답', '조건': 'quiz_100', '난이도': '보통', '포인트': 4},
        {'이름': '체력단련', '설명': '체력 스탯 30 달성', '조건': 'strength_30', '난이도': '보통', '포인트': 4},
        {'이름': '똑똑이', '설명': '지능 스탯 30 달성', '조건': 'intelligence_30', '난이도': '보통', '포인트': 4},
        {'이름': '매력적인', '설명': '외모 스탯 30 달성', '조건': 'beauty_30', '난이도': '보통', '포인트': 4},
        {'이름': '운빨좋은', '설명': '운 스탯 30 달성', '조건': 'luck_30', '난이도': '보통', '포인트': 4},
        {'이름': '전문직', '설명': '월급 5000원 이상 직업', '조건': 'high_salary_job', '난이도': '보통', '포인트': 5},
        
        # 어려운 업적 (6-8점)
        {'이름': '성공한 사업가', '설명': 'CEO 직업 달성', '조건': 'ceo_job', '난이도': '어려움', '포인트': 6},
        {'이름': '부동산왕', '설명': '펜트하우스 소유', '조건': 'penthouse', '난이도': '어려움', '포인트': 6},
        {'이름': '체력짱', '설명': '체력 스탯 50 달성', '조건': 'strength_50', '난이도': '어려움', '포인트': 6},
        {'이름': '천재', '설명': '지능 스탯 50 달성', '조건': 'intelligence_50', '난이도': '어려움', '포인트': 6},
        {'이름': '완벽한 외모', '설명': '외모 스탯 50 달성', '조건': 'beauty_50', '난이도': '어려움', '포인트': 6},
        {'이름': '행운의 여신', '설명': '운 스탯 50 달성', '조건': 'luck_50', '난이도': '어려움', '포인트': 6},
        {'이름': '억만장자', '설명': '1천만원 이상 보유', '조건': 'money_10m', '난이도': '어려움', '포인트': 7},
        {'이름': '퀴즈 박사', '설명': '퀴즈 500문제 정답', '조건': 'quiz_500', '난이도': '어려움', '포인트': 7},
        {'이름': '워커홀릭', '설명': '일하기 200번', '조건': 'work_200', '난이도': '어려움', '포인트': 7},
        {'이름': '고급 주거자', '설명': '월세 수입 50만원 이상 부동산 소유', '조건': 'luxury_home', '난이도': '어려움', '포인트': 8},
        
        # 던전 관련 업적 (새로 추가)
        {'이름': '던전 탐험가', '설명': '첫 던전 클리어', '조건': 'first_dungeon', '난이도': '보통', '포인트': 3},
        {'이름': '몬스터 헌터', '설명': '몬스터 50마리 처치', '조건': 'monster_50', '난이도': '어려움', '포인트': 5},
        
        # 전설 업적 (9-10점)
        {'이름': '전설의 레벨', '설명': '레벨 50 달성', '조건': 'level_50', '난이도': '전설', '포인트': 9},
        {'이름': '완벽한 인간', '설명': '모든 스탯 50 이상', '조건': 'all_stats_50', '난이도': '전설', '포인트': 9},
        {'이름': '재벌', '설명': '1억원 이상 보유', '조건': 'money_100m', '난이도': '전설', '포인트': 10},
        {'이름': '퀴즈 전설', '설명': '퀴즈 1000문제 정답', '조건': 'quiz_1000', '난이도': '전설', '포인트': 10}
    ]

def get_player_achievements(player):
    """플레이어가 달성한 성취 목록"""
    achieved = []
    
    # 기본 통계 초기화 (없는 경우) - 안전한 접근
    player.setdefault('일한_횟수', 0)
    player.setdefault('잠잔_횟수', 0)
    
    # 쉬운 업적
    achieved.append('game_start')  # 게임을 시작했다면 항상 달성
    if player['정답_퀴즈'] >= 1:
        achieved.append('first_quiz')
    if player['직장']:
        achieved.append('first_job')
    if player['거주지']:
        achieved.append('first_home')
    if player['레벨'] >= 5:
        achieved.append('level_5')
    if player['돈'] >= 100000:
        achieved.append('money_100k')
    
    # 보통 업적
    if player['레벨'] >= 10:
        achieved.append('level_10')
    if player['정답_퀴즈'] >= 20:
        achieved.append('quiz_20')
    if player['일한_횟수'] >= 50:
        achieved.append('work_50')
    if player['잠잔_횟수'] >= 30:
        achieved.append('sleep_30')
    if player['돈'] >= 1000000:
        achieved.append('money_1m')
    if player['정답_퀴즈'] >= 100:
        achieved.append('quiz_100')
    if player['체력스탯'] >= 30:
        achieved.append('strength_30')
    if player['지능'] >= 30:
        achieved.append('intelligence_30')
    if player['외모'] >= 30:
        achieved.append('beauty_30')
    if player['운'] >= 30:
        achieved.append('luck_30')
    
    # 월급 5000원 이상 직업 확인
    if player['직장']:
        for job in jobs:
            if job['이름'] == player['직장'] and job['월급'] >= 5000:
                achieved.append('high_salary_job')
                break
    
    # 어려운 업적
    if player['직장'] and 'CEO' in player['직장']:
        achieved.append('ceo_job')
    if player['거주지'] and '펜트하우스' in player['거주지']:
        achieved.append('penthouse')
    if player['체력스탯'] >= 50:
        achieved.append('strength_50')
    if player['지능'] >= 50:
        achieved.append('intelligence_50')
    if player['외모'] >= 50:
        achieved.append('beauty_50')
    if player['운'] >= 50:
        achieved.append('luck_50')
    if player['돈'] >= 10000000:
        achieved.append('money_10m')
    if player['정답_퀴즈'] >= 500:
        achieved.append('quiz_500')
    if player['일한_횟수'] >= 200:
        achieved.append('work_200')
    
    # 고급 주거지 확인 (월세 수입 50만원 이상)
    if player['거주지']:
        for prop in real_estate:
            if prop['이름'] == player['거주지'] and prop['월세'] >= 500000:
                achieved.append('luxury_home')
                break
    
    # 전설 업적
    if player['레벨'] >= 50:
        achieved.append('level_50')
    if (player['체력스탯'] >= 50 and player['지능'] >= 50 and 
        player['외모'] >= 50 and player['운'] >= 50):
        achieved.append('all_stats_50')
    if player['돈'] >= 100000000:
        achieved.append('money_100m')
    if player['정답_퀴즈'] >= 1000:
        achieved.append('quiz_1000')
    
    return achieved

def get_achievement_points(player):
    """플레이어가 획득한 업적 포인트 계산"""
    achieved = get_player_achievements(player)
    achievements = get_all_achievements()
    
    total_points = 0
    for achievement in achievements:
        if achievement['조건'] in achieved:
            total_points += achievement['포인트']
    
    return total_points

# ============== 던전 시스템 ==============

def load_toeic_words():
    """토익 단어 로드"""
    try:
        with open(TOEIC_WORDS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"토익 단어 로드 실패: {e}")
        return []

def load_words_by_source(word_source, category_filter=None, difficulty_filter=None):
    """카테고리별 단어 로드"""
    # user_custom인 경우 사용자가 등록한 단어만 가져오기
    if word_source == 'user_custom':
        user_words = get_user_words()  # 사용자가 추가한 단어만
        
        if not user_words or len(user_words) == 0:
            return []  # 사용자 단어가 없으면 빈 리스트 반환
        
        # 단어가 부족한 경우 반복하여 확장 (최소 50개)
        if len(user_words) < 50:
            extended_words = user_words * (50 // len(user_words) + 1)
            return extended_words[:50]
        
        return user_words
    
    # user_bank인 경우 사용자 단어장에서 가져오기
    if word_source == 'user_bank':
        all_words = get_word_bank()  # 기본 + 사용자 단어 병합
        
        # 카테고리 필터 적용
        if category_filter:
            all_words = [word for word in all_words if word.get('카테고리', '기본') == category_filter]
        
        # 난이도 필터 적용
        if difficulty_filter:
            all_words = [word for word in all_words if word.get('난이도', 'beginner') in difficulty_filter]
        
        # 단어가 부족한 경우 반복하여 확장
        if len(all_words) > 0 and len(all_words) < 50:
            extended_words = all_words * (50 // len(all_words) + 1)
            return extended_words[:50]
        
        return all_words
    
    # 기존 JSON 파일 기반 로드
    file_mapping = {
        'toeic': 'data/toeic_words.json',
        'business': 'data/business_words.json',
        'marketing': 'data/marketing_words.json',
        'finance': 'data/finance_words.json',
        'it': 'data/it_words.json',
        'programming': 'data/programming_words.json',
        'ai': 'data/ai_words.json',
        'medical': 'data/medical_words.json'
    }
    
    try:
        file_path = file_mapping.get(word_source, 'data/toeic_words.json')  # 기본값은 토익
        with open(file_path, 'r', encoding='utf-8') as f:
            words = json.load(f)
            # 단어가 적어도 카테고리 순수성 유지 - 같은 단어들을 반복하여 확장
            if len(words) < 50 and word_source != 'toeic':
                # 카테고리 단어만 반복하여 확장 (순수성 유지)
                extended_words = words * (50 // len(words) + 1)
                return extended_words[:50]  # 50개로 제한
            return words
    except Exception as e:
        print(f"{word_source} 단어 로드 실패: {e}, 토익 단어로 대체")
        return load_toeic_words()

def get_dungeons():
    """던전 목록 가져오기"""
    return dungeons

def get_dungeon_by_id(dungeon_id):
    """ID로 던전 정보 가져오기"""
    for dungeon in dungeons:
        if dungeon['id'] == dungeon_id:
            return dungeon
    return None

def init_dungeon_run(player, dungeon_id):
    """던전 실행 초기화"""
    dungeon = get_dungeon_by_id(dungeon_id)
    if not dungeon:
        return {'success': False, 'message': '존재하지 않는 던전입니다.'}
    
    # 필수 키 검증
    required_keys = ['레벨_제한', 'clear_condition', 'max_health', 'rarity_distribution']
    for key in required_keys:
        if key not in dungeon:
            return {'success': False, 'message': f'던전 설정 오류: {key} 누락'}
    
    # 레벨 제한 확인
    if player['레벨'] < dungeon['레벨_제한']:
        return {'success': False, 'message': f'레벨 {dungeon["레벨_제한"]} 이상만 입장 가능합니다.'}
    
    # 커스텀 던전 입장료 확인
    if dungeon.get('entry_fee', 0) > 0:
        entry_fee = dungeon['entry_fee']
        if player['돈'] < entry_fee:
            return {'success': False, 'message': f'입장료가 부족합니다. (필요: {entry_fee:,}원, 보유: {player["돈"]:,}원)'}
        # 입장료 차감
        player['돈'] -= entry_fee
    
    # 던전별 단어 로드 (카테고리에 맞는 단어 사용)
    words = load_words_by_source(
        dungeon.get('word_source', 'toeic'),
        category_filter=dungeon.get('category_filter'),
        difficulty_filter=dungeon.get('difficulty_filter')
    )
    if not words:
        # 커스텀 던전인데 사용자 단어가 없는 경우
        if dungeon_id == 'custom_user_words':
            return {'success': False, 'message': '등록된 단어가 없습니다. 단어 관리에서 단어를 먼저 등록해주세요.'}
        return {'success': False, 'message': '단어를 로드할 수 없습니다.'}
    
    # 던전 실행 상태 초기화 - 단어 순서 랜덤화
    random.shuffle(words)  # 단어 순서 랜덤화
    
    # 중복 제거 - 고유한 단어들만 선택
    unique_words = []
    seen_words = set()
    for word in words:
        word_key = word['단어']
        if word_key not in seen_words:
            unique_words.append(word)
            seen_words.add(word_key)
    
    # 실제 사용 가능한 단어 수에 맞춰 클리어 조건 조정
    actual_clear_condition = dungeon['clear_condition']
    # unique_words를 반복해서 word_queue 구성 (중복 없음)
    # 예: unique_words=[A, B, C], clear_condition=10 → [A, B, C, A, B, C, A, B, C, A]
    cycles_needed = (actual_clear_condition // len(unique_words)) + (1 if actual_clear_condition % len(unique_words) else 0)
    word_queue = (unique_words * cycles_needed)[:actual_clear_condition]
    
    # 간소화된 던전 실행 상태 (세션 용량 최적화)
    dungeon_run = {
        'dungeon_id': dungeon_id,
        'word_indices': list(range(len(word_queue))),  # 0, 1, 2, ...
        'current_word_index': 0,
        'current_word': None,
        'current_options': [],
        'current_rarity': None,
        'monster_id': None,
        'monster_hp': 0,
        'monster_progress': 0,
        'player_hp': player['체력'],  # 플레이어의 실제 체력 사용
        'cleared_words': 0,
        'total_words': len(word_queue),
        'actual_clear_condition': actual_clear_condition,  # 실제 클리어 조건 저장
        'word_source': dungeon.get('word_source', 'toeic'),  # 단어 카테고리 저장
        'wrong_questions': []  # 틀린 문제들 저장
    }
    
    # 첫 번째 몬스터 생성
    result = next_monster(dungeon_run, dungeon)
    if not result['success']:
        return result
        
    return {'success': True, 'dungeon_run': dungeon_run}

def init_wrong_questions_dungeon(player, wrong_questions, original_dungeon_id):
    """틀린 문제들만으로 던전 재시작"""
    if not wrong_questions:
        return {'success': False, 'message': '틀린 문제가 없습니다.'}
    
    original_dungeon = get_dungeon_by_id(original_dungeon_id)
    if not original_dungeon:
        return {'success': False, 'message': '원본 던전을 찾을 수 없습니다.'}
    
    # 레벨 제한 확인
    if player['레벨'] < original_dungeon['레벨_제한']:
        return {'success': False, 'message': f'레벨 {original_dungeon["레벨_제한"]} 이상만 입장 가능합니다.'}
    
    # 틀린 문제들만으로 던전 실행 상태 초기화
    dungeon_run = {
        'dungeon_id': f"wrong_{original_dungeon_id}",
        'wrong_questions_mode': True,
        'original_dungeon_id': original_dungeon_id,
        'wrong_questions_list': wrong_questions.copy(),
        'current_wrong_index': 0,
        'current_word': None,
        'current_options': [],
        'current_rarity': '레어',  # 틀린 문제 복습은 기본 등급
        'monster_id': None,
        'monster_hp': 1,  # 복습용이므로 낮은 체력
        'monster_progress': 0,
        'player_hp': player['체력'],
        'cleared_words': 0,
        'total_words': len(wrong_questions),
        'actual_clear_condition': len(wrong_questions),
        'word_source': original_dungeon.get('word_source', 'toeic'),
        'wrong_questions': []  # 새로운 틀린 문제들 저장
    }
    
    # 첫 번째 틀린 문제 설정
    result = next_wrong_question(dungeon_run)
    if not result['success']:
        return result
        
    return {'success': True, 'dungeon_run': dungeon_run}

def next_wrong_question(dungeon_run):
    """다음 틀린 문제 설정"""
    # 인덱스가 범위를 벗어났는지 확인
    if dungeon_run['current_wrong_index'] >= len(dungeon_run['wrong_questions_list']):
        return {'success': False, 'message': '모든 틀린 문제를 완료했습니다!'}
    
    # 현재 틀린 문제 가져오기
    wrong_q = dungeon_run['wrong_questions_list'][dungeon_run['current_wrong_index']]
    
    # 문제 설정
    dungeon_run['current_word'] = wrong_q['word']
    dungeon_run['current_options'] = wrong_q['options']
    dungeon_run['correct_answer_index'] = wrong_q['correct_index']
    
    # 몬스터 상태 초기화
    dungeon_run['monster_progress'] = 0
    dungeon_run['monster_hp'] = 1  # 틀린 문제 복습용 낮은 체력
    
    # 몬스터 ID 생성
    monster_seed = f"wrong_{wrong_q['word']['단어']}"
    monster_id = hashlib.md5(monster_seed.encode()).hexdigest()[:8]
    dungeon_run['monster_id'] = monster_id
    
    # 힌트 상태 초기화
    dungeon_run.pop('hint_used', None)
    dungeon_run.pop('hint_options', None)
    dungeon_run.pop('hint_correct_index', None)
    
    return {'success': True, 'message': '틀린 문제가 준비되었습니다.'}

def next_monster(dungeon_run, dungeon):
    """다음 몬스터 생성"""
    # 클리어한 몬스터 수가 목표에 도달했는지 확인
    if dungeon_run['cleared_words'] >= dungeon_run['actual_clear_condition']:
        return {'success': False, 'message': '던전을 완료했습니다!'}
    
    # 현재 단어 인덱스가 범위를 벗어났는지 확인
    if dungeon_run['current_word_index'] >= len(dungeon_run['word_indices']):
        # 클리어 조건을 다 채웠는지 확인
        if dungeon_run['cleared_words'] >= dungeon_run['actual_clear_condition']:
            return {'success': False, 'message': '던전을 완료했습니다!'}
        
        # 문제가 다 떨어졌지만 클리어해야 할 몬스터가 남은 경우, 사이클 재시작
        dungeon = get_dungeon_by_id(dungeon_run['dungeon_id'])
        words = load_words_by_source(
            dungeon_run.get('word_source', 'toeic'),
            category_filter=dungeon.get('category_filter') if dungeon else None,
            difficulty_filter=dungeon.get('difficulty_filter') if dungeon else None
        )
        random.shuffle(words)
        
        # 중복 제거
        unique_words = []
        seen_words = set()
        for word in words:
            word_key = word['단어']
            if word_key not in seen_words:
                unique_words.append(word)
                seen_words.add(word_key)
        
        # 사이클 재시작 - unique_words를 반복 사용
        remaining_clears = dungeon_run['actual_clear_condition'] - dungeon_run['cleared_words']
        cycles_needed = (remaining_clears // len(unique_words)) + (1 if remaining_clears % len(unique_words) else 0)
        word_queue = (unique_words * cycles_needed)[:remaining_clears]
        
        dungeon_run['word_indices'] = list(range(len(word_queue)))
        dungeon_run['current_word_index'] = 0
        dungeon_run['flash_message'] = '모든 문제를 풀었습니다! 새로운 사이클을 시작합니다.'
    
    # 현재 단어 설정
    dungeon = get_dungeon_by_id(dungeon_run['dungeon_id']) if 'dungeon_id' in dungeon_run else None
    words = load_words_by_source(
        dungeon_run.get('word_source', 'toeic'),
        category_filter=dungeon.get('category_filter') if dungeon else None,
        difficulty_filter=dungeon.get('difficulty_filter') if dungeon else None
    )
    
    # 중복 제거
    unique_words = []
    seen_words = set()
    for word in words:
        word_key = word['단어']
        if word_key not in seen_words:
            unique_words.append(word)
            seen_words.add(word_key)
    
    # unique_words를 반복해서 word_queue 구성
    actual_clear = dungeon_run['actual_clear_condition']
    cycles_needed = (actual_clear // len(unique_words)) + (1 if actual_clear % len(unique_words) else 0)
    word_queue = (unique_words * cycles_needed)[:actual_clear]
    
    word_index = dungeon_run['word_indices'][dungeon_run['current_word_index']]
    current_word = word_queue[word_index]
    dungeon_run['current_word'] = current_word
    
    # 몬스터 등급 결정 (확률 기반)
    if not dungeon:
        dungeon = get_dungeon_by_id(dungeon_run['dungeon_id'])
    if not dungeon:  # 던전을 찾을 수 없는 경우 기본값 사용
        rarity_dist = {'레어': 0.6, '에픽': 0.3, '유니크': 0.1}
    else:
        rarity_dist = dungeon['rarity_distribution']
    rand = random.random()
    cumulative = 0
    selected_rarity = '레어'  # 기본값
    
    for rarity, prob in rarity_dist.items():
        cumulative += prob
        if rand <= cumulative:
            selected_rarity = rarity
            break
    
    dungeon_run['current_rarity'] = selected_rarity
    
    # 등급별 몬스터 ID 랜덤 선택
    monsters_in_rarity = get_monsters_by_rarity(selected_rarity)
    if monsters_in_rarity:
        monster_id = random.choice(monsters_in_rarity)
    else:
        # 폴백: 레어 몬스터 선택
        monster_id = random.choice(get_monsters_by_rarity('레어'))
    
    dungeon_run['monster_id'] = monster_id
    
    # 몬스터 데이터 가져오기
    monster_data = get_monster_by_id(monster_id)
    
    # 몬스터 이미지 설정
    if monster_data:
        dungeon_run['monster_image'] = monster_data.get('이미지', '')
    else:
        dungeon_run['monster_image'] = ''
    
    # 몬스터 HP 설정
    dungeon_run['monster_hp'] = monster_rarities[selected_rarity]['required_correct']
    dungeon_run['monster_progress'] = 0
    
    # 4지선다 문제 생성
    result = build_question(dungeon_run, dungeon)
    
    # 힌트 상태 초기화
    dungeon_run.pop('hint_used', None)
    dungeon_run.pop('hint_options', None)
    dungeon_run.pop('hint_correct_index', None)
    
    return result

def build_question(dungeon_run, dungeon):
    """4지선다 문제 생성"""
    current_word = dungeon_run['current_word']
    correct_answer = current_word['뜻']
    
    # 같은 카테고리 단어에서 오답 생성
    all_words = load_words_by_source(
        dungeon.get('word_source', 'toeic') if dungeon else 'toeic',
        category_filter=dungeon.get('category_filter') if dungeon else None,
        difficulty_filter=dungeon.get('difficulty_filter') if dungeon else None
    )
    wrong_options = []
    
    # 정답과 다른 뜻들 중에서 3개 랜덤 선택
    other_meanings = [word['뜻'] for word in all_words if word['뜻'] != correct_answer]
    if len(other_meanings) >= 3:
        wrong_options = random.sample(other_meanings, 3)
    else:
        # 단어가 부족하면 기존 방식 사용
        for word in all_words:
            if word['뜻'] != correct_answer and len(wrong_options) < 3:
                wrong_options.append(word['뜻'])
    
    # 3개가 안 되면 기본 오답들로 채움
    default_wrong = ['잘못된 답', '다른 뜻', '오답입니다']
    while len(wrong_options) < 3:
        for default in default_wrong:
            if default not in wrong_options and len(wrong_options) < 3:
                wrong_options.append(default)
    
    # 선택지 생성 (정답 + 오답 3개)
    options = [correct_answer] + wrong_options[:3]
    random.shuffle(options)
    
    # 정답 인덱스 찾기
    correct_index = options.index(correct_answer)
    
    dungeon_run['current_options'] = options
    dungeon_run['correct_answer_index'] = correct_index
    
    return {'success': True, 'message': '문제가 생성되었습니다.'}

def answer_dungeon(player, dungeon_run, choice):
    """던전 답변 처리"""
    if choice == dungeon_run['correct_answer_index']:
        # 정답 - 기본 피해 1 + 무기 추가 피해 계산
        base_damage = 1
        weapon_damage = get_weapon_damage(player)
        total_damage = base_damage + weapon_damage
        
        dungeon_run['monster_progress'] += total_damage
        
        if weapon_damage > 0:
            weapon_name = player.get('장착된_무기', '')
            result_msg = f"정답! {weapon_name}으로 몬스터에게 {total_damage} 피해를 입혔습니다."
        else:
            result_msg = "정답! 몬스터에게 피해를 입혔습니다."
        
        # 몬스터 처치 확인
        if dungeon_run['monster_progress'] >= dungeon_run['monster_hp']:
            # 몬스터 처치
            rarity = dungeon_run['current_rarity']
            capture_rate = monster_rarities[rarity]['capture_rate']
            
            if random.random() < capture_rate:
                # 몬스터 포획 성공
                is_new_monster = update_compendium(player, dungeon_run)
                if is_new_monster:
                    result_msg += f" {rarity} 몬스터를 처치하고 새로운 몬스터를 도감에 추가했습니다!"
                else:
                    result_msg += f" {rarity} 몬스터를 처치하고 도감에 등록했습니다!"
            else:
                result_msg += f" {rarity} 몬스터를 처치했지만 도감 등록에 실패했습니다."
            
            # 처치한 단어 수 및 인덱스 증가
            dungeon_run['cleared_words'] += 1
            
            # 사용한 단어 사이클에 추가 (중복 방지용)
            if not dungeon_run.get('wrong_questions_mode'):
                if 'used_word_cycle' not in dungeon_run:
                    dungeon_run['used_word_cycle'] = []
                current_word_text = dungeon_run['current_word']['단어']
                if current_word_text not in dungeon_run['used_word_cycle']:
                    dungeon_run['used_word_cycle'].append(current_word_text)
            
            # 인덱스 증가
            if dungeon_run.get('wrong_questions_mode'):
                dungeon_run['current_wrong_index'] += 1
            else:
                dungeon_run['current_word_index'] += 1
            
            return {'success': True, 'correct': True, 'monster_defeated': True, 'game_over': False, 'message': result_msg}
        else:
            # 몬스터가 살아있으면 새로운 문제 생성
            progress = dungeon_run['monster_progress']
            max_hp = dungeon_run['monster_hp']
            result_msg += f" ({progress}/{max_hp})"
            
            # 다음 문제 준비 - 다른 단어로 새로운 문제 생성
            build_next_question(dungeon_run)
            
            return {'success': True, 'correct': True, 'monster_defeated': False, 'game_over': False, 'message': result_msg}
    else:
        # 오답 - 플레이어 실제 체력과 던전 체력 모두 감소
        dungeon_run['player_hp'] -= 1
        player['체력'] = max(0, player['체력'] - 1)  # 실제 체력도 감소
        
        # 틀린 문제 저장 (일반 모드에서만)
        if not dungeon_run.get('wrong_questions_mode'):
            if 'wrong_questions' not in dungeon_run:
                dungeon_run['wrong_questions'] = []
            
            wrong_question = {
                'word': dungeon_run['current_word'],
                'options': dungeon_run['current_options'],
                'correct_index': dungeon_run['correct_answer_index'],
                'player_choice': choice
            }
            dungeon_run['wrong_questions'].append(wrong_question)
        
        if dungeon_run['player_hp'] <= 0:
            return {'success': True, 'correct': False, 'game_over': True, 'message': '체력이 0이 되어 던전에서 퇴장됩니다.'}
        else:
            return {'success': True, 'correct': False, 'game_over': False, 'message': f'오답! 체력이 1 감소했습니다. (남은 체력: {dungeon_run["player_hp"]})'}

def build_next_question(dungeon_run):
    """같은 몬스터에 대해 다음 문제 생성"""
    # 같은 카테고리에서 현재 단어와 다른 단어를 랜덤하게 선택
    dungeon = get_dungeon_by_id(dungeon_run['dungeon_id']) if 'dungeon_id' in dungeon_run else None
    words = load_words_by_source(
        dungeon_run.get('word_source', 'toeic'),
        category_filter=dungeon.get('category_filter') if dungeon else None,
        difficulty_filter=dungeon.get('difficulty_filter') if dungeon else None
    )
    current_word_text = dungeon_run['current_word']['단어']
    
    # 현재 단어와 다른 단어들 중에서 랜덤 선택
    available_words = [word for word in words if word['단어'] != current_word_text]
    if available_words:
        new_word = random.choice(available_words)
        dungeon_run['current_word'] = new_word
        
        # 새로운 문제 생성
        result = build_question(dungeon_run, None)
        
        # 힌트 상태 초기화
        dungeon_run.pop('hint_used', None)
        dungeon_run.pop('hint_options', None)
        dungeon_run.pop('hint_correct_index', None)
        
        return result
    else:
        # 사용 가능한 다른 단어가 없으면 기존 문제 재생성
        result = build_question(dungeon_run, None)
        
        # 힌트 상태 초기화
        dungeon_run.pop('hint_used', None)
        dungeon_run.pop('hint_options', None)
        dungeon_run.pop('hint_correct_index', None)
        
        return result

def get_monster_stats(monster_id):
    """몬스터 고유 스탯 생성 (몬스터 ID 기반)"""
    monster_data = get_monster_by_id(monster_id)
    if not monster_data:
        return {'공격력': 5, '체력': 20}
    
    attack_range = monster_data['공격력']
    hp_range = monster_data['체력']
    
    return {
        '공격력': random.randint(attack_range[0], attack_range[1]),
        '체력': random.randint(hp_range[0], hp_range[1])
    }

def update_compendium(player, dungeon_run):
    """몬스터 도감 업데이트"""
    try:
        # 플레이어 도감 초기화 (없다면)
        if '도감' not in player:
            player['도감'] = {}
            
        monster_id = dungeon_run['monster_id']
        rarity = dungeon_run['current_rarity']
        
        # 몬스터 데이터 가져오기
        monster_data = get_monster_by_id(monster_id)
        if not monster_data:
            return False
        
        monster_name = monster_data['이름']
        monster_image = monster_data.get('이미지', '')
        monster_stats = get_monster_stats(monster_id)
        
        is_new_monster = False
        if monster_id not in player['도감']:
            player['도감'][monster_id] = {
                '이름': monster_name,
                '등급': rarity,
                '이미지': monster_image,
                '최초처치일': datetime.now().isoformat(),
                '처치수': 1,
                '포획됨': True,
                '공격력': monster_stats['공격력'],
                '체력': monster_stats['체력']
            }
            is_new_monster = True
        else:
            player['도감'][monster_id]['처치수'] += 1
        
        return is_new_monster
    except Exception as e:
        print(f"도감 업데이트 오류: {e}")
        return False

def check_dungeon_clear(dungeon_run):
    """던전 클리어 확인"""
    return dungeon_run['cleared_words'] >= dungeon_run['actual_clear_condition']

def get_dungeon_reward_info(difficulty):
    """난이도별 보상 정보 반환"""
    reward_table = {
        '쉬움': {'min_money': 5000, 'max_money': 20000, 'min_exp': 1000, 'max_exp': 2000},
        '보통': {'min_money': 20000, 'max_money': 50000, 'min_exp': 2000, 'max_exp': 4000},
        '어려움': {'min_money': 50000, 'max_money': 150000, 'min_exp': 4000, 'max_exp': 8000},
        '매우 어려움': {'min_money': 150000, 'max_money': 400000, 'min_exp': 8000, 'max_exp': 15000},
        '매우어려움': {'min_money': 150000, 'max_money': 400000, 'min_exp': 8000, 'max_exp': 15000},
    }
    return reward_table.get(difficulty, reward_table['보통'])

def apply_dungeon_clear_reward(player, dungeon):
    """던전 클리어 보상 적용"""
    if not dungeon:
        return {'success': False, 'message': '던전 정보가 없습니다.'}
    
    difficulty = dungeon.get('난이도', '보통')
    
    # 난이도별 보상 설정
    reward_table = {
        '쉬움': {'min_money': 5000, 'max_money': 20000, 'min_exp': 1000, 'max_exp': 2000},
        '보통': {'min_money': 20000, 'max_money': 50000, 'min_exp': 2000, 'max_exp': 4000},
        '어려움': {'min_money': 50000, 'max_money': 150000, 'min_exp': 4000, 'max_exp': 8000},
        '매우 어려움': {'min_money': 150000, 'max_money': 400000, 'min_exp': 8000, 'max_exp': 15000},
        '매우어려움': {'min_money': 150000, 'max_money': 400000, 'min_exp': 8000, 'max_exp': 15000},
    }
    
    # 커스텀 던전 보상 (이미 정의되어 있는 경우)
    if difficulty == '커스텀' and dungeon.get('reward_money'):
        reward_money = dungeon.get('reward_money', 0)
        reward_exp = int(50 * (dungeon.get('reward_exp_multiplier', 1.0)))
    else:
        # 난이도별 기본 보상
        rewards = reward_table.get(difficulty, reward_table['보통'])
        reward_money = random.randint(rewards['min_money'], rewards['max_money'])
        reward_exp = random.randint(rewards['min_exp'], rewards['max_exp'])
    
    # 보상 지급
    player['돈'] += reward_money
    player['경험치'] += reward_exp
    
    # 레벨업 확인
    level_ups = check_level_up(player)
    
    message = f"🎁 클리어 보상: {reward_money:,}원 + 경험치 {reward_exp}"
    if level_ups > 0:
        message += f" | 레벨업 {level_ups}회! (현재 레벨: {player['레벨']})"
    
    return {
        'success': True,
        'message': message,
        'reward_money': reward_money,
        'reward_exp': reward_exp,
        'level_ups': level_ups
    }

def get_safe_percentage(current, maximum):
    """안전한 퍼센트 계산 (division by zero 방지)"""
    if maximum <= 0:
        return 0
    return min(100, max(0, (current / maximum) * 100))

def use_dungeon_item(player, item_name, dungeon_run=None):
    """던전 아이템 사용"""
    if '던전_인벤토리' not in player or item_name not in player['던전_인벤토리']:
        return {'success': False, 'message': '해당 아이템이 없습니다.'}
    
    if player['던전_인벤토리'][item_name] <= 0:
        return {'success': False, 'message': '해당 아이템이 없습니다.'}
    
    # 아이템 사용
    player['던전_인벤토리'][item_name] -= 1
    if player['던전_인벤토리'][item_name] == 0:
        del player['던전_인벤토리'][item_name]
    
    # 아이템 효과 적용
    shop_items = get_shop_items()
    item_data = None
    for item in shop_items:
        if item['이름'] == item_name:
            item_data = item
            break
    
    if not item_data:
        return {'success': False, 'message': '아이템 정보를 찾을 수 없습니다.'}
    
    effects = item_data['효과']
    result_message = f'{item_name}을(를) 사용했습니다. '
    
    for effect, value in effects.items():
        if effect == '던전 체력' and dungeon_run:
            # 던전 체력 회복 - 플레이어 실제 체력도 함께 회복
            max_health = 10  # 플레이어 최대 체력
            old_hp = dungeon_run['player_hp']
            heal_amount = min(value, max_health - old_hp)
            dungeon_run['player_hp'] = min(dungeon_run['player_hp'] + value, max_health)
            player['체력'] = min(player['체력'] + heal_amount, max_health)
            actual_heal = dungeon_run['player_hp'] - old_hp
            result_message += f'체력이 {actual_heal} 회복되었습니다. '
        elif effect == '힌트 사용' and dungeon_run:
            # 힌트 사용 횟수 추가
            if '던전_버프' not in player:
                player['던전_버프'] = {}
            player['던전_버프']['힌트 사용'] = player['던전_버프'].get('힌트 사용', 0) + value
            result_message += f'힌트를 {value}번 사용할 수 있습니다. '
        elif effect == '문제 스킵' and dungeon_run:
            # 문제 스킵 횟수 추가  
            if '던전_버프' not in player:
                player['던전_버프'] = {}
            player['던전_버프']['문제 스킵'] = player['던전_버프'].get('문제 스킵', 0) + value
            result_message += f'문제를 {value}개 스킵할 수 있습니다. '
        elif effect == '부활' and dungeon_run:
            # 부활 효과는 나중에 처리하기 위해 플레이어에 플래그 저장
            if '던전_버프' not in player:
                player['던전_버프'] = {}
            player['던전_버프']['부활'] = player['던전_버프'].get('부활', 0) + value
            result_message += '부활 효과가 적용되었습니다. '
        # 기타 효과들은 필요시 추가 구현
    
    return {'success': True, 'message': result_message.strip(), 'item': item_data}

# ============== 일일 표현 시스템 ==============

def get_daily_expressions():
    """일일 표현 - 20가지 회화 표현"""
    expressions = [
        {
            'expression': 'Break the ice',
            'example': 'Let me break the ice by introducing myself.',
            'examples': [
                'Let me break the ice by introducing myself.',
                'She broke the ice with a funny joke.',
                'Breaking the ice on your first day is important.'
            ],
            'meaning': '어색한 분위기를 깨뜨리다',
            'situation': '처음 만난 사람들과의 대화를 시작할 때',
            'tip': '얼음을 깨뜨린다는 의미에서 비롯된 관용구입니다.'
        },
        {
            'expression': 'Piece of cake',
            'example': 'This project is a piece of cake for me.',
            'examples': [
                'This project is a piece of cake for me.',
                'The exam was a piece of cake.',
                'Learning English is no piece of cake.'
            ],
            'meaning': '아주 쉬운 일',
            'situation': '어떤 일이 매우 간단하고 쉬울 때',
            'tip': '케이크 한 조각처럼 쉽다는 의미입니다.'
        },
        {
            'expression': 'Under the weather',
            'example': 'I am feeling under the weather today.',
            'examples': [
                'I am feeling under the weather today.',
                'My mom has been under the weather lately.',
                'He called in sick, saying he was under the weather.'
            ],
            'meaning': '기분이 좋지 않은, 몸이 안 좋은',
            'situation': '감기나 피로로 컨디션이 안 좋을 때',
            'tip': '날씨 아래에 있다는 의미에서 나온 표현입니다.'
        },
        {
            'expression': 'Cost an arm and a leg',
            'example': 'This vacation will cost us an arm and a leg.',
            'examples': [
                'This vacation will cost us an arm and a leg.',
                'That new car costs an arm and a leg.',
                'Tuition fees cost students an arm and a leg.'
            ],
            'meaning': '매우 비싼, 많은 비용이 드는',
            'situation': '가격이 매우 비싼 물건이나 서비스를 설명할 때',
            'tip': '팔과 다리를 써야 할 정도로 비싸다는 의미입니다.'
        },
        {
            'expression': 'Hit the books',
            'example': 'I need to hit the books for my exam.',
            'examples': [
                'I need to hit the books for my exam.',
                'We should hit the books tonight.',
                'Students hit the books before the finals.'
            ],
            'meaning': '열심히 공부하다',
            'situation': '시험 준비나 공부에 집중할 때',
            'tip': '책을 치면서 공부한다는 의미입니다.'
        },
        {
            'expression': 'On cloud nine',
            'example': 'She has been on cloud nine since she got engaged.',
            'examples': [
                'She has been on cloud nine since she got engaged.',
                'He is on cloud nine after winning the lottery.',
                'The couple has been on cloud nine since their wedding.'
            ],
            'meaning': '매우 행복한, 넋을 잃을 정도로 기쁜',
            'situation': '사랑에 빠지거나 매우 기쁠 때',
            'tip': '9번째 구름 위에 있을 정도로 행복하다는 뜻입니다.'
        },
        {
            'expression': 'It rains cats and dogs',
            'example': 'It is raining cats and dogs outside.',
            'examples': [
                'It is raining cats and dogs outside.',
                'When it rains cats and dogs, I stay indoors.',
                'Yesterday, it rained cats and dogs all day.'
            ],
            'meaning': '매우 심하게 내리다 (비가)',
            'situation': '비가 폭주할 때',
            'tip': '개와 고양이가 내린다는 과장된 표현입니다.'
        },
        {
            'expression': 'Go the extra mile',
            'example': 'She always goes the extra mile for her customers.',
            'examples': [
                'She always goes the extra mile for her customers.',
                'To succeed, you need to go the extra mile.',
                'The team went the extra mile to finish the project.'
            ],
            'meaning': '특별한 노력을 하다, 추가로 더 하다',
            'situation': '누군가가 기대 이상의 노력을 할 때',
            'tip': '한 마일을 더 간다는 뜻입니다.'
        },
        {
            'expression': 'No pain, no gain',
            'example': 'No pain, no gain. You have to work hard to succeed.',
            'examples': [
                'No pain, no gain. You have to work hard to succeed.',
                'Remember, no pain, no gain when working out.',
                'Success requires effort - no pain, no gain.'
            ],
            'meaning': '고생 없이 얻는 것 없다',
            'situation': '성공을 위해서는 노력이 필요하다고 말할 때',
            'tip': '성공의 철칙을 나타내는 표현입니다.'
        },
        {
            'expression': 'Better late than never',
            'example': 'I know I am late, but better late than never.',
            'examples': [
                'I know I am late, but better late than never.',
                'He arrived three hours late, but better late than never.',
                'Better late than never, I finally finished the book.'
            ],
            'meaning': '늦은 것이 안 하는 것보다 낫다',
            'situation': '늦게 도착하거나 늦게 시작할 때의 변명',
            'tip': '지각이나 지연을 정당화할 때 사용합니다.'
        },
        {
            'expression': 'Spill the beans',
            'example': 'I cannot spill the beans about the surprise party.',
            'examples': [
                'I cannot spill the beans about the surprise party.',
                'She accidentally spilled the beans about the secret.',
                'Do not spill the beans until the announcement.'
            ],
            'meaning': '비밀을 말하다, 중요한 정보를 누설하다',
            'situation': '누군가가 비밀을 말하려고 할 때',
            'tip': '콩을 쏟아서 비밀이 알려진다는 의미입니다.'
        },
        {
            'expression': 'Bite the bullet',
            'example': 'Sometimes you just have to bite the bullet.',
            'examples': [
                'Sometimes you just have to bite the bullet.',
                'She bit the bullet and quit her job.',
                'You have to bite the bullet and accept the consequences.'
            ],
            'meaning': '어려운 상황을 받아들이다, 최선을 다하다',
            'situation': '어쩔 수 없는 상황에 직면했을 때',
            'tip': '전쟁 중에 마취 없이 치료할 때 총알을 깨물었던 데서 비롯되었습니다.'
        },
        {
            'expression': 'See eye to eye',
            'example': 'We do not see eye to eye on this issue.',
            'examples': [
                'We do not see eye to eye on this issue.',
                'The two companies finally saw eye to eye on the deal.',
                'My parents and I see eye to eye about my future.'
            ],
            'meaning': '의견이 같다, 동의하다 (또는 그 반대)',
            'situation': '타인과 같은 의견을 가지고 있을 때',
            'tip': '같은 높이로 눈맞춘다는 뜻입니다.'
        },
        {
            'expression': 'Give someone a hand',
            'example': 'Can you give me a hand with this project?',
            'examples': [
                'Can you give me a hand with this project?',
                'I gave her a hand moving the furniture.',
                'Will you give me a hand finishing this work?'
            ],
            'meaning': '누군가를 도와주다',
            'situation': '다른 사람에게 도움을 청하거나 도와줄 때',
            'tip': '손을 주어서 도와준다는 의미입니다.'
        },
        {
            'expression': 'Keep your fingers crossed',
            'example': 'I am keeping my fingers crossed for your interview.',
            'examples': [
                'I am keeping my fingers crossed for your interview.',
                'Keep your fingers crossed for good weather tomorrow.',
                'We are all keeping our fingers crossed for the test results.'
            ],
            'meaning': '행운을 빌다, 희망을 가지다',
            'situation': '누군가가 좋은 결과를 기원할 때',
            'tip': '손가락을 교차시키면 행운이 온다고 믿습니다.'
        },
        {
            'expression': 'Catch you later',
            'example': 'I have to go now. Catch you later!',
            'examples': [
                'I have to go now. Catch you later!',
                'Catch you later, I have an appointment.',
                'See you at the party. Catch you later!'
            ],
            'meaning': '나중에 봐, 인사',
            'situation': '누군가와 헤어질 때 인사하는 표현',
            'tip': '캐주얼한 작별 인사로 매우 자주 사용됩니다.'
        },
        {
            'expression': 'No worries',
            'example': 'I made a mistake. - No worries, it happens.',
            'examples': [
                'I made a mistake. - No worries, it happens.',
                'No worries, I will help you fix it.',
                'Sorry I am late. - No worries, take your time.'
            ],
            'meaning': '괜찮아, 걱정하지 마',
            'situation': '누군가를 안심시키거나 격려할 때',
            'tip': '걱정하지 말라는 매우 일반적인 표현입니다.'
        },
        {
            'expression': 'That is piece of cake',
            'example': 'The test was a piece of cake.',
            'examples': [
                'The test was a piece of cake.',
                'Building a website is a piece of cake for him.',
                'That problem is a piece of cake to solve.'
            ],
            'meaning': '매우 쉬운, 문제없는',
            'situation': '어떤 일이 쉬울 때 자신 있게 말할 때',
            'tip': '케이크 조각처럼 쉽다는 의미입니다.'
        },
        {
            'expression': 'Once in a blue moon',
            'example': 'I see him once in a blue moon.',
            'examples': [
                'I see him once in a blue moon.',
                'Once in a blue moon, I treat myself to something nice.',
                'We get together once in a blue moon.'
            ],
            'meaning': '매우 드물게, 거의 없이',
            'situation': '무언가가 거의 일어나지 않을 때',
            'tip': '파란 달은 매우 드물다는 데서 비롯되었습니다.'
        },
        {
            'expression': 'Get the ball rolling',
            'example': 'Let us get the ball rolling with this new project.',
            'examples': [
                'Let us get the ball rolling with this new project.',
                'We need to get the ball rolling on the proposal.',
                'I will get the ball rolling and send the email.'
            ],
            'meaning': '일을 시작하다, 시작하다',
            'situation': '새로운 프로젝트나 계획을 시작할 때',
            'tip': '공을 굴려서 시작한다는 의미입니다.'
        },
        {
            'expression': 'Speak of the devil',
            'example': 'Speak of the devil! There he comes!',
            'examples': [
                'Speak of the devil! There he comes!',
                'We were just talking about her. Speak of the devil!'
            ],
            'meaning': '얘기 나누던 사람이 나타났다',
            'situation': '우리가 얘기하던 사람이 때마침 나타났을 때',
            'tip': '악마라고 얘기하면 나타난다는 미신에서 나왔습니다.'
        },
        {
            'expression': 'Couldn\'t care less',
            'example': 'I couldn\'t care less about what others think.',
            'examples': [
                'I couldn\'t care less about what others think.',
                'He couldn\'t care less about the game result.'
            ],
            'meaning': '관심이 없다, 신경 안 쓴다',
            'situation': '어떤 것에 대해 전혀 관심이 없을 때',
            'tip': '이 표현은 매우 자주 사용되는 일상 표현입니다.'
        },
        {
            'expression': 'Hang in there',
            'example': 'Hang in there, you can do it!',
            'examples': [
                'Hang in there, you can do it!',
                'Things will get better. Just hang in there.'
            ],
            'meaning': '힘내, 계속해',
            'situation': '누군가를 격려하거나 응원할 때',
            'tip': '매우 긍정적이고 따뜻한 표현입니다.'
        },
        {
            'expression': 'Just a minute',
            'example': 'Wait, just a minute please!',
            'examples': [
                'Wait, just a minute please!',
                'Just a minute, I need to check something.'
            ],
            'meaning': '잠깐만, 잠시만',
            'situation': '누군가에게 잠깐 시간을 달라고 할 때',
            'tip': '매우 일상적인 표현입니다.'
        },
        {
            'expression': 'Let me know',
            'example': 'Let me know if you need anything.',
            'examples': [
                'Let me know if you need anything.',
                'Let me know what you think about this.'
            ],
            'meaning': '알려줘, 말해줘',
            'situation': '정보나 의견을 요청할 때',
            'tip': '매우 자주 쓰이는 표현입니다.'
        },
        {
            'expression': 'Long time no see',
            'example': 'Long time no see! How have you been?',
            'examples': [
                'Long time no see! How have you been?',
                'It has been ages. Long time no see, buddy!'
            ],
            'meaning': '오랜만이야, 오랜 시간 못 봤어',
            'situation': '오래전에 만난 사람을 다시 만났을 때',
            'tip': '친한 친구나 아는 사람을 만날 때 사용합니다.'
        },
        {
            'expression': 'By the way',
            'example': 'By the way, did you see the new movie?',
            'examples': [
                'By the way, did you see the new movie?',
                'Oh, by the way, I forgot to tell you something.'
            ],
            'meaning': '그런데, 참고로',
            'situation': '대화 중에 다른 주제를 꺼낼 때',
            'tip': '회화에서 매우 자주 사용됩니다.'
        },
        {
            'expression': 'How about you',
            'example': 'I like pizza. How about you?',
            'examples': [
                'I like pizza. How about you?',
                'I am going to the beach tomorrow. How about you?'
            ],
            'meaning': '넌 어때?, 넌 어떻게?',
            'situation': '상대방의 의견이나 계획을 묻을 때',
            'tip': '회화에서 정말 자주 사용되는 표현입니다.'
        },
        {
            'expression': 'I promise',
            'example': 'I promise I will be on time.',
            'examples': [
                'I promise I will be on time.',
                'I promise I won\'t tell anyone about this.'
            ],
            'meaning': '약속해, 약속할게',
            'situation': '어떤 것을 보장하거나 약속할 때',
            'tip': '신뢰를 나타내는 표현입니다.'
        },
        {
            'expression': 'That sounds great',
            'example': 'Let\'s go to the beach tomorrow. That sounds great!',
            'examples': [
                'Let\'s go to the beach tomorrow. That sounds great!',
                'I got a promotion! That sounds great!'
            ],
            'meaning': '좋은데?, 좋다',
            'situation': '누군가의 제안이나 좋은 소식에 동의할 때',
            'tip': '긍정적인 반응을 표현합니다.'
        },
        {
            'expression': 'That\'s right',
            'example': 'That\'s right, I forgot about it.',
            'examples': [
                'That\'s right, I forgot about it.',
                'That\'s right, the meeting is at 3 PM.'
            ],
            'meaning': '맞아, 그렇지',
            'situation': '상대의 말이나 지적에 동의할 때',
            'tip': '매우 자주 쓰이는 확인 표현입니다.'
        },
        {
            'expression': 'I completely agree',
            'example': 'I completely agree with you on this.',
            'examples': [
                'I completely agree with you on this.',
                'I completely agree, it\'s the best choice.'
            ],
            'meaning': '완전히 동의해',
            'situation': '상대의 의견에 전적으로 동의할 때',
            'tip': '강한 동의를 표현합니다.'
        },
        {
            'expression': 'Not really',
            'example': 'Do you like spicy food? Not really.',
            'examples': [
                'Do you like spicy food? Not really.',
                'Not really, I prefer something else.'
            ],
            'meaning': '별로 아니야, 아니야',
            'situation': '질문에 약하게 부정할 때',
            'tip': '부드러운 거절 표현입니다.'
        },
        {
            'expression': 'Sounds good',
            'example': 'Let\'s meet tomorrow at 10. Sounds good!',
            'examples': [
                'Let\'s meet tomorrow at 10. Sounds good!',
                'I\'ll send you the file. Sounds good.'
            ],
            'meaning': '좋아, 괜찮네',
            'situation': '제안이나 계획에 동의할 때',
            'tip': '긍정적이고 친근한 표현입니다.'
        },
        {
            'expression': 'Fair enough',
            'example': 'I understand, fair enough.',
            'examples': [
                'I understand, fair enough.',
                'That makes sense. Fair enough.'
            ],
            'meaning': '그럴 만해, 알겠어',
            'situation': '상대의 주장이 타당하다고 인정할 때',
            'tip': '이해와 수용을 표현합니다.'
        },
        {
            'expression': 'For sure',
            'example': 'I\'ll be there for sure.',
            'examples': [
                'I\'ll be there for sure.',
                'For sure, I won\'t forget.'
            ],
            'meaning': '확실해, 틀림없이',
            'situation': '확실한 약속이나 확인을 할 때',
            'tip': '강한 확신을 표현합니다.'
        },
        {
            'expression': 'Totally',
            'example': 'I totally understand what you mean.',
            'examples': [
                'I totally understand what you mean.',
                'That\'s totally fair.'
            ],
            'meaning': '완전해, 정말이야',
            'situation': '완전히 동의하거나 이해할 때',
            'tip': '강조와 동의를 함께 표현합니다.'
        },
        {
            'expression': 'Absolutely',
            'example': 'Can you help me? Absolutely!',
            'examples': [
                'Can you help me? Absolutely!',
                'Absolutely, no problem.'
            ],
            'meaning': '물론이지, 당연하지',
            'situation': '확실한 예를 강조할 때',
            'tip': '매우 긍정적인 표현입니다.'
        },
        {
            'expression': 'Good point',
            'example': 'That\'s a good point I hadn\'t considered.',
            'examples': [
                'That\'s a good point I hadn\'t considered.',
                'Good point, I agree.'
            ],
            'meaning': '좋은 지적이야, 맞는 말이네',
            'situation': '상대의 좋은 의견이나 지적을 인정할 때',
            'tip': '상대를 칭찬하면서 동의합니다.'
        },
        {
            'expression': 'I see',
            'example': 'I see what you mean now.',
            'examples': [
                'I see what you mean now.',
                'I see, thank you for explaining.'
            ],
            'meaning': '알겠어, 이해했어',
            'situation': '상대의 설명을 이해했을 때',
            'tip': '이해를 표현하는 기본 표현입니다.'
        },
        {
            'expression': 'Got it',
            'example': 'The meeting is at 2 PM. Got it!',
            'examples': [
                'The meeting is at 2 PM. Got it!',
                'Got it, I\'ll remember that.'
            ],
            'meaning': '알겠어, 됐어',
            'situation': '지시나 정보를 받을 때',
            'tip': '캐주얼하고 친근한 표현입니다.'
        },
        {
            'expression': 'Makes sense',
            'example': 'Oh, that makes sense now.',
            'examples': [
                'Oh, that makes sense now.',
                'Makes sense why you\'re busy.'
            ],
            'meaning': '말이 돼, 이해가 돼',
            'situation': '뭔가가 이해가 되거나 타당할 때',
            'tip': '자주 쓰이는 이해 표현입니다.'
        },
        {
            'expression': 'Exactly',
            'example': 'Exactly! That\'s what I was thinking.',
            'examples': [
                'Exactly! That\'s what I was thinking.',
                'Exactly right.'
            ],
            'meaning': '정확해, 맞아',
            'situation': '상대의 말이 자신의 생각과 정확히 일치할 때',
            'tip': '강한 동의를 표현합니다.'
        },
        {
            'expression': 'Definitely',
            'example': 'Will you come to the party? Definitely!',
            'examples': [
                'Will you come to the party? Definitely!',
                'Definitely, I\'m looking forward to it.'
            ],
            'meaning': '확실히, 틀림없어',
            'situation': '확실한 긍정을 할 때',
            'tip': '강한 확신과 확실성을 표현합니다.'
        },
        {
            'expression': 'Whatever',
            'example': 'You can choose, I\'m fine with whatever.',
            'examples': [
                'You can choose, I\'m fine with whatever.',
                'Whatever you think is best.'
            ],
            'meaning': '뭐 어때, 상관없어',
            'situation': '결정을 상대에게 맡기거나 무관심할 때',
            'tip': '중립적이거나 약간 무관심한 태도입니다.'
        },
        {
            'expression': 'Really?',
            'example': 'Really? I didn\'t know that!',
            'examples': [
                'Really? I didn\'t know that!',
                'Really? Tell me more.'
            ],
            'meaning': '정말?',
            'situation': '놀라움이나 의외성을 표현할 때',
            'tip': '호기심과 놀람을 나타냅니다.'
        },
        {
            'expression': 'You think so?',
            'example': 'You think so? I\'m not sure.',
            'examples': [
                'You think so? I\'m not sure.',
                'You think so? Maybe you\'re right.'
            ],
            'meaning': '그래?, 정말 그렇게 생각해?',
            'situation': '상대의 의견에 약간 의심스러울 때',
            'tip': '의문이나 회의를 표현합니다.'
        },
        {
            'expression': 'Why not?',
            'example': 'Let\'s go for a trip. Why not?',
            'examples': [
                'Let\'s go for a trip. Why not?',
                'Why not, it sounds fun.'
            ],
            'meaning': '왜 안 돼?, 좋지',
            'situation': '제안에 동의하거나 가능성을 열어둘 때',
            'tip': '긍정적인 수용을 표현합니다.'
        },
        {
            'expression': 'Sure thing',
            'example': 'Can you send me the file? Sure thing!',
            'examples': [
                'Can you send me the file? Sure thing!',
                'I\'ll get it for you. Sure thing.'
            ],
            'meaning': '물론이지, 좋아',
            'situation': '요청을 흔쾌히 수락할 때',
            'tip': '친근하고 긍정적인 표현입니다.'
        },
        {
            'expression': 'No way',
            'example': 'No way, that can\'t be true!',
            'examples': [
                'No way, that can\'t be true!',
                'No way, I don\'t believe it.'
            ],
            'meaning': '말도 안 돼, 아니야 그럴 리가',
            'situation': '믿을 수 없거나 동의할 수 없을 때',
            'tip': '강한 부정을 표현합니다.'
        },
        {
            'expression': 'I couldn\'t agree more',
            'example': 'This project is going to be amazing. I couldn\'t agree more.',
            'examples': [
                'This project is going to be amazing. I couldn\'t agree more.',
                'You\'re absolutely right. I couldn\'t agree more.'
            ],
            'meaning': '너도 같은 생각이야, 정말 그래',
            'situation': '상대방의 의견에 완전히 동의할 때',
            'tip': '강한 동의를 표현합니다.'
        },
        {
            'expression': 'That\'s a tough one',
            'example': 'Should I change my job? That\'s a tough one.',
            'examples': [
                'Should I change my job? That\'s a tough one.',
                'That\'s a tough one to answer.'
            ],
            'meaning': '그건 어려운 문제네, 고민이 많네',
            'situation': '어려운 상황이나 결정에 대해 말할 때',
            'tip': '동정과 이해를 표현합니다.'
        },
        {
            'expression': 'I\'m on board',
            'example': 'Let\'s try this new idea. I\'m on board.',
            'examples': [
                'Let\'s try this new idea. I\'m on board.',
                'I\'m on board with your plan.'
            ],
            'meaning': '난 동의해, 참여할게',
            'situation': '계획이나 제안에 동의할 때',
            'tip': '적극적인 참여 의지를 보입니다.'
        },
        {
            'expression': 'Let\'s call it a day',
            'example': 'We\'ve been working for hours. Let\'s call it a day.',
            'examples': [
                'We\'ve been working for hours. Let\'s call it a day.',
                'I\'m tired. Let\'s call it a day.'
            ],
            'meaning': '오늘은 여기서 마치자',
            'situation': '일을 멈추고 쉬기로 할 때',
            'tip': '자연스러운 종료를 제안합니다.'
        },
        {
            'expression': 'Bring something to the table',
            'example': 'You need to bring something to the table if you want to join our team.',
            'examples': [
                'You need to bring something to the table if you want to join our team.',
                'Everyone here brings something valuable to the table.'
            ],
            'meaning': '뭔가 가치있는 것을 제시하다',
            'situation': '기여하거나 도움을 줄 때',
            'tip': '가치있는 기여를 강조합니다.'
        },
        {
            'expression': 'On the same page',
            'example': 'Let\'s make sure we\'re on the same page about this project.',
            'examples': [
                'Let\'s make sure we\'re on the same page about this project.',
                'Are we on the same page here?'
            ],
            'meaning': '같은 생각을 하다, 같은 상태에 있다',
            'situation': '상호 이해나 의견 일치를 확인할 때',
            'tip': '공통 이해를 확인하는 표현입니다.'
        },
        {
            'expression': 'Ball is in your court',
            'example': 'I\'ve done my part. Ball is in your court now.',
            'examples': [
                'I\'ve done my part. Ball is in your court now.',
                'The ball is in your court. What\'s your decision?'
            ],
            'meaning': '이제 너차례야, 너의 차례',
            'situation': '책임이나 결정권이 상대방에게 있을 때',
            'tip': '다음 행동이 상대방의 책임임을 나타냅니다.'
        },
        {
            'expression': 'Take it with a grain of salt',
            'example': 'He said he\'ll finish tomorrow, but take it with a grain of salt.',
            'examples': [
                'He said he\'ll finish tomorrow, but take it with a grain of salt.',
                'Take what she says with a grain of salt.'
            ],
            'meaning': '그렇게까지 진지하게 받아들이지 말아, 반쯤만 믿어',
            'situation': '불확실한 정보나 말을 반쯤 의심할 때',
            'tip': '건전한 회의를 표현합니다.'
        },
        {
            'expression': 'Pull someone\'s leg',
            'example': 'You\'re pulling my leg! That can\'t be true.',
            'examples': [
                'You\'re pulling my leg! That can\'t be true.',
                'Are you pulling my leg?'
            ],
            'meaning': '누군가를 놀리다, 장난치다',
            'situation': '누군가가 농담이나 거짓말을 할 때',
            'tip': '친근한 놀림을 표현합니다.'
        },
        {
            'expression': 'Jump on the bandwagon',
            'example': 'Everyone\'s trying this new diet. Don\'t just jump on the bandwagon.',
            'examples': [
                'Everyone\'s trying this new diet. Don\'t just jump on the bandwagon.',
                'He jumped on the bandwagon without thinking.'
            ],
            'meaning': '유행을 따라가다, 남들이 하는 대로 하다',
            'situation': '무분별한 추종을 설명할 때',
            'tip': '대체로 부정적인 의미로 사용됩니다.'
        },
        {
            'expression': 'I\'m down',
            'example': 'Want to grab dinner later? I\'m down.',
            'examples': [
                'Want to grab dinner later? I\'m down.',
                'Are you up for a movie? I\'m down.'
            ],
            'meaning': '좋아, 할래, 참여할게',
            'situation': '제안이나 초대에 동의할 때',
            'tip': '캐주얼하고 친근한 표현입니다.'
        },
        {
            'expression': 'What\'s the deal?',
            'example': 'What\'s the deal? Why is everyone looking upset?',
            'examples': [
                'What\'s the deal? Why is everyone looking upset?',
                'What\'s the deal with him?'
            ],
            'meaning': '뭐 어떻게 된 일이야? 뭐가 문제야?',
            'situation': '이상하거나 설명이 필요한 상황에서',
            'tip': '호기심이나 의문을 표현합니다.'
        },
        {
            'expression': 'I\'m not buying it',
            'example': 'He says he was busy, but I\'m not buying it.',
            'examples': [
                'He says he was busy, but I\'m not buying it.',
                'I\'m not buying your excuse.'
            ],
            'meaning': '난 믿을 수 없어, 납득이 안 돼',
            'situation': '누군가의 말이나 설명을 의심할 때',
            'tip': '강한 의심을 표현합니다.'
        },
        {
            'expression': 'Tell me about it',
            'example': 'I\'m so tired! Tell me about it, I didn\'t sleep last night.',
            'examples': [
                'I\'m so tired! Tell me about it, I didn\'t sleep last night.',
                'Tell me about it, I know exactly how you feel.'
            ],
            'meaning': '알고 있어, 정말 그래, 나도 그래',
            'situation': '상대방의 감정이나 상황에 공감할 때',
            'tip': '공감과 동의를 표현합니다.'
        },
        {
            'expression': 'No brainer',
            'example': 'Should I take this job? No brainer, it\'s a great opportunity.',
            'examples': [
                'Should I take this job? No brainer, it\'s a great opportunity.',
                'That\'s a no brainer.'
            ],
            'meaning': '고민할 필요 없어, 당연한 것, 너무 뻔해',
            'situation': '매우 명백한 답이나 선택이 있을 때',
            'tip': '간단한 결정을 강조합니다.'
        },
        {
            'expression': 'You\'ve got to be kidding',
            'example': 'You\'ve got to be kidding! That\'s the best news I\'ve heard!',
            'examples': [
                'You\'ve got to be kidding! That\'s the best news I\'ve heard!',
                'You\'ve got to be kidding me!'
            ],
            'meaning': '농담하지 마, 진짜야? 말도 안 돼',
            'situation': '놀라거나 믿기 어려운 상황에서',
            'tip': '강한 놀라움을 표현합니다.'
        },
        {
            'expression': 'I\'m swamped',
            'example': 'Can you help me? Sorry, I\'m swamped right now.',
            'examples': [
                'Can you help me? Sorry, I\'m swamped right now.',
                'I\'m swamped with work.'
            ],
            'meaning': '난 바빠, 많은 일로 바빠',
            'situation': '매우 바쁜 상태를 설명할 때',
            'tip': '업무 과다를 표현합니다.'
        },
        {
            'expression': 'Rain check',
            'example': 'I can\'t make it today. Can we take a rain check?',
            'examples': [
                'I can\'t make it today. Can we take a rain check?',
                'Let\'s take a rain check on that.'
            ],
            'meaning': '다음에 하자, 연기하자',
            'situation': '약속을 나중으로 미룰 때',
            'tip': '예의바르게 연기를 제안합니다.'
        },
        {
            'expression': 'What\'s up?',
            'example': 'Hey, what\'s up? How have you been?',
            'examples': [
                'Hey, what\'s up? How have you been?',
                'What\'s up with you?'
            ],
            'meaning': '뭐해? 뭐 어때? 안녕?',
            'situation': '인사할 때 또는 상태를 묻을 때',
            'tip': '매우 캐주얼한 인사입니다.'
        },
        {
            'expression': 'Hold up',
            'example': 'Hold up, I need to ask you something.',
            'examples': [
                'Hold up, I need to ask you something.',
                'Hold up, wait a minute.'
            ],
            'meaning': '잠깐, 기다려, 멈춰',
            'situation': '누군가의 말을 중단시킬 때',
            'tip': '주의를 끌기 위한 표현입니다.'
        },
        {
            'expression': 'My bad',
            'example': 'I forgot to call you. My bad!',
            'examples': [
                'I forgot to call you. My bad!',
                'My bad, I\'m sorry.'
            ],
            'meaning': '내 잘못이야, 미안해',
            'situation': '실수를 인정할 때',
            'tip': '캐주얼한 사과 표현입니다.'
        },
        {
            'expression': 'Lighten up',
            'example': 'You\'re too serious. Lighten up and have some fun!',
            'examples': [
                'You\'re too serious. Lighten up and have some fun!',
                'Lighten up, it\'s just a joke.'
            ],
            'meaning': '너무 심각하지 마, 편해져',
            'situation': '누군가가 너무 진지할 때',
            'tip': '친근한 충고입니다.'
        },
        {
            'expression': 'I\'m all ears',
            'example': 'I have something important to tell you. I\'m all ears.',
            'examples': [
                'I have something important to tell you. I\'m all ears.',
                'Go ahead, I\'m all ears.'
            ],
            'meaning': '다 들을게, 말해봐',
            'situation': '누군가의 말을 들을 준비가 되어 있을 때',
            'tip': '적극적인 관심을 표현합니다.'
        },
        {
            'expression': 'Strike while the iron is hot',
            'example': 'You should apply for that job now. Strike while the iron is hot.',
            'examples': [
                'You should apply for that job now. Strike while the iron is hot.',
                'Strike while the iron is hot!'
            ],
            'meaning': '기회를 놓치지 마, 지금이 기회야',
            'situation': '좋은 기회를 놓치지 말 때',
            'tip': '시간의 중요성을 강조합니다.'
        },
        {
            'expression': 'You nailed it',
            'example': 'That presentation was perfect! You nailed it!',
            'examples': [
                'That presentation was perfect! You nailed it!',
                'You nailed it on the first try.'
            ],
            'meaning': '완벽해, 잘했어, 멋있어',
            'situation': '누군가가 잘했을 때 칭찬할 때',
            'tip': '강한 칭찬을 표현합니다.'
        },
        {
            'expression': 'Give me a break',
            'example': 'You\'re telling me you didn\'t know? Give me a break!',
            'examples': [
                'You\'re telling me you didn\'t know? Give me a break!',
                'Give me a break, that\'s not fair.'
            ],
            'meaning': '농담하지 마, 말도 안 돼',
            'situation': '상대의 말이나 행동이 황당할 때',
            'tip': '불신이나 불만을 표현합니다.'
        },
        {
            'expression': 'I\'m game',
            'example': 'Want to play football? I\'m game.',
            'examples': [
                'Want to play football? I\'m game.',
                'Let\'s do it. I\'m game.'
            ],
            'meaning': '할래, 참여할게, 좋아',
            'situation': '제안을 기꺼이 수락할 때',
            'tip': '"I\'m down"과 유사한 캐주얼한 표현입니다.'
        },
        {
            'expression': 'Cut to the chase',
            'example': 'I don\'t have much time. Cut to the chase please.',
            'examples': [
                'I don\'t have much time. Cut to the chase please.',
                'Cut to the chase, what do you want?'
            ],
            'meaning': '핵심만 말해, 말 좀 줄여',
            'situation': '불필요한 설명을 피하고 요점만 말할 때',
            'tip': '직설적인 표현입니다.'
        },
        {
            'expression': 'Wrap it up',
            'example': 'We need to wrap it up. The meeting ends in 5 minutes.',
            'examples': [
                'We need to wrap it up. The meeting ends in 5 minutes.',
                'Let\'s wrap it up and go home.'
            ],
            'meaning': '마무리해, 정리해',
            'situation': '일이나 회의를 마칠 때',
            'tip': '자연스러운 종료를 제안합니다.'
        },
        {
            'expression': 'Don\'t worry about it',
            'example': 'I\'m sorry for the mistake. Don\'t worry about it.',
            'examples': [
                'I\'m sorry for the mistake. Don\'t worry about it.',
                'Don\'t worry about it, everything will be fine.'
            ],
            'meaning': '괜찮아, 신경 쓰지 마, 괜찮아요',
            'situation': '상대방을 위로하거나 안심시킬 때',
            'tip': '따뜻한 위로와 안심을 표현합니다.'
        },
        {
            'expression': 'All in a day\'s work',
            'example': 'Fixing bugs all day? That\'s all in a day\'s work for a programmer.',
            'examples': [
                'Fixing bugs all day? That\'s all in a day\'s work for a programmer.',
                'Dealing with customer complaints is all in a day\'s work.'
            ],
            'meaning': '흔한 일이야, 일상적이야',
            'situation': '어려워 보이지만 사실 일상적인 일을 말할 때',
            'tip': '담담한 태도를 표현합니다.'
        },
        {
            'expression': 'At the end of the day',
            'example': 'We had some problems, but at the end of the day, we finished the project.',
            'examples': [
                'We had some problems, but at the end of the day, we finished the project.',
                'At the end of the day, it\'s about what matters most to you.'
            ],
            'meaning': '결국, 최종적으로, 궁극적으로',
            'situation': '결론을 짓거나 본질을 강조할 때',
            'tip': '자주 쓰이는 표현입니다.'
        },
        {
            'expression': 'Back to the drawing board',
            'example': 'This design doesn\'t work. Back to the drawing board.',
            'examples': [
                'This design doesn\'t work. Back to the drawing board.',
                'The first plan failed, so it\'s back to the drawing board.'
            ],
            'meaning': '다시 시작해야 한다, 처음부터 다시',
            'situation': '계획이 실패했을 때',
            'tip': '새로 시작해야 할 때 사용합니다.'
        },
        {
            'expression': 'Beat around the bush',
            'example': 'Stop beating around the bush and tell me the truth!',
            'examples': [
                'Stop beating around the bush and tell me the truth!',
                'Don\'t beat around the bush.'
            ],
            'meaning': '주변 이야기를 하다, 요점을 피하다',
            'situation': '직접 말하지 않고 돌려 말할 때',
            'tip': '비판적인 표현입니다.'
        },
        {
            'expression': 'Been there, done that',
            'example': 'You\'re worried? Don\'t be, I\'ve been there, done that.',
            'examples': [
                'You\'re worried? Don\'t be, I\'ve been there, done that.',
                'Been there, done that before.'
            ],
            'meaning': '나도 해본 거야, 알고 있어',
            'situation': '경험이 있음을 나타낼 때',
            'tip': '자신감 있는 표현입니다.'
        },
        {
            'expression': 'Best of both worlds',
            'example': 'Working from home gives you the best of both worlds.',
            'examples': [
                'Working from home gives you the best of both worlds.',
                'This car is the best of both worlds: fast and economical.'
            ],
            'meaning': '둘 다의 장점을 가지다',
            'situation': '두 가지 좋은 것을 모두 누릴 때',
            'tip': '긍정적인 상황을 표현합니다.'
        },
        {
            'expression': 'Between a rock and a hard place',
            'example': 'I\'m between a rock and a hard place. I don\'t know what to do.',
            'examples': [
                'I\'m between a rock and a hard place. I don\'t know what to do.',
                'He was between a rock and a hard place.'
            ],
            'meaning': '진퇴양난이다, 어려운 선택을 강요받다',
            'situation': '두 가지 어려운 선택 중 하나를 해야 할 때',
            'tip': '어려운 상황을 표현합니다.'
        },
        {
            'expression': 'Bet on it',
            'example': 'Will he come? You can bet on it!',
            'examples': [
                'Will he come? You can bet on it!',
                'You can bet on it, I\'m sure.'
            ],
            'meaning': '그거 확실해, 걸어, 가능해',
            'situation': '무언가가 확실함을 강조할 때',
            'tip': '확신을 표현합니다.'
        },
        {
            'expression': 'Better luck next time',
            'example': 'Sorry you didn\'t win. Better luck next time!',
            'examples': [
                'Sorry you didn\'t win. Better luck next time!',
                'You\'ll do better next time.'
            ],
            'meaning': '다음엔 잘될 거야, 파이팅',
            'situation': '누군가가 실패했을 때 격려할 때',
            'tip': '친근한 위로입니다.'
        },
        {
            'expression': 'Beyond a shadow of a doubt',
            'example': 'He\'s guilty beyond a shadow of a doubt.',
            'examples': [
                'He\'s guilty beyond a shadow of a doubt.',
                'I know beyond a shadow of a doubt that it\'s true.'
            ],
            'meaning': '의심의 여지 없이, 확실히',
            'situation': '확실한 사실을 강조할 때',
            'tip': '법적 표현처럼 들립니다.'
        },
        {
            'expression': 'Bite off more than you can chew',
            'example': 'Don\'t bite off more than you can chew. Take it slowly.',
            'examples': [
                'Don\'t bite off more than you can chew. Take it slowly.',
                'He bit off more than he could chew.'
            ],
            'meaning': '과욕을 부리다, 감당할 수 없는 것을 하려 하다',
            'situation': '너무 많은 일을 하려고 할 때',
            'tip': '경고적 표현입니다.'
        },
        {
            'expression': 'Burning the candle at both ends',
            'example': 'You\'re burning the candle at both ends. You need rest.',
            'examples': [
                'You\'re burning the candle at both ends. You need rest.',
                'Stop burning the candle at both ends.'
            ],
            'meaning': '무리를 하다, 과로하다',
            'situation': '누군가가 너무 열심히 일할 때',
            'tip': '걱정스러운 표현입니다.'
        },
        {
            'expression': 'Bury the hatchet',
            'example': 'Let\'s bury the hatchet and be friends again.',
            'examples': [
                'Let\'s bury the hatchet and be friends again.',
                'It\'s time to bury the hatchet.'
            ],
            'meaning': '싸움을 멈추다, 화해하다',
            'situation': '분쟁을 끝내고 화해할 때',
            'tip': '화해의 제안입니다.'
        },
        {
            'expression': 'Catch on',
            'example': 'Do you catch on? Or should I explain again?',
            'examples': [
                'Do you catch on? Or should I explain again?',
                'This trend is starting to catch on.'
            ],
            'meaning': '이해하다, 유행이 번지다',
            'situation': '누군가가 이해했는지 확인할 때',
            'tip': '다양한 의미로 사용됩니다.'
        },
        {
            'expression': 'Caught in the act',
            'example': 'He was caught in the act of stealing.',
            'examples': [
                'He was caught in the act of stealing.',
                'I caught her in the act.'
            ],
            'meaning': '현행범으로 잡히다, 적발되다',
            'situation': '누군가가 나쁜 일을 하면서 들켰을 때',
            'tip': '부정적인 상황입니다.'
        },
        {
            'expression': 'Caught red-handed',
            'example': 'She was caught red-handed cheating on the exam.',
            'examples': [
                'She was caught red-handed cheating on the exam.',
                'Caught red-handed!'
            ],
            'meaning': '증거가 남아 있는 상태로 잡히다',
            'situation': '명백한 증거와 함께 적발될 때',
            'tip': '부정적인 상황입니다.'
        },
        {
            'expression': 'Come hell or high water',
            'example': 'I\'ll be there come hell or high water.',
            'examples': [
                'I\'ll be there come hell or high water.',
                'I will finish this project come hell or high water.'
            ],
            'meaning': '어떤 일이 있어도, 어떻게 되든',
            'situation': '강한 결심을 표현할 때',
            'tip': '강한 의지를 보입니다.'
        },
        {
            'expression': 'Cry over spilled milk',
            'example': 'Don\'t cry over spilled milk. It\'s too late to change it.',
            'examples': [
                'Don\'t cry over spilled milk. It\'s too late to change it.',
                'There\'s no point crying over spilled milk.'
            ],
            'meaning': '이미 지난 일에 대해 후회하다',
            'situation': '일어난 일을 받아들여야 할 때',
            'tip': '조언적 표현입니다.'
        },
        {
            'expression': 'Crystal clear',
            'example': 'His instructions were crystal clear.',
            'examples': [
                'His instructions were crystal clear.',
                'Make it crystal clear to everyone.'
            ],
            'meaning': '아주 명확한, 분명한',
            'situation': '어떤 것이 매우 명확할 때',
            'tip': '긍정적인 표현입니다.'
        },
        {
            'expression': 'Cup of tea',
            'example': 'Math is not my cup of tea.',
            'examples': [
                'Math is not my cup of tea.',
                'Is that your cup of tea?'
            ],
            'meaning': '관심사, 좋아하는 것',
            'situation': '개인의 취향이나 관심을 말할 때',
            'tip': '자연스러운 표현입니다.'
        },
        {
            'expression': 'Cut corners',
            'example': 'Don\'t cut corners on quality.',
            'examples': [
                'Don\'t cut corners on quality.',
                'He cut corners to save money.'
            ],
            'meaning': '편법을 쓰다, 무시하다, 대충하다',
            'situation': '올바른 방법을 무시하고 빠르게 하려 할 때',
            'tip': '부정적인 의미입니다.'
        },
        {
            'expression': 'Call a spade a spade',
            'example': 'Let\'s call a spade a spade. You made a mistake.',
            'examples': [
                'Let\'s call a spade a spade. You made a mistake.',
                'We should call a spade a spade.'
            ],
            'meaning': '솔직하게 말하다, 있는 그대로 말하다',
            'situation': '직설적으로 진실을 말할 때',
            'tip': '솔직함을 강조합니다.'
        },
        {
            'expression': 'Clear as day',
            'example': 'What he meant was clear as day.',
            'examples': [
                'What he meant was clear as day.',
                'It\'s clear as day what happened.'
            ],
            'meaning': '아주 명확한, 쉽게 이해할 수 있는',
            'situation': '어떤 것이 분명할 때',
            'tip': '긍정적인 표현입니다.'
        },
        {
            'expression': 'Clear as mud',
            'example': 'Your explanation is clear as mud!',
            'examples': [
                'Your explanation is clear as mud!',
                'That\'s as clear as mud to me.'
            ],
            'meaning': '아주 모호한, 전혀 이해가 안 되는',
            'situation': '어떤 것이 이해하기 어려울 때',
            'tip': '비꼬아서 사용합니다.'
        },
        {
            'expression': 'Cold shoulder',
            'example': 'She gave me the cold shoulder when I said hello.',
            'examples': [
                'She gave me the cold shoulder when I said hello.',
                'He got the cold shoulder from his friends.'
            ],
            'meaning': '냉대하다, 무시하다',
            'situation': '누군가가 무시하거나 냉대할 때',
            'tip': '부정적인 표현입니다.'
        },
        {
            'expression': 'Come out of the woodwork',
            'example': 'When she won the lottery, people came out of the woodwork asking for money.',
            'examples': [
                'When she won the lottery, people came out of the woodwork asking for money.',
                'Problems came out of the woodwork.'
            ],
            'meaning': '갑자기 나타나다, 몰려오다',
            'situation': '예상하지 못한 것들이 갑자기 나타날 때',
            'tip': '일반적으로 부정적인 의미입니다.'
        },
        {
            'expression': 'Comparing apples and oranges',
            'example': 'You\'re comparing apples and oranges. They\'re completely different.',
            'examples': [
                'You\'re comparing apples and oranges. They\'re completely different.',
                'That\'s like comparing apples and oranges.'
            ],
            'meaning': '전혀 다른 것을 비교하다',
            'situation': '비교할 수 없는 것들을 비교할 때',
            'tip': '일반적으로 비판적입니다.'
        },
        {
            'expression': 'Crank it up',
            'example': 'Crank it up! Turn the volume louder!',
            'examples': [
                'Crank it up! Turn the volume louder!',
                'Let\'s crank it up and have fun.'
            ],
            'meaning': '볼륨을 높이다, 강도를 높이다',
            'situation': '뭔가를 더 크게 또는 강하게 할 때',
            'tip': '캐주얼한 표현입니다.'
        },
        {
            'expression': 'Creep up on someone',
            'example': 'Age is creeping up on me.',
            'examples': [
                'Age is creeping up on me.',
                'Winter is creeping up on us.'
            ],
            'meaning': '천천히 다가오다, 어느새 가까워지다',
            'situation': '시간이 빠르게 흐를 때',
            'tip': '자연스러운 표현입니다.'
        },
        {
            'expression': 'Cross that bridge when we come to it',
            'example': 'Don\'t worry about future problems. We\'ll cross that bridge when we come to it.',
            'examples': [
                'Don\'t worry about future problems. We\'ll cross that bridge when we come to it.',
                'Let\'s cross that bridge when we come to it.'
            ],
            'meaning': '그 상황이 되면 그때 생각하자',
            'situation': '지금 걱정할 필요 없다는 뜻으로 말할 때',
            'tip': '실용적인 조언입니다.'
        },
        {
            'expression': 'Cruise for a bruising',
            'example': 'If you keep talking like that, you\'re cruising for a bruising.',
            'examples': [
                'If you keep talking like that, you\'re cruising for a bruising.',
                'He\'s cruising for a bruising with that behavior.'
            ],
            'meaning': '문제를 자초하다, 곤경에 빠질 짓을 하다',
            'situation': '위험한 행동에 대해 경고할 때',
            'tip': '경고적인 표현입니다.'
        },
        {
            'expression': 'Cry uncle',
            'example': 'I give up! I cry uncle!',
            'examples': [
                'I give up! I cry uncle!',
                'You have to cry uncle to win the game.'
            ],
            'meaning': '항복하다, 포기하다',
            'situation': '누군가가 지쳐서 포기할 때',
            'tip': '게임에서 자주 사용됩니다.'
        },
        {
            'expression': 'Customary practice',
            'example': 'It\'s customary practice to shake hands when you meet.',
            'examples': [
                'It\'s customary practice to shake hands when you meet.',
                'That\'s customary practice in our company.'
            ],
            'meaning': '관례적인 관행, 전통적인 방식',
            'situation': '문화나 전통을 설명할 때',
            'tip': '공식적인 표현입니다.'
        },
        {
            'expression': 'Dead as a doornail',
            'example': 'The romance between them is dead as a doornail.',
            'examples': [
                'The romance between them is dead as a doornail.',
                'That idea is dead as a doornail.'
            ],
            'meaning': '완전히 죽었다, 더 이상 없다',
            'situation': '어떤 것이 완전히 끝났을 때',
            'tip': '부정적인 표현입니다.'
        },
        {
            'expression': 'Defeat the purpose',
            'example': 'Eating sweets on a diet defeats the purpose.',
            'examples': [
                'Eating sweets on a diet defeats the purpose.',
                'That would defeat the purpose.'
            ],
            'meaning': '목적을 무효화하다, 역효과를 내다',
            'situation': '어떤 행동이 목표와 맞지 않을 때',
            'tip': '역설적인 상황입니다.'
        },
        {
            'expression': 'Delayed gratification',
            'example': 'Delayed gratification is important for success.',
            'examples': [
                'Delayed gratification is important for success.',
                'He learned the value of delayed gratification.'
            ],
            'meaning': '즉각적인 만족을 미루다, 참다',
            'situation': '인내와 절제를 강조할 때',
            'tip': '긍정적인 개념입니다.'
        },
        {
            'expression': 'Demo or die',
            'example': 'In this company, it\'s demo or die to prove your ideas.',
            'examples': [
                'In this company, it\'s demo or die to prove your ideas.',
                'Demo or die is our motto.'
            ],
            'meaning': '구현을 보여주거나 실패하거나',
            'situation': '실제로 해봐야 한다는 뜻으로 말할 때',
            'tip': '비즈니스 문화에서 자주 사용됩니다.'
        },
        {
            'expression': 'Dime a dozen',
            'example': 'Good ideas are not dime a dozen, they\'re rare.',
            'examples': [
                'Good ideas are not dime a dozen, they\'re rare.',
                'Such skills are dime a dozen these days.'
            ],
            'meaning': '흔한 것, 많고 싼 것',
            'situation': '어떤 것이 흔하고 흔할 때',
            'tip': '대체로 부정적인 의미입니다.'
        },
        {
            'expression': 'Divide and conquer',
            'example': 'Let\'s divide and conquer this big project.',
            'examples': [
                'Let\'s divide and conquer this big project.',
                'We used a divide and conquer strategy.'
            ],
            'meaning': '나누어서 정복하다, 분할 정복',
            'situation': '큰 문제를 작게 나누어 해결할 때',
            'tip': '전략적인 표현입니다.'
        },
        {
            'expression': 'Do your best',
            'example': 'Just do your best and don\'t worry about the result.',
            'examples': [
                'Just do your best and don\'t worry about the result.',
                'Do your best and you\'ll succeed.'
            ],
            'meaning': '최선을 다하다, 열심히 하다',
            'situation': '누군가를 격려할 때',
            'tip': '격려적인 표현입니다.'
        },
        {
            'expression': 'Double take',
            'example': 'I did a double take when I saw him.',
            'examples': [
                'I did a double take when I saw him.',
                'She did a double take at the sight.'
            ],
            'meaning': '다시 한 번 확인하다, 깜짝 놀라다',
            'situation': '예상 밖의 것을 봤을 때',
            'tip': '놀라운 반응을 나타냅니다.'
        },
        {
            'expression': 'Down and out',
            'example': 'He\'s been down and out for a while.',
            'examples': [
                'He\'s been down and out for a while.',
                'Don\'t worry, he won\'t stay down and out.'
            ],
            'meaning': '낙담한, 경제적으로 어려운',
            'situation': '누군가의 어려운 상황을 말할 때',
            'tip': '동정적인 표현입니다.'
        },
        {
            'expression': 'Down in the dumps',
            'example': 'She\'s been down in the dumps ever since the breakup.',
            'examples': [
                'She\'s been down in the dumps ever since the breakup.',
                'He looks down in the dumps.'
            ],
            'meaning': '기분이 안 좋다, 낙담하다',
            'situation': '누군가가 우울해 보일 때',
            'tip': '동정적인 표현입니다.'
        },
        {
            'expression': 'Down the hatch',
            'example': 'Let\'s drink! Down the hatch!',
            'examples': [
                'Let\'s drink! Down the hatch!',
                'Down the hatch!'
            ],
            'meaning': '한 번에 마시다, 넘어간다',
            'situation': '음료를 마실 때',
            'tip': '캐주얼한 표현입니다.'
        },
        {
            'expression': 'Down to earth',
            'example': 'He\'s a famous actor, but he\'s very down to earth.',
            'examples': [
                'He\'s a famous actor, but he\'s very down to earth.',
                'She has a down to earth attitude.'
            ],
            'meaning': '실제적인, 겸손한, 친근한',
            'situation': '누군가의 성격이 겸손할 때',
            'tip': '긍정적인 표현입니다.'
        },
        {
            'expression': 'Draw the line',
            'example': 'I don\'t mind helping, but I draw the line at doing all the work.',
            'examples': [
                'I don\'t mind helping, but I draw the line at doing all the work.',
                'You need to draw the line somewhere.'
            ],
            'meaning': '선을 긋다, 한계를 정하다',
            'situation': '허용할 수 없는 한계를 표시할 때',
            'tip': '경계를 나타냅니다.'
        },
        {
            'expression': 'Dream come true',
            'example': 'Getting this job is a dream come true for me.',
            'examples': [
                'Getting this job is a dream come true for me.',
                'It\'s like a dream come true.'
            ],
            'meaning': '꿈이 실현되다',
            'situation': '오랫동안 원하던 것이 이루어질 때',
            'tip': '긍정적이고 행복한 표현입니다.'
        },
        {
            'expression': 'Dressed to kill',
            'example': 'She was dressed to kill at the party.',
            'examples': [
                'She was dressed to kill at the party.',
                'He was dressed to kill for the date.'
            ],
            'meaning': '멋지게 차려입다, 돋보이게 입다',
            'situation': '누군가가 특별하게 차려입었을 때',
            'tip': '긍정적인 의미입니다.'
        },
        {
            'expression': 'Dressed to the nines',
            'example': 'For the wedding, everyone was dressed to the nines.',
            'examples': [
                'For the wedding, everyone was dressed to the nines.',
                'She was dressed to the nines.'
            ],
            'meaning': '아주 멋지게 차려입다',
            'situation': '특별한 행사에 멋있게 옷을 입었을 때',
            'tip': '긍정적인 표현입니다.'
        },
        {
            'expression': 'Drive someone up the wall',
            'example': 'His constant talking drives me up the wall.',
            'examples': [
                'His constant talking drives me up the wall.',
                'That noise is driving me up the wall.'
            ],
            'meaning': '~를 미치게 하다, 짜증나게 하다',
            'situation': '무언가가 매우 짜증날 때',
            'tip': '부정적인 표현입니다.'
        },
        {
            'expression': 'Driving in the fast lane',
            'example': 'He\'s always driving in the fast lane of life.',
            'examples': [
                'He\'s always driving in the fast lane of life.',
                'Living in the fast lane is exhausting.'
            ],
            'meaning': '무모하게 살다, 위험하게 빠르게 살다',
            'situation': '누군가의 위험한 생활 방식을 말할 때',
            'tip': '비판적인 톤으로 사용되기도 합니다.'
        },
        {
            'expression': 'Dull as dishwater',
            'example': 'The movie was as dull as dishwater.',
            'examples': [
                'The movie was as dull as dishwater.',
                'That book is dull as dishwater.'
            ],
            'meaning': '아주 지루한, 재미없는',
            'situation': '어떤 것이 아주 지루할 때',
            'tip': '부정적인 표현입니다.'
        },
        {
            'expression': 'Dumb down',
            'example': 'Don\'t dumb down the content for kids.',
            'examples': [
                'Don\'t dumb down the content for kids.',
                'We need to avoid dumbing it down too much.'
            ],
            'meaning': '단순화하다, 수준을 낮추다',
            'situation': '복잡한 것을 쉽게 설명할 때',
            'tip': '중립적 또는 부정적 의미입니다.'
        },
        {
            'expression': 'Dust off',
            'example': 'I dusted off my old guitar and started playing again.',
            'examples': [
                'I dusted off my old guitar and started playing again.',
                'Let\'s dust off that old plan.'
            ],
            'meaning': '오래된 것을 다시 사용하다, 재개하다',
            'situation': '오래전에 하던 일을 다시 시작할 때',
            'tip': '자연스러운 표현입니다.'
        },
        {
            'expression': 'Early bird catches the worm',
            'example': 'Wake up early! The early bird catches the worm.',
            'examples': [
                'Wake up early! The early bird catches the worm.',
                'The early bird gets the advantages.'
            ],
            'meaning': '일찍 시작하는 사람이 성공한다',
            'situation': '조기 행동의 중요성을 강조할 때',
            'tip': '긍정적인 조언입니다.'
        },
        {
            'expression': 'Easy as pie',
            'example': 'This task is easy as pie.',
            'examples': [
                'This task is easy as pie.',
                'That\'s easy as pie!'
            ],
            'meaning': '아주 쉽다, 간단하다',
            'situation': '어떤 것이 매우 쉬울 때',
            'tip': '긍정적인 표현입니다.'
        },
        {
            'expression': 'Eat humble pie',
            'example': 'I was wrong about him, so I have to eat humble pie.',
            'examples': [
                'I was wrong about him, so I have to eat humble pie.',
                'He had to eat humble pie after his mistake.'
            ],
            'meaning': '자존심을 상하게 받다, 사과하다',
            'situation': '실수를 인정하고 사과할 때',
            'tip': '겸손함을 나타냅니다.'
        },
        {
            'expression': 'Eat one\'s heart out',
            'example': 'He\'s eating his heart out waiting for the results.',
            'examples': [
                'He\'s eating his heart out waiting for the results.',
                'Don\'t eat your heart out.'
            ],
            'meaning': '마음이 아프다, 애태우다',
            'situation': '누군가가 걱정스러워하거나 고통받을 때',
            'tip': '감정적인 표현입니다.'
        },
        {
            'expression': 'Eat one\'s words',
            'example': 'He said it would never happen, but now he has to eat his words.',
            'examples': [
                'He said it would never happen, but now he has to eat his words.',
                'You\'ll eat your words.'
            ],
            'meaning': '한 말을 뒤집다, 자신의 말을 철회하다',
            'situation': '누군가가 전에 한 말이 틀렸을 때',
            'tip': '약간의 조롱이 포함될 수 있습니다.'
        },
        {
            'expression': 'Edge someone out',
            'example': 'The new product edged out the competition.',
            'examples': [
                'The new product edged out the competition.',
                'She edged him out for the promotion.'
            ],
            'meaning': '~를 앞지르다, 근소하게 이기다',
            'situation': '누군가가 근소한 차이로 이길 때',
            'tip': '긍정적인 표현입니다.'
        },
        {
            'expression': 'Eleven out of ten',
            'example': 'Your performance was eleven out of ten!',
            'examples': [
                'Your performance was eleven out of ten!',
                'That\'s eleven out of ten for excellence.'
            ],
            'meaning': '최고의, 기대 이상의',
            'situation': '뭔가가 기대 이상일 때',
            'tip': '강한 칭찬입니다.'
        },
        {
            'expression': 'End in smoke',
            'example': 'All our plans ended in smoke when he got sick.',
            'examples': [
                'All our plans ended in smoke when he got sick.',
                'The business ended in smoke.'
            ],
            'meaning': '실패하다, 수포가 되다',
            'situation': '계획이 실패할 때',
            'tip': '부정적인 표현입니다.'
        },
        {
            'expression': 'Enough is enough',
            'example': 'I\'ve had it! Enough is enough!',
            'examples': [
                'I\'ve had it! Enough is enough!',
                'Enough is enough, I\'m done.'
            ],
            'meaning': '더 이상은 안 돼, 그만해',
            'situation': '한계에 도달했을 때',
            'tip': '강한 거절을 표현합니다.'
        },
        {
            'expression': 'Escape by the skin of your teeth',
            'example': 'He escaped by the skin of his teeth.',
            'examples': [
                'He escaped by the skin of his teeth.',
                'I escaped by the skin of my teeth.'
            ],
            'meaning': '간신히 벗어나다, 거의 실패할 뻔하다',
            'situation': '위험한 상황에서 거의 다 왔을 때',
            'tip': '극적인 표현입니다.'
        },
        {
            'expression': 'Every dog has its day',
            'example': 'Don\'t worry, every dog has its day.',
            'examples': [
                'Don\'t worry, every dog has its day.',
                'Every dog has its day eventually.'
            ],
            'meaning': '누구나 성공할 때가 있다',
            'situation': '실패한 사람을 격려할 때',
            'tip': '긍정적인 조언입니다.'
        },
        {
            'expression': 'Everything but the kitchen sink',
            'example': 'He packed everything but the kitchen sink.',
            'examples': [
                'He packed everything but the kitchen sink.',
                'They brought everything but the kitchen sink.'
            ],
            'meaning': '거의 모든 것, 주방 싱크대 빼고 다',
            'situation': '많은 물건을 가져갈 때',
            'tip': '유머러스한 표현입니다.'
        },
        {
            'expression': 'Eye for an eye',
            'example': 'An eye for an eye makes the world blind.',
            'examples': [
                'An eye for an eye makes the world blind.',
                'He wanted an eye for an eye.'
            ],
            'meaning': '동해보복, 앙갚음',
            'situation': '보복을 말할 때',
            'tip': '부정적인 행동을 나타냅니다.'
        },
        {
            'expression': 'Face the music',
            'example': 'You made a mistake, now you have to face the music.',
            'examples': [
                'You made a mistake, now you have to face the music.',
                'He didn\'t want to face the music.'
            ],
            'meaning': '결과에 책임지다, 벌을 받다',
            'situation': '실수의 결과를 받아들일 때',
            'tip': '부정적인 상황이지만 필요한 행동입니다.'
        },
        {
            'expression': 'Fall through the cracks',
            'example': 'Some important details fell through the cracks.',
            'examples': [
                'Some important details fell through the cracks.',
                'He fell through the cracks.'
            ],
            'meaning': '간과되다, 무시되다',
            'situation': '중요한 것이 놓쳐질 때',
            'tip': '부정적인 표현입니다.'
        },
        {
            'expression': 'Feast or famine',
            'example': 'In this job, it\'s feast or famine.',
            'examples': [
                'In this job, it\'s feast or famine.',
                'Business is feast or famine.'
            ],
            'meaning': '많거나 적거나, 양극단',
            'situation': '극단적인 상황을 말할 때',
            'tip': '극단적 변화를 나타냅니다.'
        },
        {
            'expression': 'Few and far between',
            'example': 'Good jobs are few and far between.',
            'examples': [
                'Good jobs are few and far between.',
                'Such opportunities are few and far between.'
            ],
            'meaning': '드물다, 거의 없다',
            'situation': '무언가가 흔하지 않을 때',
            'tip': '부정적인 의미가 많습니다.'
        },
        {
            'expression': 'Fit as a fiddle',
            'example': 'He\'s fit as a fiddle even at 80 years old.',
            'examples': [
                'He\'s fit as a fiddle even at 80 years old.',
                'I feel fit as a fiddle today.'
            ],
            'meaning': '매우 건강한, 좋은 상태',
            'situation': '누군가의 건강 상태가 좋을 때',
            'tip': '긍정적인 표현입니다.'
        },
        {
            'expression': 'Flash in the pan',
            'example': 'His success was just a flash in the pan.',
            'examples': [
                'His success was just a flash in the pan.',
                'That trend was a flash in the pan.'
            ],
            'meaning': '일시적인 성공, 반짝이는 것',
            'situation': '단기적인 성공에 대해 말할 때',
            'tip': '부정적인 의미입니다.'
        },
        {
            'expression': 'Flip your lid',
            'example': 'When she heard the news, she flipped her lid.',
            'examples': [
                'When she heard the news, she flipped her lid.',
                'Don\'t flip your lid!'
            ],
            'meaning': '화내다, 미치다 싶이 하다',
            'situation': '누군가가 매우 화날 때',
            'tip': '감정적인 표현입니다.'
        },
        {
            'expression': 'Flog a dead horse',
            'example': 'Don\'t flog a dead horse. That idea is dead.',
            'examples': [
                'Don\'t flog a dead horse. That idea is dead.',
                'We\'re just flogging a dead horse.'
            ],
            'meaning': '죽은 말을 때리다, 쓸데없는 짓을 하다',
            'situation': '쓸데없는 노력에 대해 말할 때',
            'tip': '조언적 표현입니다.'
        },
        {
            'expression': 'Fly on the wall',
            'example': 'I\'d like to be a fly on the wall in that meeting.',
            'examples': [
                'I\'d like to be a fly on the wall in that meeting.',
                'To be a fly on the wall...'
            ],
            'meaning': '은밀하게 보고 싶다, 몰래 보고 싶다',
            'situation': '비밀 자리에 가고 싶을 때',
            'tip': '호기심을 표현합니다.'
        },
        {
            'expression': 'Follow your heart',
            'example': 'Don\'t worry about others, just follow your heart.',
            'examples': [
                'Don\'t worry about others, just follow your heart.',
                'Follow your heart and you\'ll be happy.'
            ],
            'meaning': '마음을 따르다, 본능을 믿다',
            'situation': '누군가를 격려할 때',
            'tip': '긍정적인 조언입니다.'
        },
        {
            'expression': 'Foot the bill',
            'example': 'Who\'s going to foot the bill for this project?',
            'examples': [
                'Who\'s going to foot the bill for this project?',
                'He footed the bill.'
            ],
            'meaning': '비용을 부담하다, 돈을 내다',
            'situation': '누군가가 비용을 낼 때',
            'tip': '비즈니스 상황에서 자주 쓰입니다.'
        },
        {
            'expression': 'Foregone conclusion',
            'example': 'It\'s a foregone conclusion that he\'ll win.',
            'examples': [
                'It\'s a foregone conclusion that he\'ll win.',
                'The outcome was a foregone conclusion.'
            ],
            'meaning': '당연한 결론, 뻔한 결과',
            'situation': '결과가 이미 정해진 상황에서',
            'tip': '예측 가능한 결과를 나타냅니다.'
        },
        {
            'expression': 'Forget about it',
            'example': 'You can\'t do it? Forget about it!',
            'examples': [
                'You can\'t do it? Forget about it!',
                'Don\'t worry about it. Forget about it.'
            ],
            'meaning': '신경 쓰지 마, 잊어버려',
            'situation': '불가능한 것을 포기할 때',
            'tip': '캐주얼한 표현입니다.'
        },
        {
            'expression': 'Full steam ahead',
            'example': 'Let\'s go full steam ahead with the project!',
            'examples': [
                'Let\'s go full steam ahead with the project!',
                'Full steam ahead!'
            ],
            'meaning': '전력을 다해, 최대한 빠르게',
            'situation': '적극적으로 진행할 때',
            'tip': '긍정적이고 적극적입니다.'
        },
        {
            'expression': 'Fun and games',
            'example': 'It\'s not all fun and games, you know.',
            'examples': [
                'It\'s not all fun and games, you know.',
                'This is serious, not fun and games.'
            ],
            'meaning': '장난과 즐거움만, 심각하지 않은',
            'situation': '뭔가가 심각하지 않을 때',
            'tip': '대체로 부정적인 상황에서 사용됩니다.'
        },
        {
            'expression': 'Fundamental difference',
            'example': 'There\'s a fundamental difference between them.',
            'examples': [
                'There\'s a fundamental difference between them.',
                'It\'s a fundamental difference in approach.'
            ],
            'meaning': '근본적인 차이, 기본적인 차이',
            'situation': '뿌리 깊은 차이를 말할 때',
            'tip': '중요한 차이를 강조합니다.'
        },
        {
            'expression': 'Get a kick out of',
            'example': 'I get a kick out of watching comedy movies.',
            'examples': [
                'I get a kick out of watching comedy movies.',
                'She gets a kick out of it.'
            ],
            'meaning': '~를 즐기다, 재미있어하다',
            'situation': '누군가가 뭔가를 즐길 때',
            'tip': '긍정적인 감정을 나타냅니다.'
        },
        {
            'expression': 'Get a leg up',
            'example': 'This training will get you a leg up on the competition.',
            'examples': [
                'This training will get you a leg up on the competition.',
                'You\'ll get a leg up if you start now.'
            ],
            'meaning': '우위를 얻다, 앞서가다',
            'situation': '경쟁에서 유리해질 때',
            'tip': '긍정적인 표현입니다.'
        },
        {
            'expression': 'Get a word in edgewise',
            'example': 'She talks so much, I can\'t get a word in edgewise.',
            'examples': [
                'She talks so much, I can\'t get a word in edgewise.',
                'He wouldn\'t let me get a word in edgewise.'
            ],
            'meaning': '말을 끼워넣다, 입을 열다',
            'situation': '누군가가 계속 말할 때',
            'tip': '약간 답답한 상황입니다.'
        },
        {
            'expression': 'Get down and dirty',
            'example': 'Let\'s get down and dirty and discuss the real issues.',
            'examples': [
                'Let\'s get down and dirty and discuss the real issues.',
                'We need to get down and dirty with this.'
            ],
            'meaning': '진지하게 다루다, 핵심을 다루다',
            'situation': '어려운 문제를 직면할 때',
            'tip': '직설적인 표현입니다.'
        },
        {
            'expression': 'Get the lead out',
            'example': 'We\'re late! Get the lead out!',
            'examples': [
                'We\'re late! Get the lead out!',
                'Get the lead out, let\'s go!'
            ],
            'meaning': '빨리 해, 움직여',
            'situation': '누군가를 재촉할 때',
            'tip': '긴급함을 나타냅니다.'
        },
        {
            'expression': 'Get your feet wet',
            'example': 'You should get your feet wet in this industry.',
            'examples': [
                'You should get your feet wet in this industry.',
                'He\'s getting his feet wet.'
            ],
            'meaning': '처음 시작하다, 경험해보다',
            'situation': '새로운 분야에 처음 진입할 때',
            'tip': '긍정적인 시작을 나타냅니다.'
        },
        {
            'expression': 'Ghost town',
            'example': 'After the factory closed, the city became a ghost town.',
            'examples': [
                'After the factory closed, the city became a ghost town.',
                'The streets look like a ghost town.'
            ],
            'meaning': '인구가 거의 없는 곳, 황폐한 곳',
            'situation': '한산한 장소를 묘사할 때',
            'tip': '부정적인 이미지입니다.'
        },
        {
            'expression': 'Go against the grain',
            'example': 'It goes against the grain for me to lie.',
            'examples': [
                'It goes against the grain for me to lie.',
                'Doing this goes against my grain.'
            ],
            'meaning': '본성에 어긋나다, 본심에 반하다',
            'situation': '누군가의 성향에 맞지 않을 때',
            'tip': '개인적 신념을 나타냅니다.'
        },
        {
            'expression': 'Go for broke',
            'example': 'I\'m going to go for broke and apply for that job.',
            'examples': [
                'I\'m going to go for broke and apply for that job.',
                'Let\'s go for broke!'
            ],
            'meaning': '모든 것을 걸다, 전력을 다하다',
            'situation': '큰 위험을 감수하면서 시도할 때',
            'tip': '용감한 결정을 나타냅니다.'
        },
        {
            'expression': 'Go the distance',
            'example': 'I think we can go the distance with this project.',
            'examples': [
                'I think we can go the distance with this project.',
                'They went the distance.'
            ],
            'meaning': '끝까지 가다, 완주하다',
            'situation': '긴 과정을 완료할 때',
            'tip': '긍정적인 인내를 나타냅니다.'
        },
        {
            'expression': 'Go with the flow',
            'example': 'Just go with the flow and see what happens.',
            'examples': [
                'Just go with the flow and see what happens.',
                'I like to go with the flow.'
            ],
            'meaning': '흐름을 따르다, 자연스럽게 하다',
            'situation': '편하고 자연스럽게 진행할 때',
            'tip': '긍정적인 태도입니다.'
        },
        {
            'expression': 'Going forward',
            'example': 'Going forward, we need to improve our process.',
            'examples': [
                'Going forward, we need to improve our process.',
                'Going forward, remember this lesson.'
            ],
            'meaning': '앞으로, 이제부터',
            'situation': '미래의 행동을 말할 때',
            'tip': '비즈니스에서 자주 사용됩니다.'
        },
        {
            'expression': 'Golden opportunity',
            'example': 'This is a golden opportunity for you.',
            'examples': [
                'This is a golden opportunity for you.',
                'Don\'t miss this golden opportunity.'
            ],
            'meaning': '황금 같은 기회, 최고의 기회',
            'situation': '놓쳐서는 안 될 좋은 기회',
            'tip': '긍정적이고 중요합니다.'
        },
        {
            'expression': 'Good things come to those who wait',
            'example': 'Be patient, good things come to those who wait.',
            'examples': [
                'Be patient, good things come to those who wait.',
                'Good things come to those who wait.'
            ],
            'meaning': '인내하는 자에게 좋은 것이 온다',
            'situation': '누군가를 기다리게 할 때',
            'tip': '긍정적인 조언입니다.'
        },
        {
            'expression': 'Good time was had by all',
            'example': 'A good time was had by all at the party.',
            'examples': [
                'A good time was had by all at the party.',
                'A good time was had by all.'
            ],
            'meaning': '모두가 즐거운 시간을 보냈다',
            'situation': '행사가 잘 끝났을 때',
            'tip': '긍정적이고 공식적입니다.'
        },
        {
            'expression': 'Good times were had',
            'example': 'During our vacation, good times were had.',
            'examples': [
                'During our vacation, good times were had.',
                'Good times were had together.'
            ],
            'meaning': '좋은 시간을 보냈다',
            'situation': '즐거운 경험을 회상할 때',
            'tip': '긍정적인 표현입니다.'
        },
        {
            'expression': 'Grind to a halt',
            'example': 'The production line ground to a halt.',
            'examples': [
                'The production line ground to a halt.',
                'Everything came to a grind to a halt.'
            ],
            'meaning': '완전히 멈추다, 중단되다',
            'situation': '일이나 과정이 중단될 때',
            'tip': '부정적인 상황입니다.'
        }
    ]
    return expressions

def get_expression_quiz():
    """표현 퀴즈 생성 - 예문 + 정답 표현 + 오답 3개"""
    expressions = get_daily_expressions()
    
    # 랜덤 표현 선택
    correct_expr = random.choice(expressions)
    
    # 오답 3개 선택 (정답과 다른 표현에서만)
    other_expressions = [e for e in expressions if e['expression'] != correct_expr['expression']]
    wrong_options = random.sample(other_expressions, min(3, len(other_expressions)))
    
    # 선택지 생성
    options = [correct_expr] + wrong_options
    random.shuffle(options)
    
    # 예문 선택 (examples 중 첫 번째)
    example = correct_expr['examples'][0] if correct_expr['examples'] else correct_expr['example']
    
    return {
        'example': example,
        'correct_expression': correct_expr['expression'],
        'correct_meaning': correct_expr['meaning'],
        'options': [opt['expression'] for opt in options],
        'correct_index': next(i for i, opt in enumerate(options) if opt['expression'] == correct_expr['expression'])
    }

def get_drama_conversations():
    """드라마/애니 기반 다중턴 회화 시나리오"""
    return [
        {
            'scene': '카페에서 처음 만난 사람',
            'turns': [
                {
                    'ai_prompt': 'Hey, is this seat taken?',
                    'ai_meaning': '안녕, 이 자리 비었어요?',
                    'user_response': 'No, please sit down.',
                    'user_meaning': '아니요, 앉으세요.'
                },
                {
                    'ai_prompt': 'Thanks. So, what brings you here today?',
                    'ai_meaning': '감사합니다. 그래서 오늘 뭐 때문에 여기 왔어요?',
                    'user_response': 'I come here to study.',
                    'user_meaning': '나는 공부하러 여기 와요.'
                },
                {
                    'ai_prompt': 'That sounds nice. What are you studying?',
                    'ai_meaning': '좋네요. 뭘 공부하고 있어요?',
                    'user_response': 'English language and culture.',
                    'user_meaning': '영어와 문화를 공부합니다.'
                }
            ]
        },
        {
            'scene': '회사 면접',
            'turns': [
                {
                    'ai_prompt': 'Tell me about your strengths.',
                    'ai_meaning': '당신의 장점에 대해 말씀해주세요.',
                    'user_response': "I'm a quick learner and very dedicated.",
                    'user_meaning': '저는 빨리 배우고 매우 헌신적입니다.'
                },
                {
                    'ai_prompt': 'That\'s great. Can you give me an example?',
                    'ai_meaning': '그건 좋은데요. 예시를 들어줄 수 있어요?',
                    'user_response': 'In my previous job, I finished projects ahead of schedule.',
                    'user_meaning': '이전 직장에서 프로젝트를 일찍 완료했습니다.'
                },
                {
                    'ai_prompt': 'Excellent. When can you start?',
                    'ai_meaning': '훌륭합니다. 언제 시작할 수 있어요?',
                    'user_response': 'I can start next Monday.',
                    'user_meaning': '다음 주 월요일에 시작할 수 있습니다.'
                }
            ]
        },
        {
            'scene': '레스토랑에서 주문',
            'turns': [
                {
                    'ai_prompt': 'What would you like to order?',
                    'ai_meaning': '주문하시겠어요?',
                    'user_response': "I'll have the grilled salmon, please.",
                    'user_meaning': '그릴에 구운 연어로 주세요.'
                },
                {
                    'ai_prompt': 'Good choice. Would you like anything to drink?',
                    'ai_meaning': '좋은 선택이에요. 마실 것도 주시겠어요?',
                    'user_response': 'Yes, I\'ll have water with lemon.',
                    'user_meaning': '네, 레몬을 넣은 물로 주세요.'
                },
                {
                    'ai_prompt': 'Will that be everything?',
                    'ai_meaning': '이게 전부일까요?',
                    'user_response': 'Yes, that will be all. Thank you.',
                    'user_meaning': '네, 이게 전부입니다. 감사합니다.'
                }
            ]
        },
        {
            'scene': '여행지에서 길을 묻는 중',
            'turns': [
                {
                    'ai_prompt': 'Are you lost?',
                    'ai_meaning': '길을 잃으셨어요?',
                    'user_response': "Yes, I'm looking for the train station.",
                    'user_meaning': '네, 기차역을 찾고 있어요.'
                },
                {
                    'ai_prompt': "It's just two blocks away. Turn right at the corner.",
                    'ai_meaning': '바로 2블록 떨어진 곳이에요. 모퉁이에서 오른쪽으로 돌아가세요.',
                    'user_response': 'Thank you so much for your help!',
                    'user_meaning': '도와주셔서 정말 감사합니다!'
                },
                {
                    'ai_prompt': 'You\'re welcome. Have a safe trip!',
                    'ai_meaning': '환영합니다. 안전한 여행 되세요!',
                    'user_response': 'Thank you, goodbye!',
                    'user_meaning': '감사합니다. 안녕!'
                }
            ]
        },
        {
            'scene': '친구와의 재회',
            'turns': [
                {
                    'ai_prompt': "I haven't seen you in years!",
                    'ai_meaning': '몇 년 만이다!',
                    'user_response': 'I know! How have you been?',
                    'user_meaning': '알아요! 잘 지냈어요?'
                },
                {
                    'ai_prompt': 'Great! We should catch up over coffee.',
                    'ai_meaning': '좋아! 커피하면서 얘기해야겠다.',
                    'user_response': 'That sounds wonderful. When are you free?',
                    'user_meaning': '좋은 생각이네요. 언제 시간이 돼요?'
                },
                {
                    'ai_prompt': 'How about this Saturday?',
                    'ai_meaning': '이번 토요일은 어때요?',
                    'user_response': 'Saturday works perfectly for me!',
                    'user_meaning': '토요일이 저한테 딱 맞아요!'
                }
            ]
        },
        {
            'scene': '병원에서 의사와 상담',
            'turns': [
                {
                    'ai_prompt': 'How are you feeling today?',
                    'ai_meaning': '오늘 기분이 어떠세요?',
                    'user_response': "I've had a terrible headache for three days.",
                    'user_meaning': '3일 동안 심한 두통이 있습니다.'
                },
                {
                    'ai_prompt': 'Let me check your blood pressure.',
                    'ai_meaning': '혈압을 재어보겠습니다.',
                    'user_response': 'Okay, I understand.',
                    'user_meaning': '네, 알겠습니다.'
                },
                {
                    'ai_prompt': 'I\'ll prescribe some medicine for you.',
                    'ai_meaning': '약을 처방해드리겠습니다.',
                    'user_response': 'Thank you, doctor. How often should I take it?',
                    'user_meaning': '감사합니다. 하루에 몇 번 복용해야 하나요?'
                }
            ]
        },
        {
            'scene': '호텔 체크인',
            'turns': [
                {
                    'ai_prompt': 'Welcome to our hotel. How many nights will you be staying?',
                    'ai_meaning': '저희 호텔에 오신 것을 환영합니다. 몇 박을 하실 예정인가요?',
                    'user_response': 'I need a room for three nights, please.',
                    'user_meaning': '3박을 할 수 있는 객실을 원합니다.'
                },
                {
                    'ai_prompt': 'Do you prefer a single room or a double room?',
                    'ai_meaning': '싱글 룸이나 더블 룸 중 어느 것을 원하세요?',
                    'user_response': 'A double room with a sea view would be nice.',
                    'user_meaning': '바다가 보이는 더블 룸으로 주세요.'
                },
                {
                    'ai_prompt': 'Excellent choice. Here is your room key.',
                    'ai_meaning': '훌륭한 선택입니다. 여기 방 열쇠입니다.',
                    'user_response': 'Thank you very much. What time is breakfast?',
                    'user_meaning': '고마워요. 아침 식사는 몇 시인가요?'
                }
            ]
        },
        {
            'scene': '대중교통 표 구매',
            'turns': [
                {
                    'ai_prompt': 'Where would you like to go?',
                    'ai_meaning': '어디로 가고 싶으세요?',
                    'user_response': 'I need a ticket to downtown, please.',
                    'user_meaning': '다운타운으로 가는 표를 주세요.'
                },
                {
                    'ai_prompt': 'One-way or round trip?',
                    'ai_meaning': '편도입니까, 왕복입니까?',
                    'user_response': 'One-way ticket. How much is it?',
                    'user_meaning': '편도표 주세요. 얼마인가요?'
                },
                {
                    'ai_prompt': 'That will be fifteen dollars.',
                    'ai_meaning': '15달러입니다.',
                    'user_response': 'Here you go. Which platform does the bus leave from?',
                    'user_meaning': '여기 있습니다. 버스는 어느 플랫폼에서 출발하나요?'
                }
            ]
        },
        {
            'scene': '쇼핑몰에서 옷 구매',
            'turns': [
                {
                    'ai_prompt': 'Hi! Can I help you find anything?',
                    'ai_meaning': '안녕하세요! 무엇을 도와드릴까요?',
                    'user_response': 'I\'m looking for a blue shirt in size medium.',
                    'user_meaning': '미디엄 사이즈의 파란 셔츠를 찾고 있어요.'
                },
                {
                    'ai_prompt': 'Great! Let me check if we have that in stock.',
                    'ai_meaning': '좋습니다! 재고가 있는지 확인해보겠습니다.',
                    'user_response': 'Thank you. Can I try it on?',
                    'user_meaning': '감사합니다. 입어볼 수 있을까요?'
                },
                {
                    'ai_prompt': 'Of course! The fitting room is over there.',
                    'ai_meaning': '물론이죠! 피팅룸이 저기 있습니다.',
                    'user_response': 'Perfect! I\'ll take this shirt. Do you have a discount?',
                    'user_meaning': '좋아요! 이 셔츠로 살게요. 할인이 있나요?'
                }
            ]
        },
        {
            'scene': '영화표 구매',
            'turns': [
                {
                    'ai_prompt': 'How many tickets would you like?',
                    'ai_meaning': '표 몇 장을 원하세요?',
                    'user_response': 'Two tickets for the 7 PM showing, please.',
                    'user_meaning': '오후 7시 상영분으로 표 2장 주세요.'
                },
                {
                    'ai_prompt': 'That\'s 28 dollars in total. Would you like popcorn?',
                    'ai_meaning': '총 28달러입니다. 팝콘을 원하세요?',
                    'user_response': 'Yes, one medium popcorn and two sodas.',
                    'user_meaning': '네, 중간 사이즈 팝콘과 소다 2잔으로 주세요.'
                },
                {
                    'ai_prompt': 'That will be 42 dollars. Here are your tickets and snacks.',
                    'ai_meaning': '42달러입니다. 표와 간식이 여기 있습니다.',
                    'user_response': 'Thank you! Which theater is it?',
                    'user_meaning': '감사합니다! 어느 관에서 상영하나요?'
                }
            ]
        },
        {
            'scene': '사무실에서 상사와의 대화',
            'turns': [
                {
                    'ai_prompt': 'Do you have a moment? I\'d like to discuss your project.',
                    'ai_meaning': '시간 있어요? 당신의 프로젝트에 대해 얘기하고 싶어요.',
                    'user_response': 'Of course! What do you think about the progress?',
                    'user_meaning': '물론이죠! 진행 상황에 대해 어떻게 생각하세요?'
                },
                {
                    'ai_prompt': 'The work is impressive, but we need to speed up the timeline.',
                    'ai_meaning': '작업이 인상적이지만, 일정을 앞당겨야 해요.',
                    'user_response': 'I understand. I\'ll work on that right away.',
                    'user_meaning': '알겠습니다. 지금 바로 그것을 처리하겠습니다.'
                },
                {
                    'ai_prompt': 'Great! I have confidence in you.',
                    'ai_meaning': '좋아요! 당신을 믿습니다.',
                    'user_response': 'Thank you for the support. I won\'t let you down.',
                    'user_meaning': '격려해주셔서 감사합니다. 실망시키지 않겠습니다.'
                }
            ]
        },
        {
            'scene': '전화로 예약하기',
            'turns': [
                {
                    'ai_prompt': 'Good morning. How can I help you today?',
                    'ai_meaning': '좋은 아침입니다. 오늘 무엇을 도와드릴까요?',
                    'user_response': 'I\'d like to make a reservation for dinner tomorrow night.',
                    'user_meaning': '내일 저녁 식사 예약을 하고 싶습니다.'
                },
                {
                    'ai_prompt': 'For how many people and what time?',
                    'ai_meaning': '몇 명이고 몇 시에 하시겠어요?',
                    'user_response': 'For four people at 7:30 PM, please.',
                    'user_meaning': '4명이고 오후 7시 30분으로 주세요.'
                },
                {
                    'ai_prompt': 'What name should I put the reservation under?',
                    'ai_meaning': '누구 이름으로 예약해드릴까요?',
                    'user_response': 'Under the name John Smith. Thank you!',
                    'user_meaning': 'John Smith 이름으로 부탁합니다. 감사합니다!'
                }
            ]
        },
        {
            'scene': '공항에서 환전하기',
            'turns': [
                {
                    'ai_prompt': 'Good afternoon. What can I do for you?',
                    'ai_meaning': '좋은 오후입니다. 뭘 도와드릴까요?',
                    'user_response': 'I need to exchange 500 euros for US dollars.',
                    'user_meaning': '500유로를 미국 달러로 환전해야 합니다.'
                },
                {
                    'ai_prompt': 'What\'s the current exchange rate?',
                    'ai_meaning': '현재 환율이 어떻게 되나요?',
                    'user_response': 'Today\'s rate is 1 euro equals 1.10 dollars.',
                    'user_meaning': '오늘 환율은 1유로가 1.10달러입니다.'
                },
                {
                    'ai_prompt': 'Alright. Here are your dollars. Your receipt is attached.',
                    'ai_meaning': '좋습니다. 달러가 여기 있습니다. 영수증이 붙어 있습니다.',
                    'user_response': 'Perfect! Thank you very much for your help.',
                    'user_meaning': '완벽합니다! 도와주셔서 정말 감사합니다.'
                }
            ]
        },
        {
            'scene': '사무실 신입 직원 소개',
            'turns': [
                {
                    'ai_prompt': 'Everyone, I\'d like to introduce our new team member.',
                    'ai_meaning': '여러분, 저희 새로운 팀 멤버를 소개해드리겠습니다.',
                    'user_response': 'Hello everyone! I\'m excited to join the team.',
                    'user_meaning': '안녕하세요 여러분! 팀에 합류하게 되어 기쁩니다.'
                },
                {
                    'ai_prompt': 'Where are you from?',
                    'ai_meaning': '어디서 오셨어요?',
                    'user_response': 'I\'m from California, but I moved here six months ago.',
                    'user_meaning': '저는 캘리포니아에서 왔는데, 6개월 전에 여기로 이사했습니다.'
                },
                {
                    'ai_prompt': 'Welcome aboard! I\'m sure you\'ll do great work here.',
                    'ai_meaning': '환영합니다! 여기서 멋진 일을 할 거라고 확신합니다.',
                    'user_response': 'Thank you! I\'m looking forward to working with all of you.',
                    'user_meaning': '감사합니다! 여러분 모두와 함께 일하기를 기대합니다.'
                }
            ]
        },
        {
            'scene': '카페에서 음료 주문',
            'turns': [
                {
                    'ai_prompt': 'Welcome! What can I get for you today?',
                    'ai_meaning': '환영합니다! 오늘 무엇을 드릴까요?',
                    'user_response': 'I\'d like an iced latte and a chocolate muffin.',
                    'user_meaning': '아이스 라떼와 초콜릿 머핀 주세요.'
                },
                {
                    'ai_prompt': 'What size latte would you like?',
                    'ai_meaning': '라떼는 어느 사이즈로 하실래요?',
                    'user_response': 'Medium size, please. Can I have extra ice?',
                    'user_meaning': '중간 사이즈로 주세요. 얼음을 더 넣어도 될까요?'
                },
                {
                    'ai_prompt': 'Of course! That will be 7.50 dollars.',
                    'ai_meaning': '물론이지요! 7.50달러입니다.',
                    'user_response': 'Here you go. Can I have a receipt, please?',
                    'user_meaning': '여기 있습니다. 영수증 주실 수 있을까요?'
                }
            ]
        },
        {
            'scene': '집 구하기 상담',
            'turns': [
                {
                    'ai_prompt': 'What kind of apartment are you looking for?',
                    'ai_meaning': '어떤 종류의 아파트를 찾고 있어요?',
                    'user_response': 'I need a two-bedroom apartment near the subway.',
                    'user_meaning': '지하철 근처의 2침실 아파트가 필요해요.'
                },
                {
                    'ai_prompt': 'What\'s your budget?',
                    'ai_meaning': '예산이 얼마나 되세요?',
                    'user_response': 'Around 1500 dollars per month.',
                    'user_meaning': '한 달에 약 1500달러 정도입니다.'
                },
                {
                    'ai_prompt': 'Perfect! I have a few options for you.',
                    'ai_meaning': '완벽해요! 몇 가지 옵션이 있어요.',
                    'user_response': 'Can I see them this weekend?',
                    'user_meaning': '이번 주말에 볼 수 있을까요?'
                }
            ]
        },
        {
            'scene': '자동차 렌탈',
            'turns': [
                {
                    'ai_prompt': 'Welcome to our rental agency. How can I help you?',
                    'ai_meaning': '저희 렌탈 회사에 오신 것을 환영합니다. 뭘 도와드릴까요?',
                    'user_response': 'I need to rent a car for one week.',
                    'user_meaning': '1주일 동안 자동차를 렌탈해야 해요.'
                },
                {
                    'ai_prompt': 'What type of car do you prefer?',
                    'ai_meaning': '어떤 타입의 자동차를 선호하세요?',
                    'user_response': 'An economy car, something fuel-efficient.',
                    'user_meaning': '경제형 자동차, 연료 효율이 좋은 것으로 주세요.'
                },
                {
                    'ai_prompt': 'Great! That will be 35 dollars per day.',
                    'ai_meaning': '좋습니다! 하루에 35달러입니다.',
                    'user_response': 'Does that include insurance?',
                    'user_meaning': '보험이 포함되어 있나요?'
                }
            ]
        },
        {
            'scene': '미용실 방문',
            'turns': [
                {
                    'ai_prompt': 'Hi! Do you have an appointment?',
                    'ai_meaning': '안녕하세요! 예약이 있으세요?',
                    'user_response': 'Yes, I have an appointment at 2 PM.',
                    'user_meaning': '네, 오후 2시 예약이 있어요.'
                },
                {
                    'ai_prompt': 'What would you like to do today?',
                    'ai_meaning': '오늘 뭘 해드릴까요?',
                    'user_response': 'I\'d like a haircut and some highlights.',
                    'user_meaning': '머리를 자르고 하이라이트를 해주고 싶어요.'
                },
                {
                    'ai_prompt': 'Perfect! Let me get you to a stylist.',
                    'ai_meaning': '좋습니다! 스타일리스트를 데려올게요.',
                    'user_response': 'Thank you. How long will it take?',
                    'user_meaning': '감사합니다. 얼마나 걸릴까요?'
                }
            ]
        },
        {
            'scene': '은행에서 계좌 개설',
            'turns': [
                {
                    'ai_prompt': 'Good morning. Welcome to our bank.',
                    'ai_meaning': '좋은 아침입니다. 저희 은행에 오신 것을 환영합니다.',
                    'user_response': 'I\'d like to open a checking account.',
                    'user_meaning': '당좌 계좌를 개설하고 싶습니다.'
                },
                {
                    'ai_prompt': 'Can I see your ID and passport?',
                    'ai_meaning': '신분증과 여권을 볼 수 있을까요?',
                    'user_response': 'Here you go. What documents do I need?',
                    'user_meaning': '여기 있습니다. 어떤 서류가 필요한가요?'
                },
                {
                    'ai_prompt': 'Just these two. How much will you deposit initially?',
                    'ai_meaning': '이 두 개만 있으면 됩니다. 처음에 얼마를 입금하실 건가요?',
                    'user_response': 'I\'ll deposit 500 dollars to start.',
                    'user_meaning': '시작으로 500달러를 입금할게요.'
                }
            ]
        },
        {
            'scene': '수리점에서 휴대폰 수리',
            'turns': [
                {
                    'ai_prompt': 'What seems to be the problem with your phone?',
                    'ai_meaning': '휴대폰이 어떻게 된 거 같아요?',
                    'user_response': 'The screen is cracked and the battery is dying.',
                    'user_meaning': '화면이 깨졌고 배터리가 죽어가고 있어요.'
                },
                {
                    'ai_prompt': 'I can fix that. It will cost about 150 dollars.',
                    'ai_meaning': '그걸 고쳐드릴 수 있습니다. 약 150달러가 들 거예요.',
                    'user_response': 'How long will it take?',
                    'user_meaning': '얼마나 걸릴까요?'
                },
                {
                    'ai_prompt': 'About two hours. You can wait or come back later.',
                    'ai_meaning': '약 2시간 정도 걸립니다. 기다리거나 나중에 와도 돼요.',
                    'user_response': 'I\'ll wait. Can I get a discount?',
                    'user_meaning': '기다릴게요. 할인받을 수 있을까요?'
                }
            ]
        },
        {
            'scene': '우체국에서 소포 발송',
            'turns': [
                {
                    'ai_prompt': 'Hello! How can I help you today?',
                    'ai_meaning': '안녕하세요! 오늘 무엇을 도와드릴까요?',
                    'user_response': 'I need to send this package to Japan.',
                    'user_meaning': '이 소포를 일본으로 보내야 합니다.'
                },
                {
                    'ai_prompt': 'Standard mail or express?',
                    'ai_meaning': '일반 우편이니 익스프레스니요?',
                    'user_response': 'Express, please. How much will it cost?',
                    'user_meaning': '익스프레스로 주세요. 얼마가 들까요?'
                },
                {
                    'ai_prompt': 'It will be 45 dollars. It arrives in 7 to 10 days.',
                    'ai_meaning': '45달러입니다. 7~10일 안에 도착합니다.',
                    'user_response': 'That\'s fine. I\'ll go with express.',
                    'user_meaning': '괜찮습니다. 익스프레스로 할게요.'
                }
            ]
        },
        {
            'scene': '동물원 방문',
            'turns': [
                {
                    'ai_prompt': 'Welcome to our zoo! How many tickets do you need?',
                    'ai_meaning': '저희 동물원에 오신 것을 환영합니다! 표를 몇 장 필요하세요?',
                    'user_response': 'Three tickets for adults and one for a child.',
                    'user_meaning': '성인 표 3장과 아이 표 1장으로 주세요.'
                },
                {
                    'ai_prompt': 'That\'s 60 dollars total. Would you like a guide?',
                    'ai_meaning': '총 60달러입니다. 가이드를 원하세요?',
                    'user_response': 'Yes, that would be helpful. What time does the show start?',
                    'user_meaning': '네, 그러면 좋을 것 같습니다. 쇼는 몇 시에 시작하나요?'
                },
                {
                    'ai_prompt': 'The penguin show starts at 3 PM.',
                    'ai_meaning': '펭귄 쇼는 오후 3시에 시작합니다.',
                    'user_response': 'Perfect! Here\'s my payment.',
                    'user_meaning': '좋습니다! 결제하겠습니다.'
                }
            ]
        },
        {
            'scene': '약국에서 약 구매',
            'turns': [
                {
                    'ai_prompt': 'Hi! Do you have a prescription?',
                    'ai_meaning': '안녕하세요! 처방전이 있으세요?',
                    'user_response': 'Yes, here it is. I need this medicine.',
                    'user_meaning': '네, 여기 있습니다. 이 약이 필요합니다.'
                },
                {
                    'ai_prompt': 'Let me check if we have it in stock.',
                    'ai_meaning': '재고가 있는지 확인해볼게요.',
                    'user_response': 'How much will it cost?',
                    'user_meaning': '얼마가 될까요?'
                },
                {
                    'ai_prompt': 'It\'s 35 dollars. You can pick it up in 30 minutes.',
                    'ai_meaning': '35달러입니다. 30분 후에 가져가실 수 있습니다.',
                    'user_response': 'Great! I\'ll come back later.',
                    'user_meaning': '좋습니다! 나중에 돌아올게요.'
                }
            ]
        },
        {
            'scene': '체육관 회원 가입',
            'turns': [
                {
                    'ai_prompt': 'Welcome to our gym! Are you interested in membership?',
                    'ai_meaning': '저희 헬스장에 오신 것을 환영합니다! 회원 가입에 관심 있으세요?',
                    'user_response': 'Yes, I\'d like to join. What are your membership plans?',
                    'user_meaning': '네, 가입하고 싶습니다. 회원 플랜이 뭐가 있나요?'
                },
                {
                    'ai_prompt': 'We have monthly and annual plans.',
                    'ai_meaning': '월간과 연간 플랜이 있습니다.',
                    'user_response': 'What\'s the difference in price?',
                    'user_meaning': '가격 차이가 뭐가 있나요?'
                },
                {
                    'ai_prompt': 'Monthly is 50 dollars, annual is 500.',
                    'ai_meaning': '월간은 50달러, 연간은 500달러입니다.',
                    'user_response': 'I\'ll take the annual plan.',
                    'user_meaning': '연간 플랜으로 할게요.'
                }
            ]
        },
        {
            'scene': '레스토랑 예약 변경',
            'turns': [
                {
                    'ai_prompt': 'Good afternoon. How can I help you?',
                    'ai_meaning': '좋은 오후입니다. 뭘 도와드릴까요?',
                    'user_response': 'I need to change my reservation for tonight.',
                    'user_meaning': '오늘 밤 예약을 변경해야 합니다.'
                },
                {
                    'ai_prompt': 'Of course! What time do you need instead?',
                    'ai_meaning': '물론이지요! 언제로 바꾸길 원하세요?',
                    'user_response': 'Can you move it to 8 PM instead of 7 PM?',
                    'user_meaning': '오후 7시에서 오후 8시로 바꿀 수 있을까요?'
                },
                {
                    'ai_prompt': 'That works perfectly. You\'re all set!',
                    'ai_meaning': '좋습니다! 다 준비됐습니다!',
                    'user_response': 'Thank you so much!',
                    'user_meaning': '정말 감사합니다!'
                }
            ]
        },
        {
            'scene': '피트니스 클래스 등록',
            'turns': [
                {
                    'ai_prompt': 'Which class are you interested in?',
                    'ai_meaning': '어떤 클래스에 관심이 있으세요?',
                    'user_response': 'I\'d like to try the yoga class.',
                    'user_meaning': '요가 클래스를 해보고 싶습니다.'
                },
                {
                    'ai_prompt': 'Great choice! How many sessions would you like?',
                    'ai_meaning': '좋은 선택이에요! 몇 회 수업을 원하세요?',
                    'user_response': 'Eight sessions, please. What\'s the cost?',
                    'user_meaning': '8회 수업으로 주세요. 비용이 얼마예요?'
                },
                {
                    'ai_prompt': 'That\'s 80 dollars. We can schedule you for Tuesday and Thursday.',
                    'ai_meaning': '80달러입니다. 화요일과 목요일로 스케줄을 잡아드릴 수 있습니다.',
                    'user_response': 'Perfect! When can I start?',
                    'user_meaning': '완벽합니다! 언제 시작할 수 있나요?'
                }
            ]
        },
        {
            'scene': '도서관에서 책 대출',
            'turns': [
                {
                    'ai_prompt': 'Welcome to our library. Can I help you?',
                    'ai_meaning': '저희 도서관에 오신 것을 환영합니다. 뭘 도와드릴까요?',
                    'user_response': 'I\'m looking for books about cooking.',
                    'user_meaning': '요리에 관한 책을 찾고 있습니다.'
                },
                {
                    'ai_prompt': 'We have several cookbooks. Do you prefer Italian or Asian?',
                    'ai_meaning': '요리책이 여러 권 있습니다. 이탈리안이나 아시아 요리 중 뭘 선호하세요?',
                    'user_response': 'I\'ll take both! Can I borrow them today?',
                    'user_meaning': '둘 다 가져갈게요! 오늘 빌릴 수 있나요?'
                },
                {
                    'ai_prompt': 'Of course. You can keep them for three weeks.',
                    'ai_meaning': '물론이지요. 3주 동안 보관하실 수 있습니다.',
                    'user_response': 'Great! Thank you for your help.',
                    'user_meaning': '좋습니다! 도와주셔서 감사합니다.'
                }
            ]
        },
        {
            'scene': '택시 타기',
            'turns': [
                {
                    'ai_prompt': 'Where are you headed?',
                    'ai_meaning': '어디로 가세요?',
                    'user_response': 'I need to go to the airport, please.',
                    'user_meaning': '공항으로 가주세요.'
                },
                {
                    'ai_prompt': 'Sure! That\'s about 20 miles away. It\'s rush hour so it may take 45 minutes.',
                    'ai_meaning': '물론이지요! 약 20마일 떨어져 있어요. 러시아워라서 45분 정도 걸릴 수 있습니다.',
                    'user_response': 'That\'s fine. Can I pay with a credit card?',
                    'user_meaning': '괜찮습니다. 신용카드로 결제할 수 있나요?'
                },
                {
                    'ai_prompt': 'Absolutely! We accept all major credit cards.',
                    'ai_meaning': '물론이지요! 모든 주요 신용카드를 받습니다.',
                    'user_response': 'Perfect! Let\'s go.',
                    'user_meaning': '좋습니다! 출발합시다.'
                }
            ]
        },
        {
            'scene': '옷 수선점 방문',
            'turns': [
                {
                    'ai_prompt': 'Hello! What can I help you with?',
                    'ai_meaning': '안녕하세요! 무엇을 도와드릴까요?',
                    'user_response': 'I need to have these pants hemmed.',
                    'user_meaning': '이 바지 단장을 해줘야 합니다.'
                },
                {
                    'ai_prompt': 'How much shorter would you like them?',
                    'ai_meaning': '얼마나 짧게 하고 싶으세요?',
                    'user_response': 'About two inches. How much will it cost?',
                    'user_meaning': '약 2인치 정도로 해주세요. 비용이 얼마예요?'
                },
                {
                    'ai_prompt': 'That\'s 15 dollars. I can have it done by tomorrow.',
                    'ai_meaning': '15달러입니다. 내일까지 다 해드릴 수 있어요.',
                    'user_response': 'That\'s great! I\'ll pick it up tomorrow.',
                    'user_meaning': '좋습니다! 내일 가져가겠습니다.'
                }
            ]
        },
        {
            'scene': '카페에서 일자리 인터뷰',
            'turns': [
                {
                    'ai_prompt': 'Tell me about your experience with customer service.',
                    'ai_meaning': '고객 서비스 경험에 대해 말씀해주세요.',
                    'user_response': 'I have three years of experience in retail.',
                    'user_meaning': '소매업에서 3년의 경험이 있습니다.'
                },
                {
                    'ai_prompt': 'That\'s great. How do you handle difficult customers?',
                    'ai_meaning': '좋네요. 어려운 고객들을 어떻게 다루세요?',
                    'user_response': 'I stay calm and listen to their concerns.',
                    'user_meaning': '침착함을 유지하고 그들의 불만을 경청합니다.'
                },
                {
                    'ai_prompt': 'Perfect! When can you start?',
                    'ai_meaning': '완벽합니다! 언제 시작할 수 있어요?',
                    'user_response': 'I can start next week. Thank you for the opportunity!',
                    'user_meaning': '다음주에 시작할 수 있습니다. 기회를 주셔서 감사합니다!'
                }
            ]
        },
        {
            'scene': '수영장 등록',
            'turns': [
                {
                    'ai_prompt': 'Welcome to our swimming pool. Are you interested in lessons?',
                    'ai_meaning': '저희 수영장에 오신 것을 환영합니다. 수업에 관심이 있으세요?',
                    'user_response': 'Yes, I\'d like to learn to swim.',
                    'user_meaning': '네, 수영을 배우고 싶습니다.'
                },
                {
                    'ai_prompt': 'Have you taken lessons before?',
                    'ai_meaning': '전에 수업을 받은 적이 있으세요?',
                    'user_response': 'No, I\'m a complete beginner.',
                    'user_meaning': '아니요, 완전한 초보자입니다.'
                },
                {
                    'ai_prompt': 'No problem! We have classes for all levels.',
                    'ai_meaning': '괜찮습니다! 모든 수준의 클래스가 있습니다.',
                    'user_response': 'How much are the beginner classes?',
                    'user_meaning': '초보자 클래스는 얼마예요?'
                }
            ]
        },
        {
            'scene': '치과 예약',
            'turns': [
                {
                    'ai_prompt': 'Good morning. How can I help you?',
                    'ai_meaning': '좋은 아침입니다. 뭘 도와드릴까요?',
                    'user_response': 'I\'d like to schedule a cleaning appointment.',
                    'user_meaning': '클리닝 예약을 하고 싶습니다.'
                },
                {
                    'ai_prompt': 'When would be convenient for you?',
                    'ai_meaning': '언제가 편하세요?',
                    'user_response': 'Next Wednesday at 2 PM would be perfect.',
                    'user_meaning': '다음주 수요일 오후 2시가 딱 좋습니다.'
                },
                {
                    'ai_prompt': 'Perfect! We\'ll see you then. It\'s your first visit?',
                    'ai_meaning': '좋습니다! 그때 뵙겠습니다. 첫 방문이세요?',
                    'user_response': 'Yes, can you fill out the registration form?',
                    'user_meaning': '네, 등록 양식을 작성해주실 수 있나요?'
                }
            ]
        },
        {
            'scene': '영어 학원 등록',
            'turns': [
                {
                    'ai_prompt': 'What\'s your current English level?',
                    'ai_meaning': '현재 영어 수준이 어느 정도세요?',
                    'user_response': 'I\'m intermediate. I can hold a conversation.',
                    'user_meaning': '저는 중급입니다. 대화를 할 수 있습니다.'
                },
                {
                    'ai_prompt': 'Great! We have classes that focus on business English.',
                    'ai_meaning': '좋습니다! 비즈니스 영어에 중점을 두는 클래스가 있습니다.',
                    'user_response': 'That sounds perfect for me. When do classes start?',
                    'user_meaning': '그게 저한테 딱 맞을 것 같습니다. 클래스는 언제 시작하나요?'
                },
                {
                    'ai_prompt': 'Classes start next Monday. The cost is 200 dollars per month.',
                    'ai_meaning': '클래스는 다음 월요일에 시작합니다. 한 달에 200달러입니다.',
                    'user_response': 'I\'ll register for three months, please.',
                    'user_meaning': '3개월 등록을 해주세요.'
                }
            ]
        },
        {
            'scene': '차량 정비소',
            'turns': [
                {
                    'ai_prompt': 'What brings you in today?',
                    'ai_meaning': '오늘 뭘 하러 오셨어요?',
                    'user_response': 'My car is making a strange noise. Can you check it?',
                    'user_meaning': '제 차가 이상한 소리를 내고 있어요. 확인해주실 수 있나요?'
                },
                {
                    'ai_prompt': 'Let me take a look. I\'ll need your car keys.',
                    'ai_meaning': '확인해볼게요. 자동차 열쇠가 필요합니다.',
                    'user_response': 'Here they are. How long will it take?',
                    'user_meaning': '여기 있습니다. 얼마나 걸릴까요?'
                },
                {
                    'ai_prompt': 'About 30 minutes. I\'ll call you when it\'s ready.',
                    'ai_meaning': '약 30분 정도 걸립니다. 준비되면 전화해드릴게요.',
                    'user_response': 'Thanks! I\'ll wait in the waiting room.',
                    'user_meaning': '감사합니다! 대기실에서 기다리겠습니다.'
                }
            ]
        },
        {
            'scene': '펍에서 음료 주문',
            'turns': [
                {
                    'ai_prompt': 'Hey there! What can I get you?',
                    'ai_meaning': '안녕하세요! 뭘 드릴까요?',
                    'user_response': 'I\'ll have a beer, please. What do you have on tap?',
                    'user_meaning': '맥주 한 잔 주세요. 생맥주로 뭐가 있어요?'
                },
                {
                    'ai_prompt': 'We have several local brews. Can I recommend the IPA?',
                    'ai_meaning': '여러 지역 맥주가 있습니다. IPA를 추천할까요?',
                    'user_response': 'Sure, I\'ll try that. What\'s the price?',
                    'user_meaning': '좋아요, 그걸 해볼게요. 가격이 뭐예요?'
                },
                {
                    'ai_prompt': 'Six dollars per pint.',
                    'ai_meaning': '파인트당 6달러입니다.',
                    'user_response': 'Sounds good! Can I see the menu?',
                    'user_meaning': '좋습니다! 메뉴를 볼 수 있을까요?'
                }
            ]
        },
        {
            'scene': '사진 스튜디오 예약',
            'turns': [
                {
                    'ai_prompt': 'Welcome to our studio. What type of photos do you need?',
                    'ai_meaning': '저희 스튜디오에 오신 것을 환영합니다. 어떤 종류의 사진이 필요하세요?',
                    'user_response': 'I need professional headshots for my website.',
                    'user_meaning': '웹사이트용 전문 헤드샷이 필요합니다.'
                },
                {
                    'ai_prompt': 'Great! Do you have any specific preferences?',
                    'ai_meaning': '좋습니다! 특별한 선호사항이 있으세요?',
                    'user_response': 'Yes, a natural background would be nice.',
                    'user_meaning': '네, 자연스러운 배경이면 좋을 것 같아요.'
                },
                {
                    'ai_prompt': 'Perfect! The session is 100 dollars, and you\'ll get 20 digital images.',
                    'ai_meaning': '완벽합니다! 세션은 100달러이고 디지털 이미지 20장을 받으실 수 있습니다.',
                    'user_response': 'When can you fit me in?',
                    'user_meaning': '언제 저를 들어줄 수 있나요?'
                }
            ]
        },
        {
            'scene': '호텔 체크아웃',
            'turns': [
                {
                    'ai_prompt': 'Good morning. Checking out today?',
                    'ai_meaning': '좋은 아침입니다. 오늘 체크아웃하세요?',
                    'user_response': 'Yes, I need to check out by 11 AM.',
                    'user_meaning': '네, 오전 11시까지 체크아웃해야 합니다.'
                },
                {
                    'ai_prompt': 'No problem. Did you have any room service charges?',
                    'ai_meaning': '괜찮습니다. 룸 서비스 요금이 있으셨나요?',
                    'user_response': 'I ordered coffee this morning. How much is the bill?',
                    'user_meaning': '오늘 아침에 커피를 주문했어요. 청구서가 얼마예요?'
                },
                {
                    'ai_prompt': 'Your total is 350 dollars. How would you like to pay?',
                    'ai_meaning': '총 350달러입니다. 어떻게 결제하실 건가요?',
                    'user_response': 'Credit card, please.',
                    'user_meaning': '신용카드로 주세요.'
                }
            ]
        },
        {
            'scene': '요리 교실',
            'turns': [
                {
                    'ai_prompt': 'Welcome to our cooking class! What type of cuisine are you interested in?',
                    'ai_meaning': '저희 요리 교실에 오신 것을 환영합니다! 어떤 종류의 요리에 관심이 있으세요?',
                    'user_response': 'I\'d like to learn French cooking.',
                    'user_meaning': '프랑스 요리를 배우고 싶습니다.'
                },
                {
                    'ai_prompt': 'Excellent! We have a beginner French class. When works for you?',
                    'ai_meaning': '좋습니다! 초보자 프랑스 요리 클래스가 있습니다. 언제가 좋아요?',
                    'user_response': 'I\'m free on Saturday mornings.',
                    'user_meaning': '토요일 아침에 시간이 있습니다.'
                },
                {
                    'ai_prompt': 'Perfect! Classes are 75 dollars each and run for 3 hours.',
                    'ai_meaning': '완벽합니다! 클래스는 각각 75달러이고 3시간 동안 진행됩니다.',
                    'user_response': 'Can I register for four classes?',
                    'user_meaning': '4개의 클래스로 등록할 수 있나요?'
                }
            ]
        },
        {
            'scene': '음악 레슨',
            'turns': [
                {
                    'ai_prompt': 'Hi! Do you play any instruments?',
                    'ai_meaning': '안녕하세요! 악기를 연주하세요?',
                    'user_response': 'No, I\'ve always wanted to learn guitar.',
                    'user_meaning': '아니요, 항상 기타를 배우고 싶었어요.'
                },
                {
                    'ai_prompt': 'Great! I can offer private lessons. How many lessons per week?',
                    'ai_meaning': '좋습니다! 개인 레슨을 제공할 수 있습니다. 주당 몇 회 레슨을 원하세요?',
                    'user_response': 'Twice a week would be good. What\'s your rate?',
                    'user_meaning': '주 2회가 좋을 것 같습니다. 수강료가 얼마예요?'
                },
                {
                    'ai_prompt': 'I charge 40 dollars per one-hour lesson.',
                    'ai_meaning': '1시간 레슨에 40달러를 받습니다.',
                    'user_response': 'Perfect! Can we start this week?',
                    'user_meaning': '완벽합니다! 이번 주부터 시작할 수 있나요?'
                }
            ]
        },
        {
            'scene': '춤 클래스',
            'turns': [
                {
                    'ai_prompt': 'What style of dance are you interested in?',
                    'ai_meaning': '어떤 스타일의 춤에 관심이 있으세요?',
                    'user_response': 'I\'ve always wanted to learn salsa.',
                    'user_meaning': '항상 살사를 배우고 싶었어요.'
                },
                {
                    'ai_prompt': 'Salsa is so much fun! We have a beginner class on Tuesday.',
                    'ai_meaning': '살사는 정말 재미있어요! 화요일에 초보자 클래스가 있습니다.',
                    'user_response': 'Tuesday works for me. How many people are in the class?',
                    'user_meaning': '화요일이 괜찮습니다. 클래스에 사람이 몇 명이에요?'
                },
                {
                    'ai_prompt': 'About 12 people. The class costs 50 dollars per month.',
                    'ai_meaning': '약 12명입니다. 한 달에 50달러입니다.',
                    'user_response': 'I\'ll sign up! When does it start?',
                    'user_meaning': '등록할게요! 언제 시작하나요?'
                }
            ]
        },
        {
            'scene': '생일 파티 계획',
            'turns': [
                {
                    'ai_prompt': 'Hello! What type of party are you planning?',
                    'ai_meaning': '안녕하세요! 어떤 종류의 파티를 계획하고 있어요?',
                    'user_response': 'I\'m planning a birthday party for my friend.',
                    'user_meaning': '친구 생일 파티를 계획하고 있습니다.'
                },
                {
                    'ai_prompt': 'How many guests are you expecting?',
                    'ai_meaning': '손님이 몇 명 정도 올 예정이에요?',
                    'user_response': 'About 30 people. Can you provide catering?',
                    'user_meaning': '약 30명 정도입니다. 케이터링을 제공해주실 수 있나요?'
                },
                {
                    'ai_prompt': 'Of course! We can do appetizers, main course, and desserts.',
                    'ai_meaning': '물론이지요! 에피타이저, 메인 코스, 디저트를 제공할 수 있습니다.',
                    'user_response': 'What\'s the price per person?',
                    'user_meaning': '1인당 가격이 얼마예요?'
                }
            ]
        },
        {
            'scene': '정원 관리 서비스',
            'turns': [
                {
                    'ai_prompt': 'Thank you for calling. What garden work do you need?',
                    'ai_meaning': '전화해주셔서 감사합니다. 어떤 정원 작업이 필요하세요?',
                    'user_response': 'I need my lawn mowed and some trimming done.',
                    'user_meaning': '잔디를 깎고 일부를 정리해줄 필요가 있습니다.'
                },
                {
                    'ai_prompt': 'How large is your lawn?',
                    'ai_meaning': '잔디가 얼마나 크세요?',
                    'user_response': 'It\'s about half an acre.',
                    'user_meaning': '약 반 에이커 정도입니다.'
                },
                {
                    'ai_prompt': 'That\'s 75 dollars for mowing and 50 for trimming.',
                    'ai_meaning': '깎기가 75달러이고 정리가 50달러입니다.',
                    'user_response': 'Can you come next Saturday?',
                    'user_meaning': '다음 토요일에 올 수 있나요?'
                }
            ]
        },
        {
            'scene': '보모 고용',
            'turns': [
                {
                    'ai_prompt': 'Tell me about your childcare experience.',
                    'ai_meaning': '보육 경험에 대해 말씀해주세요.',
                    'user_response': 'I have five years of experience caring for young children.',
                    'user_meaning': '어린 아이들을 돌본 5년의 경험이 있습니다.'
                },
                {
                    'ai_prompt': 'That\'s wonderful! How many children do you typically care for?',
                    'ai_meaning': '좋습니다! 보통 아이를 몇 명 돌봐요?',
                    'user_response': 'I can handle up to 3 children.',
                    'user_meaning': '최대 3명까지 돌볼 수 있습니다.'
                },
                {
                    'ai_prompt': 'Perfect! We need someone for weekends. The pay is 15 dollars per hour.',
                    'ai_meaning': '완벽합니다! 주말에 필요합니다. 시급은 15달러입니다.',
                    'user_response': 'That works for me. When can I start?',
                    'user_meaning': '그게 괜찮습니다. 언제 시작할 수 있나요?'
                }
            ]
        },
        {'scene': '야근 후 상사와의 대화', 'turns': [{'ai_prompt': 'Great work today. Are you heading home?', 'ai_meaning': '오늘 잘했어요. 집에 가세요?', 'user_response': 'Yes, I\'m exhausted. See you tomorrow!', 'user_meaning': '네, 피곤합니다. 내일 봐요!'}, {'ai_prompt': 'You deserve a rest. Have a good night.', 'ai_meaning': '휴식을 취할 자격이 있어요. 좋은 밤 되세요.', 'user_response': 'Thank you, you too!', 'user_meaning': '감사합니다. 당신도요!'}, {'ai_prompt': 'Drive safely!', 'ai_meaning': '안전하게 운전하세요!', 'user_response': 'I will. Goodnight!', 'user_meaning': '그럼요. 안녕히!'}]},
        {'scene': '스타벅스에서 친구 만나기', 'turns': [{'ai_prompt': 'Hey! Sorry I\'m late!', 'ai_meaning': '안녕! 늦어서 미안!', 'user_response': 'No problem. I just got here too.', 'user_meaning': '괜찮아. 나도 방금 왔어.'}, {'ai_prompt': 'How have you been?', 'ai_meaning': '요즘 어떻게 지냈어?', 'user_response': 'Really good. I got a promotion!', 'user_meaning': '정말 좋아. 승진했어!'}, {'ai_prompt': 'Congratulations! I\'m so proud of you!', 'ai_meaning': '축하해! 정말 자랑스러워!', 'user_response': 'Thanks! Let\'s celebrate with coffee!', 'user_meaning': '고마워! 커피로 축하하자!'}]},
        {'scene': '약국에서 기침약 구매', 'turns': [{'ai_prompt': 'I\'m looking for cough medicine.', 'ai_meaning': '기침약을 찾고 있어요.', 'user_response': 'We have several options. What kind of cough do you have?', 'user_meaning': '여러 옵션이 있습니다. 어떤 종류의 기침이 있어요?'}, {'ai_prompt': 'A dry cough that won\'t go away.', 'ai_meaning': '사라지지 않는 마른 기침이에요.', 'user_response': 'This one is perfect for that. Take it twice daily.', 'user_meaning': '이것이 좋아요. 하루에 두 번 복용하세요.'}, {'ai_prompt': 'How much is it?', 'ai_meaning': '얼마예요?', 'user_response': 'That\'s 12 dollars. Get well soon!', 'user_meaning': '12달러입니다. 빨리 나으세요!'}]},
        {'scene': '영화 다 본 후 친구와 대화', 'turns': [{'ai_prompt': 'What did you think of the movie?', 'ai_meaning': '영화 어땠어?', 'user_response': 'It was amazing! The ending was so unexpected!', 'user_meaning': '정말 좋았어! 결말이 예상 밖이었어!'}, {'ai_prompt': 'Right? I didn\'t see that coming either.', 'ai_meaning': '맞아? 나도 몰랐어.', 'user_response': 'Me neither! It was such a plot twist!', 'user_meaning': '나도! 정말 반전이 있었어!'}, {'ai_prompt': 'Shall we grab dinner and discuss it more?', 'ai_meaning': '저녁 먹으면서 더 얘기할까?', 'user_response': 'Perfect! I\'m starving anyway!', 'user_meaning': '좋아! 나도 배고프니까!'}]},
        {'scene': '동료 생일 축하하기', 'turns': [{'ai_prompt': 'Happy birthday! I baked you a cake!', 'ai_meaning': '생일 축하해! 케이크를 구웠어!', 'user_response': 'Oh my God! Thank you so much!', 'user_meaning': '오마이갓! 정말 고마워!'}, {'ai_prompt': 'Make a wish and blow out the candles.', 'ai_meaning': '소원을 빌고 양초를 불어!', 'user_response': 'Done! This is the best birthday ever!', 'user_meaning': '했어! 이게 최고의 생일이야!'}]},
        {'scene': '부동산 중개소 방문', 'turns': [{'ai_prompt': 'Welcome! Are you looking to buy or rent?', 'ai_meaning': '환영합니다! 구매하거나 임차하시나요?', 'user_response': 'I\'m looking to buy. What\'s available in this area?', 'user_meaning': '구매하려고 합니다. 이 지역에 뭐가 있어요?'}, {'ai_prompt': 'We have several nice properties. Let me show you some listings.', 'ai_meaning': '좋은 건물이 몇 개 있어요. 리스팅을 보여드릴게요.', 'user_response': 'Great! How much is the average price?', 'user_meaning': '좋습니다! 평균 가격이 얼마예요?'}]},
        {'scene': '패션쇼에서 모델 캐스팅', 'turns': [{'ai_prompt': 'You have excellent height and features.', 'ai_meaning': '키와 외모가 훌륭하네요.', 'user_response': 'Thank you! I\'ve always wanted to be a model.', 'user_meaning': '감사합니다! 항상 모델이 되고 싶었어요.'}, {'ai_prompt': 'We\'d like to have you in our next show.', 'ai_meaning': '다음 쇼에 참여해주시면 좋겠습니다.', 'user_response': 'Really? I\'d love to! When is it?', 'user_meaning': '정말요? 정말 좋아요! 언제예요?'}]},
        {'scene': '회사 회의실에서 발표', 'turns': [{'ai_prompt': 'Good morning everyone. Let me present our new strategy.', 'ai_meaning': '좋은 아침입니다 여러분. 새로운 전략을 제시하겠습니다.', 'user_response': 'Please, go ahead. We\'re listening.', 'user_meaning': '계속하세요. 우리가 듣고 있습니다.'}]},
        {'scene': '미팅 후 커피 브레이크', 'turns': [{'ai_prompt': 'That was a productive meeting!', 'ai_meaning': '좋은 미팅이었네요!', 'user_response': 'Yes, I think we covered all the important points.', 'user_meaning': '네, 모든 중요한 포인트를 다뤘다고 생각해요.'}, {'ai_prompt': 'Let\'s grab coffee and relax a bit.', 'ai_meaning': '커피 마시고 좀 쉬어요.', 'user_response': 'Sounds perfect! I need a break!', 'user_meaning': '좋아요! 휴식이 필요해!'}]},
        {'scene': '온라인 쇼핑 배송 확인', 'turns': [{'ai_prompt': 'Your package has arrived! Can you sign here?', 'ai_meaning': '소포가 도착했습니다! 여기에 서명해주실 수 있을까요?', 'user_response': 'Perfect timing! I was waiting for this.', 'user_meaning': '완벽한 타이밍이네! 기다리고 있었어.'}, {'ai_prompt': 'Have a great day!', 'ai_meaning': '좋은 하루 되세요!', 'user_response': 'You too, thank you!', 'user_meaning': '당신도요, 감사합니다!'}]},
        {'scene': '새 학교 첫 날', 'turns': [{'ai_prompt': 'Hi there! This is your first day, right?', 'ai_meaning': '안녕! 첫 날이지?', 'user_response': 'Yes, I\'m a bit nervous. Can you help me?', 'user_meaning': '네, 좀 긴장돼요. 도와줄 수 있어요?'}, {'ai_prompt': 'Of course! Let me show you around.', 'ai_meaning': '물론이지! 둘러보게 해줄게.', 'user_response': 'Thanks, I really appreciate it!', 'user_meaning': '고마워, 정말 감사해!'}]},
        {'scene': '의사 진료 예약 확인', 'turns': [{'ai_prompt': 'Your appointment is confirmed for next Tuesday at 3 PM.', 'ai_meaning': '다음 주 화요일 오후 3시 예약이 확인되었습니다.', 'user_response': 'Perfect! I\'ll see you then.', 'user_meaning': '좋습니다! 그때 뵐게요.'}, {'ai_prompt': 'Please bring your insurance card.', 'ai_meaning': '보험 카드를 가져오세요.', 'user_response': 'I will. See you next week!', 'user_meaning': '그럼요. 다음 주에!'}]},
        {'scene': '카페 사장과 직원 대화', 'turns': [{'ai_prompt': 'We have a busy day ahead. Are you ready?', 'ai_meaning': '바쁜 하루가 될 것 같아요. 준비됐어요?', 'user_response': 'Yes! I\'m all set. Let\'s do this!', 'user_meaning': '네! 준비됐어요. 해봐요!'}, {'ai_prompt': 'Great attitude! Let\'s open up.', 'ai_meaning': '좋은 태도네요! 열어봐요.', 'user_response': 'Let\'s go make some great coffee!', 'user_meaning': '좋은 커피를 만들어봐요!'}]},
        {'scene': '은행 대출 상담', 'turns': [{'ai_prompt': 'How much are you looking to borrow?', 'ai_meaning': '얼마를 빌리고 싶으세요?', 'user_response': 'I need 200,000 dollars for a house down payment.', 'user_meaning': '주택 선금으로 20만 달러가 필요합니다.'}, {'ai_prompt': 'What\'s your annual income?', 'ai_meaning': '연간 소득이 얼마인가요?', 'user_response': 'About 80,000 dollars per year.', 'user_meaning': '연간 약 8만 달러입니다.'}]},
        {'scene': '택배 배송 실패 후 재배송', 'turns': [{'ai_prompt': 'I\'m sorry, nobody answered. Can we try again tomorrow?', 'ai_meaning': '죄송합니다. 아무도 답하지 않았어요. 내일 다시 시도할 수 있을까요?', 'user_response': 'Yes, I\'ll be home all day tomorrow.', 'user_meaning': '네, 내일 하루 종일 집에 있을게요.'}, {'ai_prompt': 'Perfect! See you tomorrow then.', 'ai_meaning': '좋습니다! 내일 뵐게요.', 'user_response': 'Thank you for your patience!', 'user_meaning': '인내심 감사합니다!'}]},
        {'scene': '카페에서 데이트 시작', 'turns': [{'ai_prompt': 'You look beautiful today!', 'ai_meaning': '오늘 정말 예뻐요!', 'user_response': 'Thank you! You look nice too.', 'user_meaning': '감사해요! 넌 더 잘 생겼어.'}, {'ai_prompt': 'I\'m really glad we\'re doing this.', 'ai_meaning': '우리가 함께 해서 정말 기뻐요.', 'user_response': 'Me too! So, tell me about yourself.', 'user_meaning': '나도야! 그래서 너 자신에 대해 말해줄래?'}]},
        {'scene': '회사 소풍 계획 회의', 'turns': [{'ai_prompt': 'So, what should we do for the company picnic?', 'ai_meaning': '그래서 회사 소풍에 뭘 할까요?', 'user_response': 'How about a beach trip? Everyone loves the beach.', 'user_meaning': '해변 여행은 어때요? 모두가 해변을 좋아해요.'}, {'ai_prompt': 'That\'s a great idea! When should we go?', 'ai_meaning': '좋은 생각이에요! 언제 가면 될까요?', 'user_response': 'Next month would be perfect.', 'user_meaning': '다음달이 좋을 것 같아요.'}]},
        {'scene': '짐 짐싸기 여행 준비', 'turns': [{'ai_prompt': 'Did you pack everything?', 'ai_meaning': '다 챙겼어?', 'user_response': 'I think so. Let me double check my list.', 'user_meaning': '그럴 거야. 리스트를 다시 확인해봐.'}, {'ai_prompt': 'Don\'t forget your passport!', 'ai_meaning': '여권 잊지 마!', 'user_response': 'Already in my bag! Let\'s go!', 'user_meaning': '이미 가방에 있어! 가자!'}]},
        {'scene': '음악 콘서트 표 구매', 'turns': [{'ai_prompt': 'Two tickets for the concert next week?', 'ai_meaning': '다음주 콘서트 표 2장?', 'user_response': 'Yes, front row if you have them.', 'user_meaning': '네, 있으면 맨 앞줄로.'}, {'ai_prompt': 'You\'re lucky! Front row is available.', 'ai_meaning': '운이 좋으셨어요! 맨 앞줄이 있어요.', 'user_response': 'Awesome! How much?', 'user_meaning': '좋아! 얼마예요?'}]},
        {'scene': '자동차 정비 예약', 'turns': [{'ai_prompt': 'My car is making weird noises. Can you check it?', 'ai_meaning': '제 차가 이상한 소리를 내요. 확인해주실 수 있나요?', 'user_response': 'Bring it in tomorrow morning.', 'user_meaning': '내일 아침에 가져오세요.'}, {'ai_prompt': 'What time should I come?', 'ai_meaning': '몇 시에 와야 할까요?', 'user_response': 'Anytime after 8 AM is fine.', 'user_meaning': '오전 8시 이후 아무 때나 괜찮아요.'}]},
        {'scene': '고등학교 학부모-교사 면담', 'turns': [{'ai_prompt': 'Your son is doing very well in my class.', 'ai_meaning': '당신의 아들이 제 반에서 매우 잘하고 있습니다.', 'user_response': 'That\'s wonderful to hear! What about his math skills?', 'user_meaning': '정말 좋네요! 수학 실력은 어떤가요?'}, {'ai_prompt': 'He\'s excelling in that too.', 'ai_meaning': '그것도 뛰어나고 있습니다.', 'user_response': 'Great! We\'re very proud of him.', 'user_meaning': '좋습니다! 우리 정말 자랑스러워합니다.'}]},
        {'scene': '피자 피자 배달 전화', 'turns': [{'ai_prompt': 'Pizza Palace, what can I get for you?', 'ai_meaning': 'Pizza Palace입니다. 뭘 드릴까요?', 'user_response': 'I\'d like a large pepperoni pizza.', 'user_meaning': '큰 페퍼로니 피자 주세요.'}, {'ai_prompt': 'Anything to drink?', 'ai_meaning': '음료는 있을까요?', 'user_response': 'Yes, two colas please.', 'user_meaning': '네, 콜라 2개 주세요.'}]},
        {'scene': '손님으로서 집 구경', 'turns': [{'ai_prompt': 'Welcome to our home! Make yourself comfortable.', 'ai_meaning': '우리 집에 오신 것을 환영합니다! 편하게 하세요.', 'user_response': 'Thank you! Your home is beautiful!', 'user_meaning': '감사합니다! 당신의 집이 정말 예뻐요!'}, {'ai_prompt': 'Would you like some refreshments?', 'ai_meaning': '음료 좀 드릴까요?', 'user_response': 'That would be nice. Thank you!', 'user_meaning': '좋겠어요. 감사합니다!'}]},
        {'scene': '시장에서 야채 사기', 'turns': [{'ai_prompt': 'Fresh vegetables! Very fresh today!', 'ai_meaning': '신선한 야채! 오늘 정말 신선합니다!', 'user_response': 'How much are the tomatoes?', 'user_meaning': '토마토는 얼마예요?'}, {'ai_prompt': 'Two dollars per pound.', 'ai_meaning': '파운드당 2달러입니다.', 'user_response': 'I\'ll take two pounds. And some lettuce too.', 'user_meaning': '2파운드 주세요. 상추도 좀.'}]},
        {'scene': '병원 응급실 방문', 'turns': [{'ai_prompt': 'What happened? Are you hurt?', 'ai_meaning': '무슨 일이에요? 다쳤어요?', 'user_response': 'I fell and I think I broke my arm.', 'user_meaning': '넘어졌는데 팔이 부러진 것 같아요.'}, {'ai_prompt': 'Let me examine you. We\'ll take an X-ray.', 'ai_meaning': '검사해드릴게요. X-레이를 찍을게요.', 'user_response': 'Okay. Will I need surgery?', 'user_meaning': '네. 수술이 필요할까요?'}]},
        {'scene': '체육관 트레이너와 상담', 'turns': [{'ai_prompt': 'What are your fitness goals?', 'ai_meaning': '운동 목표가 뭐예요?', 'user_response': 'I want to build muscle and lose weight.', 'user_meaning': '근육을 키우고 체중을 줄이고 싶어요.'}, {'ai_prompt': 'I can help you with that. Let\'s create a plan.', 'ai_meaning': '도와드릴 수 있어요. 계획을 세워봐요.', 'user_response': 'Great! When can we start?', 'user_meaning': '좋습니다! 언제 시작할 수 있나요?'}]},
        {'scene': '친구 사기 피한 후 상담', 'turns': [{'ai_prompt': 'I heard what happened. Are you okay?', 'ai_meaning': '무슨 일이 있었는지 들었어요. 괜찮아요?', 'user_response': 'Not really. I trusted him so much.', 'user_meaning': '아니에요. 나는 그를 정말 믿었어요.'}, {'ai_prompt': 'That\'s terrible. Have you reported it?', 'ai_meaning': '정말 형편없네요. 신고했어요?', 'user_response': 'Yes, I went to the police.', 'user_meaning': '네, 경찰서에 갔어요.'}]},
        {'scene': '버스 정류장에서 길 묻기', 'turns': [{'ai_prompt': 'Excuse me, which bus goes to downtown?', 'ai_meaning': '미안해요. 어느 버스가 다운타운으로 가요?', 'user_response': 'The number 15. It\'s coming in five minutes.', 'user_meaning': '15번 버스예요. 5분 후에 올 거예요.'}, {'ai_prompt': 'Thank you so much!', 'ai_meaning': '정말 감사합니다!', 'user_response': 'You\'re welcome! Good luck!', 'user_meaning': '환영합니다! 행운을 빕니다!'}]},
        {'scene': '회사 휴게실에서 점심', 'turns': [{'ai_prompt': 'Hey, want to grab lunch together?', 'ai_meaning': '안녕, 함께 점심 먹을래?', 'user_response': 'Sure! I packed a sandwich though.', 'user_meaning': '좋아! 그런데 난 샌드위치를 싸왔어.'}, {'ai_prompt': 'That\'s fine. We can eat together anyway.', 'ai_meaning': '괜찮아. 어쨌든 함께 먹을 수 있어.', 'user_response': 'Good idea! Let\'s eat together.', 'user_meaning': '좋은 생각이야! 함께 먹자.'}, {'ai_prompt': 'How\'s the project going?', 'ai_meaning': '프로젝트는 어떻게 진행되고 있어?', 'user_response': 'It\'s almost done. Should be finished by Friday!', 'user_meaning': '거의 다 됐어. 금요일까지 끝날 거야!'}]},
        {'scene': '안경점 방문 및 시력 검사', 'turns': [{'ai_prompt': 'Can you read this line?', 'ai_meaning': '이 줄을 읽을 수 있어요?', 'user_response': 'A little blurry. Next one?', 'user_meaning': '조금 흐려요. 다음은?'}, {'ai_prompt': 'Better?', 'ai_meaning': '낫습니까?', 'user_response': 'Much better! These work perfectly.', 'user_meaning': '훨씬 낫습니다! 이건 완벽합니다.'}]},
        {'scene': '팀 프로젝트 진행 상황 회의', 'turns': [{'ai_prompt': 'Everyone, let\'s review the project progress.', 'ai_meaning': '여러분, 프로젝트 진행 상황을 검토해봐요.', 'user_response': 'My team finished our section ahead of schedule.', 'user_meaning': '제 팀은 우리 부분을 일정보다 빨리 완료했어요.'}, {'ai_prompt': 'Excellent work! Can you help the other team?', 'ai_meaning': '훌륭한 일이에요! 다른 팀을 도와줄 수 있어요?', 'user_response': 'Of course! I\'m happy to help.', 'user_meaning': '물론이지요! 기꺼이 도와드릴게요.'}]},
        {'scene': '지하철 혼잡한 시간대 탑승', 'turns': [{'ai_prompt': 'Excuse me, is this train going to the airport?', 'ai_meaning': '미안해요. 이 열차가 공항으로 가나요?', 'user_response': 'Yes, just hold on tight! It\'s crowded today.', 'user_meaning': '네, 꼭 잡으세요! 오늘 붐비네요.'}]},
        {'scene': '식당 테이블 예약 확인', 'turns': [{'ai_prompt': 'Good evening. Do you have a reservation?', 'ai_meaning': '좋은 저녁입니다. 예약이 있으세요?', 'user_response': 'Yes, under Smith for 7 PM.', 'user_meaning': '네, Smith 이름으로 오후 7시 예약했어요.'}, {'ai_prompt': 'Right this way, your table is ready.', 'ai_meaning': '이쪽으로 오세요, 테이블 준비됐습니다.', 'user_response': 'Thank you! This is a beautiful restaurant.', 'user_meaning': '감사합니다! 정말 멋진 레스토랑이네요.'}]},
        {'scene': '운동화 쇼핑', 'turns': [{'ai_prompt': 'Looking for running shoes?', 'ai_meaning': '운동화를 찾고 계세요?', 'user_response': 'Yes, I need something for marathon training.', 'user_meaning': '네, 마라톤 훈련용으로 필요해요.'}, {'ai_prompt': 'I have the perfect pair. Try these.', 'ai_meaning': '완벽한 신발이 있어요. 이것을 신어봐요.', 'user_response': 'These feel great! I\'ll take them!', 'user_meaning': '이거 진짜 편해요! 이거 살게요!'}]},
        {'scene': '변호사 상담', 'turns': [{'ai_prompt': 'Tell me about your case.', 'ai_meaning': '당신의 사건에 대해 말씀해주세요.', 'user_response': 'My business partner stole my money.', 'user_meaning': '제 사업 파트너가 제 돈을 훔쳤어요.'}, {'ai_prompt': 'Do you have evidence?', 'ai_meaning': '증거가 있으세요?', 'user_response': 'I have emails and bank statements.', 'user_meaning': '이메일과 은행 통장이 있어요.'}]},
        {'scene': '미용사 상담 및 헤어 디자인', 'turns': [{'ai_prompt': 'What style are you thinking?', 'ai_meaning': '어떤 스타일을 생각하고 있어요?', 'user_response': 'Something fresh and modern. Not too short though.', 'user_meaning': '신선하고 현대적인 스타일. 너무 짧지는 않게.'}, {'ai_prompt': 'I have the perfect cut for you.', 'ai_meaning': '당신한테 딱 맞는 컷이 있어요.', 'user_response': 'Great! Let\'s do it!', 'user_meaning': '좋아요! 해봐요!'}]},
        {'scene': '불 나고 응급 상황', 'turns': [{'ai_prompt': 'Call 911! There\'s a fire!', 'ai_meaning': '911에 전화해! 불이 났어!', 'user_response': 'I\'m calling now! Everyone evacuate!', 'user_meaning': '지금 전화할게! 모두 대피해!'}, {'ai_prompt': 'I\'m calling now! Everyone evacuate!', 'ai_meaning': '지금 전화할게! 모두 대피해!', 'user_response': 'Get out now! Meet at the parking lot!', 'user_meaning': '지금 나가! 주차장에서 만나자!'}]},
        {'scene': '분실물 찾기', 'turns': [{'ai_prompt': 'Excuse me, did anyone turn in a wallet?', 'ai_meaning': '미안해요. 누가 지갑을 주셨어요?', 'user_response': 'Yes! Someone turned one in this morning.', 'user_meaning': '네! 누군가 오늘 아침에 줬어요.'}, {'ai_prompt': 'Thank you so much! I\'ve been looking everywhere!', 'ai_meaning': '정말 감사합니다! 계속 찾고 있었어요!', 'user_response': 'Of course! Is this yours?', 'user_meaning': '당연하지! 이게 당신 거예요?'}]},
        {'scene': '스포츠 경기 결과 축하', 'turns': [{'ai_prompt': 'We won! Did you see that game?', 'ai_meaning': '이겼어! 그 경기 봤어?', 'user_response': 'Yes! That was amazing! Best game ever!', 'user_meaning': '네! 정말 좋았어! 최고의 경기였어!'}, {'ai_prompt': 'Our team was incredible!', 'ai_meaning': '우리 팀이 정말 대단했어!', 'user_response': 'They deserve it! Let\'s celebrate!', 'user_meaning': '당연해! 축하해야지!'}]},
        {'scene': '온라인 쇼핑 반품', 'turns': [{'ai_prompt': 'I need to return this item. It doesn\'t fit.', 'ai_meaning': '이 물건을 반품해야 합니다. 사이즈가 안 맞네요.', 'user_response': 'Sure, we can help with that.', 'user_meaning': '물론, 도와드릴게요.'}, {'ai_prompt': 'No problem. We have a 30-day return policy.', 'ai_meaning': '괜찮습니다. 30일 반품 정책이 있습니다.', 'user_response': 'Great! How long will the refund take?', 'user_meaning': '좋습니다! 환불은 얼마나 걸려요?'}]},
        {'scene': '새 직원 첫날 교육', 'turns': [{'ai_prompt': 'Welcome to the team! Let me show you around.', 'ai_meaning': '팀에 오신 것을 환영합니다! 둘러봐요.', 'user_response': 'Thank you! I\'m excited to be here!', 'user_meaning': '감사합니다! 여기 있어서 정말 기뻐요!'}, {'ai_prompt': 'Everyone is very friendly. You\'ll fit right in.', 'ai_meaning': '모두 정말 친절해요. 잘 적응할 거예요.', 'user_response': 'I hope so! What\'s my first task?', 'user_meaning': '그럴 거 같아요! 첫 번째 일은 뭐예요?'}]},
        {'scene': '공항 선물 구매', 'turns': [{'ai_prompt': 'Are you looking for souvenirs?', 'ai_meaning': '기념품을 찾고 있어요?', 'user_response': 'Yes, something typical from this city.', 'user_meaning': '네, 이 도시의 전형적인 것 좀.'}, {'ai_prompt': 'These local crafts are very popular.', 'ai_meaning': '이 지역 공예품이 정말 인기 있어요.', 'user_response': 'Perfect! I\'ll take three of these.', 'user_meaning': '좋습니다! 이거 3개 주세요.'}]},
        {'scene': '신문배달원과 계약 취소', 'turns': [{'ai_prompt': 'I\'d like to cancel my newspaper subscription.', 'ai_meaning': '신문 구독을 취소하고 싶습니다.', 'user_response': 'I understand. Let me process that for you.', 'user_meaning': '알겠습니다. 처리해드리겠습니다.'}, {'ai_prompt': 'May I ask why?', 'ai_meaning': '이유를 물어봐도 될까요?', 'user_response': 'I\'ve switched to reading news online.', 'user_meaning': '온라인에서 뉴스를 읽기로 바꿨어요.'}]},
        {'scene': '회의실에서 브레인스토밍', 'turns': [{'ai_prompt': 'Let\'s brainstorm some new ideas for the campaign.', 'ai_meaning': '캠페인을 위한 새로운 아이디어를 브레인스토밍해봐요.', 'user_response': 'I think we should focus on social media.', 'user_meaning': '소셜 미디어에 집중해야 할 것 같아요.'}, {'ai_prompt': 'Great idea! How would you implement that?', 'ai_meaning': '좋은 생각이네요! 어떻게 시행할 건가요?', 'user_response': 'We could create viral content and engage followers.', 'user_meaning': '바이러스 성 콘텐츠를 만들고 팔로워를 참여시킬 수 있어요.'}]},
        {'scene': '친구와 싸운 후 화해', 'turns': [{'ai_prompt': 'I\'m sorry about what I said. I didn\'t mean it.', 'ai_meaning': '제가 말한 것에 대해 미안합니다. 진심이 아니었어요.', 'user_response': 'I know. I was upset too.', 'user_meaning': '알아요. 나도 화났었어요.'}, {'ai_prompt': 'I know. I was upset too.', 'ai_meaning': '알아요. 나도 화났었어요.', 'user_response': 'Can we just move past it? You\'re my best friend.', 'user_meaning': '그냥 넘어가자. 넌 내 친구 중 최고야.'}]},
        {'scene': '휴가 계획 짜기', 'turns': [{'ai_prompt': 'Where should we go for vacation?', 'ai_meaning': '휴가 어디로 갈까요?', 'user_response': 'How about Hawaii? I\'ve always wanted to go.', 'user_meaning': '하와이는 어때요? 항상 가고 싶었어요.'}, {'ai_prompt': 'That sounds amazing! When can we go?', 'ai_meaning': '정말 좋네요! 언제 갈 수 있을까요?', 'user_response': 'Maybe next summer? That gives us time to plan.', 'user_meaning': '내년 여름은 어떨까요? 계획할 시간이 있어요.'}]},
        {'scene': '피트니스 클래스 첫 참여', 'turns': [{'ai_prompt': 'Welcome! Is this your first time?', 'ai_meaning': '환영합니다! 처음이세요?', 'user_response': 'Yes, I\'m a bit nervous. What should I expect?', 'user_meaning': '네, 좀 긴장돼요. 무엇을 기대할 수 있을까요?'}, {'ai_prompt': 'Don\'t worry! It\'s fun and the class is very supportive.', 'ai_meaning': '걱정 안 하셔도 돼요! 재미있고 반이 정말 서포트해요.', 'user_response': 'Okay, let\'s do this!', 'user_meaning': '좋아, 해봐요!'}]},
        {'scene': '인테리어 디자이너 상담', 'turns': [{'ai_prompt': 'Tell me about your vision for this room.', 'ai_meaning': '이 방에 대한 당신의 비전을 말씀해주세요.', 'user_response': 'I want something modern but warm.', 'user_meaning': '현대적이지만 따뜻한 분위기를 원해요.'}, {'ai_prompt': 'I want something modern but warm.', 'ai_meaning': '현대적이지만 따뜻한 분위기를 원해요.', 'user_response': 'I can make that happen. Let me show you some options.', 'user_meaning': '그렇게 할 수 있어요. 옵션을 보여드릴게요.'}]},
        {'scene': '병원 처방전 약 약사와 대화', 'turns': [{'ai_prompt': 'I have a few questions about this medication.', 'ai_meaning': '이 약에 대해 몇 가지 질문이 있어요.', 'user_response': 'Of course. What would you like to know?', 'user_meaning': '물론이지요. 뭘 알고 싶으세요?'}, {'ai_prompt': 'Are there any side effects?', 'ai_meaning': '부작용이 있나요?', 'user_response': 'Some people experience mild dizziness. Take it with food.', 'user_meaning': '일부는 가벼운 현기증을 경험합니다. 음식과 함께 복용하세요.'}]},
        {'scene': '차 사기 협상', 'turns': [{'ai_prompt': 'This car is in excellent condition.', 'ai_meaning': '이 차는 정말 좋은 상태입니다.', 'user_response': 'It looks very nice! How much are you asking?', 'user_meaning': '정말 멋져 보이네요! 얼마를 원하세요?'}, {'ai_prompt': 'How much are you asking?', 'ai_meaning': '얼마를 원하세요?', 'user_response': '$15,000, but I\'m willing to negotiate.', 'user_meaning': '$15,000인데 협상할 수 있어요.'}]},
        {'scene': '사무실 휴게실에서 팀 게임', 'turns': [{'ai_prompt': 'Anyone up for a quick game? We have 15 minutes.', 'ai_meaning': '누가 짧은 게임 할 사람? 15분 있어요.', 'user_response': 'Sure! That\'s a great idea to unwind!', 'user_meaning': '좋아! 스트레스 풀기에 좋아!'}]},
        {'scene': '케이크 가게에서 결혼식 케이크 주문', 'turns': [{'ai_prompt': 'Congratulations on your engagement!', 'ai_meaning': '약혼을 축하합니다!', 'user_response': 'Thank you! We\'d like to order a wedding cake.', 'user_meaning': '감사합니다! 웨딩 케이크를 주문하고 싶어요.'}, {'ai_prompt': 'Thank you! We\'d like to order a wedding cake.', 'ai_meaning': '감사합니다! 웨딩 케이크를 주문하고 싶어요.', 'user_response': 'What flavors do you prefer?', 'user_meaning': '어떤 맛을 선호하세요?'}]},
        {'scene': '헬스장 PT 세션', 'turns': [{'ai_prompt': 'Okay, let\'s start with warm-up stretches.', 'ai_meaning': '좋아요, 워밍업 스트레칭부터 시작해요.', 'user_response': 'How many sets of each exercise?', 'user_meaning': '각 운동마다 몇 세트?'}, {'ai_prompt': 'Three sets of 10 reps. Let\'s go!', 'ai_meaning': '3세트 10반복. 해봐요!', 'user_response': 'I\'m ready! Let\'s burn some calories!', 'user_meaning': '준비됐어! 칼로리 태워버리자!'}]},
        {'scene': '음악 스튜디오 인터뷰', 'turns': [{'ai_prompt': 'Tell me about your musical background.', 'ai_meaning': '당신의 음악 배경에 대해 말씀해주세요.', 'user_response': 'I\'ve been playing guitar since I was 5.', 'user_meaning': '5살부터 기타를 치고 있어요.'}, {'ai_prompt': 'That\'s impressive! Do you compose?', 'ai_meaning': '정말 인상적이에요! 작곡도 해요?', 'user_response': 'Yes, I\'ve written about 20 songs.', 'user_meaning': '네, 약 20곡을 작곡했어요.'}]},
        {'scene': '주민센터 서류 접수', 'turns': [{'ai_prompt': 'I need to register a change of address.', 'ai_meaning': '주소 변경을 등록해야 합니다.', 'user_response': 'Do you have your ID with you?', 'user_meaning': '신분증 가지고 있어요?'}, {'ai_prompt': 'Yes, here it is.', 'ai_meaning': '네, 여기 있습니다.', 'user_response': 'Fill out this form and we\'ll process it today.', 'user_meaning': '이 양식을 작성하면 오늘 처리해드릴게요.'}]},
        {'scene': '음식 배달 기사와 첫 만남', 'turns': [{'ai_prompt': 'One order for apartment 201?', 'ai_meaning': '201호에 한 건?', 'user_response': 'Yes! That\'s me. Thank you so much!', 'user_meaning': '네! 맞아요. 정말 감사합니다!'}, {'ai_prompt': 'Enjoy your meal!', 'ai_meaning': '음식 즐기세요!', 'user_response': 'Have a great day!', 'user_meaning': '좋은 하루 되세요!'}]},
        {'scene': '책 클럽 모임에서의 토론', 'turns': [{'ai_prompt': 'What did everyone think of this book?', 'ai_meaning': '모두 이 책에 대해 어떻게 생각해요?', 'user_response': 'I really enjoyed it. The characters were so relatable.', 'user_meaning': '정말 좋았어요. 캐릭터가 정말 공감 가네요.'}, {'ai_prompt': 'I agree. Should we read something by the same author next?', 'ai_meaning': '동의합니다. 다음에 같은 저자의 책을 읽을까요?', 'user_response': 'Definitely! Let\'s vote on it.', 'user_meaning': '네! 투표해봐요.'}]},
        {'scene': '국제 공항 출국심사', 'turns': [{'ai_prompt': 'Passport and boarding pass, please.', 'ai_meaning': '여권과 탑승권을 주세요.', 'user_response': 'Here you go. How long is your flight?', 'user_meaning': '여기 있습니다. 비행시간은 얼마나 돼요?'}, {'ai_prompt': 'About 8 hours. Have a good trip!', 'ai_meaning': '약 8시간이에요. 좋은 여행 되세요!', 'user_response': 'Thank you! Goodbye!', 'user_meaning': '감사합니다! 안녕히!'}]},
        {'scene': '화장품 매장 피부 타입 상담', 'turns': [{'ai_prompt': 'What\'s your skin type?', 'ai_meaning': '당신의 피부 타입이 뭐예요?', 'user_response': 'I think it\'s combination. What do you recommend?', 'user_meaning': '복합 피부인 것 같아요. 뭘 추천해요?'}, {'ai_prompt': 'I have the perfect line for you.', 'ai_meaning': '당신한테 딱 맞는 라인이 있어요.', 'user_response': 'Great! I\'ll try it.', 'user_meaning': '좋아요! 해봐요.'}]},
        {'scene': '여행 가이드 투어 시작', 'turns': [{'ai_prompt': 'Welcome to our city tour. I\'m your guide today.', 'ai_meaning': '도시 투어에 오신 것을 환영합니다. 저는 오늘 가이드입니다.', 'user_response': 'Great! I\'m excited to learn about your city.', 'user_meaning': '좋습니다! 당신의 도시에 대해 배우고 싶어요.'}, {'ai_prompt': 'This building is 200 years old and has great history.', 'ai_meaning': '이 건물은 200년 되었고 큰 역사가 있어요.', 'user_response': 'Fascinating! Can you tell us more?', 'user_meaning': '흥미로워요! 더 말씀해주실 수 있어요?'}]},
        {'scene': '프로젝트 완료 축하 파티', 'turns': [{'ai_prompt': 'Great work everyone! The project is a success!', 'ai_meaning': '모두 좋은 일해요! 프로젝트가 성공했어요!', 'user_response': 'This is amazing! Let\'s celebrate!', 'user_meaning': '정말 대단해요! 축하해요!'}, {'ai_prompt': 'Let\'s celebrate! Drinks are on me!', 'ai_meaning': '축하해요! 내가 쏘는 술이에요!', 'user_response': 'Thank you! We worked really hard for this.', 'user_meaning': '감사합니다! 정말 열심히 일했어요.'}]},
        {'scene': '직업 상담사와의 진로 상담', 'turns': [{'ai_prompt': 'What career are you interested in?', 'ai_meaning': '어떤 직업에 관심이 있어요?', 'user_response': 'I\'ve always wanted to work in technology.', 'user_meaning': '항상 기술 분야에서 일하고 싶었어요.'}, {'ai_prompt': 'I\'ve always wanted to work in technology.', 'ai_meaning': '항상 기술 분야에서 일하고 싶었어요.', 'user_response': 'That\'s a great field. Let\'s explore options.', 'user_meaning': '좋은 분야네요. 옵션을 탐색해봐요.'}]},
        {'scene': '공기업 채용 면접', 'turns': [{'ai_prompt': 'Why do you want to work for our company?', 'ai_meaning': '우리 회사에서 일하고 싶은 이유가 뭐예요?', 'user_response': 'Your company\'s values align with mine.', 'user_meaning': '당신의 회사 가치가 제 가치와 일치해요.'}, {'ai_prompt': 'Your company\'s values align with mine.', 'ai_meaning': '당신의 회사 가치가 제 가치와 일치해요.', 'user_response': 'That\'s great to hear. When can you start?', 'user_meaning': '좋네요. 언제 시작할 수 있어요?'}]},
        {'scene': '스마트폰 구매 상담', 'turns': [{'ai_prompt': 'Looking for a new phone?', 'ai_meaning': '새로운 휴대폰을 찾고 있어요?', 'user_response': 'Yes, something with good camera.', 'user_meaning': '네, 좋은 카메라가 있는 것.'}, {'ai_prompt': 'Yes, something with good camera.', 'ai_meaning': '네, 좋은 카메라가 있는 것.', 'user_response': 'This model just came out and has excellent specs.', 'user_meaning': '이 모델은 최근 출시됐고 훌륭한 스펙이에요.'}, {'ai_prompt': 'This model just came out and has excellent specs.', 'ai_meaning': '이 모델은 최근 출시됐고 훌륭한 스펙이에요.', 'user_response': 'Tell me more about it!', 'user_meaning': '더 말씀해주세요!'}]},
        {'scene': '치킨 집 먹방 배달', 'turns': [{'ai_prompt': 'Welcome to Chicken Paradise! What can I get you?', 'ai_meaning': '치킨 천국에 오신 것을 환영합니다! 뭘 드릴까요?', 'user_response': 'One box of spicy chicken and some fries, please.', 'user_meaning': '스파이시 치킨 한 박스와 감자튀김 주세요.'}, {'ai_prompt': 'Great choice! Anything to drink?', 'ai_meaning': '좋은 선택이에요! 음료는?', 'user_response': 'A large cola, please!', 'user_meaning': '큰 콜라 주세요.'}, {'ai_prompt': 'Perfect! Your order will be ready in 15 minutes.', 'ai_meaning': '완벽합니다! 주문이 15분 안에 준비될 거예요.', 'user_response': 'Thank you! That sounds great!', 'user_meaning': '감사합니다! 좋네요!'}]},
        {'scene': '면허 갱신 센터', 'turns': [{'ai_prompt': 'I\'m here to renew my driver\'s license.', 'ai_meaning': '운전면허를 갱신하러 왔어요.', 'user_response': 'Do you have your old license and ID?', 'user_meaning': '이전 면허증과 신분증 있어요?'}, {'ai_prompt': 'Yes, here they are.', 'ai_meaning': '네, 여기 있습니다.', 'user_response': 'It will take about 10 minutes.', 'user_meaning': '약 10분 정도 걸릴 거예요.'}, {'ai_prompt': 'It will take about 10 minutes.', 'ai_meaning': '약 10분 정도 걸릴 거예요.', 'user_response': 'That\'s fast. Thank you!', 'user_meaning': '빨라요. 감사합니다!'}]},
        {'scene': '동물 보호소 애완동물 입양', 'turns': [{'ai_prompt': 'Are you looking to adopt?', 'ai_meaning': '입양하러 오셨어요?', 'user_response': 'Yes, I\'d like a cat. Do you have any?', 'user_meaning': '네, 고양이를 원해요. 있어요?'}, {'ai_prompt': 'Yes, I\'d like a cat. Do you have any?', 'ai_meaning': '네, 고양이를 원해요. 있어요?', 'user_response': 'We have many wonderful cats. Which one interests you?', 'user_meaning': '훌륭한 고양이가 많아요. 어느 것이 관심이 가요?'}, {'ai_prompt': 'We have many wonderful cats. Which one interests you?', 'ai_meaning': '훌륭한 고양이가 많아요. 어느 것이 관심이 가요?', 'user_response': 'This orange one is adorable!', 'user_meaning': '이 주황이 정말 귀여워요!'}]},
        {'scene': '세미나 참석 네트워킹', 'turns': [{'ai_prompt': 'Hi! I\'m from the marketing department. What about you?', 'ai_meaning': '안녕! 나는 마케팅 부서에서 왔어요. 너는?', 'user_response': 'I\'m in sales. This seminar is very interesting.', 'user_meaning': '나는 영업 부서에 있어요. 이 세미나 정말 흥미로워.'}, {'ai_prompt': 'I\'m in sales. This seminar is very interesting.', 'ai_meaning': '나는 영업 부서에 있어요. 이 세미나 정말 흥미로워.', 'user_response': 'Let\'s exchange business cards.', 'user_meaning': '명함 교환해요.'}, {'ai_prompt': 'Let\'s exchange business cards.', 'ai_meaning': '명함 교환해요.', 'user_response': 'Good idea! Maybe we can collaborate.', 'user_meaning': '좋은 생각이네! 협력할 수 있을 것 같아.'}]},
        {'scene': '번지 점프 모험 활동', 'turns': [{'ai_prompt': 'Are you ready? It\'s quite a drop.', 'ai_meaning': '준비됐어요? 꽤 높아요.', 'user_response': 'I\'ve trained for this. Let\'s do it!', 'user_meaning': '이를 위해 훈련했어요. 해봐요!'}, {'ai_prompt': 'Okay! Remember to jump on three.', 'ai_meaning': '좋아요! 3일 때 점프하는 거 기억해요.', 'user_response': '3! 2! 1! Jump!', 'user_meaning': '3! 2! 1! 점프!'}, {'ai_prompt': '3! 2! 1! Jump!', 'ai_meaning': '3! 2! 1! 점프!', 'user_response': 'Wow! That was amazing!', 'user_meaning': '와! 정말 대단했어!'}, {'ai_prompt': 'Wow! That was amazing!', 'ai_meaning': '와! 정말 대단했어!', 'user_response': 'That was the most thrilling experience!', 'user_meaning': '가장 설레는 경험이었어!'}]},
        {'scene': '금고 개설 은행 방문', 'turns': [{'ai_prompt': 'I\'d like to open a safe deposit box.', 'ai_meaning': '금고를 열고 싶어요.', 'user_response': 'We have several sizes available. What do you need it for?', 'user_meaning': '여러 사이즈가 있어요. 뭐에 사용할 거예요?'}, {'ai_prompt': 'We have several sizes available. What do you need it for?', 'ai_meaning': '여러 사이즈가 있어요. 뭐에 사용할 거예요?', 'user_response': 'To store important documents and valuables.', 'user_meaning': '중요 문서와 귀중품을 보관하려고.'}, {'ai_prompt': 'To store important documents and valuables.', 'ai_meaning': '중요 문서와 귀중품을 보관하려고.', 'user_response': 'Perfect. Let me show you what we have.', 'user_meaning': '좋습니다. 뭐가 있는지 보여드릴게요.'}, {'ai_prompt': 'Perfect. Let me show you what we have.', 'ai_meaning': '좋습니다. 뭐가 있는지 보여드릴게요.', 'user_response': 'Thank you! This sounds perfect for me.', 'user_meaning': '감사합니다! 이게 딱 좋아요.'}]},
        {'scene': '극장 표 구매 라인', 'turns': [{'ai_prompt': 'Two tickets for the evening show, please.', 'ai_meaning': '저녁 공연 표 2장 주세요.', 'user_response': 'Any preferences? Aisle or center?', 'user_meaning': '선호가 있어요? 통로 아니면 중앙?'}, {'ai_prompt': 'Center would be perfect!', 'ai_meaning': '중앙이 좋겠어요!', 'user_response': 'That\'ll be 50 dollars.', 'user_meaning': '50달러입니다.'}]},
        {'scene': '노인 요양원 방문', 'turns': [{'ai_prompt': 'Grandma! I brought you flowers!', 'ai_meaning': '할머니! 꽃을 가져왔어요!', 'user_response': 'Oh darling, how wonderful to see you!', 'user_meaning': '오 얘야, 너를 만나서 정말 좋아!'}, {'ai_prompt': 'Oh darling, how wonderful to see you!', 'ai_meaning': '오 얘야, 너를 만나서 정말 좋아!', 'user_response': 'How have you been? Are you comfortable here?', 'user_meaning': '지내시는 거 잘되세요? 여기 편해요?'}, {'ai_prompt': 'How have you been? Are you comfortable here?', 'ai_meaning': '지내시는 거 잘되세요? 여기 편해요?', 'user_response': 'The staff is very nice. I\'m settling in well.', 'user_meaning': '직원들이 정말 친절해요. 잘 적응하고 있어요.'}, {'ai_prompt': 'The staff is very nice. I\'m settling in well.', 'ai_meaning': '직원들이 정말 친절해요. 잘 적응하고 있어요.', 'user_response': 'That makes me so happy to hear.', 'user_meaning': '그렇게 들으니까 정말 기뻐요.'}]}
    ]

def _flatten_drama_conversations(raw_conversations):
    """turns 배열을 개별 회화로 평탄화 + 모든 필수 필드 보장"""
    flattened = []
    for scenario in raw_conversations:
        turns = scenario.get('turns', [])
        scene = scenario.get('scene', '')
        
        for i, turn in enumerate(turns):
            # 필수 필드 추출
            ai_prompt = turn.get('ai_prompt', '')
            ai_meaning = turn.get('ai_meaning', '')
            user_response = turn.get('user_response', '')
            user_meaning = turn.get('user_meaning', '')
            
            # ai_followup은 다음 턴의 ai_prompt 또는 빈 문자열
            ai_followup = turns[i+1].get('ai_prompt', '') if i+1 < len(turns) else ''
            ai_followup_meaning = turns[i+1].get('ai_meaning', '') if i+1 < len(turns) else ''
            
            # user_response가 있는 경우만 포함 (사용자가 대답해야 하는 turn)
            if user_response:
                flattened.append({
                    'scene': scene,
                    'ai_prompt': ai_prompt,
                    'ai_meaning': ai_meaning,
                    'user_response': user_response,
                    'user_meaning': user_meaning,
                    'ai_followup': ai_followup,
                    'ai_followup_meaning': ai_followup_meaning
                })
    
    return flattened

# 원본 함수를 다시 정의 (평탄화된 버전 반환)
_raw_drama_conversations = [
    {
        'scene': '카페에서 처음 만난 사람',
        'turns': [
            {
                'ai_prompt': 'Hey, is this seat taken?',
                'ai_meaning': '안녕, 이 자리 비었어요?',
                'user_response': 'No, please sit down.',
                'user_meaning': '아니요, 앉으세요.'
            },
            {
                'ai_prompt': 'Thanks. So, what brings you here today?',
                'ai_meaning': '감사합니다. 그래서 오늘 뭐 때문에 여기 왔어요?',
                'user_response': 'I come here to study.',
                'user_meaning': '나는 공부하러 여기 와요.'
            },
            {
                'ai_prompt': 'That sounds nice. What are you studying?',
                'ai_meaning': '좋네요. 뭘 공부하고 있어요?',
                'user_response': 'English language and culture.',
                'user_meaning': '영어와 문화를 공부합니다.'
            }
        ]
    }
]

def get_conversation_prompt(drama_data=None):
    """드라마/애니 기반 AI 대화 프롬프트"""
    if drama_data is None:
        drama_data = random.choice(get_drama_conversations())
    return drama_data['ai_prompt']

def get_conversation_translation(drama_data=None):
    """드라마/애니 기반 AI 대화 한글 번역"""
    if drama_data is None:
        drama_data = random.choice(get_drama_conversations())
    return drama_data['ai_meaning']

def get_user_response_prompt(drama_data):
    """사용자가 말해야 할 정답 문장"""
    return drama_data['user_response']

def get_user_response_meaning(drama_data):
    """사용자 정답 문장의 한글 의미"""
    return drama_data['user_meaning']

def get_ai_followup(drama_data):
    """정답 후 AI의 후속 대사"""
    return drama_data['ai_followup']

def get_ai_followup_meaning(drama_data):
    """AI 후속 대사의 한글 의미"""
    return drama_data['ai_followup_meaning']

def get_foreign_speakers():
    """외국인 강사 정보"""
    speakers = [
        {'name': 'SAM', 'image': 'young_idol_man_sam.png', 'voice': 'male1', 'gender': 'male'},
        {'name': 'OLIVIA', 'image': 'young_idol_woman_olivia.png', 'voice': 'female1', 'gender': 'female'},
        {'name': 'JAMES', 'image': 'young_idol_man_james.png', 'voice': 'male2', 'gender': 'male'},
        {'name': 'EMMA', 'image': 'young_idol_woman_emma.png', 'voice': 'female2', 'gender': 'female'},
        {'name': 'MICHAEL', 'image': 'young_idol_man_michael.png', 'voice': 'male3', 'gender': 'male'},
        {'name': 'SOPHIA', 'image': 'young_idol_woman_sophia.png', 'voice': 'female3', 'gender': 'female'},
        {'name': 'ISABELLA', 'image': 'young_idol_woman_isabella.png', 'voice': 'female4', 'gender': 'female'},
        {'name': 'NOAH', 'image': 'young_idol_man_noah.png', 'voice': 'male4', 'gender': 'male'},
        {'name': 'LUCAS', 'image': 'young_idol_man_lucas.png', 'voice': 'male5', 'gender': 'male'},
        {'name': 'MIA', 'image': 'young_idol_woman_mia.png', 'voice': 'female5', 'gender': 'female'},
        {'name': 'SOPHIE', 'image': 'young_idol_woman_sophie.png', 'voice': 'female6', 'gender': 'female'}
    ]
    return speakers

def evaluate_conversation_response(user_response, target_expression, context_sentence):
    """AI를 사용하여 사용자 응답의 문법과 적절성 평가"""
    try:
        import os
        from openai import OpenAI
        
        # Replit AI 통합 환경 변수 사용
        api_key = os.environ.get('AI_INTEGRATIONS_OPENAI_API_KEY')
        base_url = os.environ.get('AI_INTEGRATIONS_OPENAI_BASE_URL')
        
        client = OpenAI(
            api_key=api_key,
            base_url=base_url
        )
        
        prompt = f"""영어 회화 학생의 응답을 분석하고 짧은 코칭을 제공하세요.

상대가 말한 것: "{context_sentence}"
사용해야 할 표현: "{target_expression}"
학생이 말한 것: "{user_response}"

반드시 한글로만 JSON 형식으로 응답하세요 (각 피드백은 1줄):
{{
  "grammar": "문법 오류 및 개선 방법 (1줄)",
  "tip": "표현을 더 잘 사용하는 팁 (1줄)",
  "better": "더 나은 답변 예시"
}}"""

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "당신은 영어 회화 코칭 전문가입니다. 항상 한글로만 응답하고 유효한 JSON만 반환하세요."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=200
        )
        
        import json
        content = response.choices[0].message.content
        if not content:
            raise ValueError("AI 응답이 비어있습니다.")
        
        result_text = content.strip()
        
        # JSON 추출
        if "```json" in result_text:
            result_text = result_text.split("```json")[1].split("```")[0].strip()
        elif "```" in result_text:
            result_text = result_text.split("```")[1].split("```")[0].strip()
        
        result = json.loads(result_text)
        return {
            'success': True,
            'grammar': result.get('grammar', ''),
            'tip': result.get('tip', ''),
            'better': result.get('better', '')
        }
    except Exception as e:
        print(f"AI 평가 오류: {e}")
        return {
            'success': False,
            'error': str(e)
        }

def merge_monsters(player, monster_ids):
    """몬스터 합성 함수 - 같은 등급 3마리를 더 높은 등급 또는 신화급 몬스터로 변환"""
    from data.monsters import get_monster_by_id, get_monsters_by_rarity
    
    if not player.get('도감') or len(monster_ids) != 3:
        return {'success': False, 'message': '유효하지 않은 선택입니다.'}
    
    # 선택한 몬스터들이 도감에 있는지 확인
    for monster_id in monster_ids:
        if monster_id not in player['도감']:
            return {'success': False, 'message': '선택한 몬스터가 도감에 없습니다.'}
    
    # 첫 번째 몬스터로 등급 확인
    first_monster_rarity = player['도감'][monster_ids[0]].get('등급')
    
    # 모든 몬스터가 같은 등급인지 확인
    for monster_id in monster_ids[1:]:
        if player['도감'][monster_id].get('등급') != first_monster_rarity:
            return {'success': False, 'message': '같은 등급의 몬스터 3마리를 선택해주세요.'}
    
    # 도감에서 3마리 제거
    for monster_id in monster_ids:
        del player['도감'][monster_id]
    
    # 합성 결과 결정
    rarity_order = ['레어', '에픽', '유니크', '레전드리', '신화급']
    current_rarity_index = rarity_order.index(first_monster_rarity)
    
    # 레전드리 3마리 합성 -> 신화급 30% 확률적 획득
    if first_monster_rarity == '레전드리':
        if random.random() < 0.3:
            # 신화급 30% 확률 획득
            mythic_monsters = ['신화급_1', '신화급_2', '신화급_3']
            result_monster_id = random.choice(mythic_monsters)
            result_monster_data = get_monster_by_id(result_monster_id)
            
            if not result_monster_data:
                return {'success': False, 'message': '합성 중 오류가 발생했습니다.'}
            
            result_monster = {
                '이름': result_monster_data['이름'],
                '등급': '신화급',
                '이미지': result_monster_data.get('이미지', ''),
                '최초처치일': datetime.now().isoformat(),
                '처치수': 0,
                '포획됨': True,
                '공격력': random.randint(result_monster_data['공격력'][0], result_monster_data['공격력'][1]),
                '체력': random.randint(result_monster_data['체력'][0], result_monster_data['체력'][1])
            }
            
            player['도감'][result_monster_id] = result_monster
            return {
                'success': True,
                'message': f"축하합니다! 신화급 몬스터 '{result_monster_data['이름']}'을(를) 획득했습니다!",
                'result_monster_id': result_monster_id,
                'result_monster_name': result_monster_data['이름'],
                'is_mythic': True
            }
        else:
            # 70% 확률로 레전드리 재획득
            legendary_monsters = get_monsters_by_rarity('레전드리')
            
            if not legendary_monsters:
                return {'success': False, 'message': '합성 중 오류가 발생했습니다.'}
            
            result_monster_id = random.choice(legendary_monsters)
            result_monster_data = get_monster_by_id(result_monster_id)
            
            if not result_monster_data:
                return {'success': False, 'message': '합성 중 오류가 발생했습니다.'}
            
            result_monster = {
                '이름': result_monster_data['이름'],
                '등급': '레전드리',
                '이미지': result_monster_data.get('이미지', ''),
                '최초처치일': datetime.now().isoformat(),
                '처치수': 0,
                '포획됨': True,
                '공격력': random.randint(result_monster_data['공격력'][0], result_monster_data['공격력'][1]),
                '체력': random.randint(result_monster_data['체력'][0], result_monster_data['체력'][1])
            }
            
            player['도감'][result_monster_id] = result_monster
            return {
                'success': True,
                'message': f"합성 성공! 레전드리 몬스터 '{result_monster_data['이름']}'을(를) 획득했습니다!",
                'result_monster_id': result_monster_id,
                'result_monster_name': result_monster_data['이름'],
                'is_mythic': False
            }
    
    # 등급별 상위 등급 획득 확률
    rarity_upgrade_chance = {
        '레어': 0.3,      # 레어: 30% 확률로 상위 등급
        '에픽': 0.2,      # 에픽: 20% 확률로 상위 등급
        '유니크': 0.1     # 유니크: 10% 확률로 상위 등급
    }
    
    upgrade_chance = rarity_upgrade_chance.get(first_monster_rarity, 0.6)
    
    # 다른 등급 -> 더 높은 등급 또는 같은 등급으로 변환
    is_upgraded = False
    if random.random() < upgrade_chance and current_rarity_index < len(rarity_order) - 2:
        # 더 높은 등급 획득
        is_upgraded = True
        next_rarity = rarity_order[current_rarity_index + 1]
        next_rarity_monsters = get_monsters_by_rarity(next_rarity)
    else:
        # 같은 등급 획득
        next_rarity = first_monster_rarity
        next_rarity_monsters = get_monsters_by_rarity(next_rarity)
    
    # 랜덤 몬스터 선택
    if not next_rarity_monsters:
        next_rarity_monsters = get_monsters_by_rarity(first_monster_rarity)
    
    if not next_rarity_monsters:
        return {'success': False, 'message': '합성 중 오류가 발생했습니다.'}
    
    result_monster_id = random.choice(next_rarity_monsters)
    result_monster_data = get_monster_by_id(result_monster_id)
    
    if not result_monster_data:
        return {'success': False, 'message': '합성 중 오류가 발생했습니다.'}
    
    result_monster = {
        '이름': result_monster_data['이름'],
        '등급': next_rarity,
        '이미지': result_monster_data.get('이미지', ''),
        '최초처치일': datetime.now().isoformat(),
        '처치수': 0,
        '포획됨': True,
        '공격력': random.randint(result_monster_data['공격력'][0], result_monster_data['공격력'][1]),
        '체력': random.randint(result_monster_data['체력'][0], result_monster_data['체력'][1])
    }
    
    player['도감'][result_monster_id] = result_monster
    
    return {
        'success': True,
        'message': f"합성 성공! {next_rarity} 몬스터 '{result_monster_data['이름']}'을(를) 획득했습니다!",
        'result_monster_id': result_monster_id,
        'result_monster_name': result_monster_data['이름'],
        'is_mythic': False,
        'is_upgraded': is_upgraded
    }

# ===== 모험 시스템 함수들 =====

def get_adventure_stages():
    """모험 스테이지 목록 반환"""
    from data.adventure_data import ADVENTURE_STAGES
    return ADVENTURE_STAGES

def get_available_monsters(player):
    """플레이어가 보유한 도감 몬스터 반환 (높은 등급순)"""
    from data.monsters import get_monster_by_id
    available = []
    
    for monster_id, monster_data in player['도감'].items():
        monster_info = get_monster_by_id(monster_id)
        if monster_info and monster_data.get('포획됨'):
            available.append({
                'id': monster_id,
                'name': monster_data['이름'],
                'rarity': monster_data['등급'],
                'attack': monster_data.get('공격력', 0),
                'hp': monster_data.get('체력', 0),
                'image': monster_data.get('이미지', '')
            })
    
    # 등급순 정렬 (높은 등급이 위로), 같은 등급 내에서 공격력 순
    rarity_order = {'신화급': 0, '레전드리': 1, '유니크': 2, '에픽': 3, '레어': 4}
    available.sort(key=lambda x: (rarity_order.get(x['rarity'], 999), -x['attack']))
    
    return available

def start_adventure_battle(player, stage_id, selected_monster_ids):
    """모험 전투 시작 (팀 기반)"""
    from data.adventure_data import ADVENTURE_STAGES, ENEMY_DIALOGUES, PLAYER_DIALOGUES
    from data.monsters import get_monster_by_id, get_monsters_by_rarity
    from data.skills import SKILL_INFO
    import random
    
    # 스테이지 정보 가져오기
    stage = next((s for s in ADVENTURE_STAGES if s['stage_id'] == stage_id), None)
    if not stage:
        return {'success': False, 'message': '존재하지 않는 스테이지입니다.'}
    
    # 플레이어 몬스터 팀 구성 확인
    player_team = []
    for monster_id in selected_monster_ids:
        if monster_id not in player['도감']:
            return {'success': False, 'message': '해당 몬스터를 보유하고 있지 않습니다.'}
        
        monster_data = player['도감'][monster_id]
        monster_info = get_monster_by_id(monster_id)
        
        if not monster_info:
            return {'success': False, 'message': '플레이어 몬스터 정보를 찾을 수 없습니다.'}
        
        player_team.append({
            'id': monster_id,
            'name': monster_data['이름'],
            'rarity': monster_data['등급'],
            'attack': monster_data.get('공격력', 0),
            'max_hp': monster_data.get('체력', 0),
            'current_hp': monster_data.get('체력', 0),
            'image': monster_data.get('이미지', '')
        })
    
    # 적 몬스터 생성
    rarity_list = stage['enemy_rarity']
    enemy_rarity = random.choice(rarity_list)
    enemy_monsters = get_monsters_by_rarity(enemy_rarity)
    
    if not enemy_monsters:
        return {'success': False, 'message': '적 몬스터를 생성할 수 없습니다.'}
    
    enemy_monster_id = random.choice(enemy_monsters)
    enemy_monster_info = get_monster_by_id(enemy_monster_id)
    
    if not enemy_monster_info:
        return {'success': False, 'message': '적 몬스터 정보를 찾을 수 없습니다.'}
    
    # 적 몬스터 스탯 계산
    enemy_attack = int(random.randint(enemy_monster_info['공격력'][0], enemy_monster_info['공격력'][1]) * stage['enemy_attack_multiplier'])
    enemy_hp = int(random.randint(enemy_monster_info['체력'][0], enemy_monster_info['체력'][1]) * stage['enemy_hp_multiplier'])
    
    # 난이도에 따른 대사 레벨 결정
    difficulty_level = {
        '쉬움': 'level_1',
        '보통': 'level_2',
        '어려움': 'level_3',
        '매우 어려움': 'level_4',
        '최악': 'level_4'
    }
    dialogue_level = difficulty_level.get(stage['난이도'], 'level_1')
    
    # 기술 사용 횟수 초기화 (기술당 4번 제한)
    player_skills = player.get('모험_기술', ['박치기'])
    skill_usage_count = {skill: 0 for skill in player_skills}
    
    # 현재 활성 몬스터 (첫 번째)
    current_player_monster = player_team[0]
    
    battle_state = {
        'stage_id': stage_id,
        'stage_name': stage['이름'],
        'difficulty': stage['난이도'],
        'enemy_count': stage.get('enemy_count', 1),
        'defeated_monsters': 0,
        'player_team': player_team,  # 팀 전체
        'current_team_index': 0,  # 현재 활성 몬스터 인덱스
        'player_monster': current_player_monster,  # 현재 활성 몬스터
        'enemy_monster': {
            'id': enemy_monster_id,
            'name': enemy_monster_info['이름'],
            'rarity': enemy_rarity,
            'attack': enemy_attack,
            'max_hp': enemy_hp,
            'current_hp': enemy_hp,
            'image': enemy_monster_info.get('이미지', '')
        },
        'turn': 0,
        'player_dialogue': random.choice(PLAYER_DIALOGUES.get(dialogue_level, PLAYER_DIALOGUES['level_1'])),
        'enemy_dialogue': random.choice(ENEMY_DIALOGUES.get(dialogue_level, ENEMY_DIALOGUES['level_1'])),
        'log': [],
        'player_skills': player_skills,
        'skill_usage_count': skill_usage_count,
        'game_over': False,
        'winner': None,
        'enemy_attack_debuff': 0.0
    }
    
    # 선공 결정
    if current_player_monster['attack'] >= enemy_attack:
        battle_state['player_turn'] = True
        battle_state['log'].append(f"플레이어 몬스터가 높은 공격력으로 선공합니다!")
    else:
        battle_state['player_turn'] = False
        battle_state['log'].append(f"적 몬스터가 높은 공격력으로 선공합니다!")
    
    return {'success': True, 'battle_state': battle_state}

def execute_enemy_turn(battle_state):
    """적의 턴 자동 실행 (등급/난이도별 기술 사용)"""
    from data.adventure_data import SKILLS
    import random
    
    if battle_state['game_over'] or battle_state['player_turn']:
        return {'success': False, 'battle_state': battle_state}
    
    enemy_monster = battle_state['enemy_monster']
    player_monster = battle_state['player_monster']
    
    # 등급/난이도별 기술 선택 확률
    rarity = enemy_monster.get('rarity', '레어')
    difficulty = battle_state.get('difficulty', 'EASY')
    
    # 기술 사용 확률 결정
    skill_use_probability = {
        '레어': {'EASY': 0.2, 'NORMAL': 0.3, 'HARD': 0.4},
        '에픽': {'EASY': 0.4, 'NORMAL': 0.6, 'HARD': 0.8},
        '유니크': {'EASY': 0.7, 'NORMAL': 0.8, 'HARD': 0.95},
        '레전드리': {'EASY': 0.9, 'NORMAL': 0.95, 'HARD': 1.0},
    }
    
    use_skill = random.random() < skill_use_probability.get(rarity, {}).get(difficulty, 0.3)
    
    # 사용 가능한 기술 목록 (플레이어가 가진 기술 활용)
    available_skills = list(SKILLS.keys())
    
    if use_skill and available_skills:
        # 등급별 기술 확률 가중치 설정
        skill_weights = []
        for skill_name in available_skills:
            skill = SKILLS[skill_name]
            skill_rarity = skill.get('등급', '레어')
            
            # 몬스터 등급에 따라 기술 가중치 설정
            weight = 0
            if rarity == '레어':
                # 레어: 레어(70%), 에픽(25%), 유니크(4%), 레전드리(1%)
                if skill_rarity == '레어': weight = 70
                elif skill_rarity == '에픽': weight = 25
                elif skill_rarity == '유니크': weight = 4
                elif skill_rarity == '레전드리': weight = 1
            elif rarity == '에픽':
                # 에픽: 레어(15%), 에픽(60%), 유니크(20%), 레전드리(5%)
                if skill_rarity == '레어': weight = 15
                elif skill_rarity == '에픽': weight = 60
                elif skill_rarity == '유니크': weight = 20
                elif skill_rarity == '레전드리': weight = 5
            elif rarity == '유니크':
                # 유니크: 레어(5%), 에픽(10%), 유니크(70%), 레전드리(15%)
                if skill_rarity == '레어': weight = 5
                elif skill_rarity == '에픽': weight = 10
                elif skill_rarity == '유니크': weight = 70
                elif skill_rarity == '레전드리': weight = 15
            elif rarity == '레전드리':
                # 레전드리: 유니크(20%), 레전드리(80%)
                if skill_rarity == '유니크': weight = 20
                elif skill_rarity == '레전드리': weight = 80
            
            skill_weights.append(weight)
        
        # 가중치에 따라 기술 선택 (0 이상의 가중치만)
        if sum(skill_weights) > 0:
            skill_name = random.choices(available_skills, weights=skill_weights, k=1)[0]
        else:
            skill_name = random.choice(available_skills)
        
        skill = SKILLS[skill_name]
        
        # 기술의 공격력 보정 적용
        multiplier_min = skill.get('공격력_보정_min', 1.0)
        multiplier_max = skill.get('공격력_보정_max', 1.0)
        multiplier = random.uniform(multiplier_min, multiplier_max)
        
        # 적 공격력에 debuff 적용
        enemy_attack = enemy_monster['attack']
        debuff_ratio = battle_state.get('enemy_attack_debuff', 0.0)
        if debuff_ratio > 0:
            enemy_attack = int(enemy_attack * (1 - debuff_ratio))
            battle_state['log'].append(f"(약화됨: {enemy_monster['attack']} → {enemy_attack})")
        
        damage = int(enemy_attack * multiplier)
        player_monster['current_hp'] -= damage
        battle_state['log'].append(f"적 [{skill_name}] 사용! {damage} 데미지")
    else:
        # 기본 공격
        enemy_attack = enemy_monster['attack']
        debuff_ratio = battle_state.get('enemy_attack_debuff', 0.0)
        if debuff_ratio > 0:
            enemy_attack = int(enemy_attack * (1 - debuff_ratio))
            battle_state['log'].append(f"(약화됨: {enemy_monster['attack']} → {enemy_attack})")
        
        damage = enemy_attack
        player_monster['current_hp'] -= damage
        battle_state['log'].append(f"적의 공격! {damage} 데미지")
    
    # 플레이어 체력 확인
    if player_monster['current_hp'] <= 0:
        player_monster['current_hp'] = 0
        battle_state['game_over'] = True
        battle_state['winner'] = 'enemy'
        battle_state['log'].append(f"패배했습니다...")
        return {'success': True, 'battle_state': battle_state}
    
    # 플레이어 차례로 돌아감
    battle_state['player_turn'] = True
    battle_state['turn'] += 1
    
    return {'success': True, 'battle_state': battle_state}

def get_skill_uses(skill):
    """기술의 배수에 따라 최대 사용 횟수 계산"""
    multiplier_max = skill.get('공격력_보정_max', 1.0)
    
    # 배수 범위: 1.0 ~ 2.4
    min_mult = 1.0
    max_mult = 2.4
    min_uses = 3
    max_uses = 10
    
    if multiplier_max <= min_mult:
        return max_uses
    if multiplier_max >= max_mult:
        return min_uses
    
    # 선형 보간
    ratio = (multiplier_max - min_mult) / (max_mult - min_mult)
    uses = max_uses - (ratio * (max_uses - min_uses))
    return max(min_uses, min(max_uses, round(uses)))

def execute_skill(battle_state, skill_name):
    """기술 실행"""
    from data.adventure_data import SKILLS
    import random
    
    if skill_name not in SKILLS:
        return {'success': False, 'message': '존재하지 않는 기술입니다.'}
    
    skill = SKILLS[skill_name]
    
    if battle_state['game_over']:
        return {'success': False, 'message': '전투가 이미 끝났습니다.'}
    
    if not battle_state['player_turn']:
        return {'success': False, 'message': '지금은 플레이어 차례가 아닙니다.'}
    
    # 기술별 최대 사용 횟수 계산
    max_skill_uses = get_skill_uses(skill)
    
    # 기술 사용 횟수 제한 확인
    if skill_name not in battle_state['skill_usage_count']:
        battle_state['skill_usage_count'][skill_name] = 0
    
    if battle_state['skill_usage_count'][skill_name] >= max_skill_uses:
        return {'success': False, 'message': f'{skill_name}은(는) 더 이상 사용할 수 없습니다. ({max_skill_uses}회 사용 완료)'}
    
    # 기술 사용 횟수 증가
    battle_state['skill_usage_count'][skill_name] += 1
    
    # 플레이어 공격 (랜덤 범위 적용)
    player_monster = battle_state['player_monster']
    multiplier_min = skill.get('공격력_보정_min', 1.0)
    multiplier_max = skill.get('공격력_보정_max', 1.0)
    multiplier = random.uniform(multiplier_min, multiplier_max)
    damage = int(player_monster['attack'] * multiplier)
    battle_state['enemy_monster']['current_hp'] -= damage
    
    usage_count = battle_state['skill_usage_count'][skill_name]
    battle_state['log'].append(f"플레이어 [{skill_name}] 사용! {damage} 데미지 (사용 {usage_count}/{max_skill_uses}회)")
    
    # 특수효과 처리
    special_effect = skill.get('특수효과', None)
    if special_effect == 'debuff_attack':
        # 검은빛: 상대 공격력 15% 감소
        battle_state['enemy_attack_debuff'] = 0.15
        battle_state['log'].append(f"적 [{battle_state['enemy_monster']['name']}]의 공격력이 15% 감소했습니다!")
    
    # 적 체력 확인
    if battle_state['enemy_monster']['current_hp'] <= 0:
        battle_state['enemy_monster']['current_hp'] = 0
        battle_state['defeated_monsters'] = battle_state.get('defeated_monsters', 0) + 1
        battle_state['log'].append(f"적 몬스터를 격파했습니다! ({battle_state['defeated_monsters']}/{battle_state.get('enemy_count', 1)})")
        
        # 남은 몬스터가 있는지 확인
        if battle_state['defeated_monsters'] < battle_state.get('enemy_count', 1):
            # 다음 몬스터 생성
            stage_id = battle_state['stage_id']
            stages = get_adventure_stages()
            stage = next((s for s in stages if s['stage_id'] == stage_id), None)
            
            if stage:
                # 다음 몬스터 생성
                import random
                from data.monsters import get_monster_by_id, get_monsters_by_rarity
                
                enemy_rarity = random.choice(stage.get('enemy_rarity', ['레어']))
                enemy_monsters = get_monsters_by_rarity(enemy_rarity)
                
                if enemy_monsters:
                    enemy_monster_id = random.choice(enemy_monsters)
                    enemy_monster_info = get_monster_by_id(enemy_monster_id)
                    
                    if enemy_monster_info:
                        enemy_attack = int(random.randint(enemy_monster_info['공격력'][0], enemy_monster_info['공격력'][1]) * stage.get('enemy_attack_multiplier', 1.0))
                        enemy_hp = int(random.randint(enemy_monster_info['체력'][0], enemy_monster_info['체력'][1]) * stage.get('enemy_hp_multiplier', 1.0))
                        
                        battle_state['enemy_monster'] = {
                            'id': enemy_monster_id,
                            'name': enemy_monster_info['이름'],
                            'rarity': enemy_rarity,
                            'attack': enemy_attack,
                            'max_hp': enemy_hp,
                            'current_hp': enemy_hp,
                            'image': enemy_monster_info.get('이미지', '')
                        }
                        # 새 몬스터 생성 시 debuff 초기화
                        battle_state['enemy_attack_debuff'] = 0.0
                        battle_state['log'].append(f"\n다음 적 몬스터 등장: {enemy_monster_info['이름']} ({enemy_rarity})")
            
            # 플레이어 차례로 돌아감
            battle_state['player_turn'] = True
            return {'success': True, 'battle_state': battle_state}
        else:
            # 모든 몬스터 처치 완료
            battle_state['game_over'] = True
            battle_state['winner'] = 'player'
            battle_state['log'].append(f"스테이지를 클리어했습니다!")
            return {'success': True, 'battle_state': battle_state}
    
    # 적 차례
    battle_state['player_turn'] = False
    battle_state['log'].append(f"\n적 [{battle_state['enemy_monster']['name']}] 차례...")
    
    # 적의 기술 또는 공격
    enemy_monster = battle_state['enemy_monster']
    rarity = enemy_monster.get('rarity', '레어')
    difficulty = battle_state.get('difficulty', 'EASY')
    
    # 기술 사용 확률
    skill_use_probability = {
        '레어': {'EASY': 0.2, 'NORMAL': 0.3, 'HARD': 0.4},
        '에픽': {'EASY': 0.4, 'NORMAL': 0.6, 'HARD': 0.8},
        '유니크': {'EASY': 0.7, 'NORMAL': 0.8, 'HARD': 0.95},
        '레전드리': {'EASY': 0.9, 'NORMAL': 0.95, 'HARD': 1.0},
    }
    
    use_skill = random.random() < skill_use_probability.get(rarity, {}).get(difficulty, 0.3)
    
    if use_skill and SKILLS:
        skill_name = random.choice(list(SKILLS.keys()))
        skill = SKILLS[skill_name]
        multiplier_min = skill.get('공격력_보정_min', 1.0)
        multiplier_max = skill.get('공격력_보정_max', 1.0)
        multiplier = random.uniform(multiplier_min, multiplier_max)
        
        # 적 공격력에 debuff 적용
        enemy_attack = enemy_monster['attack']
        debuff_ratio = battle_state.get('enemy_attack_debuff', 0.0)
        if debuff_ratio > 0:
            enemy_attack = int(enemy_attack * (1 - debuff_ratio))
        
        enemy_damage = int(enemy_attack * multiplier)
        battle_state['player_monster']['current_hp'] -= enemy_damage
        battle_state['log'].append(f"적 [{skill_name}] 사용! {enemy_damage} 데미지")
    else:
        # 기본 공격
        enemy_attack = enemy_monster['attack']
        debuff_ratio = battle_state.get('enemy_attack_debuff', 0.0)
        if debuff_ratio > 0:
            enemy_attack = int(enemy_attack * (1 - debuff_ratio))
        
        enemy_damage = enemy_attack
        battle_state['player_monster']['current_hp'] -= enemy_damage
        battle_state['log'].append(f"적의 공격! {enemy_damage} 데미지")
    
    # 플레이어 체력 확인
    if battle_state['player_monster']['current_hp'] <= 0:
        battle_state['player_monster']['current_hp'] = 0
        battle_state['log'].append(f"플레이어의 [{battle_state['player_monster']['name']}]이(가) 격파당했습니다!")
        
        # 팀 기반 - 다음 몬스터 확인
        player_team = battle_state.get('player_team', [])
        current_index = battle_state.get('current_team_index', 0)
        
        # 남은 팀원이 있는지 확인
        if current_index + 1 < len(player_team):
            # 다음 몬스터로 전환
            current_index += 1
            battle_state['current_team_index'] = current_index
            next_monster = player_team[current_index]
            
            battle_state['player_monster'] = {
                'id': next_monster['id'],
                'name': next_monster['name'],
                'rarity': next_monster['rarity'],
                'attack': next_monster['attack'],
                'max_hp': next_monster['max_hp'],
                'current_hp': next_monster['max_hp'],  # 풀 체력으로 회복
                'image': next_monster['image']
            }
            battle_state['log'].append(f"\n다음 팀원 등장: {next_monster['name']} ({next_monster['rarity']})")
            
            # 플레이어 차례로 돌아감
            battle_state['player_turn'] = True
            battle_state['turn'] += 1
            return {'success': True, 'battle_state': battle_state}
        else:
            # 남은 팀원이 없음 - 패배
            battle_state['game_over'] = True
            battle_state['winner'] = 'enemy'
            battle_state['log'].append(f"모든 팀원이 격파당했습니다... 패배했습니다...")
            return {'success': True, 'battle_state': battle_state}
    
    # 플레이어 차례로 돌아감
    battle_state['player_turn'] = True
    battle_state['turn'] += 1
    
    return {'success': True, 'battle_state': battle_state}

def complete_adventure_battle(player, battle_state):
    """모험 전투 완료 처리"""
    from data.adventure_data import SKILL_DROP_POOLS, REWARD_ITEMS, SKILLS
    import random
    
    if battle_state['winner'] != 'player':
        return {'success': False, 'message': '전투에 패배했습니다.', 'rewards': {}}
    
    stage_id = battle_state['stage_id']
    stage_config = next((s for s in get_adventure_stages() if s['stage_id'] == stage_id), None)
    
    if not stage_config:
        return {'success': False, 'message': '스테이지 정보를 찾을 수 없습니다.', 'rewards': {}}
    
    rewards = {
        'skills': [],
        'items': []
    }
    
    # 기술 카드 드롭
    if random.random() < stage_config.get('skill_reward_rate', 0.02):
        skill_pools = SKILL_DROP_POOLS.get(stage_id, {})
        skill_rarity_weights = stage_config.get('skill_rarity_weights', {})
        
        # 가중치에 따라 등급 선택
        rarities_to_use = [r for r, w in skill_rarity_weights.items() if w > 0]
        weights = [skill_rarity_weights[r] for r in rarities_to_use]
        
        if rarities_to_use and weights:
            selected_rarity = random.choices(rarities_to_use, weights=weights, k=1)[0]
            selected_skills = skill_pools.get(selected_rarity, [])
            
            if selected_skills:
                new_skill = random.choice(selected_skills)
                if new_skill not in player.get('모험_기술', ['박치기']):
                    if len(player.get('모험_기술', [])) < 4:
                        player['모험_기술'].append(new_skill)
                        rewards['skills'].append(new_skill)
    
    # 돈 지급 안함 (경험치도 안 오름)
    
    # 스테이지 클리어 업데이트
    if stage_id > player.get('모험_클리어스테이지', 0):
        player['모험_클리어스테이지'] = stage_id
    
    return {'success': True, 'rewards': rewards}

def get_skill_info(skill_name):
    """기술 정보 가져오기"""
    from data.adventure_data import SKILLS
    return SKILLS.get(skill_name, {})

def get_all_skills_info():
    """모든 기술 정보 가져오기"""
    from data.adventure_data import SKILLS
    return SKILLS
