from flask import render_template, request, redirect, url_for, flash, session, jsonify, make_response
from app import app
import game_logic
import json
import os
import random
from datetime import datetime

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
    """일일 표현 페이지 - 표현 목록"""
    if 'player_data' not in session:
        return redirect(url_for('index'))
    
    player = session['player_data']
    expressions = game_logic.get_daily_expressions()
    selected_index = request.args.get('index', None, type=int)
    progress = player.get('일일표현_진도', 0)
    
    return render_template('daily_expressions.html',
                         expressions=expressions,
                         progress=progress,
                         selected_index=selected_index,
                         expression_count=len(expressions))

@app.route('/conversation_practice')
def conversation_practice():
    """대화형 표현 연습"""
    if 'player_data' not in session:
        return redirect(url_for('index'))
    
    player = session['player_data']
    expressions = game_logic.get_daily_expressions()
    speakers = game_logic.get_foreign_speakers()
    
    # 랜덤 표현과 외국인 선택
    random_expr = random.choice(expressions)
    random_speaker = random.choice(speakers)
    alien_sentence = game_logic.get_conversation_prompt(random_expr)
    alien_translation = game_logic.get_conversation_translation(random_expr['expression'])
    
    return render_template('conversation_practice.html',
                         expression=random_expr,
                         alien_sentence=alien_sentence,
                         alien_translation=alien_translation,
                         speaker=random_speaker,
                         player=player)

@app.route('/submit_conversation', methods=['POST'])
def submit_conversation():
    """대화 응답 제출 - AI 평가"""
    if 'player_data' not in session:
        return redirect(url_for('index'))
    
    player = session['player_data']
    user_response = request.form.get('user_response', '').strip()
    expr_name = request.form.get('expression', '').strip()
    context_sentence = request.form.get('context_sentence', '').strip()
    
    expressions = game_logic.get_daily_expressions()
    target_expr = next((e for e in expressions if e['expression'] == expr_name), None)
    
    if target_expr and user_response:
        # AI를 사용하여 코칭 피드백 제공
        coaching = game_logic.evaluate_conversation_response(user_response, expr_name, context_sentence)
        
        if coaching.get('success'):
            grammar = coaching.get('grammar', '')
            tip = coaching.get('tip', '')
            better = coaching.get('better', '')
            
            coaching_message = f"📝 {grammar}\n💡 {tip}\n💬 {better}"
            flash(coaching_message, 'info')
        else:
            flash(f'코칭 중 오류가 발생했습니다. 다시 시도해주세요.', 'error')
    
    session['player_data'] = player
    session.modified = True
    game_logic.save_game(player)
    
    return redirect(url_for('conversation_practice'))

@app.route('/check_daily_expression', methods=['POST'])
def check_daily_expression():
    """일일 표현 확인 - 무한 학습"""
    if 'player_data' not in session:
        return redirect(url_for('index'))
    
    player = session['player_data']
    user_input = request.form.get('user_input', '').strip().lower()
    try:
        index = int(request.form.get('index', 0))
    except (ValueError, TypeError):
        flash('잘못된 인덱스입니다.', 'error')
        return redirect(url_for('daily_expressions'))
    
    expressions = game_logic.get_daily_expressions()
    correct_expression = expressions[index]['expression'].lower()
    
    # 부분 일치 확인 (사용자 입력이 정답을 포함하면 정답)
    if correct_expression in user_input or user_input in correct_expression:
        player['일일표현_진도'] = player.get('일일표현_진도', 0) + 1
        flash(f'정답입니다! ✓ (총 {player["일일표현_진도"]}개 완료)', 'success')
        
        # 매번 경험치 +10 보상
        exp_gained = 10
        player['경험치'] += exp_gained
        
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
    
    return redirect(url_for('daily_expressions', index=index))

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
        
        wrong_question = {
            'word': quiz_word,
            'meaning': full_word_info['뜻'] if full_word_info else '알 수 없음',
            'question_type': question_type,
            'correct_answer': correct_answer,
            'player_answer': answer,
            'category': selected_category
        }
        
        # 중복 방지: 같은 단어의 틀린 문제가 이미 있으면 덮어쓰기
        session[wrong_session_key] = [q for q in session[wrong_session_key] if q['word'] != quiz_word]
        session[wrong_session_key].append(wrong_question)
        session.modified = True
        
        message = f'틀렸습니다. 정답은 "{result["correct_answer"]}"입니다.'
        message_type = 'error'
    
    # AJAX 요청인지 확인
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # 다음 단어 가져오기
        word_bank = game_logic.get_word_by_category(selected_category)
        session_key = f'quiz_session_correct_{selected_category}'
        correct_words = session.get(session_key, [])
        available_words = [word for word in word_bank if word['단어'] not in correct_words]
        
        total_words = len(word_bank)
        completed_words = len(correct_words)
        
        if len(available_words) > 0:
            import random
            next_quiz_word = random.choice(available_words)
            
            # 다음 문제의 유형 결정
            if selected_language == 'english':
                next_question_type = '단어맞히기'
            elif selected_language == 'korean':
                next_question_type = '뜻맞히기'
            else:
                next_question_type = random.choice(['뜻맞히기', '단어맞히기'])
            
            wrong_session_key = f'quiz_session_wrong_{selected_category}'
            wrong_questions = session.get(wrong_session_key, [])
            
            return jsonify({
                'success': True,
                'correct': result['correct'],
                'message': message,
                'message_type': message_type,
                'next_word': next_quiz_word,
                'next_question_type': next_question_type,
                'completed_words': completed_words,
                'total_words': total_words,
                'all_completed': False,
                'wrong_questions_count': len(wrong_questions),
                'has_wrong_questions': len(wrong_questions) > 0
            })
        else:
            # 모든 단어를 맞혔을 때
            return jsonify({
                'success': True,
                'correct': result['correct'],
                'message': message,
                'message_type': message_type,
                'completed_words': completed_words,
                'total_words': total_words,
                'all_completed': True
            })
    
    # 기존 방식 (form submit)
    flash(message, message_type)
    return redirect(url_for('quiz', category=selected_category, language=selected_language))

