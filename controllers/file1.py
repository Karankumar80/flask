from flask import render_template, request, redirect, url_for, flash, session
from app import app, db
from models.models import User
from datetime import datetime

@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            session['user_id'] = user.id
            if user.is_admin:
                return redirect(url_for('admin_dashboard'))
            return redirect(url_for('user_dashboard'))
            
        flash('Invalid email or password')
    return render_template('file1.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        full_name = request.form.get('full_name')
        qualification = request.form.get('qualification')
        dob = datetime.strptime(request.form.get('dob'), '%Y-%m-%d').date()

        if User.query.filter_by(email=email).first():
            flash('Email already exists')
            return redirect(url_for('register'))

        user = User(
            email=email,
            full_name=full_name,
            qualification=qualification,
            dob=dob
        )
        user.set_password(password)

        db.session.add(user)
        db.session.commit()

        flash('Registration successful')
        return redirect(url_for('login'))

    return render_template('file1.html', register=True)

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))