from flask import Flask, render_template, request, redirect
from models import db, NameSuggestion, Pet
from flask import Flask, session

app = Flask(__name__)
app.secret_key = "stinky_Farts"  # Replace with a secure, random string


#app = Flask(__name__)

# Configure SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pets.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database
db.init_app(app)


# Sample pet data (for now, hardcoded — we'll move this to a DB later)
# pets = [
#     {
#         "id": 1,
#         "breed": "Golden Retriever",
#         "color": "Golden",
#         "age": "2 years",
#         "image": "golden.jpg"
#     },
#     {
#         "id": 2,
#         "breed": "Tabby Cat",
#         "color": "Orange",
#         "age": "1 year",
#         "image": "tabby.jpg"
#     },
#     {
#         "id": 3,
#         "breed": "Bulldog",
#         "color": "White and Brown",
#         "age": "3 years",
#         "image": "bulldog.jpg"
#     }
# ]


#app = Flask(__name__)

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
        suggestion = NameSuggestion.create_from_form(pet_id, request.form)
        db.session.add(suggestion)
        db.session.commit()


        return redirect("/success")

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