@app.route('/reset_quiz_session', methods=['POST'])
def reset_quiz_session():
    """퀴즈 세션 초기화"""
    selected_category = request.form.get('selected_category', 'all')
    selected_language = request.form.get('selected_language', request.args.get('language', 'random'))
    session_key = f'quiz_session_correct_{selected_category}'
    wrong_session_key = f'quiz_session_wrong_{selected_category}'
    if session_key in session:
        del session[session_key]
    if wrong_session_key in session:
        del session[wrong_session_key]
    flash('새로운 퀴즈 세션을 시작합니다!', 'info')
    return redirect(url_for('quiz', category=selected_category, language=selected_language))

@app.route('/quiz/retry_wrong')
def retry_wrong_quiz():
    """틀린 문제 재도전"""
    if 'player_data' not in session:
        return redirect(url_for('index'))
    
    category = request.args.get('category', 'all')
    selected_language = request.args.get('language', 'random')
    wrong_session_key = f'quiz_session_wrong_{category}'
    wrong_questions = session.get(wrong_session_key, [])
    
    if not wrong_questions:
        flash('틀린 문제가 없습니다.', 'info')
        return redirect(url_for('quiz', category=category, language=selected_language))
    
    # 틀린 문제들을 재도전 모드로 초기화
    session['wrong_questions_retry_mode'] = True
    session['wrong_questions_retry_category'] = category
    session['wrong_questions_retry_index'] = 0
    session['wrong_questions_retry_correct'] = []
    
    return render_template('quiz_wrong_retry.html',
                         player=session['player_data'],
                         wrong_questions=wrong_questions,
                         category=category,
                         current_index=0)

@app.route('/quiz/retry_wrong/answer', methods=['POST'])
def answer_wrong_quiz():
    """틀린 문제 재도전 답안 처리"""
    if 'player_data' not in session or not session.get('wrong_questions_retry_mode'):
        return redirect(url_for('quiz'))
    
    player = session['player_data']
    category = session.get('wrong_questions_retry_category', 'all')
    wrong_session_key = f'quiz_session_wrong_{category}'
    wrong_questions = session.get(wrong_session_key, [])
    current_index = session.get('wrong_questions_retry_index', 0)
    
    if current_index >= len(wrong_questions):
        flash('모든 틀린 문제를 완료했습니다!', 'success')
        session.pop('wrong_questions_retry_mode', None)
        return redirect(url_for('quiz', category=category))
    
    current_question = wrong_questions[current_index]
    answer = request.form.get('answer', '').strip()
    correct_answer = current_question['correct_answer']
    
    result = game_logic.process_quiz_answer(player, answer, correct_answer, current_question['question_type'])
    session['player_data'] = player
    game_logic.save_game(player)
    
    if result['correct']:
        # 맞춘 문제를 기록
        if 'wrong_questions_retry_correct' not in session:
            session['wrong_questions_retry_correct'] = []
        session['wrong_questions_retry_correct'].append(current_index)
        
        # 틀린 문제 목록에서 제거
        wrong_questions.pop(current_index)
        session[wrong_session_key] = wrong_questions
        
        flash(f'정답! 경험치 +{result["exp_gained"]}', 'success')
        
        # 다음 문제로 이동하지만 인덱스는 증가하지 않음 (문제가 제거되었으므로)
        if current_index >= len(wrong_questions):
            # 모든 문제 완료
            flash('모든 틀린 문제를 완료했습니다!', 'success')
            session.pop('wrong_questions_retry_mode', None)
            return redirect(url_for('quiz', category=category))
    else:
        # 틀렸으면 다음 문제로 이동
        session['wrong_questions_retry_index'] = current_index + 1
        flash(f'틀렸습니다. 정답은 "{correct_answer}"입니다.', 'error')
        
        if session['wrong_questions_retry_index'] >= len(wrong_questions):
            flash('틀린 문제 재도전을 완료했습니다.', 'info')
            session.pop('wrong_questions_retry_mode', None)
            return redirect(url_for('quiz', category=category))
    
    return redirect(url_for('retry_wrong_quiz', category=category))

