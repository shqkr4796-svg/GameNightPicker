import json
import random
import os
from datetime import datetime
from data.game_data import *

SAVE_FILE = 'savegame.json'
EVENTS_FILE = 'events.json'

def create_new_player():
    """새 플레이어 생성"""
    return {
        '레벨': 1, '경험치': 0, '경험치최대': 100, '스탯포인트': 0,
        '힘': 0, '지능': 0, '외모': 0, '체력스탯': 0, '운': 0,
        '체력': 10, '기력': 10, '직장': None, '직장정보': None,
        '돈': 0, '거주지': None, '날짜': 1, '시간': 8, '질병': None,
        '인벤토리': [], '성취': [], '총_퀴즈': 0, '정답_퀴즈': 0
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
                return json.load(f)
    except Exception as e:
        print(f"불러오기 실패: {e}")
    return None

def check_level_up(player):
    """레벨업 확인"""
    level_ups = 0
    while player['경험치'] >= player['경험치최대']:
        player['레벨'] += 1
        player['스탯포인트'] += 5
        player['경험치'] -= player['경험치최대']
        player['경험치최대'] = int(player['경험치최대'] * 1.2)
        level_ups += 1
    return level_ups

def get_player_stats(player):
    """플레이어 통계 정보"""
    total_stats = player['힘'] + player['지능'] + player['외모'] + player['체력스탯'] + player['운']
    quiz_accuracy = 0
    if player['총_퀴즈'] > 0:
        quiz_accuracy = (player['정답_퀴즈'] / player['총_퀴즈']) * 100
    
    return {
        'total_stats': total_stats,
        'quiz_accuracy': quiz_accuracy,
        'wealth_rank': get_wealth_rank(player['돈']),
        'days_played': player['날짜']
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

def get_word_bank():
    """단어장 가져오기"""
    return word_bank

def get_word_categories():
    """단어 카테고리 목록"""
    categories = set()
    for word in word_bank:
        categories.add(word.get('카테고리', '기본'))
    return list(categories)

def add_word_to_bank(word, meaning, category='기본'):
    """단어장에 단어 추가"""
    word_bank.append({
        '단어': word,
        '뜻': meaning,
        '카테고리': category
    })

def delete_word_from_bank(word_index):
    """단어장에서 단어 삭제"""
    try:
        if 0 <= word_index < len(word_bank):
            deleted_word = word_bank.pop(word_index)
            return {'success': True, 'message': f'단어 "{deleted_word["단어"]}"가 삭제되었습니다.'}
        else:
            return {'success': False, 'message': '잘못된 단어 번호입니다.'}
    except Exception as e:
        return {'success': False, 'message': '단어 삭제 중 오류가 발생했습니다.'}

def edit_word_in_bank(word_index, new_word, new_meaning, new_category):
    """단어장의 단어 수정"""
    try:
        if 0 <= word_index < len(word_bank):
            word_bank[word_index] = {
                '단어': new_word,
                '뜻': new_meaning,
                '카테고리': new_category
            }
            return {'success': True, 'message': f'단어 "{new_word}"가 수정되었습니다.'}
        else:
            return {'success': False, 'message': '잘못된 단어 번호입니다.'}
    except Exception as e:
        return {'success': False, 'message': '단어 수정 중 오류가 발생했습니다.'}

def get_word_by_category(category='all'):
    """카테고리별 단어 조회"""
    if category == 'all':
        return word_bank
    else:
        return [word for word in word_bank if word.get('카테고리', '기본') == category]

def search_words(search_term):
    """단어 검색"""
    search_term = search_term.lower()
    results = []
    for i, word in enumerate(word_bank):
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
    
    # 스탯 요구사항 확인 (간단한 예시)
    required_stats = job['힘'] + job['지능'] + job['외모'] + job['체력스탯'] + job['운']
    player_stats = player['힘'] + player['지능'] + player['외모'] + player['체력스탯'] + player['운']
    
    if player_stats >= required_stats * 0.5:  # 요구 스탯의 50% 이상
        player['직장'] = job['이름']
        player['직장정보'] = job
        return {'success': True, 'message': f"{job['이름']}에 취업했습니다!"}
    else:
        return {'success': False, 'message': '스탯이 부족하여 취업할 수 없습니다.'}

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
    
    level_ups = check_level_up(player)
    
    message = f"{salary}원을 벌었습니다. 기력 -3, 경험치 획득"
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
    
    player['돈'] -= property_info['매매']
    player['거주지'] = property_info['이름']
    player['기력'] = min(10, player['기력'] + property_info['기력회복'])
    
    return {'success': True, 'message': f"{property_info['이름']}을(를) 구매했습니다!"}

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
    """아이템 구매"""
    if item_id < 0 or item_id >= len(shop_items):
        return {'success': False, 'message': '잘못된 아이템 선택입니다.'}
    
    item = shop_items[item_id]
    
    if player['돈'] < item['가격']:
        return {'success': False, 'message': '돈이 부족합니다.'}
    
    player['돈'] -= item['가격']
    
    # 아이템 효과 적용
    for effect, value in item['효과'].items():
        if effect in player:
            player[effect] = min(player[effect] + value, 10)  # 최대 10으로 제한
    
    player['인벤토리'].append(item['이름'])
    
    return {'success': True, 'message': f"{item['이름']}을(를) 구매했습니다!"}

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
    recovery = 10
    if player['거주지']:
        for prop in real_estate:
            if prop['이름'] == player['거주지']:
                recovery = prop['기력회복']
                break
    
    player['기력'] = recovery
    player['체력'] = 10
    player['시간'] += 8
    
    if player['시간'] >= 24:
        player['시간'] -= 24
        player['날짜'] += 1
        
        # 월세 지불
        if player['거주지']:
            for prop in real_estate:
                if prop['이름'] == player['거주지']:
                    if player['돈'] >= prop['월세']:
                        player['돈'] -= prop['월세']
                    else:
                        player['거주지'] = None  # 월세를 못 내면 쫓겨남
                        return {'message': f'월세를 내지 못해 {prop["이름"]}에서 쫓겨났습니다.'}
    
    return {'message': '충분히 잠을 잤습니다. 기력과 체력이 회복되었습니다.'}

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
    """성취 확인"""
    achievements = []
    
    # 레벨 관련 성취
    if player['레벨'] >= 10:
        achievements.append('레벨 마스터')
    
    # 돈 관련 성취
    if player['돈'] >= 1000000:
        achievements.append('백만장자')
    
    # 퀴즈 관련 성취
    if player['정답_퀴즈'] >= 100:
        achievements.append('퀴즈왕')
    
    # 직업 관련 성취
    if player['직장'] and 'CEO' in player['직장']:
        achievements.append('성공한 사업가')
    
    return achievements

def get_all_achievements():
    """모든 성취 목록"""
    return [
        {'이름': '레벨 마스터', '설명': '레벨 10 달성', '조건': 'level_10'},
        {'이름': '백만장자', '설명': '100만원 이상 보유', '조건': 'money_1m'},
        {'이름': '퀴즈왕', '설명': '퀴즈 100문제 정답', '조건': 'quiz_100'},
        {'이름': '성공한 사업가', '설명': 'CEO 직업 달성', '조건': 'ceo_job'},
        {'이름': '부동산왕', '설명': '펜트하우스 소유', '조건': 'penthouse'},
        {'이름': '체력짱', '설명': '체력 스탯 50 달성', '조건': 'strength_50'},
        {'이름': '천재', '설명': '지능 스탯 50 달성', '조건': 'intelligence_50'}
    ]

def get_player_achievements(player):
    """플레이어가 달성한 성취 목록"""
    achieved = []
    
    if player['레벨'] >= 10:
        achieved.append('level_10')
    if player['돈'] >= 1000000:
        achieved.append('money_1m')
    if player['정답_퀴즈'] >= 100:
        achieved.append('quiz_100')
    if player['직장'] and 'CEO' in player['직장']:
        achieved.append('ceo_job')
    if player['거주지'] and '펜트하우스' in player['거주지']:
        achieved.append('penthouse')
    if player['체력스탯'] >= 50:
        achieved.append('strength_50')
    if player['지능'] >= 50:
        achieved.append('intelligence_50')
    
    return achieved
