from flask import *
import pymongo
from flask_mail import *
import random
from flask_socketio import *
import os
from werkzeug.utils import secure_filename
import numpy as np  # linear algebra
import pandas as pd  # data processing, CSV file I/O (e.. pd.read_csv)
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from datetime import timedelta


app = Flask(__name__)
UPLOAD_FOLDER = 'static/uploads/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
ALLOWED_EXTENSIONS = {'mp4'}

global randam_otp

randam_otp = random.randrange(10000, 100000)
app.permanent_session_lifetime = timedelta(minutes=5)

connection = pymongo.MongoClient('localhost', 27017)
database = connection['users']
app.config['SECRET_KEY'] = "Your_secret_string"
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'duaacare786@gmail.com'
app.config['MAIL_PASSWORD'] = 'iqswptjoxkrslrgj'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)
socket = SocketIO(app)


@app.route('/')
def get_user():
    return render_template("main_page.html")


@app.route('/first')
def first():
    return render_template("register.html")


@app.route('/second')
def second():
    return render_template("main_page.html")


@app.route('/forget')
def forget():
    return render_template("forget.html")


@app.route('/hello')
def hello():
    return render_template("otp.html")


@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        # mobileno = request.form['mobileno']
        connection = pymongo.MongoClient('localhost', 27017)
        database = connection['users']
        # collection = database['mycol_o1']
        collection = database[email]
        existing_email = collection.find_one({'email': request.form['email']})
        if existing_email is None:
            data = {'email': email, 'password': password}
            collection.insert_one(data)
            # when the email and username is not exist then it's will insert the value and it redirect to hello.html
            flash("Register successfully!")
            return redirect(url_for('second'))
        flash("email id is already exists!please choose the another email id...")
        return redirect(url_for('first'))


@app.route('/login', methods=['POST'])
def login():
    global email
    connection = pymongo.MongoClient('localhost', 27017)
    password = request.form['user']
    email = request.form['email']
    database = connection['users']
    # collection = database['mycol_o1']
    collection = database[email]
    session['email'] = email
    session.permanent = True
    user_login = collection.find_one({'password': password})
    email_login = collection.find_one({'email': email})
    fullname = collection.find_one({'email': email})
    print(fullname)
    finder = collection.find_one({'last_update': '0'}, {"last_update": 1, "_id": False})
    finder = str(finder)
    print(finder)
    finder1 = "{'last_update': '0'}"
    if user_login:
        if email_login and user_login == email_login:
            if (finder != finder1):
                return render_template("profile.html")
            else:
                return render_template("home.html", user=fullname)
    flash("Invalid username or password!")
    return redirect(url_for('second'))


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('second'))


@app.route('/account', methods=['POST', 'GET'])
def account():
    connection = pymongo.MongoClient('localhost', 27017)
    database = connection['users']
    collection = database[email]
    if request.method == 'POST':
        first_name = request.form['name']
        last_name = request.form['name1']
        full_name = first_name
        brday = request.form['bdate']
        pho = request.form['pho']
        # print(typeew)
        country = request.form['country']
        # address = request.form['address']
        city = request.form['city']
        state = request.form['state']
        # pincode = request.form['code']
        data = {'Name': full_name, 'birthday': brday, 'pho': pho, 'country': country,
                'city': city,
                'state': state, 'last_update': '0'}
        collection.update_one({'email': session['email']}, {"$set": data})
        full_name = collection.find_one({'email': email})
        return render_template("home.html", user=full_name)


@app.route('/forgetpassword', methods=['POST', 'GET'])
def forgot():
    global forgot_email
    forgot_email = request.form['email']
    connection = pymongo.MongoClient('localhost', 27017)
    database = connection['users']
    # collection = database['mycol_o1']
    collection = database[forgot_email]
    database_email = collection.find_one({'email': forgot_email})
    if database_email:
        msg = Message('otp', sender='dummyforh@gmail.com', recipients=[forgot_email])
        msg.body = str("otp verfication \n " + str(randam_otp))
        mail.send(msg)
        return render_template('otp.html')
    else:
        flash("email is not valid!!!")
        return redirect(url_for('forget'))