@app.route('/add_word', methods=['POST'])
def add_word():
    """단어 추가"""
    if 'player_data' not in session:
        return redirect(url_for('index'))
    
    player = session['player_data']
    words_text = request.form.get('words', '').strip()
    meanings_text = request.form.get('meanings', '').strip()
    
    # 카테고리 처리: 새 카테고리가 선택되면 사용자 입력값 사용
    category = request.form.get('category', '기본')
    if category == 'custom':
        custom_category = request.form.get('custom_category', '').strip()
        if custom_category:
            category = custom_category
        else:
            flash('새 카테고리 이름을 입력해주세요.', 'error')
            return redirect(url_for('quiz'))
    
    if words_text and meanings_text:
        words = [w.strip() for w in words_text.split('\n') if w.strip()]
        meanings = [m.strip() for m in meanings_text.split('\n') if m.strip()]
        
        if len(words) != len(meanings):
            flash('단어와 뜻의 개수가 다릅니다. 같은 순서로 입력해주세요.', 'error')
        else:
            added_count = game_logic.add_words_to_bank(words, meanings, category, player)
            
            if added_count > 0:
                session['player_data'] = player
                game_logic.save_game(player)
                flash(f'{added_count}개의 단어가 "{category}" 카테고리에 추가되었습니다!', 'success')
            else:
                flash('추가할 수 있는 단어가 없습니다.', 'info')
    else:
        flash('단어와 뜻을 모두 입력해주세요.', 'error')
    
    return redirect(url_for('quiz'))

@app.route('/save_word_from_quiz', methods=['POST'])
def save_word_from_quiz():
    """퀴즈에서 단어 저장 (AJAX)"""
    if 'player_data' not in session:
        return jsonify({'success': False, 'message': '로그인이 필요합니다.'})
    
    try:
        data = request.get_json()
        word = data.get('word', '').strip()
        meaning = data.get('meaning', '').strip()
        category = data.get('category', '기본').strip()
        
        if not word or not meaning:
            return jsonify({'success': False, 'message': '단어와 뜻을 모두 입력해주세요.'})
        
        if not category:
            return jsonify({'success': False, 'message': '카테고리를 선택해주세요.'})
        
        player = session['player_data']
        
        # 단어 추가
        success = game_logic.add_word_to_bank(word, meaning, category)
        
        if success:
            session['player_data'] = player
            game_logic.save_game(player)
            
            return jsonify({
                'success': True, 
                'message': f'"{word}" 단어가 "{category}" 카테고리에 저장되었습니다!'
            })
        else:
            return jsonify({'success': False, 'message': '단어 저장 중 오류가 발생했습니다.'})
            
    except Exception as e:
        print(f"Error saving word from quiz: {e}")
        return jsonify({'success': False, 'message': '단어 저장 중 오류가 발생했습니다.'})

@app.route('/save_category_words', methods=['POST'])
def save_category_words():
    """던전 카테고리의 모든 단어를 사용자 단어장에 저장"""
    if 'player_data' not in session:
        return jsonify({'success': False, 'message': '로그인이 필요합니다.'})
    
    try:
        data = request.get_json()
        dungeon_id = data.get('dungeon_id', '').strip()
        category_name = data.get('category_name', '').strip()
        
        if not dungeon_id or not category_name:
            return jsonify({'success': False, 'message': '던전 ID와 카테고리 이름이 필요합니다.'})
        
        result = game_logic.save_category_words_to_bank(dungeon_id, category_name)
        
        if result['success']:
            return jsonify({
                'success': True,
                'message': result['message'],
                'added_count': result['added_count'],
                'total_words': result['total_words']
            })
        else:
            return jsonify(result)
            
    except Exception as e:
        print(f"Error saving category words: {e}")
        return jsonify({'success': False, 'message': '카테고리 단어 저장 중 오류가 발생했습니다.'})

