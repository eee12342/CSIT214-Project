from flask import Flask, render_template, url_for, request, redirect
import hashlib
import json

app = Flask(__name__)


class User():
    # private attribute, we should only access it through get and set methods
    __logged_in = False
    __error_msg = ""

    # public attributes, we can just access them directly
    current_page = ""

    @staticmethod
    # returns boolean of if user is logged in or not
    def get_login_status():
        return User._User__logged_in

    @staticmethod
    # flag is a boolean, sets whether or not user is logged in
    def set_login_status(flag):
        User._User__logged_in = flag

    @staticmethod
    # returns users most recent error message
    def get_error_msg():
        return User._User__error_msg

    @staticmethod
    # sets user's most recent error message to argument provided
    def set_error_msg(msg):
        User._User__error_msg = msg


# loads the user database json as a dictionary
def get_user_from_json():
    with open("data/userdb.json", "r") as file:
        return json.load(file)
    
# saves all users back to the json
def save_users_to_json(users):
    with open("data/userdb.json", "w") as file:
        json.dump(users, file, indent=4)

def get_lounge_data_from_json():
    with open("data/loungedb.json", "r") as file:
        return json.load(file)
    
def get_searched_lounge_data(query):
    data = get_lounge_data_from_json()
    lounges = data.get("lounges")

    results = []
    for lounge in lounges:
        if query.lower() in lounge["name"].lower():
            results.append(lounge)

    return results


# our main landing page
@app.route("/")
def hello_world():
    print(User.get_login_status())
    return render_template("index.html", user=User)

# explore lounges page
@app.route("/explore")
def explore():
    query = request.args.get("query")
    if query:
        lounge_data = get_searched_lounge_data(query)
    else:
        lounge_data = get_lounge_data_from_json().get("lounges")
        print(lounge_data)

    return render_template("explore.html", lounge_data=lounge_data)



# if user does not yet have an account
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        users = get_user_from_json()
        username = request.form["username"]

        # check that username isn't already taken
        for user in users.keys():
            if username == user:
                User.set_error_msg("Username already taken. Please try another.")
                return redirect(url_for("signup"))

        # hash the password BEFORE checking it against the database
        sha256_hash = hashlib.sha256()
        sha256_hash.update(request.form["password"].encode('utf-8'))
        hashed_password = sha256_hash.hexdigest()
        print(hashed_password)

        users[username] = hashed_password

        save_users_to_json(users)

        # we are now logged in
        User.set_login_status(True)
        User.set_error_msg("")

        return redirect(url_for("hello_world"))
    return render_template("signup.html", message=User.get_error_msg())


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
                User.set_error_msg("")

                redirect_page = User.current_page
                if redirect:
                    return redirect(url_for(redirect_page))
            else:
                User.set_error_msg("Password invalid. Please try again.")
                return redirect(url_for("login"))
        else:
            User.set_error_msg("This username is not associated with an account. Please try again or create an account.")
            return redirect(url_for("login"))

        print(User.get_login_status())
        # go back to the landing page 
        return redirect(url_for("hello_world"))
    
    message = User.get_error_msg()
    # if we are simply request the page, just load it
    return render_template("login.html", message=message)


# if we decide to logout
@app.route("/logout", methods=["GET", "POST"])
def logout():
    # we are logged out
    User.set_login_status(False)
    # return to landing page
    return redirect(url_for("hello_world"))


# customer makes booking
@app.route("/book")
def book():
    if not User.get_login_status():
        User.current_page = "explore"
        return redirect(url_for("login"))
    return render_template("book.html")


if __name__ == "__main__":
    app.run(debug=True)