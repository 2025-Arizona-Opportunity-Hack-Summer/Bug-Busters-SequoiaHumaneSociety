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

    status = db.Column(db.String(20), default="pending")  #pending, approved, rejected by admin

   

    pet = db.relationship('Pet', backref=db.backref('suggestions', lazy=True))


    @classmethod
    def create_from_form(cls, pet_id, form):
        return cls(
            pet_id=pet_id,
            first_name=form.get("first_name"),
            last_name=form.get("last_name"),
            email=form.get("email"),
            suggested_name=form.get("suggested_name"),
            donation=float(form.get("donation")),
            status="pending"
        )

    status = db.Column(db.String(20), default="pending")  #pending, approved, rejected by admin

from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
class AdminUser(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    work_id = db.Column(db.String(50), nullable=False)
    is_approved = db.Column(db.Boolean, default=False)  

    @classmethod
    def create_admin_user(cls, first_name, last_name, username, password, work_id):
        password_hash = generate_password_hash(password)
        admin = cls(
            first_name=first_name,
            last_name=last_name,
            username=username,
            password_hash=password_hash,
            work_id=work_id,
            is_approved=True
        )
        db.session.add(admin)
        db.session.commit()
        return admin

    @classmethod
    def delete_admin_user(cls, admin_id):
        admin = cls.query.get(admin_id)
        if admin:
            db.session.delete(admin)
            db.session.commit()
            return True
        return False

    @classmethod
    def login_admin(cls, username, password):
        admin = cls.query.filter_by(username=username, is_approved=True).first()
        if admin and check_password_hash(admin.password_hash, password):
            return admin
        return None

    @classmethod
    def admin_exists(cls, username):
        return cls.query.filter_by(username=username).first() is not None
    
    @classmethod
    def approve_admin_request(cls, request_id):
        req = AdminAccessRequest.query.get(request_id)
        if not req:
            return None
            
            admin = cls(
                first_name=req.first_name,
                last_name=req.last_name,
                username=req.username,
                password_hash=req.password_hash,
                work_id=req.work_id,
                is_approved=True
                )
            db.session.add(admin)
            db.session.delete(req)
            db.session.commit()
            return admin

    @classmethod
    def reject_admin_request(cls, request_id):
        req = AdminAccessRequest.query.get(request_id)
        if req:
            db.session.delete(req)
            db.session.commit()
            return True
        return False

    @classmethod
    def list_all_admins(cls):
        return cls.query.all()

    @classmethod
    def list_access_requests(cls):
        return AdminAccessRequest.query.order_by(AdminAccessRequest.timestamp.desc()).all()







class AdminAccessRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    work_id = db.Column(db.String(50), nullable=False)
    timestamp = db.Column(db.DateTime, server_default=db.func.now())

class AdminActivityLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    admin_id = db.Column(db.Integer, db.ForeignKey('admin_user.id'), nullable=False)
    action = db.Column(db.String(255), nullable=False)
    timestamp = db.Column(db.DateTime, server_default=db.func.now())

    admin = db.relationship('AdminUser', backref=db.backref('activities', lazy=True))

    @classmethod
    def log_admin_activity(cls, admin_id, action):
        log = cls(admin_id=admin_id, action=action)
        db.session.add(log)
        db.session.commit()



#stripe api idk how tho???



#add a pet -caro

#delete a pet -caro

#update pet -caro

#get pet by id -caro

#get all pets -caro

#add name suggestion -carp

#get all name suggestions -caro

#get pending name suggestions - caro

#delete name suggestion -caro

#approve pet name suggestion -caro

#reject pet name suggestion -caro
