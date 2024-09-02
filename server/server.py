from flask import *
import requests
import jwt
from functools import wraps
import humanize
from datetime import datetime
import pytz

app = Flask(__name__)
app.secret_key = "qwerty"
host = "http://localhost:8000"
SECRET_KEY = "Q4epX5pDd_kjTbvRZ-8tLrXjFskv45pXyswhv48H8oM"


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.cookies.get('access_token')
        if not token:
            return redirect(url_for('login'))
        
        try:
            # Decode the token to verify its validity
            jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            return redirect(url_for('login'))  # Token expired, redirect to login
        except jwt.InvalidTokenError:
            return jsonify({"message": "Invalid token"}), 401
        
        return f(*args, **kwargs)
    
    return decorated


def verify_token(token):
    try:
        # Decode the JWT token (use your secret key here)
        decoded = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return decoded
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


@app.route('/', methods=['POST','GET'])
def home():
    token = request.cookies.get('access_token')
    logged_in = None

    page = request.args.get('page')
    size = request.args.get('size')
    if page == None or size == None:
        page = 1
        size = 1
        
    properties = requests.get(f'{host}/v1/properties/?page={page}&size={size}')
    if properties.status_code == 200:
        properties_json = properties.json()
        for prop in properties_json['items']:
            price = prop['price']
            bathrooms = prop['bathrooms']
            if price.is_integer():
                price = int(price)
            
            if bathrooms.is_integer():
                bathrooms = int(bathrooms)

            humanized_price = humanize.intcomma(price)
            prop['bathrooms'] = bathrooms
            prop['price'] = humanized_price
            # Assume data contains a 'timestamp' field in string format
            timestamp_str = prop['created_at']
            
            # Convert the string to a datetime object
            timestamp = datetime.fromisoformat(timestamp_str)
            
            # Optionally localize to a specific timezone if needed
            timestamp = timestamp.astimezone(pytz.timezone("Africa/Lagos"))

            # # Format the datetime as needed, e.g., 'Sep 2, 2024, 5:08 AM'
            # formatted_time = timestamp.strftime('%b %d, %Y, %I:%M %p')
            
            # Alternatively, you can use humanize to make it more natural, like "2 days ago"
            humanized_time = humanize.naturaltime(timestamp)
            prop['created_at'] = humanized_time
            total = properties_json['total']
            current_page = properties_json['page']
            size = properties_json['size']
            total_pages = properties_json['pages']
    else:
        return {
            "status_code": str(properties.status_code)
        }
    if token and verify_token(token):
         token_verification = verify_token(token)
         if token_verification['landlord']:
             res = requests.get(f"{host}/v1/users/landlords/{token_verification['user_id']}")
             data = res.json()
             data['img_path'] = "http://localhost:8000/static/profile_pics/"
         else:
            res = requests.get(f"{host}/v1/users/tenants/{token_verification['user_id']}")
            data = res.json()
            data['img_path'] = "http://localhost:8000/static/profile_pics/"
         logged_in = True
         return render_template("home.html",
                                logged_in=logged_in,
                                data=data,
                                properties=properties_json,
                                total=total,
                                page=current_page,
                                size=size,
                                total_pages=total_pages
                                )

    else:
         logged_in = False
         return render_template("home.html",
                                 logged_in=logged_in, 
                                 properties=properties_json, 
                                 total=total,
                                 page=current_page,
                                 size=size,
                                 total_pages=total_pages
                                 )

   
@app.route('/login', methods=['POST', "GET"])
def login():
    if request.method == "POST":
        email = request.form.get('email')
        password = request.form.get('password')

        res = requests.post(f"{host}/v1/auth/login", data={"username":email, "password":password})
        if res.status_code == 200:
            access_code = res.json().get('access_token')
            response =  redirect(url_for('home', page=1, size=1))
            response.set_cookie('access_token', access_code)
            return response
        else:
            return {
                "status_code": str(res.status_code),
                "detail": str(res.json().get('detail'))
            }

    return render_template("login.html")


