from flask import *
import requests
import jwt
from functools import wraps
import humanize
from datetime import datetime, timezone, timedelta
import pytz
from config import host, profile_pic_dir, property_uploads_dir, tenant_applications_dir, SECRET_KEY, flask_secret_key

app = Flask(__name__)
app.secret_key = flask_secret_key


def humanize_res(data):
    for prop in data['items']:
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
    return data


def humanize_res_single(data):

    price = data['price']
    bathrooms = data['bathrooms']
    if price.is_integer():
        price = int(price)
    
    if bathrooms.is_integer():
        bathrooms = int(bathrooms)

    humanized_price = humanize.intcomma(price)
    data['bathrooms'] = bathrooms
    data['price'] = humanized_price
    # Assume data contains a 'timestamp' field in string format
    timestamp_str = data['created_at']
    
    # Convert the string to a datetime object
    timestamp = datetime.fromisoformat(timestamp_str)
    
    # Optionally localize to a specific timezone if needed
    timestamp = timestamp.astimezone(pytz.timezone("Africa/Lagos"))

    # # Format the datetime as needed, e.g., 'Sep 2, 2024, 5:08 AM'
    # formatted_time = timestamp.strftime('%b %d, %Y, %I:%M %p')
    
    # Alternatively, you can use humanize to make it more natural, like "2 days ago"
    humanized_time = humanize.naturaltime(timestamp)
    data['created_at'] = humanized_time

    return data


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
        properties_json['property_imgs'] = property_uploads_dir
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
             data['img_path'] = profile_pic_dir
         else:
            res = requests.get(f"{host}/v1/users/tenants/{token_verification['user_id']}")
            data = res.json()
            data['img_path'] = profile_pic_dir
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
            response =  redirect(url_for('home'))
            response.set_cookie('access_token', access_code)
            verified_access_code = verify_token(access_code)

            if verified_access_code['landlord']:
                user = requests.get(f"{host}/v1/users/landlords/{verified_access_code['user_id']}")
            else:
                user =  requests.get(f"{host}/v1/users/tenants/{verified_access_code['user_id']}")
            user_data = user.json()
            session['user_id'] = user_data['id']
            session['first_name'] = user_data['first_name']
            session['last_name'] = user_data['last_name']
            session['email'] = user_data['email']
            session['phone_number'] = user_data["phone_number"]
            session['landlord'] = user_data["landlord"]
            # session['password'] = user_data['password']
            session['profile_pic'] = user_data["profile_pic"]
            session['profile_pic_path'] = profile_pic_dir
            
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
                        "password": session['password'],
                        "profile_pic": session['profile_pic']
                    }
                    user_id = session['user_id']
                    session['profile_pic_path'] = f"{profile_pic_dir}{filename}"
                    login = requests.post(f"{host}/v1/auth/login", data={"username":signup_data['email'], "password":signup_data['password']})
                    if login.status_code == 200:
                        access_token = login.json().get("access_token")
                        session.pop('password', None)
                        headers = {
                        'Authorization': f'Bearer {access_token}',
                        "Content-Type": "application/json"
                        }
                        signup_data['profile_pic'] = filename
                        del signup_data['password']
                        update_res = requests.put(f"{host}/v1/users/{user_id}", headers=headers, json=signup_data )
                        print(update_res.json())
                        if update_res.status_code == 200:
                            # session['profile_pic'] = f"{profile_pic_dir}{filename}"
                            session['profile_pic'] = f"{filename}"
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
@token_required
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
                        
                        if token_verification['landlord']:
                            res = requests.get(f"{host}/v1/users/landlords/{token_verification['user_id']}")
                            data = res.json()
                            del data['id']
                            del data['created_at']
                            del data['property']
                            del data['landlord']
                        else:
                            res = requests.get(f"{host}/v1/users/tenants/{token_verification['user_id']}")
                            data = res.json()
                            del data['id']
                            del data['created_at']
                            del data['tenant_application']
                            del data['landlord']
                            del data['payments']
                        data['profile_pic'] = filename
                        headers = {
                            'Authorization': f'Bearer {token}',
                            "Content-Type": "application/json"
                            }
                        res = requests.put(f"{host}/v1/users/{token_verification['user_id']}",  headers=headers, json=data)
                        if res.status_code == 200:
                            # session['profile_pic'] = f"{profile_pic_dir}{filename}"
                            session['profile_pic'] = f"{filename}"
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
    property_id = request.args.get("id")
    res = requests.get(f"{host}/v1/properties/{property_id}")
    if res.status_code == 200:
            property_data = res.json()

            price = property_data['price']
            if price.is_integer():
                price = int(price)
            
            bathrooms = property_data['bathrooms']
            if bathrooms.is_integer():
                bathrooms = int(bathrooms)

            humanized_price = humanize.intcomma(price)
            property_data['bathrooms'] = bathrooms
            property_data['price'] = humanized_price

            property_data['property_imgs'] = property_uploads_dir
            property_data['img_path'] = profile_pic_dir

            landlord_res = requests.get(f"{host}/v1/users/landlords/{property_data['landlord_id']}")
            if landlord_res.status_code == 200:
                landlord_data = landlord_res.json()
            else:
                return {
            "status_code": str(res.status_code),
            "text": str(res.text)
        }

    else:
        return {
            "status_code": str(res.status_code),
            "text": str(res.text)
        }
    logged_in = None
    token = request.cookies.get('access_token')
    if token and verify_token(token):
        user_profile_picture = session['profile_pic']
        property_data['profile_pic'] =f"{session['profile_pic_path']}{user_profile_picture}" 
        logged_in = True
        user_data = {
            "first_name": session['first_name'],
            "last_name": session['last_name'],
            "email": session['email'],
            "phone_number": session['phone_number'],
            "landlord": session['landlord'],  # Assuming 'landlord' is stored as a boolean in the session
            "profile_pic": session['profile_pic']  # Defaults to 'null' if 'profile_pic' is not in session
        }
        property_data['user_data'] = user_data
        
    else:
        logged_in = False
    return render_template("property.html",
                           data=property_data,
                            logged_in=logged_in,
                            landlord_data=landlord_data)
        

