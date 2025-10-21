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
    points = 0
    username = ""
    current_booking_id = ""

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

def get_user_data():
    with open("data/userdata.json", "r") as file:
        return json.load(file)
    
def save_user_data(user_data):
    with open("data/userdata.json", "w") as file:
        json.dump(user_data, file, indent=4)

def refresh_points():
    user_data = get_user_data()
    User.points = user_data[User.username]["points"]

def add_points(amount):
    user_data = get_user_data()
    user_data[User.username]["points"] += amount
    save_user_data(user_data)

def get_lounge_by_id(id):
    lounge_data = get_lounge_data_from_json()
    for lounge in lounge_data["lounges"]:
        if lounge["id"] == id:
            return lounge

def add_booking(username, lounge, start, end, date):
    user_data = get_user_data()
    bookings = user_data[username].get("bookings")
    booking_info = {
        "id": lounge["id"],
        "start_time": start,
        "end_time": end,
        "date": date,
    }
    if bookings:
        user_data[username]["bookings"].append(booking_info)
    else:
        user_data[username]["bookings"] = [booking_info]

    save_user_data(user_data)


def get_booked_lounges():
    user_data = get_user_data()[User.username]
    bookings = []
    user_bookings = user_data.get("bookings")
    if user_bookings:
        for booking in user_bookings:
            bookings.append(get_lounge_by_id(booking["id"]))
    return bookings

def cancel_booking(id):
    user_data = get_user_data()
    lounges_to_remove = []
    for i in range(len(user_data[User.username]["bookings"])):
        booking = user_data[User.username]["bookings"][i]
        if booking["id"] == id:
            lounges_to_remove.append(booking)
    user_data[User.username]["bookings"] = [i for i in user_data[User.username]["bookings"] if i not in lounges_to_remove]


    if user_data[User.username]["bookings"] == lounges_to_remove:
        user_data[User.username]["bookings"] = []
    
    save_user_data(user_data)



# our main landing page
@app.route("/")
def hello_world():
    if User.get_login_status():
        refresh_points()
    print(User.get_login_status())
    print(get_user_data())
    return render_template("index.html", user=User)

# explore lounges page
@app.route("/explore", methods=["GET", "POST"])
def explore():
    if User.get_login_status():
        query = request.form.get("query")
        lounge_data = ""
        if request.args.get("query") == "booked":
            lounge_data = get_booked_lounges()
        elif query:
            lounge_data = get_searched_lounge_data(query)
        if not lounge_data:
            lounge_data = get_lounge_data_from_json().get("lounges")

        booked_ids = [l["id"] for l in get_booked_lounges()]
    else:
        lounge_data = get_lounge_data_from_json().get("lounges")
        booked_ids = None

    print(lounge_data)

    return render_template("explore.html", lounge_data=lounge_data, booked_ids=booked_ids)



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

        # create new user data and set points to 0
        user_data = get_user_data()
        user_data[username] = {"points": 0}
        User.points = 0
        save_user_data(user_data)

        User.username = username

        # we are now logged in
        User.set_login_status(True)
        User.set_error_msg("")

        redirect_page = User.current_page
        if redirect_page:
            return redirect(url_for(redirect_page))

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
                User.username = username

                redirect_page = User.current_page
                if redirect_page:
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
    print(User.get_login_status())
    if not User.get_login_status():
        User.current_page = "explore"
        return redirect(url_for("login"))
    lounge = get_lounge_by_id(request.args["lounge_id"])
    return render_template("book.html", lounge=lounge)


@app.route("/pay", methods=["GET", "POST"])
def pay():
    lounge_id = request.args["lounge_id"]
    lounge = get_lounge_by_id(lounge_id)
    lounge_point_cost = int(lounge["points"])

    if request.form["payment_option"] == "money":
        add_points(50)
    elif request.form["payment_option"] == "points":
        print("POINTS")
        add_points(-lounge_point_cost)
    
    print(request.form["start_time"], request.form["end_time"], request.form["booking_date"])
    add_booking(User.username, lounge, request.form["start_time"], request.form["end_time"], request.form["booking_date"])
    return redirect(url_for("hello_world"))

@app.route("/profile")
def profile():
    if User.get_login_status():
        username = User.username
        user_data = get_user_data()[username]

        bookings = user_data["bookings"]
        lounge_details = []
        for booking in bookings:
            booking_id = booking["id"]
            lounge_details.append(get_lounge_by_id(booking_id))

        return render_template("profile.html", username=username, user_data=user_data, bookings=lounge_details)
    else:
        User.current_page = "profile"
        return redirect(url_for("login"))


@app.route("/cancel")
def cancel():
    lounge_id = request.args["lounge_id"]
    cancel_booking(lounge_id)
    return redirect(url_for("hello_world"))


if __name__ == "__main__":
    app.run(debug=True)