@app.route('/signup', methods=['POST', "GET"])
def signup():
    if request.method == "POST":
        user_data =   {
        "first_name": request.form.get("firstname"),
        "last_name": request.form.get("lastname"),
        "email": request.form.get("email"),
        "phone_number": request.form.get("phone"),
        "landlord": bool(request.form.get('landlord')),
        "password": request.form.get("password"),
        "profile_pic": "null"
    }
        res = requests.post(f'{host}/v1/users/', json=user_data )
        if res.status_code == 201:
            session['user_id'] = res.json().get('id')
            session['first_name'] = res.json().get('first_name')
            session['last_name'] = res.json().get('last_name')
            session['email'] = res.json().get('email')
            session['phone_number'] = res.json().get('phone_number')
            session['landlord'] = res.json().get('landlord')
            session['password'] = user_data['password']
            session['profile_pic'] = res.json().get('profile_pic')
            return redirect(url_for('profile_pic'))
        else:
            return {
                "status_code": str(res.status_code),
                "detail": str(res.json().get('detail'))
            }
    return render_template("signup.html")


@app.route('/signup_profile_pic', methods=['POST', "GET"])
def profile_pic():
    if request.method == "POST":
        file = request.files['profile_pic']

        # Check if the file is selected
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)

        if file:

            # Prepare the file to be sent to the FastAPI endpoint
            files = {'file': (file.filename, file.stream, file.mimetype)}

            try:
                # Send the file to the FastAPI endpoint
                response = requests.post(f"{host}/v1/uploads/upload_profile_pic", files=files)

                # Handle the response from FastAPI
                if response.status_code == 200:
                    data = response.json()
                    filename = data.get('filename')
                    signup_data = {
                        "first_name": session['first_name'],
                        "last_name": session['last_name'],
                        "email": session['email'],
                        "phone_number": str(session['phone_number']),
                        "landlord": session['landlord'],
                        "password": session['password'],
                        "profile_pic": session['profile_pic']
                    }
                    user_id = session['user_id']
                    session['img_path'] = f"http://localhost:8000/static/profile_pics/{filename}"
                    login = requests.post(f"{host}/v1/auth/login", data={"username":signup_data['email'], "password":signup_data['password']})
                    if login.status_code == 200:
                        access_token = login.json().get("access_token")
                        headers = {
                        'Authorization': f'Bearer {access_token}',
                        "Content-Type": "application/json"
                        }
                        signup_data['profile_pic'] = filename
                        update_res = requests.put(f"{host}/v1/users/{user_id}", headers=headers, json=signup_data )
                        print(update_res.json())
                        if update_res.status_code == 200:
                            return redirect(url_for('login'))
                        else:
                            return "image update failed"
                    else:
                        return "Login failed"
                else:
                    flash(f"Failed to upload file. Status code: {response.status_code}, Detail: {response.json().get('detail')}")
                    return redirect(request.url)

            except requests.exceptions.RequestException as e:
                flash(f"An error occurred: {e}")
                return redirect(request.url)
                
    return render_template('profile_pic.html')


@app.route('/change_profile_pic', methods=['POST', 'GET'])
def change_profile_pic():
    token = request.cookies.get('access_token')
    print(token)
    if token and verify_token(token):
      
        token_verification = verify_token(token)
        if request.method == "POST":
            file = request.files['profile_pic']

            # Check if the file is selected
            if file.filename == '':
                flash('No selected file')
                return redirect(request.url)

            if file:

                # Prepare the file to be sent to the FastAPI endpoint
                files = {'file': (file.filename, file.stream, file.mimetype)}

                try:
                    # Send the file to the FastAPI endpoint
                    response = requests.post(f"{host}/v1/uploads/upload_profile_pic", files=files)
                    if response.status_code == 200:
                        filename = response.json().get('filename')
                        session['img_path'] = f"http://localhost:8000/static/profile_pics/{filename}"
                        if token_verification['landlord']:
                            res = requests.get(f"{host}/v1/users/landlords/{token_verification['user_id']}")
                            data = res.json()
                        else:
                            res = requests.get(f"{host}/v1/users/tenants/{token_verification['user_id']}")
                            data = res.json()
                        data['profile_pic'] = filename
                        data['password'] = session['password']
                        del data['id']
                        del data['created_at']
                        del data['property']
                        headers = {
                            'Authorization': f'Bearer {token}',
                            "Content-Type": "application/json"
                            }
                        print(data)
                        res = requests.put(f"{host}/v1/users/{token_verification['user_id']}",  headers=headers, json=data)
                        if res.status_code == 200:
                            return redirect(url_for('home'))
                        else:
                            return "image update failed"
                    else:
                        return "image uplaod failed"
                except requests.exceptions.RequestException as e:
                    flash(f"An error occurred: {e}")
                    return redirect(request.url)
    else:
        return "unauthorized"
 
    return redirect(url_for('home'))
                