@app.route('/search', methods=['POST', 'GET'])
def search():
    token = request.cookies.get('access_token')
    page = request.args.get('page')
    size = request.args.get('size')

    total = session.get('total', 0)
    total_pages = session.get('pages', 0)

    if page == None or size == None:
        page = 1
        size = 1
       
    if request.method == "POST":
        state = request.form.get('state')
        city = request.form.get('city')
        bedrooms = request.form.get('bedrooms')
        bathrooms = request.form.get("bathrooms")
        price = request.form.get("price")
        status = request.form.get("status")

        search_params = {
            "state": state if state else None,
            "city": city if city else None,
            "bedrooms": int(bedrooms) if bedrooms else None,
            "bathrooms": float(bathrooms) if bathrooms else None,
            "price": float(price) if price else None,
            "status": status
        }

        res = requests.post(f"{host}/v1/properties/search?page={page}&size=1", params=search_params)
        if res.status_code == 200:
            session['state'] = state if state else None
            session['city'] = city if city else None
            session['bedrooms'] = int(bedrooms) if bedrooms else None
            session['bathrooms'] = float(bathrooms) if bathrooms else None
            session['price'] = float(price) if price else None
            session['status'] = status

            data = res.json()
            data['property_imgs'] = property_uploads_dir
            for prop in data['items']:
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

                total = data['total']
                current_page = data['page']
                size = data['size']
                total_pages = data['pages']

                session['total'] = total
                session['page'] = current_page
                session['size'] = size
                session['pages'] = total_pages

            if token and verify_token(token):
                logged_in = True
                profile_picture = f"{session['profile_pic_path']}{session['profile_pic']}"
                data['first_name'] = session.get('first_name', None)
                data['last_name'] = session.get("last_name", None)
                data['email'] = session.get("email", None)
                data['landlord'] = session.get("landlord", None)
                data['phone_number'] = session.get("phone_number", None)
                
                return render_template(
                                    'search.html',
                                    data=data,
                                    logged_in=logged_in,
                                    profile_picture=profile_picture,
                                    total=total,
                                    page=current_page,
                                    size=size,
                                    total_pages=total_pages)
            else:
                logged_in = False
                return render_template(
                                    'search.html',
                                    data=data,
                                    logged_in=logged_in,
                                    total=total,
                                    page=current_page,
                                    size=size,
                                    total_pages=total_pages)
        else:
            return {
                "status_code": str(res.status_code),
                "detail": str(res.text)
            }
    if token and verify_token(token):
        logged_in = True

        state = session.get('state')
        city = session.get('city')
        bedrooms = session.get('bedrooms')
        bathrooms = session.get('bathrooms')
        price = session.get('price')
        status = session.get('status')
        # Store these variables in a dictionary or JSON object
        search_params = {
            "state": state,
            "city": city,
            "bedrooms": bedrooms,
            "bathrooms": bathrooms,
            "price": price,
            "status": status
        }
        res = requests.post(f"{host}/v1/properties/search?page={page}&size=1", params=search_params)
        if res.status_code == 200:
            data = res.json()
            data = data if data else None
            data['property_imgs'] = property_uploads_dir
            data = humanize_res(data=data)
            data = data if data else None
            data['first_name'] = session.get('first_name', None)
            data['last_name'] = session.get("last_name", None)
            data['email'] = session.get("email", None)
            data['landlord'] = session.get("landlord", None)
            data['phone_number'] = session.get("phone_number", None)
            profile_picture = f"{session['profile_pic_path']}{session['profile_pic']}"
            return render_template('search.html',
                                    data=data,
                                    total=total,
                                    page=int(page),
                                    size=size,
                                    total_pages=total_pages,
                                    logged_in=logged_in,
                                    profile_picture=profile_picture)
        else:
            return {
                "status_code": str(res.status_code)
            }
    else:
        logged_in = False

        state = session.get('state')
        city = session.get('city')
        bedrooms = session.get('bedrooms')
        bathrooms = session.get('bathrooms')
        price = session.get('price')
        status = session.get('status')

        # Store these variables in a dictionary or JSON object
        search_params = {
            "state": state,
            "city": city,
            "bedrooms": bedrooms,
            "bathrooms": bathrooms,
            "price": price,
            "status": status
        }
        res = requests.post(f"{host}/v1/properties/search?page={page}&size=1", params=search_params)
        if res.status_code == 200:
            data = res.json()
            data = data if data else None
            data['property_imgs'] = property_uploads_dir
            data = humanize_res(data=data)
            return render_template('search.html',
                                    data=data,
                                    total=total,
                                    page=int(page),
                                    size=size,
                                    total_pages=total_pages,
                                    logged_in=logged_in)
        else:
            return {
                "status_code": str(res.status_code)
            }

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
            data['img_path'] = profile_pic_dir
        else:
            res = requests.get(f"{host}/v1/users/tenants/{token_verification['user_id']}")
            data = res.json()
            data['img_path'] = profile_pic_dir
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
            return redirect(url_for('add_property_imgs'))
    return render_template('add_prop_img.html')