@app.route('/otp', methods=['POST', 'GET'])
def otp():
    email_otp1 = request.form['otp1']
    email_otp2 = request.form['otp2']
    email_otp3 = request.form['otp3']
    email_otp4 = request.form['otp4']
    email_otp5 = request.form['otp5']
    email_otp = email_otp1 + email_otp2 + email_otp3 + email_otp4 + email_otp5
    if email_otp == str(randam_otp):
        return render_template('new_password.html')
    else:
        flash("Wrong otp")
        return redirect(url_for('hello'))


@app.route('/newpwd', methods=['POST', 'GET'])
def newpssd():
    newpss = request.form['password']
    connection = pymongo.MongoClient('localhost', 27017)
    database = connection['users']
    # collection = database['mycol_o1']
    collection = database[forgot_email]
    existing_email = collection.find_one({'email': forgot_email})
    if existing_email:
        # update the new password
        collection.update_one({'email': forgot_email}, {"$set": {'password': newpss}})
        flash(" New password is updated")
        return redirect(url_for('second'))
    else:
        flash(" Some error is occured please try again!")
        return redirect(url_for('newpwd'))


@app.route('/admin1')
def admin1():
    return render_template("admin_login.html")


@app.route('/first_admin', methods=['POST', 'GET'])
# @login_required
def first_admin():
    if request.method == 'POST':
        collection = database['admin']
        admin_email = request.form['email']
        admin_password = request.form["password"]
        admin_table = collection.find_one({'password': admin_password})
        admin1_table = collection.find_one({'email': admin_email})
        if admin_table:
            if admin1_table:
                return redirect('/admin')

        else:
            flash("Invalid admin login")
            return redirect(url_for('admin1'))

# @app.route('/panel')
# def panel():
#     return render_template('info.html')

@app.route('/admin')
def admin():
    x1 = database.list_collection_names()
    x2 = len(x1)
    x2 = x2 - 1
    print(x2)
    print(x1)
    return render_template('admin.html', x1=x1, x2=x2)

@app.route('/fifth')
def fifth():
    collection = database['young talents']
    cusor = collection.find({}, {"_id": 0, "email": 1, "Name": 1, "date": 1, "time": 1, "message": 1,"type":1 , "year":1})
    x = list(cusor)
    # cursor2=collection.find({})
    # #print(cursor2)
    # y=list(cursor2)
    # uu=collection.count_documents({})
    # print(uu)
    return render_template('info.html',x=x)

@app.route('/admin_user')
def admin_user():
    return render_template("admin_demo.html")


@app.route('/insert', methods=['POST'])
def insert():
    global email
    database = connection['users']
    email = request.form["email"]
    collection = database[email]
    password = request.form["password"]
    print(email, password)
    data = {"email": email, "password": password}
    collection.insert_one(data)
    return redirect('/admin')


@app.route('/update', methods=['POST'])
def update():
    database = connection['users']
    email = request.form["email"]
    collection = database[email]
    email = request.form["email"]
    password = request.form["password"]
    Name = request.form["Name"]
    # address = request.form["address"]
    birthday = request.form["birthday"]
    pho = request.form["pho"]
    city = request.form["city"]
    country = request.form["country"]
    last_update = request.form["last_update"]
    # pincode = request.form["pincode"]
    state = request.form["state"]
    print(email, password, Name, birthday, pho, city, country)
    existing_email = collection.find_one({'email': email})
    if existing_email:
        collection.update_one({'email': email}, {
            "$set": {"email": email, "password": password, "Name": Name, "birthday": birthday,
                     "pho": pho, "city": city, "country": country, "last_update": last_update, "state": state}})

        return redirect('/admin')
    else:
        return "no email is found"


@app.route('/delete', methods=['POST'])
def delete():
    database = connection['users']
    email = request.form["email"]
    collection = database[email]
    existing_email = collection.find_one({'email': email})
    if existing_email:
        myquery = {"email": email}
        collection.delete_one(myquery)
        return redirect('/admin')
    else:
        return "no email is found"


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/upload_form')
def upload_form():
    return render_template("index.html")


@app.route('/fileup', methods=['POST'])
def upload_video():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        flash('No video selected for uploading')
        return redirect(request.url)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        # print('upload_image filename: ' + filename)
        flash('Image successfully uploaded and displayed below')
        return render_template("index.html", filename=filename)
    else:
        flash('Only Mp4 extension')
        return redirect(request.url)


