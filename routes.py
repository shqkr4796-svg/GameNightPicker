from flask import render_template, request, redirect, url_for, flash, session, jsonify
from app import app
import game_logic
import json
import os
import random

@app.route('/')
def index():
    """메인 페이지"""
    return render_template('index.html')

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

@app.route('/daily_expressions')
def daily_expressions():
    """일일 표현 페이지"""
    if 'player_data' not in session:
        return redirect(url_for('index'))
    
    player = session['player_data']
    expressions = game_logic.get_daily_expressions()
    current_date = player['날짜']
    
    # 새로운 날짜이면 진도 초기화
    if player['일일표현_마지막날짜'] != current_date:
        player['일일표현_진도'] = 0
        player['일일표현_완료'] = False
        player['일일표현_마지막날짜'] = current_date
        session.modified = True
    
    progress = player['일일표현_진도']
    completed = player['일일표현_완료']
    current_index = min(progress, 4)  # 0~4 인덱스
    
    return render_template('daily_expressions.html',
                         expressions=expressions,
                         progress=progress,
                         completed=completed,
                         current_index=current_index)

@app.route('/check_daily_expression', methods=['POST'])
def check_daily_expression():
    """일일 표현 확인"""
    if 'player_data' not in session:
        return redirect(url_for('index'))
    
    player = session['player_data']
    user_input = request.form.get('user_input', '').strip().lower()
    index = int(request.form.get('index', 0))
    
    expressions = game_logic.get_daily_expressions()
    correct_expression = expressions[index]['expression'].lower()
    
    # 부분 일치 확인 (사용자 입력이 정답을 포함하면 정답)
    if correct_expression in user_input or user_input in correct_expression:
        player['일일표현_진도'] += 1
        flash(f'정답입니다! ✓ ({player["일일표현_진도"]}/5)', 'success')
        
        # 5개를 모두 완료했는지 확인
        if player['일일표현_진도'] >= 5:
            player['일일표현_완료'] = True
            # 보상: 경험치 +50
            exp_gained = 50
            player['경험치'] += exp_gained
            flash(f'오늘의 표현 학습을 완료했습니다! 경험치 +{exp_gained} 획득! 🎉', 'success')
            
            # 레벨업 확인
            while player['경험치'] >= player['경험치최대']:
                player['경험치'] -= player['경험치최대']
                player['레벨'] += 1
                player['경험치최대'] = int(player['경험치최대'] * 1.1)
                player['스탯포인트'] += 5
                flash(f'레벨업! 현재 레벨: {player["레벨"]}', 'warning')
    else:
        flash(f'틀렸습니다. 다시 시도해보세요. (정답: {correct_expression})', 'error')
    
    session['player_data'] = player
    session.modified = True
    game_logic.save_game(player)
    
    return redirect(url_for('daily_expressions'))

@app.route('/quiz')
def quiz():
    """단어 퀴즈 페이지"""
    if 'player_data' not in session:
        return redirect(url_for('index'))
    
    player = session['player_data']
    word_bank = game_logic.get_user_words()
    # 사용자 단어에서만 카테고리 추출
    categories = list(set([word.get('카테고리', '기본') for word in word_bank]))
    
    # 선택된 카테고리 및 언어 확인
    selected_category = request.args.get('category', 'all')
    selected_language = request.args.get('language', 'random')
    
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
    
    # 틀린 문제들 가져오기
    wrong_session_key = f'quiz_session_wrong_{selected_category}'
    wrong_questions = session.get(wrong_session_key, [])
    
    return render_template('quiz.html', 
                         player=player, 
                         word_bank=available_words,
                         full_word_bank=word_bank,
                         categories=categories,
                         selected_category=selected_category,
                         selected_language=selected_language,
                         total_words=total_words,
                         completed_words=completed_words,
                         wrong_questions=wrong_questions,
                         has_wrong_questions=len(wrong_questions) > 0)