@app.route('/add_property', methods=['POST', "GET"])
@token_required
def add_property():
    filenames = session.get('img_files')['files']
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

    return render_template("add_property.html", data=data)


@app.route('/make_booking', methods=['POST', "GET"])
def make_booking():
    property_id = int(request.args.get("property_id"))
    if request.method == "POST":
        name = request.form.get('name').title()
        email = request.form.get('email')
        phone_number = request.form.get('phone_number')
        viewing_date_str = request.form.get('viewing_date')
        viewing_time = request.form.get('viewing_time')
        notes = request.form.get('notes')

        viewing_date = datetime.strptime(viewing_date_str, '%Y-%m-%d').date()

        booking_data = {
        "property_id": property_id,
        'name': name,
        'email': email,
        'phone_number': phone_number,
        'viewing_date': viewing_date.isoformat(),
        'viewing_time': viewing_time,
        'notes': notes
        }

        res = requests.post(f"{host}/v1/bookings/{property_id}", json=booking_data)
        if res.status_code == 201:
            return redirect(request.url)
        else:
            return {
                "status_code": str(res.status_code),
                "detail": str(res.json().get('detail'))
            }
    return redirect(url_for('property', id=property_id))


@app.route('/make_maintenance_req', methods=['POST', "GET"])
@token_required
def make_maintenance_req():
    if request.method == "POST":
        token = request.cookies.get('access_token')
        headers = {
                        'Authorization': f'Bearer {token}',
                        "Content-Type": "application/json"
                        }
        property_id = request.form.get('property')
        request_date = request.form.get("request_date")
        description = request.form.get("description")

        data = {
            "property_id": property_id,
            "tenant_id": session.get('user_id'),
            "request_date": request_date,
            "description": description
        }

        res = requests.post(f"{host}/v1/maintenance_reqs/{property_id}", headers=headers, json=data)
        if res.status_code == 201:
            return redirect(url_for('view_maintenance_reqs'))
        else:
            return {
                "status_code": res.status_code,
                "detail": res.text
            }

