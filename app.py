from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///quiz.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your-secret-key'

# Initialize SQLAlchemy
db = SQLAlchemy(app)

# Import routes after db initialization to avoid circular imports
from controllers.file1 import *
from controllers.file2 import *
from models.models import User

def create_admin():
    admin = User.query.filter_by(is_admin=True).first()
    if not admin:
        admin = User(
            email='admin@admin.com',
            full_name='Administrator',
            is_admin=True,
            qualification='Admin',
            dob=datetime.now().date()
        )
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        print("Admin user created successfully!")

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        create_admin()
    app.run(debug=True)