@app.route('/take_quiz', methods=['POST'])
def take_quiz():
    """퀴즈 풀기"""
    if 'player_data' not in session:
        return redirect(url_for('index'))
    
    player = session['player_data']
    selected_category = request.form.get('selected_category', 'all')
    selected_language = request.form.get('selected_language', request.args.get('language', 'random'))  # POST에서 우선, 없으면 URL에서
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
        
        message = f'정답! 경험치 +{result["exp_gained"]}'
        message_type = 'success'
    else:
        # 틀린 문제 저장 (카테고리별로)
        wrong_session_key = f'quiz_session_wrong_{selected_category}'
        if wrong_session_key not in session:
            session[wrong_session_key] = []
        
        # 단어 정보를 완전하게 저장 (사용자 단어에서만)
        user_word_bank = game_logic.get_user_words()
        full_word_info = None
        for word_info in user_word_bank:
            if word_info['단어'] == quiz_word:
                full_word_info = word_info
                break
        
        if full_word_info and full_word_info not in session[wrong_session_key]:
            session[wrong_session_key].append(full_word_info)
            session.modified = True
        
        message = f'틀렸습니다. 정답: {correct_answer}'
        message_type = 'error'
    
    return jsonify({
        'correct': result['correct'],
        'message': message,
        'message_type': message_type,
        'exp_gained': result.get('exp_gained', 0)
    })

@app.route('/reset_quiz_session', methods=['POST'])
def reset_quiz_session():
    """퀴즈 세션 초기화"""
    if 'player_data' not in session:
        return redirect(url_for('index'))
    
    selected_category = request.form.get('selected_category', 'all')
    
    # 해당 카테고리의 세션 초기화
    session_key = f'quiz_session_correct_{selected_category}'
    wrong_session_key = f'quiz_session_wrong_{selected_category}'
    
    if session_key in session:
        del session[session_key]
    if wrong_session_key in session:
        del session[wrong_session_key]
    
    session.modified = True
    flash('퀴즈 진행 상황이 초기화되었습니다.', 'info')
    
    return redirect(url_for('quiz', category=selected_category))

@app.route('/quiz/retry_wrong')
def quiz_retry_wrong():
    """틀린 문제 다시 풀기"""
    if 'player_data' not in session:
        return redirect(url_for('index'))
    
    player = session['player_data']
    selected_category = request.args.get('category', 'all')
    
    wrong_session_key = f'quiz_session_wrong_{selected_category}'
    wrong_questions = session.get(wrong_session_key, [])
    
    if not wrong_questions:
        flash('틀린 문제가 없습니다.', 'info')
        return redirect(url_for('quiz', category=selected_category))
    
    return render_template('quiz_wrong_retry.html',
                         player=player,
                         wrong_questions=wrong_questions,
                         selected_category=selected_category,
                         total_wrong=len(wrong_questions))

@app.route('/quiz/retry_wrong/answer', methods=['POST'])
def quiz_retry_wrong_answer():
    """틀린 문제 답변"""
    if 'player_data' not in session:
        return redirect(url_for('index'))
    
    player = session['player_data']
    selected_category = request.form.get('selected_category', 'all')
    answer = request.form.get('answer', '').strip()
    question_type = request.form.get('question_type')
    correct_answer = request.form.get('correct_answer')
    word_to_remove = request.form.get('word_to_remove')
    
    result = game_logic.process_quiz_answer(player, answer, correct_answer, question_type)
    
    if result['correct']:
        wrong_session_key = f'quiz_session_wrong_{selected_category}'
        if wrong_session_key in session:
            session[wrong_session_key] = [w for w in session[wrong_session_key] if w.get('단어') != word_to_remove]
            session.modified = True
        
        message = f'정답! 경험치 +{result["exp_gained"]}'
        message_type = 'success'
    else:
        message = f'틀렸습니다. 정답: {correct_answer}'
        message_type = 'error'
    
    session['player_data'] = player
    game_logic.save_game(player)
    
    return jsonify({
        'correct': result['correct'],
        'message': message,
        'message_type': message_type,
        'exp_gained': result.get('exp_gained', 0)
    })

@app.route('/add_word', methods=['POST'])
def add_word():
    """단어 추가"""
    if 'player_data' not in session:
        return redirect(url_for('index'))
    
    word = request.form.get('word')
    meaning = request.form.get('meaning')
    example = request.form.get('example')
    category = request.form.get('category', '기본')
    
    result = game_logic.add_user_word(word, meaning, example, category)
    
    if result['success']:
        flash(f'단어 "{word}"가 추가되었습니다!', 'success')
    else:
        flash(result['message'], 'error')
    
    return redirect(url_for('word_management'))

