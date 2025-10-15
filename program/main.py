from flask import Flask, render_template, url_for, request, redirect
import hashlib
import json

app = Flask(__name__)


class User():
    # private attribute, we should only access it through get and set methods
    __logged_in = False

    @staticmethod
    # returns boolean of if user is logged in or not
    def get_login_status():
        return User._User__logged_in

    @staticmethod
    # flag is a boolean, sets whether or not user is logged in
    def set_login_status(flag):
        User._User__logged_in = flag

# loads the user database json as a dictionary
def get_user_from_json():
    with open("userdb.json", "r") as file:
        return json.load(file)
    
# saves all users back to the json
def save_users_to_json(users):
    with open("userdb.json", "w") as file:
        json.dump(users, file, indent=4)

# our main landing page
@app.route("/")
def hello_world():
    print(User.get_login_status())
    return render_template("index.html", user=User)


# if user does not yet have an account
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        users = get_user_from_json()
        username = request.form["username"]

        # hash the password BEFORE checking it against the database
        sha256_hash = hashlib.sha256()
        sha256_hash.update(request.form["password"].encode('utf-8'))
        hashed_password = sha256_hash.hexdigest()
        print(hashed_password)

        users[username] = hashed_password

        save_users_to_json(users)

        # we are now logged in
        User.set_login_status(True)

        return redirect(url_for("hello_world"))
    return render_template("signup.html")


# login page
@app.route("/login", methods=["GET", "POST"])
def login():
    # this means we are trying to login
    if request.method == "POST":
        username = request.form["username"]

        # hash the password BEFORE checking it against the database
        sha256_hash = hashlib.sha256()
        sha256_hash.update(request.form["password"].encode('utf-8'))
        hashed_password = sha256_hash.hexdigest()
        print(hashed_password)

        # open the user database
        users = get_user_from_json()
        
        # get the current user
        matched_password = users.get(username)
        # this means a user with this username exists
        if matched_password:
            # this asks does their password hash match the hashed password from the user
            if matched_password == hashed_password:
                print("LOGIN SUCCESS")
                # we are now logged in
                User.set_login_status(True)
            else:
                print("LOGIN UNSUCCESSFUL")
        else:
            print("USER NOT FOUND")


        print(User.get_login_status())
        # go back to the landing page 
        return redirect(url_for("hello_world"))
    
    # if we are simply request the page, just load it
    return render_template("login.html")

# if we decide to logout
@app.route("/logout", methods=["GET", "POST"])
def logout():
    # we are logged out
    User.set_login_status(False)
    # return to landing page
    return redirect(url_for("hello_world"))


if __name__ == "__main__":
    app.run(debug=True)