@app.route('/display/<filename>')
def display_video(filename):
    # print('display_video filename: ' + filename)
    return redirect(url_for('static', filename='uploads/' + filename), code=301)


movie_data = pd.read_csv('data/movies.csv')

movie_data = movie_data.drop_duplicates()

movie_data.movie_title = movie_data.movie_title.str.lower().str.strip()
movie_data['index'] = movie_data.index

movie_data.genres = movie_data['genres'].str.split('|').fillna('').apply(lambda x: ' '.join(x))
movie_data.plot_keywords = movie_data['plot_keywords'].str.split('|').fillna('').apply(lambda x: ' '.join(x))
movie_data = movie_data.fillna('')
features = ['director_name', 'actor_2_name', 'actor_1_name', 'genres', 'actor_3_name', 'language', 'country',
            'content_rating',
            'imdb_score', 'plot_keywords']


def combine_features(row):
    return row['director_name'] + " " + row['actor_2_name'] + " " + row["actor_1_name"] + " " + row["genres"] + " " + \
           row["actor_3_name"] + " " + row["language"] + " " + row['country'] + " " + row['content_rating'] + " " + str(
        row['imdb_score']) + " " + row['plot_keywords']


movie_data["combined_features"] = movie_data.apply(combine_features, axis=1)
cv = CountVectorizer()
count_matrix = cv.fit_transform(movie_data["combined_features"])

cosine_sim = cosine_similarity(count_matrix)


def get_title_from_index(df, index):
    return df[df.index == index]["movie_title"].values[0]


def get_index_from_title(df, title):
    return df[df.movie_title == title]["index"].values[0]


def get_plot_from_index(df, index):
    return df[df.index == index]["plot"].values[0]


def recommend(movie_user_likes):
    try:
        movie_user_likes = movie_user_likes.lower()
        movie_index = get_index_from_title(movie_data, movie_user_likes)
        similar_movies = list(enumerate(cosine_sim[movie_index]))
        sorted_similar_movies = sorted(similar_movies, key=lambda x: x[1], reverse=True)[1:]
        i = 0
        print("Top 5 similar shows like " + movie_user_likes + " are:\n")
        recommended_movies = []

        for element in sorted_similar_movies:

            recommended_movies.append(
                [get_title_from_index(movie_data, element[0]), get_plot_from_index(movie_data, element[0])])
            i = i + 1
            if i >= 5:
                break
        return recommended_movies
    except:
        # return('Movie not found . Please retry!')
        return None


@app.route('/home')
def home():
    return render_template('rec.html')


@app.route('/predict', methods=['POST'])
def predict():
    if request.method == 'POST':
        input_movie = request.form.get('movie')
    movies = recommend(input_movie)
    if movies is not None:
        return render_template('output.html', movies=movies, input_movie=input_movie.title())
    else:
        return render_template('error.html')


@app.route('/fourth')
def fourth():
    return render_template('young.html')

#
# @app.route('/young', methods=['POST', 'GET'])
# def young():
#     global email
#     database = connection['users']
#     collection = database['young talents']
#     email = request.form["email"]
#     print(email)
#     data = {"email": email}
#     collection.insert_one(data)
#     return redirect('/fourth')


@app.route('/talents', methods=['POST'])
def talents():
    database = connection['users']
    collection = database['young talents']
    email = request.form["email"]
    Name = request.form["Name"]
    date = request.form["date"]
    time = request.form["time"]
    message = request.form["message"]
    type = request.form["type"]
    year = request.form["year"]
    print(email, Name, date, time, message,type , year)
    data = {"email": email, "Name": Name, "date": date, "time": time, "message": message,
             "type": type, "year": year}
    collection.insert_one(data)
    flash('Your Message is added successfully')
    return redirect('/second')