@app.route('/make_tenant_app', methods=['POST'])
@token_required
def make_tenant_app():
    access_token = request.cookies.get('access_token')

    property_id = request.args.get('id')
    first_name = request.form.get('first_name')
    last_name = request.form.get('last_name')
    date_of_birth = request.form.get('date_of_birth')
    national_identity_number = request.form.get('national_identity_number')
    email_address = request.form.get('email_address')
    phone_number = request.form.get('phone_number')
    current_address = request.form.get('current_address')
    previous_address = request.form.get('previous_address')
    employer_name = request.form.get('employer_name')
    job_title = request.form.get('job_title')
    employment_duration = request.form.get('employment_duration')
    monthly_income = request.form.get('monthly_income')
    previous_landlord_name = request.form.get('previous_landlord_name')
    previous_landlord_contact = request.form.get('previous_landlord_contact')
    reason_for_moving = request.form.get('reason_for_moving')
    personal_reference_name = request.form.get('personal_reference_name')
    personal_reference_contact = request.form.get('personal_reference_contact')
    professional_reference_name = request.form.get('professional_reference_name')
    professional_reference_contact = request.form.get('professional_reference_contact')
    application_date = request.form.get('application_date')
    desired_move_in_date = request.form.get('desired_move_in_date')
    criminal_record = request.form.get('criminal_record')
    pets = request.form.get('pets')
    number_of_occupants = request.form.get('number_of_occupants')
    special_requests = request.form.get('special_requests')

    # Handling file upload
    file = request.files['file_upload']
    filename = None
    
    if file:
        files = {"file": (file.filename, file.stream, file.mimetype)}
        try:
            file_res = requests.post(f"{host}/v1/uploads/upload_application", files=files)
            if file_res.status_code == 200:
                filename = file_res.json().get('filename')
                print(filename)
            else:
                return  {
                    "status_code": file_res.status_code,
                    "detail": file_res.text
                }
                
        except requests.exceptions.RequestException as e:
                flash(f"An error occurred: {e}")
                return redirect(request.url)
        
    headers = {
            'Authorization': f'Bearer {access_token}',
            "Content-Type": "application/json"
                        }

    tenant_application =  {
        "first_name": first_name,
        "last_name": last_name,
        "tenant_id": session.get('user_id', None),
        "property_id": property_id,
        "date_of_birth": date_of_birth,
        "national_identity_number": national_identity_number,
        "email_address": email_address,
        "phone_number": phone_number,
        "current_address": current_address,
        "previous_address": previous_address,
        "employer_name": employer_name,
        "job_title": job_title,
        "employment_duration": employment_duration,
        "monthly_income": float(monthly_income),
        "previous_landlord_name": previous_landlord_name,
        "previous_landlord_contact": previous_landlord_contact,
        "reason_for_moving": reason_for_moving,
        "personal_reference_name": personal_reference_name,
        "personal_reference_contact": personal_reference_contact,
        "professional_reference_name": professional_reference_name,
        "professional_reference_contact": professional_reference_contact,
        "application_date": application_date,
        "desired_move_in_date": desired_move_in_date,
        "criminal_record": criminal_record,
        "pets": pets,
        "number_of_occupants": number_of_occupants,
        "special_requests": special_requests,
        "file_name": filename
    }

    try:
        res = requests.post(f"{host}/v1/applications/{property_id}", headers=headers, json=tenant_application)
        if res.status_code == 201:
            return redirect(url_for('home'))
        else:
            return {
                "status_code": res.status_code,
                "detail": res.text
            }
    except requests.exceptions.RequestException as e:
        flash(f"An error occurred: {e}")
        return redirect(request.url)


