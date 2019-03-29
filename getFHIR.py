#create methods for FHIR
from fhirclient import client
import fhirclient.models.patient as p
import fhirclient.models.condition as c
import fhirclient.models.observation as obs
import pandas as pd
import plotly
import plotly.graph_objs as go
from datetime import datetime
from fhirclient import client
import fhirclient.models.patient as p
import fhirclient.models.condition as c

#A dictionary used to initialize the FHIRClient settings and specify the FHIR server you want to query.

def getPatient():
    '''
    This method shows how to use the fhirclient's Patient model to get FHIR data from a server.
    This example returns the ID, name, and birth year for all females over 45 years old.
    '''
    settings = {
        'app_id': 'python_FHIR_app',
        'api_base': 'https://api-v8-stu3.hspconsortium.org/Diabetes/open/'
    }
    server = client.FHIRClient(settings=settings).server

    #Query to FHIR server for all female patients
    search = p.Patient.where(struct={'gender': 'female'})
    results = search.perform_resources(server)
    count = 0
    data = ''
    #For each female Patient resource returned, extract the birth year to determine age
    for r in results:
        try:
            birthyear = int(r.as_json()['birthDate'].split('-')[0])
            print(birthyear)
            if birthyear > 2001:
                data += r.as_json()['id'] + '\n' + \
                         r.as_json()['name'][0]['given'][0] + ' ' + r.as_json()['name'][0]['family'] + '\n' + \
                         'Born: ' + r.as_json()['birthDate'] + '\n\n'
                count += 1
        except:
            continue
    #Return this information to app.py to include in the HTML rendering
    return 'ID, name, and birth year for each female less than 18 years old in the ' + settings['api_base'] + \
           ' FHIR server.\n\nTotal: ' + str(count) + '\n\n' + data

def getCondition():
    '''
    This method shows how to use both the fhirclient Condition and Patient models to get FHIR data from a server.
    This example returns the ID and name of each patient with hypertension.
    '''
    settings = {
        'app_id': 'python_FHIR_app',
        'api_base': 'https://api-v8-stu3.hspconsortium.org/Diabetes/open/'
    }
    server = client.FHIRClient(settings=settings).server

    #Query the FHIR server for all hypertension conditions using the SMOMED code for hypertension
    search = c.Condition.where(struct={'code': '46635009'})
    results = search.perform_resources(server)
    count = 0
    patients = []
    data = ''
    #For each hypertension Condition resource returned, extract the corresponsing patient ID from the 'subject' field.
    for r in results:
        p_id = r.as_json()['subject']['reference'].split('/')[1]
        if p_id not in patients:
            patients.append(p_id)
    #For each extracted patient ID, query for FHIR server for that Patient resource to extract their name.
    for p_id in patients:
        search = p.Patient.where(struct={'_id': p_id})
        results = search.perform_resources(server)
        for r in results:
            try:
                data += r.as_json()['id'] + '\n' + \
                      r.as_json()['name'][0]['given'][0] + ' ' + r.as_json()['name'][0]['family'] +'\n'+ 'Born: ' + r.as_json()['birthDate'] +  '\n\n'
                count += 1
            except:
                continue
    #Return this information to app.py to include in the HTML rendering
    return 'ID and name of each patient with diabetes in the ' + settings['api_base'] + \
           ' FHIR server.\n\nTotal: ' + str(count) + '\n\n' + data

def serverconnect(api_base):
    '''This method creates the connection to the server'''
    settings = {
        'app_id': 'python_FHIR_app',
        'api_base': api_base
    }
    server = client.FHIRClient(settings=settings).server
    return server

def allobsforpat(patid,loinc,server):
    '''
    This method pulls all the observations for a given patient for a given loinc code.
    It requires a string patientID and loinc as inputs.
    returns a pandas dataframe
    '''
    patient_id = 'Patient/'+patid
    loinc = loinc
    search = obs.Observation.where(struct={'subject': patient_id, 'code': loinc})
    fhir_obs = search.perform_resources(server)
    #create lists from all observations of dates and values
    listdates =[]
    for date in fhir_obs:
        listdates.append(date.as_json()["effectiveDateTime"])
    listvals = []
    for val in fhir_obs:
        listvals.append(val.as_json()["valueQuantity"]['value'])
    #first make dictionary
    d = {'Obs_Rsrc_Values':listvals,'Dates':listdates}
    #make pandas df from dictionary
    d = pd.DataFrame(d)
    d = d.sort_values('Dates',ascending=True)
    return d

    #example of pulling all the observations for a single patient into a pandas df
    patid = 'SMART-1134281'
    loinc = '2339-0'
    api_base = 'https://api-v8-stu3.hspconsortium.org/Diabetes/open/'
    server = serverconnect(api_base)
    df = allobsforpat(patid,loinc,server)
    print(df)

    return 'ID and name of each patient with diabetes in the ' + settings['api_base'] + \
           ' FHIR server.\n\nTotal: ' + str(count) + '\n\n' + data