@app.route('/save_word_from_quiz', methods=['POST'])
def save_word_from_quiz():
    """퀴즈에서 단어 저장"""
    if 'player_data' not in session:
        return redirect(url_for('index'))
    
    word = request.form.get('word')
    meaning = request.form.get('meaning')
    
    result = game_logic.add_user_word(word, meaning, '', '기본')
    
    if result['success']:
        return jsonify({'success': True, 'message': f'단어 "{word}"가 저장되었습니다!'})
    else:
        return jsonify({'success': False, 'message': result['message']})

@app.route('/save_category_words', methods=['POST'])
def save_category_words():
    """카테고리 단어 저장"""
    data = request.get_json()
    category = data.get('category')
    words = data.get('words', [])
    
    success_count = 0
    for word_data in words:
        result = game_logic.add_user_word(
            word_data.get('word'),
            word_data.get('meaning'),
            word_data.get('example', ''),
            category
        )
        if result['success']:
            success_count += 1
    
    return jsonify({
        'success': True,
        'message': f'{success_count}개의 단어가 저장되었습니다!'
    })

@app.route('/delete_word', methods=['POST'])
def delete_word():
    """단어 삭제"""
    if 'player_data' not in session:
        return redirect(url_for('index'))
    
    word = request.form.get('word')
    result = game_logic.delete_user_word(word)
    
    if result['success']:
        flash(f'단어 "{word}"가 삭제되었습니다!', 'success')
    else:
        flash(result['message'], 'error')
    
    return redirect(url_for('word_management'))

@app.route('/delete_multiple_words', methods=['POST'])
def delete_multiple_words():
    """여러 단어 삭제"""
    if 'player_data' not in session:
        return redirect(url_for('index'))
    
    words = request.form.getlist('words[]')
    
    success_count = 0
    for word in words:
        result = game_logic.delete_user_word(word)
        if result['success']:
            success_count += 1
    
    flash(f'{success_count}개의 단어가 삭제되었습니다!', 'success')
    return redirect(url_for('word_management'))

@app.route('/change_multiple_categories', methods=['POST'])
def change_multiple_categories():
    """여러 단어 카테고리 변경"""
    if 'player_data' not in session:
        return redirect(url_for('index'))
    
    words = request.form.getlist('words[]')
    new_category = request.form.get('category')
    
    success_count = 0
    for word in words:
        result = game_logic.change_word_category(word, new_category)
        if result['success']:
            success_count += 1
    
    flash(f'{success_count}개의 단어 카테고리가 변경되었습니다!', 'success')
    return redirect(url_for('word_management'))

@app.route('/edit_word', methods=['POST'])
def edit_word():
    """단어 수정"""
    if 'player_data' not in session:
        return redirect(url_for('index'))
    
    old_word = request.form.get('old_word')
    new_word = request.form.get('word')
    meaning = request.form.get('meaning')
    example = request.form.get('example', '')
    category = request.form.get('category', '기본')
    
    result = game_logic.edit_user_word(old_word, new_word, meaning, example, category)
    
    if result['success']:
        flash(f'단어가 수정되었습니다!', 'success')
    else:
        flash(result['message'], 'error')
    
    return redirect(url_for('word_management'))

@app.route('/word_management')
def word_management():
    """단어 관리 페이지"""
    if 'player_data' not in session:
        return redirect(url_for('index'))
    
    player = session['player_data']
    words = game_logic.get_user_words()
    categories = list(set([word.get('카테고리', '기본') for word in words]))
    categories.sort()
    
    return render_template('word_management.html',
                         player=player,
                         words=words,
                         categories=categories,
                         total_words=len(words))

@app.route('/search_words')
def search_words_route():
    return redirect(url_for('word_management'))

@app.route('/job')
def job():
    """직업 선택 페이지"""
    if 'player_data' not in session:
        return redirect(url_for('index'))
    
    player = session['player_data']
    
    return render_template('job.html', player=player, jobs=game_logic.get_jobs())