@app.route('/view_properties', methods=['POST', "GET"])
@token_required
def view_properties():
    token = request.cookies.get('access_token')
    headers = {'Authorization': f'Bearer {token}',
                "Content-Type": "application/json"
                        }
    
    res = requests.get(f"{host}/v1/properties/user", headers=headers)
    
    if res.status_code == 200:
        data = res.json()
        if data['items']:
            data = humanize_res(data)
        data['property_imgs'] = property_uploads_dir
        return render_template("view_prop.html", data=data)
    else:
        return {
            "status_code": str(res.status_code),
            "detail": res.text
        }


@app.route('/user_property', methods=["POST", "GET"])
@token_required
def user_property():
    property_id = int(request.args.get('id'))
    user_id = session.get('user_id', None)
    first_name = session.get('first_name', None)
    last_name = session.get('last_name', None)
    phone_number = session.get('phone_number', None)
    landlord = session.get('landlord', None)

    user_data = {
        "id": user_id,
        "first_name": first_name,
        "last_name": last_name,
        "phone_number": phone_number,
        "landlord": landlord
    }

    res = requests.get(f"{host}/v1/properties/{property_id}")
    if res.status_code == 200:
        data = res.json()
        data = humanize_res_single(data)
        data['property_imgs'] = property_uploads_dir

        landlord_id = data['landlord_id']
        landlord_res = requests.get(f"{host}/v1/users/landlords/{landlord_id}")
        if landlord_res.status_code == 200:
            landlord_info = landlord_res.json()
            landlord_data = {
                "landlord_id": landlord_info['id'],
                "profile_pic": landlord_info['profile_pic'],
                "email": landlord_info['email']
            }
            data['user_data'] = user_data
            data['landlord_data'] = landlord_data
            data['img_path'] = profile_pic_dir
            return render_template("user_property.html", data=data, logged_in=True)
        else:
            return {
            "status_code": str(landlord_res.status_code),
            "detail": str( landlord_res.text)
        }


    else:
        return {
            "status_code": str(res.status_code),
            "detail": str( res.text)
        }

   
@app.route('/view_bookings', methods=['POST', "GET"])
@token_required
def view_bookings():
    access_token = request.cookies.get('access_token')
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    res = requests.get(f"{host}/v1/bookings/", headers=headers)
    if res.status_code == 200:
        data = res.json()
        data['bookings_length'] = len(data['items'])
        for booking in data['items']:
            prop_res = requests.get(f"{host}/v1/properties/{booking['property_id']}")
            if prop_res.status_code == 200:
                booking['property_address'] = prop_res.json().get('address')
                booking['state'] = prop_res.json().get('state')
                booking['city'] = prop_res.json().get('city')

        return render_template("view_bookings.html", data=data)
    else:
        return {
            "status_code": str(res.status_code),
            "detail": str(res.text)
        }


@app.route('/view_maintenance_reqs', methods=['POST', "GET"])
@token_required
def view_maintenance_reqs():
    access_token = request.cookies.get('access_token')
    verify_AT = verify_token(access_token)
    landlord = None
    if verify_AT['landlord']:
        landlord = True
    else:
        landlord = False

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    prop_res = requests.get(f"{host}/v1/properties/user", headers=headers)
    if prop_res.status_code == 200:
        prop_data = prop_res.json().get('items')
        prop_details = []
        for prop in prop_data:
            property_ = {"id": prop['id'], "address": prop['address']}
            prop_details.append(property_)
    else:
         return {
                    "status_code": prop_res.status_code,
                    "detail": prop_res.text
                }
    res = requests.get(f"{host}/v1/maintenance_reqs/", headers=headers)
    if res.status_code == 200:
        data = res.json()
        for mr in data['items']:
            property_resp = requests.get(f"{host}/v1/properties/{mr['property_id']}")
            if property_resp.status_code == 200:
                mr['address'] = property_resp.json().get('address')
                mr['city'] = property_resp.json().get('city')
                mr['state'] = property_resp.json().get('state')
            else:
                return {
                    "status_code": property_resp.status_code,
                    "detail": property_resp.text
                }
            tenant_resp = requests.get(f"{host}/v1/users/tenants/{mr['tenant_id']}")
            if tenant_resp.status_code == 200:
                mr['tenant_firstname'] = tenant_resp.json().get('first_name')
                mr['tenant_lastname'] = tenant_resp.json().get('last_name')
            else:
                 return {
                    "status_code": tenant_resp.status_code,
                    "detail": tenant_resp.text
                }
    elif res.status_code == 204:
        data = {"message":"No Maintenance Request Made Yet", "items": []}

    data['property_data'] = prop_details
    data['landlord'] = landlord
    return render_template("view_maintenance_reqs.html", data=data)