@app.route('/delete_word', methods=['POST'])
def delete_word():
    """단어 삭제"""
    try:
        word_index_str = request.form.get('word_index', '0')
        if not word_index_str or word_index_str == '':
            flash('잘못된 단어 인덱스입니다.', 'error')
            return redirect(url_for('word_management'))
        word_index = int(word_index_str)
    except (ValueError, TypeError):
        flash('잘못된 단어 인덱스입니다.', 'error')
        return redirect(url_for('word_management'))
    
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

@app.route('/change_multiple_categories', methods=['POST'])
def change_multiple_categories():
    """여러 단어의 카테고리 일괄 변경"""
    word_indices_str = request.form.get('word_indices', '')
    new_category = request.form.get('new_category', '').strip()
    custom_category = request.form.get('custom_category', '').strip()
    
    if not word_indices_str:
        flash('카테고리를 변경할 단어를 선택해주세요.', 'error')
        return redirect(url_for('word_management'))
    
    # 새 카테고리가 custom이면 사용자 입력값 사용
    if new_category == 'custom':
        if custom_category:
            new_category = custom_category
        else:
            flash('새 카테고리 이름을 입력해주세요.', 'error')
            return redirect(url_for('word_management'))
    
    if not new_category:
        flash('변경할 카테고리를 선택해주세요.', 'error')
        return redirect(url_for('word_management'))
    
    word_indices = word_indices_str.split(',')
    result = game_logic.change_multiple_categories(word_indices, new_category)
    
    if result['success']:
        flash(result['message'], 'success')
    else:
        flash(result['message'], 'error')
    
    return redirect(url_for('word_management'))

@app.route('/edit_word', methods=['POST'])
def edit_word():
    """단어 수정"""
    try:
        word_index_str = request.form.get('word_index', '0')
        if not word_index_str or word_index_str == '':
            flash('잘못된 단어 인덱스입니다.', 'error')
            return redirect(url_for('word_management'))
        word_index = int(word_index_str)
    except (ValueError, TypeError):
        flash('잘못된 단어 인덱스입니다.', 'error')
        return redirect(url_for('word_management'))
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
    word_bank = game_logic.get_user_words()
    # 사용자 단어에서만 카테고리 추출
    categories = list(set([word.get('카테고리', '기본') for word in word_bank]))
    
    # 검색 기능
    search_term = request.args.get('search', '').strip()
    if search_term:
        # 사용자 단어에서만 검색
        all_user_words = game_logic.get_user_words()
        word_bank = [word for word in all_user_words if 
                    search_term.lower() in word.get('단어', '').lower() or 
                    search_term.lower() in word.get('뜻', '').lower()]
    
    # 카테고리 필터
    category_filter = request.args.get('category', 'all')
    if category_filter != 'all':
        word_bank = [word for word in word_bank if word.get('카테고리', '기본') == category_filter]
    
    # 모든 경우에 인덱스 추가 (원본 단어장에서의 실제 인덱스)
    all_user_words = game_logic.get_user_words()
    for word in word_bank:
        # 원본 단어장에서의 실제 인덱스 찾기
        for original_idx, original_word in enumerate(all_user_words):
            if (word.get('단어') == original_word.get('단어') and 
                word.get('뜻') == original_word.get('뜻') and 
                word.get('카테고리') == original_word.get('카테고리')):
                word['인덱스'] = str(original_idx)
                break
    
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
    try:
        job_id = int(request.form.get('job_id', 0))
    except (ValueError, TypeError):
        flash('잘못된 직업 ID입니다.', 'error')
        return redirect(url_for('job'))
    
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
    try:
        property_id = int(request.form.get('property_id', 0))
    except (ValueError, TypeError):
        flash('잘못된 부동산 ID입니다.', 'error')
        return redirect(url_for('real_estate'))
    
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
    try:
        item_id = int(request.form.get('item_id', 0))
    except (ValueError, TypeError):
        flash('잘못된 아이템 ID입니다.', 'error')
        return redirect(url_for('shop'))
    
    result = game_logic.buy_item(player, item_id)
    session['player_data'] = player
    game_logic.save_game(player)
    
    if result['success']:
        flash(result['message'], 'success')
    else:
        flash(result['message'], 'error')
    
    return redirect(url_for('shop'))