# @app.route('/talents', methods=['POST' , 'GET'])
# def talents():
#     global email
#     connection = pymongo.MongoClient('localhost', 27017)
#     database = connection['users']
#     collection = database['young talents']
#
#     collection1 = collection[email]
#     session['email'] = email
#     if request.method == 'POST':
#         first_name = request.form['name']
#         last_name = request.form['name1']
#         full_name = first_name
#         brday = request.form['bdate']
#         pho = request.form['pho']
#         # print(typeew)
#         country = request.form['country']
#         # address = request.form['address']
#         city = request.form['city']
#         state = request.form['state']
#         # pincode = request.form['code']
#         data = {'Name': full_name, 'birthday': brday, 'pho': pho, 'country': country,
#                 'city': city,
#                 'state': state, 'last_update': '0'}
#         collection1.update_one({'young talents': session['email']}, {"$set": data})
#         return render_template("main_page.html")

# import stripe
# This is your test secret API key.
# stripe.api_key = 'sk_test_51KbuzuSDtTtSYB2Snr0PR0Lv26xsm3F9bolShSxuf2UtjKMOrlhFtu7YjOs6ss17adg2Dym0N2SJ3qtrgyYra33F00fqtMkJfA'
#
#
# YOUR_DOMAIN = 'http://localhost:5000'
#
# @app.route('/payment')
# def get_index():
#     return render_template('checkout.html')
#
#
# @app.route('/create-checkout-session', methods=['POST'])
# def create_checkout_session():
#     try:
#         prices = stripe.Price.list(
#             lookup_keys=[request.form['lookup_key']],
#             expand=['data.product']
#         )
#
#         checkout_session = stripe.checkout.Session.create(
#             line_items=[
#                 {
#                     'price': 'price_1L0SuWSDtTtSYB2SZ3syUvTh',
#                     'quantity': 1,
#                 },
#             ],
#             mode='subscription',
#             # success_url=YOUR_DOMAIN +
#             # '/success.html?session_id={CHECKOUT_SESSION_ID}',
#             # cancel_url=YOUR_DOMAIN + '/cancel.html',
#
#         )
#         return redirect(checkout_session.url, code=303)
#     except Exception as e:
#         print(e)
#         return "Server error", 500
#
# @app.route('/create-portal-session', methods=['POST'])
# def customer_portal():
#     # For demonstration purposes, we're using the Checkout session to retrieve the customer ID.
#     # Typically this is stored alongside the authenticated user in your database.
#     checkout_session_id = request.form.get('session_id')
#     checkout_session = stripe.checkout.Session.retrieve(checkout_session_id)
#
#     # This is the URL to which the customer will be redirected after they are
#     # done managing their billing with the portal.
#     return_url = YOUR_DOMAIN
#
#     portalSession = stripe.billing_portal.Session.create(
#         customer=checkout_session.customer,
#         return_url=return_url,
#     )
#     return redirect(portalSession.url, code=303)
#
# @app.route('/webhook', methods=['POST'])
# def webhook_received():
#     # Replace this endpoint secret with your endpoint's unique secret
#     # If you are testing with the CLI, find the secret by running 'stripe listen'
#     # If you are using an endpoint defined with the API or dashboard, look in your webhook settings
#     # at https://dashboard.stripe.com/webhooks
#     webhook_secret = 'whsec_12345'
#     request_data = json.loads(request.data)
#
#     if webhook_secret:
#         # Retrieve the event by verifying the signature using the raw body and secret if webhook signing is configured.
#         signature = request.headers.get('stripe-signature')
#         try:
#             event = stripe.Webhook.construct_event(
#                 payload=request.data, sig_header=signature, secret=webhook_secret)
#             data = event['data']
#         except Exception as e:
#             return e
#         # Get the type of webhook event sent - used to check the status of PaymentIntents.
#         event_type = event['type']
#     else:
#         data = request_data['data']
#         event_type = request_data['type']
#     data_object = data['object']
#
#     print('event ' + event_type)
#
#     if event_type == 'checkout.session.completed':
#         print('🔔 Payment succeeded!')
#     elif event_type == 'customer.subscription.trial_will_end':
#         print('Subscription trial will end')
#     elif event_type == 'customer.subscription.created':
#         print('Subscription created %s', event.id)
#     elif event_type == 'customer.subscription.updated':
#         print('Subscription created %s', event.id)
#     elif event_type == 'customer.subscription.deleted':
#         # handle subscription canceled automatically based
#         # upon your subscription settings. Or if the user cancels it.
#         print('Subscription canceled: %s', event.id)
#
#     return jsonify({'status': 'success'})


if __name__ == '__main__':
    app.run(debug=True)