@app.route('/view_tenant_apps', methods=['POST', "GET"])
@token_required
def view_tenant_apps():
    access_token = request.cookies.get('access_token')
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    res = requests.get(f"{host}/v1/applications/", headers=headers)
    if res.status_code == 200:
        data = res.json()
        data['applications_length'] = len(data['items'])
        for app in data['items']:
            prop_res = requests.get(f"{host}/v1/properties/{app['property_id']}")
            if prop_res.status_code == 200:
                app['property_address'] = prop_res.json().get('address')
                app['state'] = prop_res.json().get('state')
                app['city'] = prop_res.json().get('city')

        return render_template("view_tenant_apps.html", data=data)
    else:
        return {
            "status_code": str(res.status_code),
            "detail": str(res.text)
        }
   

@app.route('/payments', methods=['POST', "GET"])
def payments():
    return render_template("payments.html")


@app.route('/payment_history')
def payment_history():
    return render_template("payment.history.html")


@app.route('/booking')
@token_required
def booking():
    property_id = request.args.get('pid')
    booking_id = request.args.get('bid')
    access_token = request.cookies.get('access_token')
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    res = requests.get(f"{host}/v1/bookings/{property_id}/{booking_id}", headers=headers)
    if res.status_code == 200:
        data = res.json()
        prop_resp = requests.get(f"{host}/v1/properties/{data['property_id']}")
        if prop_resp.status_code == 200:
            data['address'] = prop_resp.json().get('address')
            data['state'] = prop_resp.json().get('state')
            data['city'] = prop_resp.json().get('city')
            return render_template("booking.html", data=data)
        else:
            return {
            "status_code": str(prop_resp.status_code),
            "detail": str(prop_resp.text)
        }


    else:
        return {
            "status_code": str(res.status_code),
            "detail": str(res.text)
        }


@app.route('/maintenace_req')
@token_required
def maintenance_req():
    property_id = request.args.get('pid')
    booking_id = request.args.get('id')
    access_token = request.cookies.get('access_token')
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    res = requests.get(f"{host}/v1/maintenance_reqs/{property_id}/{booking_id}", headers=headers)
    if res.status_code == 200:
        data = res.json()
        data['first_name'] = data['tenant']['first_name']
        data['last_name'] = data['tenant']['last_name']
        prop_resp = requests.get(f"{host}/v1/properties/{data['property_id']}")
        if prop_resp.status_code == 200:
            data['address'] = prop_resp.json().get('address')
            data['state'] = prop_resp.json().get('state')
            data['city'] = prop_resp.json().get('city')
            return render_template("maintenance_req.html", data=data)
        else:
            return {
            "status_code": str(prop_resp.status_code),
            "detail": str(prop_resp.text)
        }


    else:
        return {
            "status_code": str(res.status_code),
            "detail": str(res.text)
        }


