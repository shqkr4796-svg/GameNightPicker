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
                if '던전_인벤토리' not in player:
                    player['던전_인벤토리'] = {}
                
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

def get_random_monster_image(rarity):
    """등급별 몬스터 이미지를 랜덤으로 선택"""
    if rarity == '레어':
        rare_images = [
            '/static/images/monster_1.png',
            '/static/images/monster_2.png', 
            '/static/images/monster_3.png',
            '/static/images/monster_rare_1.png',
            '/static/images/monster_rare_2.png', 
            '/static/images/monster_rare_3.png',
            '/static/images/monster_rare_4.png',
            '/static/images/monster_rare_5.png',
            '/static/images/monster_rare_6.png',
            '/static/images/monster_rare_7.png',
            '/static/images/monster_rare_8.png'
        ]
        return random.choice(rare_images)
    elif rarity == '에픽':
        epic_images = [
            '/static/images/epic_monster_1.png',
            '/static/images/epic_monster_2.png',
            '/static/images/epic_monster_3.png',
            '/static/images/epic_monster_4.png',
            '/static/images/epic_monster_5.png',
            '/static/images/epic_monster_6.png',
            '/static/images/epic_monster_7.png'
        ]
        return random.choice(epic_images)
    elif rarity == '유니크':
        unique_images = [
            '/static/images/unique_monster_1.png',
            '/static/images/unique_monster_2.png',
            '/static/images/unique_monster_3.png',
            '/static/images/unique_monster_4.png',
            '/static/images/unique_monster_5.png',
            '/static/images/unique_monster_6.png',
            '/static/images/unique_monster_7.png',
            '/static/images/unique_monster_8.png',
            '/static/images/unique_monster_9.png'
        ]
        return random.choice(unique_images)
    else:
        # 레전더리는 전용 이미지 사용
        legendary_images = [
            '/static/images/legendary_monster_1.png',
            '/static/images/legendary_monster_2.png',
            '/static/images/legendary_monster_3.png',
            '/static/images/legendary_monster_4.png',
            '/static/images/legendary_monster_5.png',
            '/static/images/legendary_monster_6.png',
            '/static/images/legendary_monster_7.png',
            '/static/images/legendary_monster_8.png',
            '/static/images/legendary_monster_9.png'
        ]
        return random.choice(legendary_images)

def get_tier_conditions():
    """티어별 조건 반환 (업적 포인트 기준)"""
    return [
        {'name': '언랭크', 'image': None, 'color': 'secondary', 'conditions': {'dungeon': 0, 'real_estate': 0, 'level': 1, 'achievement_points': 0}},
        {'name': '브론즈', 'image': '/static/tier_bronze.png', 'color': 'warning', 'conditions': {'dungeon': 1, 'real_estate': 1, 'level': 3, 'achievement_points': 5}},
        {'name': '실버', 'image': '/static/tier_silver.png', 'color': 'light', 'conditions': {'dungeon': 6, 'real_estate': 1, 'level': 7, 'achievement_points': 20}},
        {'name': '골드', 'image': '/static/tier_gold.png', 'color': 'warning', 'conditions': {'dungeon': 16, 'real_estate': 1, 'level': 12, 'achievement_points': 40}},
        {'name': '다이아', 'image': '/static/tier_diamond.png', 'color': 'info', 'conditions': {'dungeon': 31, 'real_estate': 1, 'level': 18, 'achievement_points': 70}},
        {'name': '마스터', 'image': '/static/tier_master.png', 'color': 'primary', 'conditions': {'dungeon': 101, 'real_estate': 1, 'level': 25, 'achievement_points': 120}},
        {'name': '챌린저', 'image': '/static/tier_challenger.png', 'color': 'danger', 'conditions': {'dungeon': 501, 'real_estate': 1, 'level': 35, 'achievement_points': 161}}
    ]

def get_player_tier(player):
    """플레이어 통계에 따른 티어 계산 (업적 포인트 기준)"""
    dungeon_clears = player.get('던전클리어횟수', 0)
    real_estate_count = 1 if player.get('거주지') else 0
    level = player['레벨']
    achievement_points = get_achievement_points(player)
    
    conditions = get_tier_conditions()
    
    # 가장 높은 달성 가능한 티어 찾기
    current_tier = conditions[0]  # 언랭크부터 시작
    
    for tier in conditions[1:]:  # 언랭크 제외
        req = tier['conditions']
        if (dungeon_clears >= req['dungeon'] and 
            real_estate_count >= req['real_estate'] and 
            level >= req['level'] and
            achievement_points >= req['achievement_points']):
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
    """부동산 구매"""
    if property_id < 0 or property_id >= len(real_estate):
        return {'success': False, 'message': '잘못된 부동산 선택입니다.'}
    
    property_info = real_estate[property_id]
    
    if player['돈'] < property_info['매매']:
        return {'success': False, 'message': '돈이 부족합니다.'}
    
    # 기존 거주지가 있다면 최대기력 감소
    if player['거주지']:
        for prop in real_estate:
            if prop['이름'] == player['거주지']:
                player['최대기력'] -= prop['기력회복']
                break
    
    player['돈'] -= property_info['매매']
    player['거주지'] = property_info['이름']
    player['최대기력'] += property_info['기력회복']
    player['기력'] = min(player['최대기력'], player['기력'])
    
    # 부동산 구매 날짜 기록 (30일마다 월세 받기 위함)
    player['부동산구매날짜'] = player['날짜']
    player['마지막월세날짜'] = player['날짜']  # 마지막 월세 받은 날
    
    return {'success': True, 'message': f"{property_info['이름']}을(를) 구매했습니다! 최대 기력이 {property_info['기력회복']}만큼 증가했습니다. 30일마다 월세 수입을 받습니다."}

