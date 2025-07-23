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


class AdminUser(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    work_id = db.Column(db.String(50), nullable=False)
    is_approved = db.Column(db.Boolean, default=False)  

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


#create admin user -shelby

#delete admin user -shelby

#admin login -shelby

#does user exist -shelby

#approve admin access request -shelby

#reject access request -shelby

#list admins/ access requests -shelby

#login admin activity -shelby


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