@app.route('/property', methods=['POST', 'GET'])
def property():
    return render_template("property.html")


@app.route('/search', methods=['POST', 'GET'])
def search():
    return render_template('search.html')


@app.route('/dashboard', methods=["POST", "GET"])
@token_required
def dashboard():
    token = request.cookies.get('access_token')
    logged_in = None
    if token and verify_token(token):
        token_verification = verify_token(token)
        if token_verification['landlord']:
            res = requests.get(f"{host}/v1/users/landlords/{token_verification['user_id']}")
            data = res.json()
            data['img_path'] = "http://localhost:8000/static/profile_pics/"
        else:
            res = requests.get(f"{host}/v1/users/tenants/{token_verification['user_id']}")
            data = res.json()
            data['img_path'] = "http://localhost:8000/static/profile_pics/"
        logged_in = True

    return render_template("dashboard.html", logged_in=logged_in, data=data)


@app.route('/add_property_img', methods=['POST', "GET"])
@token_required
def add_property_img():
    if request.method == "POST":
        image1 = request.files.get("image1")
        image2 = request.files.get("image2")
        image3 = request.files.get("image3")

         # Prepare the files to send to FastAPI
        files = []
        if image1:
            files.append(('files', (image1.filename, image1.stream, image1.mimetype)))
        if image2:
            files.append(('files', (image2.filename, image2.stream, image2.mimetype)))
        if image3:
            files.append(('files', (image3.filename, image3.stream, image3.mimetype)))

        if len(files) < 3:
            return "one or more of the required files is missing"

        # Send the files to the FastAPI endpoint
        try:
            response = requests.post(f'{host}/v1/uploads/upload_imgs', files=files)
            
            # Check if the request was successful
            if response.status_code == 200:
                filenames = {"files": response.json().get('filenames')}
                session['img_files'] = filenames
                print(filenames)
                return redirect(url_for('add_property'))
            else:
                return f"Failed to upload images: {response.status_code} - {response.text}"

        except requests.exceptions.RequestException as e:
            flash(f"An error occurred: {e}")
            return redirect(url_for('upload_images'))
    return render_template('add_prop_img.html')


@app.route('/add_property', methods=['POST', "GET"])
@token_required
def add_property():
    filenames = session.get('img_files')['files']
    print(filenames)
    profile_pic = session['img_path']
    token = request.cookies.get('access_token')
    if token and verify_token(token):
        token_verification = verify_token(token)
        if token_verification['landlord']:
             res = requests.get(f"{host}/v1/users/landlords/{token_verification['user_id']}")
             data = res.json()
             
    if request.method == "POST":
        address = request.form.get("address").title()
        bedrooms = request.form.get("bedrooms")
        bathrooms = request.form.get("bathrooms")
        sqft = request.form.get("sqft")
        price = request.form.get('price')
        city = request.form.get('city').title()
        state = request.form.get("state").title()
        description = request.form.get("description")
        status = request.form.get("status")
        file_1 = filenames[0] if len(filenames) > 0 else None
        file_2 = filenames[1] if len(filenames) > 1 else None
        file_3 = filenames[2] if len(filenames) > 2 else None

        if sqft == "":
            sqft = None
        
        if not file_1 or not file_2 or not file_3:
            return "At least one of the required images is missing"

        property_data = {
            "address": address,
            "bedrooms": bedrooms,
            "bathrooms": bathrooms,
            "sqft": sqft,
            "price": price,
            "city": city,
            "state": state,
            "description": description,
            "landlord_id": token_verification['user_id'],
            "status": status,
            "file_1": file_1,
            "file_2": file_2,
            "file_3": file_3
        }

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        res = requests.post(f"{host}/v1/properties", headers=headers, json=property_data)
        if res.status_code == 201:
            session.pop("img_files", None)
            return redirect(url_for('dashboard'))
        else:
            return {"status_code": str(res.status_code), "detail": str(res.json().get('detail'))}

    return render_template("add_property.html", profile_pic=profile_pic, data=data)


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