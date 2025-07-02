from flask import Flask, render_template, request, redirect

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # Placeholder for name + payment logic
        pet_name = request.form.get("name")
        print(f"Name submitted: {pet_name}")
        return redirect("/success")
    return render_template("index.html")

@app.route("/success")
def success():
    return render_template("success.html")

if __name__ == "__main__":
    app.run(debug=True)
