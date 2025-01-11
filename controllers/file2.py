from flask import render_template, request, redirect, url_for, flash, session, jsonify
from app import app, db
from models.models import User, Subject, Chapter, Quiz, Question, Score
from datetime import datetime
from functools import wraps

# Login decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Admin decorator
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        user = User.query.get(session['user_id'])
        if not user or not user.is_admin:
            flash('Admin access required')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Admin routes
@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    subjects = Subject.query.all()
    users = User.query.filter_by(is_admin=False).all()
    return render_template('file2.html', subjects=subjects, users=users)

@app.route('/admin/subject', methods=['POST'])
@admin_required
def add_subject():
    name = request.form.get('name')
    description = request.form.get('description')
    subject = Subject(name=name, description=description)
    db.session.add(subject)
    db.session.commit()
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/chapter/<int:subject_id>', methods=['POST'])
@admin_required
def add_chapter(subject_id):
    name = request.form.get('name')
    description = request.form.get('description')
    chapter = Chapter(name=name, description=description, subject_id=subject_id)
    db.session.add(chapter)
    db.session.commit()
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/quiz/<int:chapter_id>', methods=['POST'])
@admin_required
def add_quiz(chapter_id):
    date = datetime.strptime(request.form.get('date'), '%Y-%m-%d').date()
    duration = int(request.form.get('duration'))
    quiz = Quiz(chapter_id=chapter_id, date_of_quiz=date, time_duration=duration)
    db.session.add(quiz)
    db.session.commit()
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/question/<int:quiz_id>', methods=['POST'])
@admin_required
def add_question(quiz_id):
    question = Question(
        quiz_id=quiz_id,
        question_text=request.form.get('question'),
        option_1=request.form.get('option1'),
        option_2=request.form.get('option2'),
        option_3=request.form.get('option3'),
        option_4=request.form.get('option4'),
        correct_option=int(request.form.get('correct_option'))
    )
    db.session.add(question)
    db.session.commit()
    return redirect(url_for('admin_dashboard'))

# User routes
@app.route('/dashboard')
@login_required
def user_dashboard():
    user = User.query.get(session['user_id'])
    subjects = Subject.query.all()
    scores = Score.query.filter_by(user_id=user.id).all()
    return render_template('file2.html', subjects=subjects, scores=scores, is_admin=False)

@app.route('/quiz/<int:quiz_id>')
@login_required
def take_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    questions = Question.query.filter_by(quiz_id=quiz_id).all()
    return render_template('file2.html', quiz=quiz, questions=questions, mode='quiz')

@app.route('/submit_quiz/<int:quiz_id>', methods=['POST'])
@login_required
def submit_quiz(quiz_id):
    user_id = session['user_id']
    questions = Question.query.filter_by(quiz_id=quiz_id).all()
    
    correct_answers = 0
    total_questions = len(questions)
    
    for question in questions:
        user_answer = int(request.form.get(f'question_{question.id}', 0))
        if user_answer == question.correct_option:
            correct_answers += 1
    
    score_percentage = (correct_answers / total_questions) * 100
    
    score = Score(
        user_id=user_id,
        quiz_id=quiz_id,
        score=score_percentage
    )
    
    db.session.add(score)
    db.session.commit()
    
    flash(f'Quiz submitted! Your score: {score_percentage:.2f}%')
    return redirect(url_for('user_dashboard'))