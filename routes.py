from flask import render_template, request, redirect, url_for, flash, session, jsonify
from app import app
import game_logic
import json
import os

@app.route('/')
def index():
    """메인 페이지"""
    if 'player_data' not in session:
        return render_template('index.html')
    return redirect(url_for('dashboard'))

@app.route('/start_game', methods=['POST'])
def start_game():
    """새 게임 시작"""
    player_data = game_logic.create_new_player()
    session['player_data'] = player_data
    game_logic.save_game(player_data)
    flash('새로운 인생이 시작되었습니다!', 'success')
    return redirect(url_for('dashboard'))

@app.route('/load_game', methods=['POST'])
def load_game():
    """게임 불러오기"""
    loaded_data = game_logic.load_game()
    if loaded_data:
        session['player_data'] = loaded_data
        flash('게임을 불러왔습니다!', 'success')
        return redirect(url_for('dashboard'))
    else:
        flash('저장된 게임이 없습니다.', 'error')
        return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    """대시보드"""
    if 'player_data' not in session:
        return redirect(url_for('index'))
    
    player = session['player_data']
    stats = game_logic.get_player_stats(player)
    recent_events = game_logic.get_recent_events()
    achievements = game_logic.get_achievements(player)
    
    return render_template('dashboard.html', 
                         player=player, 
                         stats=stats,
                         recent_events=recent_events,
                         achievements=achievements)

@app.route('/quiz')
def quiz():
    """단어 퀴즈 페이지"""
    if 'player_data' not in session:
        return redirect(url_for('index'))
    
    player = session['player_data']
    word_bank = game_logic.get_word_bank()
    categories = game_logic.get_word_categories()
    
    # 선택된 카테고리 확인
    selected_category = request.args.get('category', 'all')
    
    # 카테고리별 단어 필터링
    if selected_category != 'all':
        word_bank = [word for word in word_bank if word.get('카테고리', '기본') == selected_category]
    
    # 퀴즈 세션에서 맞춘 단어들 제외
    session_key = f'quiz_session_correct_{selected_category}'
    if session_key not in session:
        session[session_key] = []
    
    correct_words = session[session_key]
    available_words = [word for word in word_bank if word['단어'] not in correct_words]
    
    # 진행률 계산
    total_words = len(word_bank)
    completed_words = len(correct_words)
    
    return render_template('quiz.html', 
                         player=player, 
                         word_bank=available_words,
                         full_word_bank=word_bank,
                         categories=categories,
                         selected_category=selected_category,
                         total_words=total_words,
                         completed_words=completed_words)

@app.route('/take_quiz', methods=['POST'])
def take_quiz():
    """퀴즈 풀기"""
    if 'player_data' not in session:
        return redirect(url_for('index'))
    
    player = session['player_data']
    selected_category = request.form.get('selected_category', 'all')
    answer = request.form.get('answer', '').strip()
    question_type = request.form.get('question_type')
    correct_answer = request.form.get('correct_answer')
    quiz_word = request.form.get('quiz_word')  # 현재 퀴즈 단어
    
    result = game_logic.process_quiz_answer(player, answer, correct_answer, question_type)
    session['player_data'] = player
    game_logic.save_game(player)
    
    if result['correct']:
        # 세션에서 맞춘 단어 추가 (카테고리별로)
        session_key = f'quiz_session_correct_{selected_category}'
        if session_key not in session:
            session[session_key] = []
        if quiz_word not in session[session_key]:
            session[session_key].append(quiz_word)
            session.modified = True
        
        flash(f'정답! 경험치 +{result["exp_gained"]}', 'success')
    else:
        flash(f'틀렸습니다. 정답은 "{result["correct_answer"]}"입니다.', 'error')
    
    return redirect(url_for('quiz', category=selected_category))

@app.route('/reset_quiz_session', methods=['POST'])
def reset_quiz_session():
    """퀴즈 세션 초기화"""
    selected_category = request.form.get('selected_category', 'all')
    session_key = f'quiz_session_correct_{selected_category}'
    if session_key in session:
        del session[session_key]
    flash('새로운 퀴즈 세션을 시작합니다!', 'info')
    return redirect(url_for('quiz', category=selected_category))