def sell_property(player):
    """부동산 판매"""
    if player['거주지'] is None:
        return {'success': False, 'message': '거주지가 없습니다.'}
    
    for prop in real_estate:
        if prop['이름'] == player['거주지']:
            sell_price = int(prop['매매'] * 0.8)  # 80% 가격으로 판매
            player['돈'] += sell_price
            player['거주지'] = None
            return {'success': True, 'message': f"{sell_price}원에 판매했습니다."}
    
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
    rent_message = None
    
    if player['시간'] >= 24:
        player['시간'] -= 24
        player['날짜'] += 1
        
        # 30일마다 월세 수입
        rent_message = None
        if player['거주지'] and '부동산구매날짜' in player:
            # 구매일로부터 30일이 지났는지 확인
            days_since_purchase = player['날짜'] - player.get('부동산구매날짜', 0)
            last_rent_day = player.get('마지막월세날짜', player.get('부동산구매날짜', 0))
            days_since_last_rent = player['날짜'] - last_rent_day
            
            # 30일마다 월세 지급 (마지막 월세 받은 날로부터 30일 후)
            if days_since_last_rent >= 30:
                for prop in real_estate:
                    if prop['이름'] == player['거주지']:
                        player['돈'] += prop['월세']
                        player['마지막월세날짜'] = player['날짜']
                        rent_cycles = days_since_last_rent // 30
                        if rent_cycles > 1:
                            rent_message = f'부동산 월세 수입으로 {prop["월세"]:,}원을 받았습니다. ({rent_cycles}개월분)'
                            player['돈'] += prop['월세'] * (rent_cycles - 1)  # 추가 개월분
                        else:
                            rent_message = f'부동산 월세 수입으로 {prop["월세"]:,}원을 받았습니다.'
                        break
    
    # 업적용 통계 업데이트
    if '잠잔_횟수' not in player:
        player['잠잔_횟수'] = 0
    player['잠잔_횟수'] += 1
    
    # 월세 수입 메시지 추가
    base_message = f'충분히 잠을 잤습니다. 기력 +{total_recovery} (기본 4 + 집 보너스 {bonus_recovery}), 체력이 회복되었습니다.'
    if rent_message is not None:
        return {'message': f'{base_message} {rent_message}'}
    else:
        return {'message': base_message}

