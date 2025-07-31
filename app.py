from flask import Flask, render_template, request, redirect
from models import db, NameSuggestion, Pet
from flask import Flask, session
from flask import flash, url_for
from models import AdminUser, AdminAccessRequest, AdminActivityLog
from werkzeug.security import generate_password_hash

app = Flask(__name__)
app.secret_key = "dev-key-1234"  # Replace with a secure, random string

# Configure SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pets.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database
db.init_app(app)


@app.route("/")
def home():
    return render_template("home.html")

    #changes

@app.route("/admin/login", methods=["GET", "POST"])
def adminlogin():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        #debug
        print("Username from form:", username)
        print("Password from form:", password)


        admin = AdminUser.login_admin(username, password)
        #debug
        print("Admin from login_admin():", admin)

        if admin:
            session["admin_id"] = admin.id
            session["admin_logged_in"] = True 
            print("Admin logged in:", session["admin_logged_in"])
            #debug
            print("Logged in successfully. Session:", session)

            AdminActivityLog.log_admin_activity(admin.id, "Logged in")
            return redirect(url_for("adminhome"))
        else:
            flash("Invalid username or password, or you are not approved.")
            #debug
            print("Login failed: Invalid credentials or not approved.")

    return render_template("adminLogin.html")


@app.route("/admin/home")
def adminhome():
    if not session.get("admin_logged_in"):
        print("Session data:", dict(session)) #debug

        return redirect(url_for("adminlogin"))

    suggestions = NameSuggestion.get_pending()
    pending_admin_requests = AdminAccessRequest.query.filter_by(status="pending").all()
    return render_template("adminHome.html", suggestions=suggestions, pending_admin_requests=pending_admin_requests)

@app.route("/admin/suggestion/approve/<int:suggestion_id>", methods=["POST"])
def approve_suggestion(suggestion_id):
    NameSuggestion.approve(suggestion_id)
    return redirect(url_for("adminhome"))

@app.route("/admin/suggestion/reject/<int:suggestion_id>", methods=["POST"])
def reject_suggestion(suggestion_id):
    NameSuggestion.reject(suggestion_id)
    return redirect(url_for("adminhome"))




@app.route("/pets", methods=["GET"])
def index():
    pets = Pet.query.all() 
    return render_template("index.html", pets=pets)

@app.route("/name/<int:pet_id>", methods=["GET", "POST"])
def name_pet(pet_id):
    pet = Pet.query.get_or_404(pet_id)
    if request.method == "POST":
        suggestion = NameSuggestion.create_from_form(pet_id, request.form)
        db.session.add(suggestion)
        db.session.commit()


        return redirect("/success")

    return render_template("name_pet.html", pet=pet)


@app.route("/success")
def success():
    return render_template("success.html")

@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.")
    return redirect(url_for("adminlogin"))

@app.route("/admin/request-status/<username>")
def admin_request_status(username):
    request_entry = AdminAccessRequest.query.filter_by(username=username).first()
    approved_admin = AdminUser.query.filter_by(username=username).first()

    if approved_admin:
        # Approved → redirect to login
        flash("Your request has been approved. Please log in.")
        return redirect(url_for("adminlogin"))
    elif request_entry:
        status = "pending"
    else:
        status = "declined"

    return render_template("adminRequestStatus.html", username=username, status=status)


@app.route("/admin/request", methods=["GET", "POST"])
def request_admin_access():
    if request.method == "POST":
        first_name = request.form.get("first_name")
        last_name = request.form.get("last_name")
        username = request.form.get("username")
        password = request.form.get("password")
        work_id = request.form.get("work_id")

        # Check if user already submitted a request
        if AdminAccessRequest.query.filter_by(username=username).first():
            flash("You have already submitted a request.")
            return redirect(url_for("admin_request_status", username=username))

        # Save to DB
        password_hash = generate_password_hash(password)
        request_entry = AdminAccessRequest(
            first_name=first_name,
            last_name=last_name,
            username=username,
            password_hash=password_hash,
            work_id=work_id
        )
        db.session.add(request_entry)
        db.session.commit()

        # Redirect to status page
        return redirect(url_for("admin_request_status", username=username))

    return render_template("adminRequestForm.html")

# @app.route("/admin/check-status", methods=["GET", "POST"])
# def check_admin_status():
#     if request.method == "POST":
#         username = request.form.get("username")
#         return redirect(url_for("admin_request_status", username=username))
#     return render_template("checkStatusForm.html")

@app.route("/admin/check-status", methods=["GET", "POST"])
def check_admin_status_form():
    if request.method == "POST":
        username = request.form.get("username")
        if username:
            return redirect(url_for("admin_request_status", username=username))
        else:
            flash("Please enter your username.")
    return render_template("checkStatusForm.html")

@app.route("/admin/request/approve/<int:request_id>", methods=["POST"])
def approve_admin_request(request_id):
    request_entry = AdminAccessRequest.query.get_or_404(request_id)

    # Create approved admin user
    AdminUser.create_admin_user(
        first_name=request_entry.first_name,
        last_name=request_entry.last_name,
        username=request_entry.username,
        password=request_entry.password_hash,  # This assumes it's already hashed
        work_id=request_entry.work_id
    )

    # Update status
    request_entry.status = "approved"
    db.session.commit()

    flash(f"{request_entry.username} has been approved as an admin.")
    return redirect(url_for("adminhome"))

@app.route("/admin/request/decline/<int:request_id>", methods=["POST"])
def decline_admin_request(request_id):
    request_entry = AdminAccessRequest.query.get_or_404(request_id)
    request_entry.status = "declined"
    db.session.commit()

    flash(f"{request_entry.username}'s admin request has been declined.")
    return redirect(url_for("adminhome"))

@app.route("/admin/debug")
def debug_admins():
    admins = AdminUser.query.all()
    return "<br>".join([f"{a.username} | approved: {a.is_approved}" for a in admins])
   





#fake admin test
@app.route("/create-initial-admin")
def create_initial_admin():
    if AdminUser.query.first():
        return "Admin already exists."
    AdminUser.create_admin_user(
        first_name="Shelby",
        last_name="Alonso",
        username="Salonsoe",
        password="111728",
        work_id="001"
    )
    return "Initial admin created. You can now log in at /admin/login."
    
if __name__ == "__main__":
        with app.app_context():
            db.create_all()
app.run(debug=True)
