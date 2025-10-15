from flask import Flask, render_template, url_for, request, redirect
import hashlib

app = Flask(__name__)

# our main landing page
@app.route("/")
def hello_world():
    return render_template("index.html")

# login page
@app.route("/login", methods=["GET", "POST"])
def login():
    # this means we are trying to login
    if request.method == "POST":
        username = request.form["username"]

        # hash the password BEFORE checking it against the database
        sha256_hash = hashlib.sha256()
        sha256_hash.update(request.form.get["password"].encode('utf-8'))
        hashed_password = sha256_hash.hexdigest()
        print(hashed_password)

        return redirect(url_for("hello_world"))
    
    # if we are simply request the page, just load it
    return render_template("login.html")


if __name__ == "__main__":
    app.run(debug=True)