@app.route('/apply_job', methods=['POST'])
def apply_job():
    """직업 선택"""
    if 'player_data' not in session:
        return redirect(url_for('index'))
    
    player = session['player_data']
    job_name = request.form.get('job')
    
    # 직업 정보 가져오기
    jobs = game_logic.get_jobs()
    selected_job = None
    for job in jobs:
        if job['이름'] == job_name:
            selected_job = job
            break
    
    if selected_job:
        player['직장'] = job_name
        player['직장정보'] = selected_job
        flash(f'{job_name} 직업을 선택했습니다!', 'success')
        game_logic.save_game(player)
        session['player_data'] = player
        game_logic.record_event(f'{job_name} 직업 시작')
    else:
        flash('직업을 찾을 수 없습니다.', 'error')
    
    return redirect(url_for('dashboard'))

@app.route('/shop')
def shop():
    """상점"""
    if 'player_data' not in session:
        return redirect(url_for('index'))
    
    player = session['player_data']
    shop_items = game_logic.get_shop_items()
    return render_template('shop.html', player=player, shop_items=shop_items)

@app.route('/inventory')
def inventory():
    """인벤토리"""
    if 'player_data' not in session:
        return redirect(url_for('index'))
    
    player = session['player_data']
    return render_template('inventory.html', player=player)

@app.route('/real_estate')
def real_estate():
    """부동산"""
    if 'player_data' not in session:
        return redirect(url_for('index'))
    
    player = session['player_data']
    properties = game_logic.get_real_estate()
    
    return render_template('real_estate.html', player=player, properties=properties)

@app.route('/work', methods=['POST'])
def work():
    """일하기"""
    if 'player_data' not in session:
        return redirect(url_for('index'))
    
    player = session['player_data']
    result = game_logic.work(player)
    
    session['player_data'] = player
    game_logic.save_game(player)
    
    flash(result['message'], result['type'])
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
    
    flash(result['message'], 'success')
    return redirect(url_for('dashboard'))

@app.route('/allocate_stats', methods=['POST'])
def allocate_stats():
    """스탯 분배"""
    if 'player_data' not in session:
        return redirect(url_for('index'))
    
    player = session['player_data']
    stat_type = request.form.get('stat_type')
    points = int(request.form.get('points', 0))
    
    result = game_logic.allocate_stats(player, stat_type, points)
    
    session['player_data'] = player
    game_logic.save_game(player)
    
    flash(result['message'], 'success')
    return redirect(url_for('dashboard'))

@app.route('/buy_item', methods=['POST'])
def buy_item():
    """아이템 구매"""
    if 'player_data' not in session:
        return redirect(url_for('index'))
    
    player = session['player_data']
    item_name = request.form.get('item_name')
    
    result = game_logic.buy_item(player, item_name)
    
    session['player_data'] = player
    game_logic.save_game(player)
    
    flash(result['message'], 'success' if result['success'] else 'error')
    return redirect(url_for('shop'))

@app.route('/buy_property', methods=['POST'])
def buy_property():
    """부동산 구매"""
    if 'player_data' not in session:
        return redirect(url_for('index'))
    
    player = session['player_data']
    property_name = request.form.get('property_name')
    
    result = game_logic.buy_property(player, property_name)
    
    session['player_data'] = player
    game_logic.save_game(player)
    
    flash(result['message'], 'success' if result['success'] else 'error')
    
    if result['success']:
        game_logic.record_event(f'{property_name} 구매')
    
    return redirect(url_for('real_estate'))

@app.route('/achievements')
def achievements():
    """성취 페이지"""
    if 'player_data' not in session:
        return redirect(url_for('index'))
    
    player = session['player_data']
    
    # 플레이어의 성취 조건들 가져오기
    achieved_conditions = game_logic.get_player_achievements(player)
    all_achievements = game_logic.get_all_achievements()
    
    # 성취를 난이도별로 분류
    achievements_by_difficulty = {}
    for achievement in all_achievements:
        difficulty = achievement['난이도']
        is_achieved = achievement['조건'] in achieved_conditions
        
        if difficulty not in achievements_by_difficulty:
            achievements_by_difficulty[difficulty] = {'achieved': [], 'not_achieved': []}
        
        if is_achieved:
            achievements_by_difficulty[difficulty]['achieved'].append(achievement)
        else:
            achievements_by_difficulty[difficulty]['not_achieved'].append(achievement)
    
    # 성취 포인트 계산
    achievement_points = game_logic.get_achievement_points(player)
    
    return render_template('achievements.html',
                         player=player,
                         achievements_by_difficulty=achievements_by_difficulty,
                         achievement_points=achievement_points,
                         total_achievements=len(all_achievements),
                         achieved_count=len(achieved_conditions))

