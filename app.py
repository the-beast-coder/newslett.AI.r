from flask import Flask, render_template, request
from firebase_admin import db
import firebase_admin

cred_obj = firebase_admin.credentials.Certificate('C:/Users/aadij/Downloads/')
default_app = firebase_admin.initialize_app(cred_obj, {
	'databaseURL':"https://newslaiter-default-rtdb.firebaseio.com/"
	})


# Create a Flask app instance
app = Flask(__name__)

# Define the home route
people_ref = db.reference("people")
@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        # Get the email and interests from the form data
        email = request.form['email'].replace(".", ",")
        interests = request.form.getlist('interests')

        people_ref.child(email).set(interests)

    return render_template('home.html')

if __name__ == '__main__':
    app.run(port=3324, debug=True)