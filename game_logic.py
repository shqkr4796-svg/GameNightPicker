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
        '도감': {}  # 몬스터 도감
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
                
                # 부동산 30일 월세 시스템 마이그레이션
                if player['거주지'] and '부동산구매날짜' not in player:
                    # 기존 플레이어는 즉시 월세를 받을 수 있도록 설정
                    player['부동산구매날짜'] = player['날짜'] - 30
                    player['마지막월세날짜'] = player['날짜'] - 30
                
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
    """단어장 가져오기 - 항상 최신 데이터 반환"""
    global _word_bank_cache
    # 캐시를 사용하지 않고 항상 파일에서 직접 로드
    if os.path.exists(WORD_BANK_FILE):
        _word_bank_cache = load_word_bank()
    else:
        _word_bank_cache = word_bank.copy()  # 기본값 복사
        save_word_bank(_word_bank_cache)  # 초기 파일 생성
    return _word_bank_cache.copy()  # 복사본 반환으로 원본 보호

def get_word_categories():
    """단어 카테고리 목록"""
    current_word_bank = get_word_bank()
    categories = set()
    for word in current_word_bank:
        categories.add(word.get('카테고리', '기본'))
    return list(categories)

def add_word_to_bank(word, meaning, category='기본'):
    """단어장에 단어 추가"""
    current_word_bank = get_word_bank()
    
    # 중복 체크
    existing_words = {w['단어'].lower() for w in current_word_bank}
    if word.lower() not in existing_words:
        current_word_bank.append({
            '단어': word,
            '뜻': meaning,
            '카테고리': category
        })
        save_word_bank(current_word_bank)
        return True
    return False

def add_words_to_bank(words, meanings, category, player):
    """여러 단어를 단어장에 추가하고 새 단어에 대해 경험치 지급"""
    current_word_bank = get_word_bank()  # 최신 단어장 로드
    
    added_count = 0
    exp_gained = 0
    
    # 기존 단어 목록 (소문자로 변환해서 비교)
    existing_words = {word['단어'].lower() for word in current_word_bank}
    
    for word, meaning in zip(words, meanings):
        # 중복 체크 (대소문자 무시)
        if word.lower() not in existing_words:
            current_word_bank.append({
                '단어': word,
                '뜻': meaning,
                '카테고리': category
            })
            existing_words.add(word.lower())  # 같은 요청 내에서 중복 방지
            added_count += 1
            
            # 새 단어 등록 시 경험치 0.5 획득
            player['경험치'] += 0.5
            exp_gained += 0.5
    
    # 단어장 저장
    save_word_bank(current_word_bank)
    
    # 레벨업 확인
    level_ups = check_level_up(player)
    
    return added_count, exp_gained

def delete_word_from_bank(word_index):
    """단어장에서 단어 삭제"""
    current_word_bank = get_word_bank()  # 최신 단어장 로드
    
    try:
        if 0 <= word_index < len(current_word_bank):
            deleted_word = current_word_bank.pop(word_index)
            save_word_bank(current_word_bank)  # 변경사항 저장
            return {'success': True, 'message': f'단어 "{deleted_word["단어"]}"가 삭제되었습니다.'}
        else:
            return {'success': False, 'message': '잘못된 단어 번호입니다.'}
    except Exception as e:
        return {'success': False, 'message': '단어 삭제 중 오류가 발생했습니다.'}

def delete_multiple_words_from_bank(word_indices):
    """단어장에서 여러 단어 삭제"""
    current_word_bank = get_word_bank()  # 최신 단어장 로드
    
    try:
        # 인덱스를 내림차순으로 정렬하여 뒤에서부터 삭제
        word_indices = sorted([int(idx) for idx in word_indices], reverse=True)
        deleted_words = []
        
        for index in word_indices:
            if 0 <= index < len(current_word_bank):
                deleted_word = current_word_bank.pop(index)
                deleted_words.append(deleted_word['단어'])
        
        if deleted_words:
            save_word_bank(current_word_bank)  # 변경사항 저장
            return {'success': True, 'message': f'{len(deleted_words)}개의 단어가 삭제되었습니다.'}
        else:
            return {'success': False, 'message': '삭제할 수 있는 단어가 없습니다.'}
    except Exception as e:
        return {'success': False, 'message': '단어 삭제 중 오류가 발생했습니다.'}

def edit_word_in_bank(word_index, new_word, new_meaning, new_category):
    """단어장의 단어 수정"""
    current_word_bank = get_word_bank()  # 최신 단어장 로드
    
    try:
        if 0 <= word_index < len(current_word_bank):
            current_word_bank[word_index] = {
                '단어': new_word,
                '뜻': new_meaning,
                '카테고리': new_category
            }
            save_word_bank(current_word_bank)  # 변경사항 저장
            return {'success': True, 'message': f'단어 "{new_word}"가 수정되었습니다.'}
        else:
            return {'success': False, 'message': '잘못된 단어 번호입니다.'}
    except Exception as e:
        return {'success': False, 'message': '단어 수정 중 오류가 발생했습니다.'}

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
    
    # 토익 단어 로드
    words = load_toeic_words()
    if not words:
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
        'actual_clear_condition': actual_clear_condition  # 실제 클리어 조건 저장
    }
    
    # 첫 번째 몬스터 생성
    result = next_monster(dungeon_run, dungeon)
    if not result['success']:
        return result
        
    return {'success': True, 'dungeon_run': dungeon_run}