@app.route('/dungeons')
def dungeons():
    """던전 목록"""
    if 'player_data' not in session:
        return redirect(url_for('index'))
    
    player = session['player_data']
    dungeons = game_logic.get_dungeons()
    
    return render_template('dungeons.html', player=player, dungeons=dungeons)

@app.route('/dungeon_preview/<dungeon_id>')
def dungeon_preview(dungeon_id):
    """던전 미리보기"""
    if 'player_data' not in session:
        return redirect(url_for('index'))
    
    player = session['player_data']
    dungeon = game_logic.get_dungeon_by_id(dungeon_id)
    
    if not dungeon:
        flash('던전을 찾을 수 없습니다.', 'error')
        return redirect(url_for('dungeons'))
    
    return render_template('dungeon_preview.html', player=player, dungeon=dungeon)

@app.route('/start_dungeon/<dungeon_id>', methods=['POST'])
def start_dungeon(dungeon_id):
    """던전 시작"""
    if 'player_data' not in session:
        return redirect(url_for('index'))
    
    player = session['player_data']
    
    # 던전 정보 가져오기
    dungeon = game_logic.get_dungeon_by_id(dungeon_id)
    if not dungeon:
        flash('던전을 찾을 수 없습니다.', 'error')
        return redirect(url_for('dungeons'))
    
    # 입장료 확인
    if player['돈'] < dungeon['입장료']:
        flash('입장료가 부족합니다.', 'error')
        return redirect(url_for('dungeons'))
    
    # 입장료 차감
    player['돈'] -= dungeon['입장료']
    
    # 던전 초기화
    dungeon_run = game_logic.initialize_dungeon_run(player, dungeon)
    
    session['player_data'] = player
    session['dungeon_run'] = dungeon_run
    session.modified = True
    game_logic.save_game(player)
    
    flash(f'{dungeon["이름"]} 던전에 진입했습니다!', 'success')
    return redirect(url_for('dungeon_run'))

@app.route('/dungeon_run')
def dungeon_run():
    """던전 진행"""
    if 'player_data' not in session or 'dungeon_run' not in session:
        return redirect(url_for('dungeons'))
    
    player = session['player_data']
    dungeon_run = session['dungeon_run']
    
    return render_template('dungeon_run.html', player=player, dungeon_run=dungeon_run)