@app.route('/equip_weapon', methods=['POST'])
def equip_weapon():
    """무기 장착"""
    if 'player_data' not in session:
        return redirect(url_for('index'))
    
    player = session['player_data']
    weapon_name = request.form.get('weapon_name', '')
    
    result = game_logic.equip_weapon(player, weapon_name)
    session['player_data'] = player
    game_logic.save_game(player)
    
    if result['success']:
        flash(result['message'], 'success')
    else:
        flash(result['message'], 'error')
    
    return redirect(url_for('inventory'))

@app.route('/unequip_weapon', methods=['POST'])
def unequip_weapon():
    """무기 해제"""
    if 'player_data' not in session:
        return redirect(url_for('index'))
    
    player = session['player_data']
    
    result = game_logic.unequip_weapon(player)
    session['player_data'] = player
    game_logic.save_game(player)
    
    if result['success']:
        flash(result['message'], 'success')
    else:
        flash(result['message'], 'error')
    
    return redirect(url_for('inventory'))

@app.route('/inventory')
def inventory():
    """인벤토리 페이지"""
    if 'player_data' not in session:
        return redirect(url_for('index'))
    
    player = session['player_data']
    shop_items = game_logic.get_shop_items()
    
    # 빠른 접근을 위해 아이템 정보를 딕셔너리로 변환
    weapons_info = {}
    items_info = {}
    for item in shop_items:
        if item['타입'] == '무기':
            weapons_info[item['이름']] = item
        elif item.get('타입') == '던전':
            items_info[item['이름']] = item
    
    return render_template('inventory.html', player=player, weapons_info=weapons_info, items_info=items_info)

@app.route('/allocate_stats', methods=['POST'])
def allocate_stats():
    """스탯 분배"""
    if 'player_data' not in session:
        return redirect(url_for('index'))
    
    player = session['player_data']
    stat_type = request.form.get('stat_type')
    try:
        points = int(request.form.get('points', 0))
    except (ValueError, TypeError):
        flash('잘못된 포인트입니다.', 'error')
        return redirect(url_for('dashboard'))
    
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

# ============== 던전 시스템 라우트 ==============

@app.route('/dungeons')
def dungeons():
    """던전 목록 페이지"""
    if 'player_data' not in session:
        return redirect(url_for('index'))
    
    player = session['player_data']
    dungeons_list = game_logic.get_dungeons()
    
    # 커스텀 던전을 제일 위에 배치
    dungeons_list.sort(key=lambda d: d.get('난이도') != '커스텀')
    
    # 각 던전에 보상 정보 추가
    for dungeon in dungeons_list:
        if dungeon.get('난이도') == '커스텀':
            # 커스텀 던전은 이미 reward_money가 설정됨
            dungeon['reward_info'] = f"{dungeon.get('reward_money', 0):,}원"
        else:
            # 난이도별 보상 정보 추가
            reward_info = game_logic.get_dungeon_reward_info(dungeon.get('난이도', '보통'))
            dungeon['reward_info'] = f"{reward_info['min_money']:,}~{reward_info['max_money']:,}원 + 경험치 {reward_info['min_exp']}~{reward_info['max_exp']}"
    
    return render_template('dungeons.html', 
                         player=player, 
                         dungeons=dungeons_list)

@app.route('/dungeon/<dungeon_id>/preview')
def dungeon_preview(dungeon_id):
    """던전 미리보기 페이지"""
    if 'player_data' not in session:
        return redirect(url_for('index'))
    
    player = session['player_data']
    dungeon = game_logic.get_dungeon_by_id(dungeon_id)
    
    if not dungeon:
        flash('존재하지 않는 던전입니다.', 'error')
        return redirect(url_for('dungeons'))
    
    # 던전별 단어 로드 (모든 단어 표시)
    words = game_logic.load_words_by_source(dungeon.get('word_source', 'toeic'))
    
    return render_template('dungeon_preview.html', 
                         player=player, 
                         dungeon=dungeon,
                         all_words=words,
                         total_words=len(words))