def next_monster(dungeon_run, dungeon):
    """다음 몬스터 생성"""
    # 클리어한 몬스터 수가 목표에 도달했는지 확인
    if dungeon_run['cleared_words'] >= dungeon_run['actual_clear_condition']:
        return {'success': False, 'message': '던전을 완료했습니다!'}
    
    # 현재 단어 인덱스가 범위를 벗어났는지 확인
    if dungeon_run['current_word_index'] >= len(dungeon_run['word_indices']):
        return {'success': False, 'message': '던전을 완료했습니다!'}
    
    # 현재 단어 설정 (랜덤 단어 선택)
    words = load_toeic_words()
    current_word = random.choice(words)
    dungeon_run['current_word'] = current_word
    
    # 몬스터 등급 결정 (확률 기반)
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
    
    # 몬스터 HP 설정
    dungeon_run['monster_hp'] = monster_rarities[selected_rarity]['required_correct']
    dungeon_run['monster_progress'] = 0
    
    # 4지선다 문제 생성
    result = build_question(dungeon_run, dungeon)
    return result

def build_question(dungeon_run, dungeon):
    """4지선다 문제 생성"""
    current_word = dungeon_run['current_word']
    correct_answer = current_word['뜻']
    
    # 토익 단어에서 오답 생성
    all_words = load_toeic_words()
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
        # 정답
        dungeon_run['monster_progress'] += 1
        
        result_msg = "정답! 몬스터에게 피해를 입혔습니다."
        
        # 몬스터 처치 확인
        if dungeon_run['monster_progress'] >= dungeon_run['monster_hp']:
            # 몬스터 처치
            rarity = dungeon_run['current_rarity']
            capture_rate = monster_rarities[rarity]['capture_rate']
            
            if random.random() < capture_rate:
                # 몬스터 포획 성공
                update_compendium(player, dungeon_run)
                result_msg += f" {rarity} 몬스터를 처치하고 도감에 등록했습니다!"
            else:
                result_msg += f" {rarity} 몬스터를 처치했지만 도감 등록에 실패했습니다."
            
            # 처치한 단어 수 및 인덱스 증가
            dungeon_run['cleared_words'] += 1
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
        
        if dungeon_run['player_hp'] <= 0:
            return {'success': True, 'correct': False, 'game_over': True, 'message': '체력이 0이 되어 던전에서 퇴장됩니다.'}
        else:
            return {'success': True, 'correct': False, 'game_over': False, 'message': f'오답! 체력이 1 감소했습니다. (남은 체력: {dungeon_run["player_hp"]})'}

def build_next_question(dungeon_run):
    """같은 몬스터에 대해 다음 문제 생성"""
    # 모든 단어에서 현재 단어와 다른 단어를 랜덤하게 선택
    words = load_toeic_words()
    current_word_text = dungeon_run['current_word']['단어']
    
    # 현재 단어와 다른 단어들 중에서 랜덤 선택
    available_words = [word for word in words if word['단어'] != current_word_text]
    if available_words:
        new_word = random.choice(available_words)
        dungeon_run['current_word'] = new_word
        
        # 새로운 문제 생성
        return build_question(dungeon_run, None)
    else:
        # 사용 가능한 다른 단어가 없으면 기존 문제 재생성
        return build_question(dungeon_run, None)

def update_compendium(player, dungeon_run):
    """몬스터 도감 업데이트"""
    try:
        # 플레이어 도감 초기화 (없다면)
        if '도감' not in player:
            player['도감'] = {}
            
        monster_id = dungeon_run['monster_id']
        rarity = dungeon_run['current_rarity']
        word = dungeon_run['current_word']['단어']
        
        if monster_id not in player['도감']:
            player['도감'][monster_id] = {
                '이름': f"{word} {rarity}",
                '등급': rarity,
                '단어': word,
                '최초처치일': datetime.now().isoformat(),
                '처치수': 1,
                '포획됨': True
            }
        else:
            player['도감'][monster_id]['처치수'] += 1
    except Exception as e:
        print(f"도감 업데이트 오류: {e}")
        # 오류가 발생해도 게임이 멈추지 않도록 pass

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
        if effect == '던전_체력' and dungeon_run:
            # 던전 체력 회복 - 플레이어 실제 체력도 함께 회복
            max_health = 10  # 플레이어 최대 체력
            old_hp = dungeon_run['player_hp']
            heal_amount = min(value, max_health - old_hp)
            dungeon_run['player_hp'] = min(dungeon_run['player_hp'] + value, max_health)
            player['체력'] = min(player['체력'] + heal_amount, max_health)
            actual_heal = dungeon_run['player_hp'] - old_hp
            result_message += f'체력이 {actual_heal} 회복되었습니다. '
        elif effect == '부활' and dungeon_run:
            # 부활 효과는 나중에 처리하기 위해 플레이어에 플래그 저장
            if '던전_버프' not in player:
                player['던전_버프'] = {}
            player['던전_버프']['부활'] = player['던전_버프'].get('부활', 0) + value
            result_message += '부활 효과가 적용되었습니다. '
        # 기타 효과들은 필요시 추가 구현
    
    return {'success': True, 'message': result_message.strip(), 'item': item_data}
