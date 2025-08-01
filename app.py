from flask import Flask, render_template, request, redirect, url_for, session
from models import db, NameSuggestion, Pet
import stripe
import os
from dotenv import load_dotenv
load_dotenv()
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import ssl
import urllib3
#print("TEST_MESSAGE:", os.environ.get("TEST_MESSAGE"))


from flask import flash, url_for
from models import AdminUser, AdminAccessRequest, AdminActivityLog
from werkzeug.security import generate_password_hash

app = Flask(__name__)

from datetime import timedelta

app.permanent_session_lifetime = timedelta(minutes=30)
app.secret_key = os.environ.get("FLASK_SECRET_KEY")  # Replace with a secure, random string

ssl._create_default_https_context = ssl._create_unverified_context

#app = Flask(__name__)

# Configure SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pets.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database
db.init_app(app)

#keys for stripe checkout
app.config['STRIPE_PUBLIC_KEY'] = os.environ.get("STRIPE_PUBLIC_KEY")
app.config['STRIPE_SECRET_KEY'] = os.environ.get("STRIPE_SECRET_KEY")

stripe.api_key = app.config['STRIPE_SECRET_KEY']

#key for sendgrid

sg = SendGridAPIClient(os.environ.get("SENDGRID_API_KEY"))
#app = Flask(__name__)

#route for stripe
@app.route("/create-checkout-session", methods=["GET", "POST"])
def create_checkout_session():
    # session = stripe.checkout.Session.create(
    #     payment_method_types=['card'],
    #     line_items=[{
    #         'price_data': {
    #             'currency': 'usd',
    #             'product_data': {
    #                 'name': 'Shelter Donation',
    #             },
    #             'unit_amount': int(float(request.form['donation']) * 100),  # Convert dollars to cents
    #         },
    #         'quantity': 1,
    #     }],
    #     mode='payment',
    #     success_url=url_for('success', _external=True),
    #     cancel_url=url_for('index', _external=True),
    # )
    # return redirect(session.url, code=303)
    form_data = session.get("form_data")
    if not form_data:
        return redirect("/")  # No form data found, redirect safely

    session_stripe = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price_data': {
                'currency': 'usd',
                'product_data': {
                    'name': 'Shelter Donation',
                },
                'unit_amount': int(float(form_data["donation"]) * 100),
            },
            'quantity': 1,
        }],
        mode='payment',
        success_url=url_for('payment_success', _external=True),
        cancel_url=url_for('index', _external=True),
    )
    return redirect(session_stripe.url, code=303)

def send_confirmation_email(name_suggestion):
    message = Mail(
        from_email='carolmilan69@gmail.com',
        to_emails=name_suggestion.email,
        subject='Thanks for your name suggestion!',
        plain_text_content=f"""
Hi {name_suggestion.first_name},

Thanks for suggesting "{name_suggestion.suggested_name}" for the {name_suggestion.pet.breed}!

Your donation of ${name_suggestion.donation:.2f} was received. We appreciate your support!

- Sequoia Humane Society
""")

    try:
        sg = SendGridAPIClient(app.config('SENDGRID_API_KEY'))
        sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
        response = sg.send(message)
        print(f"Email sent! Status code: {response.status_code}")
    except Exception as e:
        print(f"Error sending email: {e}")


@app.route("/payment-success")
def payment_success():
    form_data = session.pop("form_data", None)
    if not form_data:
        return "No data to save", 400

    print("Saving this data:", form_data)  # ✅ Add this for debug


    # Save name suggestion to DB
    suggestion = NameSuggestion.create_from_form(
        pet_id=form_data["pet_id"],
        form=form_data
    )
    db.session.add(suggestion)
    db.session.commit()

    send_confirmation_email(suggestion)

    return render_template("success.html", donation=suggestion.donation)


@app.route("/admin/suggestion/approve/<int:suggestion_id>", methods=["POST"])
def approve_suggestion(suggestion_id):
    NameSuggestion.approve(suggestion_id)
    return redirect(url_for("adminhome"))

@app.route("/admin/suggestion/reject/<int:suggestion_id>", methods=["POST"])
def reject_suggestion(suggestion_id):
    NameSuggestion.reject(suggestion_id)
    return redirect(url_for("adminhome"))


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
            session.permanent = True
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
    #debug
    print("Pending admin requests:", pending_admin_requests)
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
        # first_name = request.form.get("first_name")
        # last_name = request.form.get("last_name")
        # email = request.form.get("email")
        # suggested_name = request.form.get("suggested_name")
        # donation = request.form.get("donation")

        # Create a new NameSuggestion record
        #testing: below works but erasing in meantimes
        # suggestion = NameSuggestion.create_from_form(pet_id, request.form)
        # db.session.add(suggestion)
        # db.session.commit()

# Create Stripe checkout session
        # session = stripe.checkout.Session.create(
        #     payment_method_types=['card'],
        #     line_items=[{
        #         'price_data': {
        #             'currency': 'usd',
        #             'product_data': {
        #                 'name': f"Donation for {pet.breed}",
        #             },
        #             'unit_amount': int(float(request.form['donation']) * 100),  # convert dollars to cents
        #         },
        #         'quantity': 1,
        #     }],
        #     mode='payment',
        #     success_url=url_for('success', _external=True),
        #     cancel_url=url_for('index', _external=True),
        # )
        print("Storing in session, not DB") #used for debug
        session['form_data'] = {
            "pet_id": pet_id,
            "first_name": request.form["first_name"],
            "last_name": request.form["last_name"],
            "email": request.form["email"],
            "suggested_name": request.form["suggested_name"],
            "donation": request.form["donation"]
        }
        return redirect("/create-checkout-session")

       # return redirect(session.url, code=303)

    return render_template("name_pet.html", pet=pet)


@app.route("/success")
def success():
    return render_template("success.html")

@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.")
    return redirect(url_for("home"))

@app.route("/admin/request-status/<username>")
def admin_request_status(username):
    request_entry = AdminAccessRequest.query.filter_by(username=username).first()
    approved_admin = AdminUser.query.filter_by(username=username).first()

    if approved_admin:
        status = "approved"
    elif request_entry:
        status = request_entry.status
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
            work_id=work_id,
            status="pending"
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
        work_id=request_entry.work_id,
        pre_hashed=True
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

#debug
@app.route("/admin/debug/delete-broken-admin/<username>")
def delete_broken_admin(username):
    admin = AdminUser.query.filter_by(username=username).first()
    if admin:
        db.session.delete(admin)
        db.session.commit()
        return f"Deleted admin {username}"
    return "Admin not found"

@app.route("/debug/delete-request/<username>")
def delete_admin_request_by_username(username):
    req = AdminAccessRequest.query.filter_by(username=username).first()
    if req:
        db.session.delete(req)
        db.session.commit()
        return f"Deleted request for {username}"
    return "Request not found"


#debug
@app.route("/debug/admin-requests")
def debug_admin_requests():
    requests = AdminAccessRequest.query.all()
    return "<br>".join([f"{r.username} - {r.status}" for r in requests])


    
if __name__ == "__main__":
        with app.app_context():
            db.create_all()
app.run(debug=True)