@app.route('/dungeon/start', methods=['POST'])
def start_dungeon():
    """던전 시작"""
    if 'player_data' not in session:
        return redirect(url_for('index'))
    
    player = session['player_data']
    dungeon_id = request.form.get('dungeon_id')
    
    # 최소 체력 확인 (체력 = 기력)
    if player['기력'] < 1:
        flash('던전에 입장하려면 최소 기력 1이 필요합니다.', 'error')
        return redirect(url_for('dungeons'))
    
    # 던전 실행 초기화
    result = game_logic.init_dungeon_run(player, dungeon_id)
    
    if not result['success']:
        flash(result['message'], 'error')
        return redirect(url_for('dungeons'))
    
    # 입장료 차감이 반영되도록 먼저 게임 저장
    game_logic.save_game(player)
    
    # 세션에 던전 실행 상태 및 수정된 플레이어 데이터 저장
    session['dungeon_run'] = result['dungeon_run']
    session['player_data'] = player
    
    # 입장료가 있는 던전인 경우 안내
    dungeon = game_logic.get_dungeon_by_id(dungeon_id)
    if dungeon and dungeon.get('entry_fee', 0) > 0:
        flash(f'던전에 입장했습니다! (입장료 {dungeon["entry_fee"]:,}원 차감)', 'success')
    else:
        flash('던전에 입장했습니다!', 'success')
    
    return redirect(url_for('dungeon_run'))

@app.route('/dungeon/run')
def dungeon_run():
    """던전 실행 화면"""
    if 'player_data' not in session or 'dungeon_run' not in session:
        return redirect(url_for('dungeons'))
    
    player = session['player_data']
    dungeon_run = session['dungeon_run']
    
    # 던전런에서 플래시 메시지 확인 및 처리
    if 'flash_message' in dungeon_run:
        flash(dungeon_run['flash_message'], 'info')
        del dungeon_run['flash_message']  # 메시지 표시 후 삭제
        session['dungeon_run'] = dungeon_run  # 세션 업데이트
    
    dungeon = game_logic.get_dungeon_by_id(dungeon_run['dungeon_id'])
    
    # 던전 클리어 확인
    if game_logic.check_dungeon_clear(dungeon_run):
        flash('던전을 클리어했습니다! 축하합니다!', 'success')
        # 던전 실행 상태 삭제
        session.pop('dungeon_run', None)
        return redirect(url_for('dungeons'))
    
    return render_template('dungeon_run.html', 
                         player=player, 
                         dungeon=dungeon,
                         dungeon_run=dungeon_run)

@app.route('/dungeon/answer', methods=['POST'])
def answer_dungeon():
    """던전 답변 처리 (AJAX 지원)"""
    if 'player_data' not in session or 'dungeon_run' not in session:
        msg = '던전 정보가 없습니다.'
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': False, 'message': msg, 'game_over': True})
        flash(msg, 'error')
        return redirect(url_for('dungeons'))
    
    player = session['player_data']
    dungeon_run = session['dungeon_run']
    
    # 안전한 choice 값 처리
    try:
        choice = int(request.form.get('choice', -1))
    except (ValueError, TypeError):
        msg = '잘못된 선택입니다.'
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': False, 'message': msg})
        flash(msg, 'error')
        return redirect(url_for('dungeon_run'))
    
    # 선택지 유효성 검사
    if 'current_options' not in dungeon_run or not dungeon_run['current_options']:
        msg = '게임 오류가 발생했습니다.'
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            session.pop('dungeon_run', None)
            return jsonify({'success': False, 'message': msg, 'game_over': True})
        session.pop('dungeon_run', None)
        flash(msg, 'error')
        return redirect(url_for('dungeons'))
    
    if choice < 0 or choice >= len(dungeon_run['current_options']):
        msg = '잘못된 선택입니다.'
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': False, 'message': msg})
        flash(msg, 'error')
        return redirect(url_for('dungeon_run'))
    
    # 답변 처리
    result = game_logic.answer_dungeon(player, dungeon_run, choice)
    
    if result.get('game_over', False):
        session.pop('dungeon_run', None)
        session['player_data'] = player
        game_logic.save_game(player)
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': False, 'message': result['message'], 'game_over': True})
        flash(result['message'], 'error')
        return redirect(url_for('dungeons'))
    
    # 몬스터가 처치되었으면 다음 몬스터 생성
    if result.get('monster_defeated'):
        if dungeon_run.get('wrong_questions_mode'):
            if dungeon_run['current_wrong_index'] >= len(dungeon_run['wrong_questions_list']):
                next_result = {'success': False, 'message': '틀린 문제 복습을 완료했습니다!'}
            else:
                next_result = game_logic.next_wrong_question(dungeon_run)
        else:
            dungeon = game_logic.get_dungeon_by_id(dungeon_run['dungeon_id'])
            next_result = game_logic.next_monster(dungeon_run, dungeon)
        
        if not next_result['success']:
            wrong_questions = dungeon_run.get('wrong_questions', [])
            if not dungeon_run.get('wrong_questions_mode'):
                # 커스텀 던전이 아닐 때만 던전클리어횟수 증가
                dungeon = game_logic.get_dungeon_by_id(dungeon_run['dungeon_id'])
                if dungeon.get('난이도') != '커스텀':
                    player['던전클리어횟수'] = player.get('던전클리어횟수', 0) + 1
                
                # 던전 클리어 보상 적용
                reward_result = game_logic.apply_dungeon_clear_reward(player, dungeon)
                
                if reward_result['success']:
                    clear_message = f"던전을 클리어했습니다!\n{reward_result['message']}"
                else:
                    clear_message = "던전을 클리어했습니다!"
            else:
                clear_message = "던전을 클리어했습니다!"
            
            session.pop('dungeon_run', None)
            session['player_data'] = player
            game_logic.save_game(player)
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': False, 'message': clear_message, 'game_over': True, 'clear': True})
            flash(clear_message, 'success')
            return redirect(url_for('dungeons'))
    
    # 상태 업데이트
    session['dungeon_run'] = dungeon_run
    session['player_data'] = player
    game_logic.save_game(player)
    
    # AJAX 요청인 경우 JSON 반환 (flash 메시지 설정 X)
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # 포획 여부 감지
        is_captured = '도감에 등록했습니다' in result['message'] or '도감에 추가했습니다' in result['message']
        return jsonify({
            'success': result['correct'],
            'message': result['message'],
            'captured': is_captured
        })
    
    # Flash 메시지 설정 (AJAX가 아닐 때만)
    flash(result['message'], 'success' if result['correct'] else 'warning')
    return redirect(url_for('dungeon_run'))