@app.route('/add_word', methods=['POST'])
def add_word():
    """단어 추가"""
    if 'player_data' not in session:
        return redirect(url_for('index'))
    
    player = session['player_data']
    words_text = request.form.get('words', '').strip()
    meanings_text = request.form.get('meanings', '').strip()
    category = request.form.get('category', '기본')
    
    if words_text and meanings_text:
        words = [w.strip() for w in words_text.split('\n') if w.strip()]
        meanings = [m.strip() for m in meanings_text.split('\n') if m.strip()]
        
        if len(words) != len(meanings):
            flash('단어와 뜻의 개수가 다릅니다. 같은 순서로 입력해주세요.', 'error')
        else:
            added_count, exp_gained = game_logic.add_words_to_bank(words, meanings, category, player)
            
            if added_count > 0:
                session['player_data'] = player
                game_logic.save_game(player)
                flash(f'{added_count}개의 단어가 추가되었습니다! 경험치 +{exp_gained}', 'success')
            else:
                flash('모두 중복되는 단어입니다.', 'info')
    else:
        flash('단어와 뜻을 모두 입력해주세요.', 'error')
    
    return redirect(url_for('quiz'))

@app.route('/delete_word', methods=['POST'])
def delete_word():
    """단어 삭제"""
    word_index = int(request.form.get('word_index', 0))
    
    result = game_logic.delete_word_from_bank(word_index)
    
    if result['success']:
        flash(result['message'], 'success')
    else:
        flash(result['message'], 'error')
    
    return redirect(url_for('word_management'))

@app.route('/delete_multiple_words', methods=['POST'])
def delete_multiple_words():
    """여러 단어 삭제"""
    word_indices_str = request.form.get('word_indices', '')
    
    if not word_indices_str:
        flash('삭제할 단어를 선택해주세요.', 'error')
        return redirect(url_for('word_management'))
    
    word_indices = word_indices_str.split(',')
    result = game_logic.delete_multiple_words_from_bank(word_indices)
    
    if result['success']:
        flash(result['message'], 'success')
    else:
        flash(result['message'], 'error')
    
    return redirect(url_for('word_management'))

@app.route('/edit_word', methods=['POST'])
def edit_word():
    """단어 수정"""
    word_index = int(request.form.get('word_index', 0))
    new_word = request.form.get('word', '').strip()
    new_meaning = request.form.get('meaning', '').strip()
    new_category = request.form.get('category', '기본')
    
    if new_word and new_meaning:
        result = game_logic.edit_word_in_bank(word_index, new_word, new_meaning, new_category)
        if result['success']:
            flash(result['message'], 'success')
        else:
            flash(result['message'], 'error')
    else:
        flash('단어와 뜻을 모두 입력해주세요.', 'error')
    
    return redirect(url_for('word_management'))

@app.route('/word_management')
def word_management():
    """단어 관리 페이지"""
    if 'player_data' not in session:
        return redirect(url_for('index'))
    
    player = session['player_data']
    word_bank = game_logic.get_word_bank()
    categories = game_logic.get_word_categories()
    
    # 검색 기능
    search_term = request.args.get('search', '').strip()
    if search_term:
        word_bank = game_logic.search_words(search_term)
    else:
        # 인덱스 추가
        for i, word in enumerate(word_bank):
            word['인덱스'] = str(i)
    
    # 카테고리 필터
    category_filter = request.args.get('category', 'all')
    if category_filter != 'all':
        if search_term:
            word_bank = [word for word in word_bank if word.get('카테고리', '기본') == category_filter]
        else:
            word_bank = game_logic.get_word_by_category(category_filter)
            for i, word in enumerate(word_bank):
                word['인덱스'] = str(i)
    
    return render_template('word_management.html', 
                         player=player, 
                         word_bank=word_bank,
                         categories=categories,
                         search_term=search_term,
                         category_filter=category_filter)

@app.route('/search_words')
def search_words_route():
    """단어 검색 API"""
    search_term = request.args.get('q', '')
    results = game_logic.search_words(search_term) if search_term else []
    return jsonify({'results': results})

@app.route('/job')
def job():
    """직업 관리 페이지"""
    if 'player_data' not in session:
        return redirect(url_for('index'))
    
    player = session['player_data']
    jobs = game_logic.get_jobs()
    
    return render_template('job.html', player=player, jobs=jobs)

@app.route('/apply_job', methods=['POST'])
def apply_job():
    """취업 신청"""
    if 'player_data' not in session:
        return redirect(url_for('index'))
    
    player = session['player_data']
    job_id = int(request.form.get('job_id', 0))
    
    result = game_logic.apply_for_job(player, job_id)
    session['player_data'] = player
    game_logic.save_game(player)
    
    if result['success']:
        flash(result['message'], 'success')
    else:
        flash(result['message'], 'error')
    
    return redirect(url_for('job'))