@app.route('/tenant_app', methods=['GET'])
@token_required
def tenant_app():
    property_id = request.args.get('pid')
    application_id = request.args.get('tid')
    token = request.cookies.get('access_token')
    t_v = verify_token(token)

    headers = {
            'Authorization': f'Bearer {token}',
            "Content-Type": "application/json"
            }
    res = requests.get(f"{host}/v1/applications/{property_id}/{application_id}", headers=headers)
    if res.status_code == 200:
        data = res.json()
        data['landlord'] = t_v['landlord']
        data['monthly_income'] = humanize.intcomma(data['monthly_income'])
        prop_resp = requests.get(f"{host}/v1/properties/{data['property_id']}")
        if prop_resp.status_code == 200:
            data['address'] = prop_resp.json().get('address')
            data['state'] = prop_resp.json().get('state')
            data['city'] = prop_resp.json().get('city')
            return render_template("tenant_app.html", data=data)
        else:
            return {
            "status_code": str(prop_resp.status_code),
            "detail": str(prop_resp.text)
        }
       
    else:
        return  {
                    "status_code": res.status_code,
                    "detail": res.text
                }


@app.route('/download/<filename>', methods=['GET'])
@token_required
def download_application(filename):
    try:
        # Make a GET request to the FastAPI server to retrieve the file
        fastapi_url = f"{tenant_applications_dir}/{filename}"
        response = requests.get(fastapi_url, stream=True)
        
        if response.status_code == 404:
            abort(404)  # File not found on FastAPI server
        elif response.status_code != 200:
            abort(500)  # Handle any other server error

        # Serve the file to the client
        return Response(
            response.iter_content(chunk_size=8192),
            content_type=response.headers['Content-Type'],
            headers={
                'Content-Disposition': f'attachment;filename={filename}'
            }
        )

    except Exception as e:
        print(f"Error: {e}")
        abort(500)  # Internal Server Error if something goes wrong


@app.route('/edit_property_img', methods=['POST', "GET"])
@token_required
def edit_property_img():
    property_id = request.args.get('id')
    res = requests.get(f"{host}/v1/properties/{property_id}")
    if res.status_code == 200:
        data = res.json()
        data['property_imgs'] = property_uploads_dir
        prop_images = {
            "image_1": data['file_1'],
            "image_2": data['file_2'],
            "image_3": data['file_3']
        }
        data['images'] = prop_images
        session['prop_images'] = prop_images
    
    if request.method == "POST":
        property_id = request.args.get('id')
        prop_images = session['prop_images']

        for i in range(1, 4):
            file = request.files.get(f"image{i}")
            if file and file.filename != "":
                files = {'file': (file.filename, file.stream, file.mimetype)}
                try:
                    response = requests.post(f'{host}/v1/uploads/upload_img', files=files)
                    if response.status_code == 200:
                        unique_name = response.json().get('filename')
                        prop_images[f'image_{i}'] = unique_name
                    else:
                        return {
                            "status_code": str(response.status_code),
                            "detail": str(response.text)
                        }
                except requests.exceptions.RequestException as e:
                    flash(f"An error occurred: {e}")
                    return redirect(url_for('edit_property_img'))
        filenames = [filename for filename in  prop_images.values()]
        session['edit_imgs'] = filenames
        session.pop('prop_images', None)
        return redirect(url_for('edit_property', id=property_id))

    return render_template("edit_prop_img.html", data=data)


@app.route('/edit_property', methods=['POST', "GET"])
@token_required
def edit_property():
    property_id = request.args.get('id')
    res = requests.get(f"{host}/v1/properties/{property_id}")
    
    if request.method == "POST":
        property_id = request.args.get('id')
        filenames = session.get('edit_imgs')
        token = request.cookies.get('access_token')
        if token and verify_token(token):
            token_verification = verify_token(token)
            if token_verification['landlord']:
                res = requests.get(f"{host}/v1/users/landlords/{token_verification['user_id']}")
                data = res.json()

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

        res = requests.put(f"{host}/v1/properties/{property_id}", headers=headers, json=property_data)
        if res.status_code == 200:
            session.pop("edit_imgs", None)
            return redirect(url_for('dashboard'))
        else:
            return {"status_code": str(res.status_code), "detail": str(res.json().get('detail'))}

        
    if res.status_code == 200:
        data = res.json()
        return render_template("edit_property.html", data=data)
        
    else:
        return {
            "status": res.status_code,
            "detail": res.text
        }
    