@app.route('/dungeon/leave', methods=['POST'])
def leave_dungeon():
    """던전 나가기"""
    if 'dungeon_run' in session:
        session.pop('dungeon_run', None)
    
    flash('던전에서 나갔습니다. 진행 상황이 초기화됩니다.', 'info')
    return redirect(url_for('dungeons'))

@app.route('/dungeon/retry_wrong', methods=['POST'])
def retry_wrong_questions():
    """틀린 문제들로 재도전"""
    if 'player_data' not in session:
        return redirect(url_for('index'))
    
    player = session['player_data']
    
    # 세션에서 틀린 문제들 가져오기
    last_wrong = session.get('last_wrong_questions')
    if not last_wrong or not last_wrong.get('questions'):
        flash('재도전할 틀린 문제가 없습니다.', 'error')
        return redirect(url_for('dungeons'))
    
    # 최소 체력 확인 (체력 = 기력)
    if player['기력'] < 1:
        flash('던전에 입장하려면 최소 기력 1이 필요합니다.', 'error')
        return redirect(url_for('dungeons'))
    
    # 기력 소모
    player['기력'] -= 1
    
    # 틀린 문제들로 던전 초기화
    result = game_logic.init_wrong_questions_dungeon(
        player, 
        last_wrong['questions'], 
        last_wrong['original_dungeon_id']
    )
    
    if not result['success']:
        flash(result['message'], 'error')
        return redirect(url_for('dungeons'))
    
    # 세션에 던전 실행 상태 저장
    session['dungeon_run'] = result['dungeon_run']
    session['player_data'] = player
    session.modified = True
    
    # 데이터 저장 (일관성을 위해)
    game_logic.save_game(player)
    
    # 사용한 틀린 문제 정보 삭제
    session.pop('last_wrong_questions', None)
    
    flash('틀린 문제들로 재도전을 시작합니다!', 'success')
    return redirect(url_for('dungeon_run'))

@app.route('/compendium')
def compendium():
    """몬스터 도감 페이지"""
    if 'player_data' not in session:
        return redirect(url_for('index'))
    
    player = session['player_data']
    filter_rarity = request.args.get('rarity', 'all')
    
    # 도감 데이터 가져오기
    compendium = player.get('도감', {})
    
    # 필터링
    if filter_rarity != 'all':
        compendium = {k: v for k, v in compendium.items() if v.get('등급') == filter_rarity}
    
    rarities = ['레어', '에픽', '유니크', '레전드리']
    total_monsters = len(player.get('도감', {}))
    
    return render_template('compendium.html', 
                         player=player,
                         compendium=compendium,
                         filter_rarity=filter_rarity,
                         rarities=rarities,
                         total_monsters=total_monsters)