def check_random_event(player):
    """랜덤 이벤트 확인"""
    if random.random() < 0.1:  # 10% 확률
        event = random.choice(random_events)
        
        # 이벤트 효과 적용
        for effect, value in event['효과'].items():
            if effect in player:
                player[effect] += value
                player[effect] = max(0, player[effect])  # 음수 방지
        
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
    
    # 실제 사용 가능한 단어 수에 맞춰 클리어 조건 조정
    actual_clear_condition = min(dungeon['clear_condition'], len(words))
    word_queue = words[:actual_clear_condition]  # 실제 사용 가능한 단어만큼 선택
    
    # 간소화된 던전 실행 상태 (세션 용량 최적화)
    dungeon_run = {
        'dungeon_id': dungeon_id,
        'word_indices': [words.index(w) for w in word_queue],  # 인덱스만 저장
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
        
        # 문제가 다 떨어졌지만 클리어해야 할 몬스터가 남은 경우, 문제 재사용
        dungeon = get_dungeon_by_id(dungeon_run['dungeon_id'])
        words = load_words_by_source(
            dungeon_run.get('word_source', 'toeic'),
            category_filter=dungeon.get('category_filter') if dungeon else None,
            difficulty_filter=dungeon.get('difficulty_filter') if dungeon else None
        )
        random.shuffle(words)  # 단어 순서 다시 섞기
        
        # 이미 사용한 문제들을 추적하여 중복 방지
        if 'used_word_cycle' not in dungeon_run:
            dungeon_run['used_word_cycle'] = []
        
        # 현재 사이클에서 아직 사용하지 않은 단어들만 선택
        unused_words = [word for word in words if word['단어'] not in dungeon_run['used_word_cycle']]
        
        if not unused_words:
            # 모든 단어를 다 사용했으면 새 사이클 시작
            dungeon_run['used_word_cycle'] = []
            unused_words = words
            flash_message = '모든 문제를 풀었습니다! 새로운 사이클을 시작합니다.'
        else:
            flash_message = None
        
        # 새로운 단어 인덱스 목록 생성 (남은 클리어 조건만큼)
        remaining_clears = dungeon_run['actual_clear_condition'] - dungeon_run['cleared_words']
        new_word_queue = unused_words[:remaining_clears]
        
        # 단어 인덱스 업데이트
        dungeon_run['word_indices'] = [words.index(w) for w in new_word_queue]
        dungeon_run['current_word_index'] = 0
        dungeon_run['total_words'] += len(new_word_queue)
        
        if flash_message:
            # 플래시 메시지를 던전런에 저장 (라우트에서 처리)
            dungeon_run['flash_message'] = flash_message
    
    # 현재 단어 설정
    dungeon = get_dungeon_by_id(dungeon_run['dungeon_id']) if 'dungeon_id' in dungeon_run else None
    words = load_words_by_source(
        dungeon_run.get('word_source', 'toeic'),
        category_filter=dungeon.get('category_filter') if dungeon else None,
        difficulty_filter=dungeon.get('difficulty_filter') if dungeon else None
    )
    word_index = dungeon_run['word_indices'][dungeon_run['current_word_index']]
    current_word = words[word_index]
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
    
    # 몬스터 ID 생성 (단어 + 등급 기반 해시)
    monster_seed = f"{current_word['단어']}_{selected_rarity}"
    monster_id = hashlib.md5(monster_seed.encode()).hexdigest()[:8]
    dungeon_run['monster_id'] = monster_id
    
    # 몬스터 이미지 등급별 랜덤 할당
    dungeon_run['monster_image'] = get_random_monster_image(selected_rarity)
    
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

def update_compendium(player, dungeon_run):
    """몬스터 도감 업데이트"""
    try:
        # 플레이어 도감 초기화 (없다면)
        if '도감' not in player:
            player['도감'] = {}
            
        monster_id = dungeon_run['monster_id']
        rarity = dungeon_run['current_rarity']
        word = dungeon_run['current_word']['단어']
        
        is_new_monster = False
        if monster_id not in player['도감']:
            player['도감'][monster_id] = {
                '이름': f"{word} {rarity}",
                '등급': rarity,
                '단어': word,
                '이미지': dungeon_run.get('monster_image', '/static/images/monster_1.png'),
                '최초처치일': datetime.now().isoformat(),
                '처치수': 1,
                '포획됨': True
            }
            is_new_monster = True
        else:
            player['도감'][monster_id]['처치수'] += 1
        
        return is_new_monster
    except Exception as e:
        print(f"도감 업데이트 오류: {e}")
        # 오류가 발생해도 게임이 멈추지 않도록 pass
        return False

def check_dungeon_clear(dungeon_run):
    """던전 클리어 확인"""
    return dungeon_run['cleared_words'] >= dungeon_run['actual_clear_condition']

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
    """오늘의 표현 5개 반환"""
    expressions = [
        {
            'expression': 'Break the ice',
            'example': 'Let me break the ice by introducing myself.',
            'meaning': '어색한 분위기를 깨뜨리다',
            'situation': '처음 만난 사람들과의 대화를 시작할 때',
            'tip': '얼음을 깨뜨린다는 의미에서 비롯된 관용구입니다.'
        },
        {
            'expression': 'Piece of cake',
            'example': 'This project is a piece of cake for me.',
            'meaning': '아주 쉬운 일',
            'situation': '어떤 일이 매우 간단하고 쉬울 때',
            'tip': '케이크 한 조각처럼 쉽다는 의미입니다.'
        },
        {
            'expression': 'Under the weather',
            'example': 'I am feeling under the weather today.',
            'meaning': '기분이 좋지 않은, 몸이 안 좋은',
            'situation': '감기나 피로로 컨디션이 안 좋을 때',
            'tip': '날씨 아래에 있다는 의미에서 나온 표현입니다.'
        },
        {
            'expression': 'Cost an arm and a leg',
            'example': 'This vacation will cost us an arm and a leg.',
            'meaning': '매우 비싼, 많은 비용이 드는',
            'situation': '가격이 매우 비싼 물건이나 서비스를 설명할 때',
            'tip': '팔과 다리를 써야 할 정도로 비싸다는 의미입니다.'
        },
        {
            'expression': 'Hit the books',
            'example': 'I need to hit the books for my exam.',
            'meaning': '열심히 공부하다',
            'situation': '시험 준비나 공부에 집중할 때',
            'tip': '책을 치면서 공부한다는 의미입니다.'
        }
    ]
    return expressions
