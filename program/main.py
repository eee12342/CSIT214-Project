from flask import Flask, render_template, url_for

app = Flask(__name__)

# our main landing page
@app.route("/")
def hello_world():
    return render_template("index.html")