@app.route('/dungeon/answer', methods=['POST'])
def dungeon_answer():
    """던전 문제 답변"""
    if 'player_data' not in session or 'dungeon_run' not in session:
        return redirect(url_for('dungeons'))
    
    player = session['player_data']
    dungeon_run = session['dungeon_run']
    
    answer = request.form.get('answer', '').strip()
    question_type = request.form.get('question_type')
    correct_answer = request.form.get('correct_answer')
    
    # 정답 확인
    answer_lower = answer.lower()
    correct_lower = correct_answer.lower()
    is_correct = answer_lower == correct_lower
    
    result_msg = ""
    
    if is_correct:
        result_msg = "정답입니다! 몬스터에게 피해를 입혔습니다!"
        
        # 플레이어 공격 - 몬스터 진행도 증가
        dungeon_run['monster_progress'] += 1
        
        # 경험치 획득
        exp_gained = 10 + dungeon_run['cleared_words'] * 2
        player['경험치'] += exp_gained
        result_msg += f" (경험치 +{exp_gained})"
        
        # 레벨업 확인
        while player['경험치'] >= player['경험치최대']:
            player['경험치'] -= player['경험치최대']
            player['레벨'] += 1
            player['경험치최대'] = int(player['경험치최대'] * 1.1)
            player['스탯포인트'] += 5
            result_msg += f" | 레벨업! (Lv.{player['레벨']})"
        
        # 몬스터 처치 확인
        if dungeon_run['monster_progress'] >= dungeon_run['monster_hp']:
            result_msg += f" | 몬스터를 처치했습니다!"
            
            # 몬스터 정보 추가
            rarity = game_logic.get_monster_rarity()
            monster_data = game_logic.get_random_monster(rarity)
            
            is_new_monster = game_logic.update_compendium(player, dungeon_run)
            if is_new_monster:
                result_msg += f" {rarity} 몬스터를 처치하고 새로운 몬스터를 도감에 추가했습니다!"
            else:
                result_msg += f" {rarity} 몬스터를 처치하고 도감에 등록했습니다!"
        else:
            result_msg += f" ({dungeon_run['monster_progress']}/{dungeon_run['monster_hp']})"
        
        # 처치한 단어 수 및 인덱스 증가
        dungeon_run['cleared_words'] += 1
        dungeon_run['current_word_index'] += 1
        
        # 다음 몬스터 생성
        dungeon = game_logic.get_dungeon_by_id(dungeon_run['dungeon_id'])
        next_result = game_logic.next_monster(dungeon_run, dungeon)
        
        if not next_result['success']:
            # 던전 클리어
            flash('던전을 클리어했습니다!', 'success')
            session.pop('dungeon_run', None)
            session['player_data'] = player
            session.modified = True
            game_logic.save_game(player)
            return redirect(url_for('dungeons'))
    else:
        # 플레이어 피격 - 체력 감소
        damage = 2
        player['체력'] -= damage
        result_msg = f"틀렸습니다! 몬스터에게 {damage} 피해를 입었습니다. (체력 -{damage})"
        result_msg += f" (정답: {correct_answer})"
        
        # 게임 오버 확인
        if player['체력'] <= 0:
            flash('게임 오버! 던전에서 탈출했습니다.', 'danger')
            session.pop('dungeon_run', None)
            session['player_data'] = player
            session.modified = True
            game_logic.save_game(player)
            return redirect(url_for('dungeons'))
    
    # 상태 업데이트
    session['player_data'] = player
    session['dungeon_run'] = dungeon_run
    session.modified = True
    game_logic.save_game(player)
    
    flash(result_msg, 'success' if is_correct else 'warning')
    return redirect(url_for('dungeon_run'))

@app.route('/dungeon/use_item', methods=['POST'])
def use_dungeon_item():
    """던전에서 아이템 사용"""
    if 'player_data' not in session or 'dungeon_run' not in session:
        return redirect(url_for('dungeons'))
    
    player = session['player_data']
    dungeon_run = session['dungeon_run']
    
    item_name = request.form.get('item_name')
    result = game_logic.use_dungeon_item(player, item_name, dungeon_run)
    
    session['player_data'] = player
    session['dungeon_run'] = dungeon_run
    session.modified = True
    game_logic.save_game(player)
    
    flash(result['message'], 'success' if result['success'] else 'error')
    
    return redirect(url_for('dungeon_run'))

@app.route('/dungeon/use_hint', methods=['POST'])
def use_hint():
    """던전에서 힌트 사용"""
    if 'player_data' not in session or 'dungeon_run' not in session:
        return redirect(url_for('dungeons'))
    
    player = session['player_data']
    dungeon_run = session['dungeon_run']
    
    # 던전 버프 딕셔너리 초기화 (없는 경우)
    if '던전_버프' not in player:
        player['던전_버프'] = {}
    
    # 힌트 사용 가능 횟수 확인
    hint_count = player['던전_버프'].get('힌트 사용', 0)
    
    if hint_count <= 0:
        flash('사용할 수 있는 힌트가 없습니다.', 'error')
        return redirect(url_for('dungeon_run'))
    
    # 힌트 사용 횟수 차감
    player['던전_버프']['힌트 사용'] -= 1
    
    # 현재 문제 옵션에서 정답을 제외한 옵션들 선택
    current_options = dungeon_run.get('options', [])
    correct_answer = dungeon_run.get('correct_answer', '')
    
    if not current_options or not correct_answer:
        flash('현재 문제 정보를 찾을 수 없습니다.', 'error')
        return redirect(url_for('dungeon_run'))
    
    # 정답의 인덱스 찾기
    correct_answer_index = -1
    for i, opt in enumerate(current_options):
        if opt == correct_answer:
            correct_answer_index = i
            break
    
    if correct_answer_index == -1:
        flash('정답을 찾을 수 없습니다.', 'error')
        return redirect(url_for('dungeon_run'))
    
    # 정답을 제외한 옵션들 중에서 하나를 제거
    wrong_options = [opt for i, opt in enumerate(current_options) if i != correct_answer_index]
    selected_wrong = random.choice(wrong_options)
    
    # 2지선다 생성
    hint_options = [correct_answer, selected_wrong]
    random.shuffle(hint_options)
    
    # 힌트 사용 표시
    dungeon_run['hint_used'] = True
    dungeon_run['hint_options'] = hint_options
    dungeon_run['hint_correct_index'] = hint_options.index(correct_answer)
    
    flash('힌트를 사용했습니다! 선택지가 2개로 줄어들었습니다.', 'info')
    
    # 상태 업데이트
    session['player_data'] = player
    session['dungeon_run'] = dungeon_run
    session.modified = True
    game_logic.save_game(player)
    
    return redirect(url_for('dungeon_run'))

