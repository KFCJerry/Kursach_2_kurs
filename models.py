# models.py
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True)
    phone = db.Column(db.String(20), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    education = db.Column(db.String(200))
    experience = db.Column(db.String(100))
    is_blocked = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Animal(db.Model):
    __tablename__ = 'animals'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    type = db.Column(db.String(10), nullable=False)
    breed = db.Column(db.String(50))
    gender = db.Column(db.String(10))
    color = db.Column(db.String(30))
    photo_url = db.Column(db.String(200))
    status = db.Column(db.String(20), default='available')
    curator_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class MedicalCard(db.Model):
    __tablename__ = 'medical_cards'
    id = db.Column(db.Integer, primary_key=True)
    animal_id = db.Column(db.Integer, db.ForeignKey('animals.id'), unique=True, nullable=False)
    vet_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    exam_date = db.Column(db.String(20))
    is_sterilized = db.Column(db.Boolean, default=False)
    vaccination_date = db.Column(db.String(20))
    diagnosis = db.Column(db.Text)
    weight = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Owner(db.Model):
    __tablename__ = 'owners'
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(100))
    address = db.Column(db.String(200))

class AdoptionRequest(db.Model):
    __tablename__ = 'adoption_requests'
    id = db.Column(db.Integer, primary_key=True)
    animal_id = db.Column(db.Integer, db.ForeignKey('animals.id'), nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey('owners.id'), nullable=False)
    curator_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    status = db.Column(db.String(20), default='pending')
    contract_date = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Donation(db.Model):
    __tablename__ = 'donations'
    id = db.Column(db.Integer, primary_key=True)
    volunteer_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    donor_name = db.Column(db.String(100))
    type = db.Column(db.String(10))
    amount = db.Column(db.Float)
    donation_date = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)