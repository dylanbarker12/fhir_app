from flask import Flask, render_template, flash, request, redirect
from wtforms import Form, TextField, TextAreaField, validators, StringField, SubmitField
import getFHIR
import fhir_resources

# App config
DEBUG = True
app = Flask(__name__)
app.all_details = [] #creating an empty array that the function will populate.
app.observations = {'glucose': [], 'carbs': [], 'insulin': [], 'exercise':[]}
# app.glucose_details = []
# app.carb_details = []
# app.insulin_details = []
# app.exercise_details = []
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
        patient = {'glucose_': glucose, 'carbs_': carbs, 'insulin_': insulin, 'exercise_': exercise}
        # app.observations['glucose'].append(glucose)
        # app.observations['carbs'].append(carbs)
        # app.observations['insulin'].append(insulin)
        # app.observations['exercise'].append(exercise)
        app.all_details, app.observations = fhir_resources.append_details(patient, app.all_details, app.observations) # all info that is to be displayed in the table
        #app.glucose_details =
        #app.carb_details =
        #app.insulin_details =
        #app.exercise_details =
        fhir_resources.store_data(patient)
        return render_template('dashboard.html', patient_details=app.all_details, patient=patient, observations = app.observations)
    return render_template('dashboard.html')

@app.route('/input', methods=['GET', 'POST'])
def input():
    app.all_details = []

    app.observations = {'glucose': [], 'carbs': [], 'insulin': [], 'exercise':[]}
    app.all_details = fhir_resources.fetch_all_details(app.all_details, app.observations) # this function should return an array of dictionary. This happens on submit from the input file.
    return render_template('input.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        return redirect('/input')
    return render_template('login.html')

@app.route('/calculator', methods=['GET', 'POST'])
def calc():
    error = None
    if request.method == 'POST':
        flash('You should take 8 Units of Insulin!')
        return redirect('/input')
    return render_template('calculator.html')


#Allows you to run this file with the command 'python app.py' and launch the Flask server on the designated host and port.
if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=8080)