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
        '모험_현재스테이지': 1,  # 현재 스테이지
        '모험_클리어스테이지': 0,  # 클리어한 최대 스테이지
        '모험_기술': ['박치기'],  # 보유한 기술 목록
        '모험_대표몬스터': None,  # 대표 몬스터 ID
        '모험_아이템': {},  # 모험 아이템 인벤토리
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
        player['경험치최대'] = int(player['경험치최대'] * 1.2)
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
    if random.random() < 0.1:  # 10% 확률
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

def get_conversation_prompt(expression_data):
    """표현에 맞는 대화 프롬프트 생성"""
    conversation_starters = {
        'Break the ice': "I'm new here and don't know anyone. What should I do?",
        'Piece of cake': "This assignment looks really hard. How do you feel about it?",
        'Under the weather': "I haven't seen you in days. Is everything okay?",
        'Cost an arm and a leg': "Have you seen the prices at that new restaurant?",
        'Hit the books': "The exam is next week. What are you planning to do?",
        'On cloud nine': "You look so happy today! What happened?",
        'It rains cats and dogs': "Look at this weather! What do you think?",
        'Go the extra mile': "We need to finish this project on time. Are you willing to work hard?",
        'No pain, no gain': "Training is really tough. Should I keep going?",
        'Better late than never': "I know I'm late with this report, but I finished it!",
        'Spill the beans': "You look like you have something to tell me!",
        'Bite the bullet': "I have to make a difficult decision. What do you think?",
        'See eye to eye': "You and I have different opinions about this project.",
        'Give someone a hand': "I have too many boxes to carry. Can you help?",
        'Keep your fingers crossed': "I'm taking the test tomorrow. Wish me luck!",
        'Catch you later': "I need to go now. See you soon!",
        'No worries': "I'm sorry I made a mistake.",
        'That is piece of cake': "Do you think that problem is difficult?",
        'Once in a blue moon': "How often do you go on vacation?",
        'Get the ball rolling': "We should start this new project soon.",
        'Speak of the devil': "I was just thinking about you!",
        'Couldn\'t care less': "What do you think about this gossip?",
        'Hang in there': "I'm having a really tough time.",
        'Just a minute': "Wait, I need to ask you something!",
        'Let me know': "I need your opinion on this.",
        'Long time no see': "Hey, I haven't seen you in forever!",
        'By the way': "Oh, one more thing before you leave!",
        'How about you': "I love pizza. What's your favorite food?",
        'I promise': "Will you really help me finish this?",
        'That sounds great': "Would you like to go to the beach tomorrow?"
    }
    return conversation_starters.get(expression_data['expression'], "How would you respond to this?")

def get_conversation_translation(expression_name):
    """대화 프롬프트의 한글 해석"""
    translations = {
        'Break the ice': "나는 여기서 아무도 모르는 새로운 사람입니다. 뭘 해야 할까요?",
        'Piece of cake': "이 과제가 정말 어려워 보이는데, 당신은 어떻게 생각하세요?",
        'Under the weather': "며칠 동안 당신을 못 봤는데, 괜찮아요?",
        'Cost an arm and a leg': "그 새로운 레스토랑 가격을 봤나요?",
        'Hit the books': "시험이 다음 주네요. 뭘 할 계획이에요?",
        'On cloud nine': "오늘 정말 행복해 보이는데, 뭐가 있었어요?",
        'It rains cats and dogs': "이 날씨 봤어요? 어떻게 생각하세요?",
        'Go the extra mile': "이 프로젝트를 제 시간에 마쳐야 하는데, 열심히 일할 의향이 있어요?",
        'No pain, no gain': "훈련이 정말 힘든데, 계속해야 할까요?",
        'Better late than never': "이 보고서가 늦었지만, 완료했어요!",
        'Spill the beans': "뭔가 말하고 싶은 게 있는 것 같은데!",
        'Bite the bullet': "어려운 결정을 내려야 하는데, 어떻게 생각하세요?",
        'See eye to eye': "우리는 이 프로젝트에 대해 의견이 다르네요.",
        'Give someone a hand': "박스가 너무 많아서 옮길 수 없어요. 도와줄 수 있어요?",
        'Keep your fingers crossed': "내일 시험을 보는데, 응원해 주세요!",
        'Catch you later': "이제 가야 해요. 곧 봐요!",
        'No worries': "실수해서 미안해요.",
        'That is piece of cake': "그 문제가 어렵다고 생각해요?",
        'Once in a blue moon': "얼마나 자주 휴가를 떠나세요?",
        'Get the ball rolling': "새 프로젝트를 곧 시작해야 할 것 같은데요.",
        'Speak of the devil': "너의 얘기를 하고 있었어!",
        'Couldn\'t care less': "이 소문에 대해 어떻게 생각해요?",
        'Hang in there': "정말 힘든 시간을 보내고 있어요.",
        'Just a minute': "잠깐만, 뭔가 물어볼 게 있어!",
        'Let me know': "당신의 의견이 필요해요.",
        'Long time no see': "오랜만이야, 잘 지냈어?",
        'By the way': "가기 전에 한 가지 더!",
        'How about you': "나는 피자를 좋아해. 너는 어떤 음식을 좋아해?",
        'I promise': "정말 이것을 끝낼 때까지 도와줄 거야?",
        'That sounds great': "내일 해변에 가는 거 어때?"
    }
    return translations.get(expression_name, "이것에 대해 어떻게 대답하시겠어요?")

