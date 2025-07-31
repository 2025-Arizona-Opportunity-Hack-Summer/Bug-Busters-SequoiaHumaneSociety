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



app = Flask(__name__)
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


@app.route("/")
def home():
    return render_template("home.html")

@app.route("/adminLogin", methods=["GET", "POST"])
def adminlogin():
    return render_template("adminLogin.html")



@app.route("/pets", methods=["GET"])
def index():
    pets = Pet.query.all() #is getting the pets from db rather than it being hardcoded
    return render_template("index.html", pets=pets)

@app.route("/name/<int:pet_id>", methods=["GET", "POST"])
def name_pet(pet_id):
    #pet = next((p for p in pets if p["id"] == pet_id), None)
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




# @app.route("/", methods=["GET", "POST"])
# def index():
#     if request.method == "POST":
#         # Placeholder for name + payment logic
#         pet_name = request.form.get("name")
#         print(f"Name submitted: {pet_name}")
#         return redirect("/success")
#     return render_template("index.html")




@app.route("/success")
def success():
    return render_template("success.html")

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
