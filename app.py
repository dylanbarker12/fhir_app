from flask import Flask, render_template, flash, request, redirect
from wtforms import Form, TextField, TextAreaField, validators, StringField, SubmitField
import getFHIR
import fhir_resources

# App config
DEBUG = True
app = Flask(__name__)
app.all_details = [] #creating an empty array that the function will populate.
app.observations = {'glucose': [], 'carbs': [], 'insulin': [], 'exercise': []}
app.datetime = ['2018-06-22 10:55:36', '2018-06-22 10:55:36', '2018-06-22 10:55:36', '2018-06-22 10:55:36', '2018-06-22 10:55:36', '2018-06-22 10:55:36']
app.username = ""
app.config.from_object(__name__)
app.config['SECRET_KEY'] = '7d441f27d441f27567d441f2b6176a'

'''
The app route parameter specifies when each function in app.py will be called. Since this is our initial function we
want called, we will designate it to run when users navigate to the base url of our app. In this example the base 
will be http://0.0.0.0:8080/ but you could specify other routes such as http://0.0.0.0:8080/details or 
http://0.0.0.0:8080/list to launch additional views for your app with each function rendering different templates.
'''
@app.route('/')
def launch():
    '''
    Launches our initial view by rendering dashboard.html and calling each method from our imported getFHIR.py file.
    The return from each method will populate the dynamic variables designated by double curly braces in the HTML.
    '''
    return render_template('index.html',
                           patient_example=getFHIR.getPatient(),
                           condition_example=getFHIR.getCondition(),
                           obs_example=getFHIR.allobsforpat())

@app.route('/dashboard', methods=['GET', 'POST'])
def dash():
    if request.method == 'POST':
    # fetch the input given by the user and use those values to query
        glucose = int(request.form['glucose'])
        carbs = int(request.form['carbs'])
        insulin = int(request.form['insulin'])
        exercise = int(request.form['exercise'])
        note = str(request.form['note'])
        patient = {'glucose_': glucose, 'carbs_': carbs, 'insulin_': insulin, 'exercise_': exercise}
        app.all_details, app.observations = fhir_resources.append_details(patient, app.all_details, app.observations, app.datetime) # all info that is to be displayed in the table
        app.all_details = sorted(app.all_details, key=lambda k: k['date'])

        fhir_resources.store_data(patient)
        return render_template('dashboard.html', patient_details=app.all_details, patient=patient, observations=app.observations, username=app.username, datetime=app.datetime)
    return render_template('dashboard.html')

@app.route('/input', methods=['GET', 'POST'])
def input():
    app.all_details = []
    app.datetime = []
    app.observations = {'glucose': [], 'carbs': [], 'insulin': [], 'exercise': []}
    app.all_details = fhir_resources.fetch_all_details(app.all_details, app.observations, app.datetime) # this function should return an array of dictionary. This happens on submit from the input file.
    return render_template('input.html', username = app.username)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        app.username = request.form['username']
        return redirect('/input')
    return render_template('login.html', username = app.username)

@app.route('/calculator', methods=['GET', 'POST'])
def calc():
    error = None
    if request.method == 'POST':
        carbs = int(request.form['carbo'])
        cho = int(request.form['cho_ratio'])
        actual = int(request.form['actul_blood_sugar'])
        target = int(request.form['target_blood_sugar'])
        result = int((carbs/cho) + ((actual-target)/50))
        result = str(result)
        flash('***You should take '+result+' Units of Insulin!***')
        return redirect('/input')
    return render_template('calculator.html')


#Allows you to run this file with the command 'python app.py' and launch the Flask server on the designated host and port.
if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=8080)