@app.route('/work', methods=['POST'])
def work():
    """근무하기"""
    if 'player_data' not in session:
        return redirect(url_for('index'))
    
    player = session['player_data']
    result = game_logic.work(player)
    session['player_data'] = player
    game_logic.save_game(player)
    
    if result['success']:
        flash(result['message'], 'success')
    else:
        flash(result['message'], 'error')
    
    return redirect(url_for('job'))

@app.route('/real_estate')
def real_estate():
    """부동산 페이지"""
    if 'player_data' not in session:
        return redirect(url_for('index'))
    
    player = session['player_data']
    properties = game_logic.get_real_estate()
    
    return render_template('real_estate.html', player=player, properties=properties)

@app.route('/buy_property', methods=['POST'])
def buy_property():
    """부동산 구매"""
    if 'player_data' not in session:
        return redirect(url_for('index'))
    
    player = session['player_data']
    property_id = int(request.form.get('property_id', 0))
    
    result = game_logic.buy_property(player, property_id)
    session['player_data'] = player
    game_logic.save_game(player)
    
    if result['success']:
        flash(result['message'], 'success')
    else:
        flash(result['message'], 'error')
    
    return redirect(url_for('real_estate'))

@app.route('/sell_property', methods=['POST'])
def sell_property():
    """부동산 판매"""
    if 'player_data' not in session:
        return redirect(url_for('index'))
    
    player = session['player_data']
    result = game_logic.sell_property(player)
    session['player_data'] = player
    game_logic.save_game(player)
    
    if result['success']:
        flash(result['message'], 'success')
    else:
        flash(result['message'], 'error')
    
    return redirect(url_for('real_estate'))

@app.route('/shop')
def shop():
    """상점 페이지"""
    if 'player_data' not in session:
        return redirect(url_for('index'))
    
    player = session['player_data']
    items = game_logic.get_shop_items()
    
    return render_template('shop.html', player=player, items=items)

@app.route('/buy_item', methods=['POST'])
def buy_item():
    """아이템 구매"""
    if 'player_data' not in session:
        return redirect(url_for('index'))
    
    player = session['player_data']
    item_id = int(request.form.get('item_id', 0))
    
    result = game_logic.buy_item(player, item_id)
    session['player_data'] = player
    game_logic.save_game(player)
    
    if result['success']:
        flash(result['message'], 'success')
    else:
        flash(result['message'], 'error')
    
    return redirect(url_for('shop'))

@app.route('/allocate_stats', methods=['POST'])
def allocate_stats():
    """스탯 분배"""
    if 'player_data' not in session:
        return redirect(url_for('index'))
    
    player = session['player_data']
    stat_type = request.form.get('stat_type')
    points = int(request.form.get('points', 0))
    
    result = game_logic.allocate_stat_points(player, stat_type, points)
    session['player_data'] = player
    game_logic.save_game(player)
    
    if result['success']:
        flash(result['message'], 'success')
    else:
        flash(result['message'], 'error')
    
    return redirect(url_for('dashboard'))

@app.route('/sleep', methods=['POST'])
def sleep():
    """잠자기"""
    if 'player_data' not in session:
        return redirect(url_for('index'))
    
    player = session['player_data']
    result = game_logic.sleep(player)
    session['player_data'] = player
    game_logic.save_game(player)
    
    # 랜덤 이벤트 체크
    event = game_logic.check_random_event(player)
    if event:
        flash(f"이벤트 발생: {event['메시지']}", 'info')
    
    flash(result['message'], 'success')
    return redirect(url_for('dashboard'))

@app.route('/achievements')
def achievements():
    """성취 페이지"""
    if 'player_data' not in session:
        return redirect(url_for('index'))
    
    player = session['player_data']
    achievements = game_logic.get_all_achievements()
    player_achievements = game_logic.get_player_achievements(player)
    achievement_points = game_logic.get_achievement_points(player)
    
    return render_template('achievements.html', 
                         player=player, 
                         achievements=achievements,
                         player_achievements=player_achievements,
                         achievement_points=achievement_points)

@app.route('/api/player_stats')
def api_player_stats():
    """플레이어 통계 API (차트용)"""
    if 'player_data' not in session:
        return jsonify({'error': 'No player data'})
    
    player = session['player_data']
    stats = {
        'stats': [player['힘'], player['지능'], player['외모'], player['체력스탯'], player['운']],
        'labels': ['힘', '지능', '외모', '체력', '운'],
        'level': player['레벨'],
        'exp': player['경험치'],
        'max_exp': player['경험치최대']
    }
    
    return jsonify(stats)
