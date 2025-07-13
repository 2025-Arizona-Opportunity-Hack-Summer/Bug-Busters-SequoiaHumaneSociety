from flask import Flask, render_template, request, redirect

# Sample pet data (for now, hardcoded — we'll move this to a DB later)
pets = [
    {
        "id": 1,
        "breed": "Golden Retriever",
        "color": "Golden",
        "age": "2 years",
        "image": "golden.jpg"
    },
    {
        "id": 2,
        "breed": "Tabby Cat",
        "color": "Orange",
        "age": "1 year",
        "image": "tabby.jpg"
    },
    {
        "id": 3,
        "breed": "Bulldog",
        "color": "White and Brown",
        "age": "3 years",
        "image": "bulldog.jpg"
    }
]


app = Flask(__name__)

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/admin")
def admin():
    return render_template("admin.html")


@app.route("/pets", methods=["GET"])
def index():
    return render_template("index.html", pets=pets)

@app.route("/name/<int:pet_id>", methods=["GET", "POST"])
def name_pet(pet_id):
    pet = next((p for p in pets if p["id"] == pet_id), None)
    if request.method == "POST":
        # process form submission here
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
    app.run(debug=True)
