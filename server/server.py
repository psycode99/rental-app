from flask import *
import requests


app = Flask(__name__)

@app.route('/', methods=['POST','GET'])
def home():
    return render_template("home.html")


@app.route('/login', methods=['POST', "GET"])
def login():
    return render_template("login.html")


@app.route('/signup', methods=['POST', "GET"])
def signup():
    return render_template("signup.html")


@app.route('/property', methods=['POST', 'GET'])
def property():
    return render_template("property.html")


@app.route('/search', methods=['POST', 'GET'])
def search():
    return render_template('search.html')


@app.route('/dashboard', methods=["POST", "GET"])
def dashboard():
    return render_template("dashboard.html")


@app.route('/add_property', methods=['POST', "GET"])
def add_property():
    return render_template('add_prop_img.html')


@app.route('/make_booking', methods=['POST', "GET"])
def make_booking():
    pass


@app.route('/make_maintenance_req', methods=['POST', "GET"])
def make_maintenance_req():
    pass


@app.route('/make_tenant_app', methods=['POST', "GET"])
def make_tenant_app():
    pass


@app.route('/view_properties', methods=['POST', "GET"])
def view_properties():
    return render_template("view_prop.html")


@app.route('/view_bookings', methods=['POST', "GET"])
def view_bookings():
    return render_template("view_bookings.html")


@app.route('/view_maintenance_reqs', methods=['POST', "GET"])
def view_maintenance_reqs():
    return render_template("view_maintenance_reqs.html")


@app.route('/view_tenant_apps', methods=['POST', "GET"])
def view_tenant_apps():
    return render_template("view_tenant_apps.html")


@app.route('/payments', methods=['POST', "GET"])
def payments():
    return render_template("payments.html")


@app.route('/payment_history')
def payment_history():
    return render_template("payment.history.html")


@app.route('/booking')
def booking():
    return render_template("booking.html")


@app.route('/maintenace_req')
def maintenance_req():
    return render_template("maintenance_req.html")


@app.route('/tenant_app')
def tenant_app():
    return render_template("tenant_app.html")


@app.route('/edit_property', methods=['POST', "GET"])
def edit_property():
    return render_template("edit_prop_img.html")


@app.route('/edit_user_info', methods=['POST', "GET"])
def edit_user_info():
    return render_template("edit_user_info.html")


@app.route('/forgot_password', methods=['POST', "GET"])
def forgot_password():
    return render_template("fp_email.html")


@app.route('/otp_pwd', methods=['POST', "GET"])
def otp_pwd():
    return render_template("fp_otp.html")


@app.route('/password_reset', methods=['POST', "GET"])
def password_reset():
    return render_template("fp_password_reset.html")

if __name__ == "__main__":
    app.run(debug=True)