@app.route('/dungeon/skip_question', methods=['POST'])
def skip_question():
    """던전에서 문제 스킵"""
    if 'player_data' not in session or 'dungeon_run' not in session:
        return redirect(url_for('dungeons'))
    
    player = session['player_data']
    dungeon_run = session['dungeon_run']
    
    # 던전 버프 딕셔너리 초기화 (없는 경우)
    if '던전_버프' not in player:
        player['던전_버프'] = {}
    
    # 스킵 사용 가능 횟수 확인
    skip_count = player['던전_버프'].get('문제 스킵', 0)
    
    if skip_count <= 0:
        flash('사용할 수 있는 스킵이 없습니다.', 'error')
        return redirect(url_for('dungeon_run'))
    
    # 스킵 사용 횟수 차감
    player['던전_버프']['문제 스킵'] -= 1
    
    # 문제를 정답으로 처리 (스킵이므로 몬스터 진행도 증가)
    dungeon_run['monster_progress'] += 1
    
    result_msg = "문제를 스킵했습니다! 몬스터에게 피해를 입혔습니다."
    
    # 몬스터 처치 확인
    if dungeon_run['monster_progress'] >= dungeon_run['monster_hp']:
        result_msg += " 몬스터를 처치했습니다!"
        
        # 경험치 획득
        exp_gained = 10 + dungeon_run['cleared_words'] * 2
        player['경험치'] += exp_gained
        result_msg += f" (경험치 +{exp_gained})"
        
        # 처치한 단어 수 및 인덱스 증가
        dungeon_run['cleared_words'] += 1
        dungeon_run['current_word_index'] += 1
        
        # 다음 몬스터 생성
        dungeon = game_logic.get_dungeon_by_id(dungeon_run['dungeon_id'])
        next_result = game_logic.next_monster(dungeon_run, dungeon)
        
        if not next_result['success']:
            # 던전 클리어
            flash('던전을 클리어했습니다!', 'success')
            session.pop('dungeon_run', None)
            session['player_data'] = player
            session.modified = True
            game_logic.save_game(player)
            return redirect(url_for('dungeons'))
    else:
        # 몬스터가 살아있으면 새로운 문제 생성
        progress = dungeon_run['monster_progress']
        max_hp = dungeon_run['monster_hp']
        result_msg += f" ({progress}/{max_hp})"
        
        # 다음 문제 준비 - 다른 단어로 새로운 문제 생성
        game_logic.build_next_question(dungeon_run)
    
    flash(result_msg, 'success')
    
    # 상태 업데이트
    session['player_data'] = player
    session['dungeon_run'] = dungeon_run
    session.modified = True
    game_logic.save_game(player)
    
    return redirect(url_for('dungeon_run'))

@app.route('/compendium')
def compendium():
    """몬스터 도감"""
    if 'player_data' not in session:
        return redirect(url_for('index'))
    
    player = session['player_data']
    compendium_data = game_logic.get_compendium_data(player)
    
    return render_template('compendium.html', player=player, compendium=compendium_data)

@app.route('/api/player_stats')
def api_player_stats():
    """플레이어 통계 API"""
    if 'player_data' not in session:
        return jsonify({'error': 'No player data'}), 400
    
    player = session['player_data']
    stats = game_logic.get_player_stats(player)
    
    return jsonify({
        'labels': ['힘', '지능', '외모', '체력', '운'],
        'stats': [
            player['힘'],
            player['지능'],
            player['외모'],
            player['체력스탯'],
            player['운']
        ]
    })