@app.route('/all_monsters')
def all_monsters():
    """게임에 존재하는 모든 몬스터 정보 페이지"""
    if 'player_data' not in session:
        return redirect(url_for('index'))
    
    player = session['player_data']
    filter_rarity = request.args.get('rarity', 'all')
    
    # 모든 몬스터 정보 가져오기
    all_monsters_data = game_logic.get_all_monster_images()
    
    # 필터링
    if filter_rarity != 'all':
        all_monsters_data = {k: v for k, v in all_monsters_data.items() if v.get('등급') == filter_rarity}
    
    rarities = ['레어', '에픽', '유니크', '레전드리']
    
    return render_template('all_monsters.html',
                         player=player,
                         all_monsters=all_monsters_data,
                         filter_rarity=filter_rarity,
                         rarities=rarities)

@app.route('/delete_monster/<monster_id>', methods=['POST'])
def delete_monster(monster_id):
    """몬스터 삭제"""
    if 'player_data' not in session:
        return redirect(url_for('index'))
    
    player = session['player_data']
    
    if '도감' in player and monster_id in player['도감']:
        monster_name = player['도감'][monster_id]['이름']
        del player['도감'][monster_id]
        session['player_data'] = player
        game_logic.save_game(player)
        flash(f'"{monster_name}"을(를) 도감에서 삭제했습니다.', 'success')
    else:
        flash('몬스터를 찾을 수 없습니다.', 'error')
    
    return redirect(url_for('compendium'))

@app.route('/fusion')
def fusion():
    """몬스터 합성 페이지"""
    if 'player_data' not in session:
        return redirect(url_for('index'))
    
    player = session['player_data']
    compendium = player.get('도감', {})
    
    # 등급별로 몬스터 분류
    monsters_by_rarity = {}
    for monster_id, monster in compendium.items():
        rarity = monster.get('등급', '레어')
        if rarity not in monsters_by_rarity:
            monsters_by_rarity[rarity] = []
        monsters_by_rarity[rarity].append({'id': monster_id, 'name': monster['이름']})
    
    return render_template('fusion.html', 
                         player=player,
                         compendium=compendium,
                         monsters_by_rarity=monsters_by_rarity)

@app.route('/perform_fusion', methods=['POST'])
def perform_fusion():
    """몬스터 합성 실행"""
    if 'player_data' not in session:
        return redirect(url_for('index'))
    
    player = session['player_data']
    monster_ids = request.form.getlist('selected_monsters')
    
    result = game_logic.merge_monsters(player, monster_ids)
    
    session['player_data'] = player
    game_logic.save_game(player)
    
    if result['success']:
        flash(result['message'], 'success')
    else:
        flash(result['message'], 'error')
    
    return redirect(url_for('fusion'))

@app.route('/dungeon/use_item', methods=['POST'])
def use_dungeon_item():
    """던전 아이템 사용"""
    if 'player_data' not in session or 'dungeon_run' not in session:
        return redirect(url_for('dungeons'))
    
    player = session['player_data']
    dungeon_run = session['dungeon_run']
    item_name = request.form.get('item_name')
    
    if not item_name:
        flash('아이템을 선택해주세요.', 'error')
        return redirect(url_for('dungeon_run'))
    
    # 아이템 사용
    result = game_logic.use_dungeon_item(player, item_name, dungeon_run)
    
    if result['success']:
        flash(result['message'], 'success')
    else:
        flash(result['message'], 'error')
    
    # 상태 업데이트
    session['player_data'] = player
    session['dungeon_run'] = dungeon_run
    game_logic.save_game(player)
    
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
    
    # 힌트 생성 (4지선다를 2지선다로 줄이기)
    current_options = dungeon_run['current_options']
    correct_answer_index = dungeon_run['correct_answer_index']
    
    # 정답과 오답 1개만 남기기 (랜덤하게 선택)
    correct_answer = current_options[correct_answer_index]
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
        # 몬스터 처치
        rarity = dungeon_run['current_rarity']
        capture_rate = game_logic.monster_rarities[rarity]['capture_rate']
        
        if random.random() < capture_rate:
            # 몬스터 포획 성공
            is_new_monster = game_logic.update_compendium(player, dungeon_run)
            if is_new_monster:
                result_msg += f" {rarity} 몬스터를 처치하고 새로운 몬스터를 도감에 추가했습니다!"
            else:
                result_msg += f" {rarity} 몬스터를 처치하고 도감에 등록했습니다!"
        else:
            result_msg += f" {rarity} 몬스터를 처치했지만 도감 등록에 실패했습니다."
        
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
