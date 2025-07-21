from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Table 1: Pet
class Pet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    breed = db.Column(db.String(50))
    color = db.Column(db.String(30))
    age = db.Column(db.String(30))
    image = db.Column(db.String(100))

class NameSuggestion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pet_id = db.Column(db.Integer, db.ForeignKey('pet.id'), nullable=False)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    email = db.Column(db.String(120))
    suggested_name = db.Column(db.String(50))
    donation = db.Column(db.Float)
    timestamp = db.Column(db.DateTime, server_default=db.func.now())

    pet = db.relationship('Pet', backref=db.backref('suggestions', lazy=True))