def get_foreign_speakers():
    """외국인 강사 정보"""
    speakers = [
        {'name': 'SAM', 'image': 'young_idol_man_sam.png'},
        {'name': 'OLIVIA', 'image': 'young_idol_woman_olivia.png'},
        {'name': 'JAMES', 'image': 'young_idol_man_james.png'},
        {'name': 'EMMA', 'image': 'young_idol_woman_emma.png'},
        {'name': 'MICHAEL', 'image': 'young_idol_man_michael.png'}
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
    """플레이어가 보유한 도감 몬스터 반환"""
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
    
    return available

def start_adventure_battle(player, stage_id, selected_monster_id):
    """모험 전투 시작"""
    from data.adventure_data import ADVENTURE_STAGES, ENEMY_DIALOGUES, PLAYER_DIALOGUES
    from data.monsters import get_monster_by_id, get_monsters_by_rarity
    from data.skills import SKILL_INFO
    import random
    
    # 스테이지 정보 가져오기
    stage = next((s for s in ADVENTURE_STAGES if s['stage_id'] == stage_id), None)
    if not stage:
        return {'success': False, 'message': '존재하지 않는 스테이지입니다.'}
    
    # 플레이어 몬스터 확인
    if selected_monster_id not in player['도감']:
        return {'success': False, 'message': '해당 몬스터를 보유하고 있지 않습니다.'}
    
    player_monster = player['도감'][selected_monster_id]
    player_monster_info = get_monster_by_id(selected_monster_id)
    
    if not player_monster_info:
        return {'success': False, 'message': '플레이어 몬스터 정보를 찾을 수 없습니다.'}
    
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
    
    battle_state = {
        'stage_id': stage_id,
        'stage_name': stage['이름'],
        'difficulty': stage['난이도'],
        'player_monster': {
            'id': selected_monster_id,
            'name': player_monster['이름'],
            'rarity': player_monster['등급'],
            'attack': player_monster.get('공격력', 0),
            'max_hp': player_monster.get('체력', 0),
            'current_hp': player_monster.get('체력', 0),
            'image': player_monster.get('이미지', '')
        },
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
        'player_skills': player.get('모험_기술', ['박치기']),
        'game_over': False,
        'winner': None
    }
    
    # 선공 결정 (공격력이 높은 쪽이 먼저)
    if player_monster['공격력'] >= enemy_attack:
        battle_state['player_turn'] = True
        battle_state['log'].append(f"플레이어 몬스터가 높은 공격력으로 선공합니다!")
    else:
        battle_state['player_turn'] = False
        battle_state['log'].append(f"적 몬스터가 높은 공격력으로 선공합니다!")
    
    return {'success': True, 'battle_state': battle_state}

def execute_enemy_turn(battle_state):
    """적의 턴 자동 실행"""
    import random
    
    if battle_state['game_over'] or battle_state['player_turn']:
        return {'success': False, 'battle_state': battle_state}
    
    # 적의 기본 공격
    enemy_damage = battle_state['enemy_monster']['attack']
    battle_state['player_monster']['current_hp'] -= enemy_damage
    battle_state['log'].append(f"적의 공격! {enemy_damage} 데미지")
    
    # 플레이어 체력 확인
    if battle_state['player_monster']['current_hp'] <= 0:
        battle_state['player_monster']['current_hp'] = 0
        battle_state['game_over'] = True
        battle_state['winner'] = 'enemy'
        battle_state['log'].append(f"패배했습니다...")
        return {'success': True, 'battle_state': battle_state}
    
    # 플레이어 차례로 돌아감
    battle_state['player_turn'] = True
    battle_state['turn'] += 1
    
    return {'success': True, 'battle_state': battle_state}

def execute_skill(battle_state, skill_name):
    """기술 실행"""
    from data.skills import SKILL_INFO
    import random
    
    if skill_name not in SKILL_INFO:
        return {'success': False, 'message': '존재하지 않는 기술입니다.'}
    
    skill = SKILL_INFO[skill_name]
    
    if battle_state['game_over']:
        return {'success': False, 'message': '전투가 이미 끝났습니다.'}
    
    if not battle_state['player_turn']:
        return {'success': False, 'message': '지금은 플레이어 차례가 아닙니다.'}
    
    # 플레이어 공격
    player_monster = battle_state['player_monster']
    damage = int(player_monster['attack'] * skill['multiplier'])
    battle_state['enemy_monster']['current_hp'] -= damage
    battle_state['log'].append(f"플레이어 [{skill_name}] 사용! {damage} 데미지")
    
    # 적 체력 확인
    if battle_state['enemy_monster']['current_hp'] <= 0:
        battle_state['enemy_monster']['current_hp'] = 0
        battle_state['game_over'] = True
        battle_state['winner'] = 'player'
        battle_state['log'].append(f"플레이어가 승리했습니다!")
        return {'success': True, 'battle_state': battle_state}
    
    # 적 차례
    battle_state['player_turn'] = False
    battle_state['log'].append(f"\n적 [{battle_state['enemy_monster']['name']}] 차례...")
    
    # 적의 기본 공격
    enemy_damage = battle_state['enemy_monster']['attack']
    battle_state['player_monster']['current_hp'] -= enemy_damage
    battle_state['log'].append(f"적의 공격! {enemy_damage} 데미지")
    
    # 플레이어 체력 확인
    if battle_state['player_monster']['current_hp'] <= 0:
        battle_state['player_monster']['current_hp'] = 0
        battle_state['game_over'] = True
        battle_state['winner'] = 'enemy'
        battle_state['log'].append(f"패배했습니다...")
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
        'exp': 50 * stage_id,
        'money': 100 * stage_id,
        'skills': [],
        'items': []
    }
    
    # 기술 카드 드롭
    if random.random() < stage_config.get('skill_reward_rate', 0.02):
        skill_pools = SKILL_DROP_POOLS.get(stage_id, {})
        all_skills = []
        for rarity, skills in skill_pools.items():
            all_skills.extend(skills)
        
        if all_skills:
            new_skill = random.choice(all_skills)
            if new_skill not in player.get('모험_기술', ['박치기']):
                if len(player.get('모험_기술', [])) < 4:
                    player['모험_기술'].append(new_skill)
                    rewards['skills'].append(new_skill)
    
    # 아이템 드롭
    if random.random() < 0.3:
        item_name = random.choice(list(REWARD_ITEMS.keys()))
        item_count = player['모험_아이템'].get(item_name, 0)
        player['모험_아이템'][item_name] = item_count + 1
        rewards['items'].append(item_name)
    
    # 경험치와 돈 지급
    player['경험치'] += rewards['exp']
    player['돈'] += rewards['money']
    
    # 스테이지 클리어 업데이트
    if stage_id > player.get('모험_클리어스테이지', 0):
        player['모험_클리어스테이지'] = stage_id
    
    return {'success': True, 'rewards': rewards}