@app.route('/edit_user_info', methods=['POST', "GET"])
@token_required
def edit_user_info():
    if request.method == 'POST':
        user_id = request.args.get('id')
        access_token = request.cookies.get('access_token')
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        first_name = request.form.get("firstName")
        last_name = request.form.get("lastName")
        email = request.form.get("email")
        phone_number = request.form.get('phone')

        data = {
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "phone_number": phone_number,
            "profile_pic": session.get('profile_pic')
        }

        res = requests.put(f"{host}/v1/users/{user_id}", headers=headers, json=data)
        if res.status_code == 200:
            session['first_name'] = res.json().get('first_name')
            session['last_name'] = res.json().get('last_name')
            session['email'] = res.json().get('email')
            session['phone_number'] = res.json().get('phone_number')
            return redirect(url_for('dashboard'))
        else:
            return {
            "status_code": str(res.status_code),
            "detail": str(res.text)
        }


    data = {
        "id": session.get('user_id'),
        "first_name": session.get('first_name'),
        "last_name": session.get('last_name'),
        "email": session.get('email'),
        "phone_number": session.get('phone_number')
    }
    return render_template("edit_user_info.html", data=data)


@app.route('/update_maintenance_req')
@token_required
def update_maintenance_req():
    pass


@app.route('/approve_tenant_app')
@token_required
def approve_tenant_app():
    property_id = request.args.get('pid')
    application_id = request.args.get('aid')
    tenant_id = request.args.get('tid')

    access_token = request.cookies.get('access_token')
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    data = {
        "tenant_id": tenant_id,
        "application_status": "approved"
    }

    res = requests.put(f"{host}/v1/applications/{property_id}/{application_id}", headers=headers, json=data)
    if res.status_code == 200:
        return redirect(url_for('dashboard'))
    else:
        return {
            "status_code": res.status_code,
            "detail": res.text
        }


@app.route('/forgot_password', methods=['POST', "GET"])
def forgot_password():
    if request.method == "POST":
        email = request.form.get('email')
        data = {
            "email": email
        }
        res = requests.post(f'{host}/v1/auth/fpa_otp', json=data)
        if res.status_code == 200:
            data = res.json()
            session['otp'] = data['otp']
            session['otp_expiration'] = (datetime.now(timezone.utc) + timedelta(minutes=5)).isoformat()
            session['otp_email'] = data['email']
            return redirect(url_for('otp_pwd'))
    return render_template("fp_email.html")


@app.route('/otp_pwd', methods=['POST', "GET"])
def otp_pwd():
    if request.method == "POST":
        sent_otp = session.get('otp')
        exp = session.get('otp_expiration')
        email = session.get('otp_email')
   
        if not sent_otp or not exp:
            return "OTP does not exist or has expired", 400
        
        exp_time = datetime.fromisoformat(exp)
        if datetime.now(timezone.utc) > exp_time:
            session.pop('otp', None)
            session.pop('otp_expiration_time', None)
            return "OTP has expired"
        
        typed_otp = request.form.get('otp')
   
        data = {
            "otp": sent_otp,
            "typed_otp": typed_otp,
            "email": email
        }

        res = requests.post(f'{host}/v1/auth/verify_otp', json=data)
        if res.status_code == 200:
            res_data = res.json()
            session['otp_email'] = res_data['email']
            session.pop('otp', None)
            session.pop('otp_expiration_time', None)
            return redirect(url_for('password_reset'))
    return render_template("fp_otp.html")


@app.route('/password_reset', methods=['POST', "GET"])
def password_reset():
    if request.method == "POST":
        new_password = request.form.get('password')
        data = {
            "email": session.get('otp_email'),
            "new_password": new_password
        }

        res = requests.put(f"{host}/v1/auth/reset_password", json=data)
        if res.status_code == 200:
            session.pop('otp_email', None)
            return redirect(url_for('login'))
    return render_template("fp_password_reset.html")


@app.route('/delete_property')
@token_required
def delete_property():
    pass


@app.route('/delete_user')
@token_required
def delete_user():
    pass


@app.route('/logout')
def logout():
    # Clear all session data (user metadata like id, name, etc.)
    session.clear()

    # Optionally, remove the access_token from cookies as well
    resp = make_response(redirect('/login'))
    resp.set_cookie('access_token', '', expires=0)  # Clear the JWT token from cookies
    
    return resp

if __name__ == "__main__":
    app.run(debug=True)