# create methods for FHIR
from fhirclient import client
import fhirclient.models.patient as p
import fhirclient.models.condition as c
import fhirclient.models.observation as obs
import fhirclient.models.procedure as proc
import fhirclient.models.medicationadministration as MA
import requests, json
import pandas as pd


def serverconnect(api_base):
    '''This method creates the connection to the server'''
    settings = {
        'app_id': 'python_FHIR_app',
        'api_base': api_base
    }
    server = client.FHIRClient(settings=settings).server
    return server


def allobsforpat(patid, loinc, server):
    '''
    This method pulls all the observations for a given patient for a given loinc code.
    It requires a string patientID, loinc, and server item as inputs.
    server item is the result of the server_connect(api_base) function.
    For example: if api_base = 'https://api-v8-stu3.hspconsortium.org/Diabetes/open/', use the following server result
    as input into the allobsforpat() function
    server = serverconnect(api_base)
    allobsforpat() returns a pandas dataframe
    '''
    patient_id = 'Patient/' + patid
    loinc = loinc
    search = obs.Observation.where(struct={'patient': patient_id, 'code': loinc})
    fhir_obs = search.perform_resources(server)
    # create lists from all observations of dates and values
    listdates = []
    for date in fhir_obs:
        listdates.append(date.as_json()["effectiveDateTime"])
    listvals = []
    for val in fhir_obs:
        listvals.append(val.as_json()["valueQuantity"]['value'])
    # first make dictionary
    d = {'Obs_Rsrc_Values': listvals, 'Dates': listdates}
    # make pandas df from dictionary
    d = pd.DataFrame(d)
    d = d.sort_values('Dates', ascending=True)
    return d

#https://api-v8-stu3.hspconsortium.org/Diabetes/open/Observation?code=41653-7&patient=16952

# enter Glucometer Reading
def EnterGlucometerReading(server, patid, value, time):
    '''Push a LOINC observation to a FHIR server
    Inputs required:
    the server as a string,
    the patientid as a string,
    the value as a string,
    the time as a string,
    the loinc code as string
    the '''

    patient = 'Patient/' + patid

    #if __name__ == '__main__':
    obs = {
        "resourceType": "Observation",
        "text": {
            "status": "generated",
            "div": "<div xmlns='http://www.w3.org/1999/xhtml'><a name='mm'/></div>"
        },
        "id": "",  # The ID is auto-generated by the server if you leave it blank
        "subject": {
            "reference": patient
        },
        "status": "preliminary",
        "category": [
            {
                "coding": [
                    {
                        "code": "activity",
                        # http://terminology.hl7.org/CodeSystem/observation-category defines activity as "	Observations that measure or record any bodily activity that enhances or maintains physical fitness and overall health and wellness.
                        # Not under direct supervision of practitioner such as a physical therapist. (e.g., laps swum, steps, sleep data)"
                        "system": "http://hl7.org/fhir/obervation-category",
                        "display": "Activity"
                    }
                ]
            }
        ],
        "code": {
            "coding": [
                {
                    "code": "41653-7",  # Glucose [Mass/volume] in Capillary blood by Glucometer
                    "system": "http://loinc.org",
                    "display": "Glucose Glucometer (BldC) [Mass/Vol]"
                }
            ]
        },
        "effectiveDateTime": time,
        "valueQuantity": {
            "value": value,
            "unit": "mg/dL"
        },
        "method": {
            "coding": [
                {
                    "code": "166900001",
                    "system": "http://snomed.info/sct",
                    "display": "Glucometer blood glucose"
                }
            ]
        }
    }
    obs = json.dumps(obs, indent=4)

    r = requests.post(server + 'Observation', data=obs)
    if r.status_code != 201:
        print(r.status_code)
        print(obs)


# enter Carbohydrate Tracker
def EnterCarbohydrates(server, patid, value, time):
    '''Push a LOINC observation to a FHIR server
    Inputs required:
    the server as a string,
    the patientid as a string,
    the value as a string,
    the time as a string,
     '''
    import requests, json
    patient = 'Patient/' + patid
    # print("**************************** in enter carbs")
    #if __name__ == '__main__':

    obs = {
        "resourceType": "Observation",
        "text": {
            "status": "generated",
            "div": "<div xmlns='http://www.w3.org/1999/xhtml'><a name='mm'/></div>"
        },
        "id": "",
        "subject": {
            "reference": patient
        },
        "status": "final",
        "code": {
            "coding": [
                {
                    "code": "LP72222-0",
                    "system": "http://loinc.org",
                    "display": "Carbohydrate intake"
                }
            ]
        },
        "performer": [
            {
                "reference": patient
            }
        ],
        "effectiveDateTime": time,
        "valueQuantity": {
            "value": value,
            "unit": "gr"
        },
    }
    obs = json.dumps(obs, indent=4)

    r = requests.post(server + 'Observation', data=obs)
    # print("*******************************************", r.status_code)
    if r.status_code != 201:
        print(r.status_code)
        print(obs)


# enter Exercise Tracker
def EnterExercise(server, patid, ExerciseText, time):
    '''Push a LOINC observation to a FHIR server
    Inputs required:
    the server as a string,
    the patientid as a string,
    the value as a string,
    the time as a string,
    the loinc code as string
    the '''
    patient = 'Patient/' + patid

    #if __name__ == '__main__':

    obs = {
        "resourceType": "Procedure",
        "id": "",
        "text": {
            "status": "generated",
            "div": "<div xmlns='http://www.w3.org/1999/xhtml'><a name='mm'/></div>"
        },
        "status": "completed",
        "code": {
            "coding": [
                {
                    "system": "http://snomed.info/sct",
                    "code": "183302000",
                    "display": "Active exercise"
                }
            ]
        },
        "subject": {
            "reference": patient
        },
        "performedDateTime": time,
        # "performedPeriod"{'start':time, #future changes would be to include period performed
        #                  'end':time2}, #by adding a duration input and adding the duration
        # to the time input to create a time2 var
        "performer": [{  # The people/person who performed the procedure
            "actor": {
                "reference": patient
            }
        }],
        "note": [
            {
                "text": ExerciseText  # ex - 'Ran for 30 minutes'
            }
        ]
    }

    obs = json.dumps(obs, indent=4)

    r = requests.post(server + 'Procedure', data=obs)
    if r.status_code != 201:
        print(r.status_code)
        print(obs)


def allprocsforpat(patid, snomed, server):
    '''
    This method pulls all the procedures for a given patient for a given snomed code.
    It requires a string patientID, snomed, and server item as inputs.
    server item is the result of the server_connect(api_base) function.
    For example: if api_base = 'https://api-v8-stu3.hspconsortium.org/Diabetes/open/', use the following server result
    as input into the allprocsforpat() function
    server = serverconnect(api_base)

    allprocsforpat() returns a pandas dataframe
    '''
    patient_id = 'Patient/' + patid
    search = proc.Procedure.where(struct={'subject': patient_id, 'code': snomed})
    fhir_obs = search.perform_resources(server)
    # create lists from all observations of dates and values
    listdates = []
    for date in fhir_obs:
        listdates.append(date.as_json()["performedDateTime"])
    listvals = []
    for val in fhir_obs:
        for a in val.as_json()["note"]:
            listvals.append(a['text'])
    # duration should be added in a future iteration
    # duration = []
    # for time in fhir_obs:
    #    duration.append(time.as_json()["performedPeriod"])
    # first make dictionary
    d = {'Proc_Rsrc_Values': listvals, 'Dates': listdates
         # , 'Duration':duration
         }
    # make pandas df from dictionary
    d = pd.DataFrame(d)
    d = d.sort_values('Dates', ascending=True)
    return d


# enter Insulin Data
# at some point this also needs to incorporate the type of Insulin
def EnterInsulin_Lantus100u_ml(server, patid, value, time):
    '''Push a LOINC observation to a FHIR server
    Inputs required:
    the server as a string,
    the patientid as a string,
    the value as a string,
    the time as a string,
    the loinc code as string
    the '''
    patient = 'Patient/' + patid

    #if __name__ == '__main__':

    obs = {
        "resourceType": "MedicationAdministration",
        "id": "",
        "text": {
            "status": "generated",
            "div": "<div xmlns='http://www.w3.org/1999/xhtml'>insulin<a name='mm'/></div>"
        },
        "status": "completed",
        "medicationCodeableConcept": {
            "coding": [
                {
                    "system": "http://www.nlm.nih.gov/research/umls/rxnorm",
                    "code": "285018",
                    "display": "Lantus 100 unit/ml injectable solution"
                }
            ]
        },
        "subject": {
            "reference": patient
        },
        "effectiveDateTime": time,
        "performer": [
            {  # The people/person who performed the procedure
                "actor": {
                    "reference": patient
                }
            }],
        "dosage": {
            "route": {
                "coding": [
                    {
                        "system": "http://snomed.info/sct",
                        "code": "263887005",
                        "display": "Subcutaneous (qualifier value)"
                    }
                ]
            },
            "dose": {
                "value": value,
                "unit": "U",
                "system": "http://unitsofmeasure.org",
                "code": "U"
            }
        }
    }

    obs = json.dumps(obs, indent=4)

    r = requests.post(server + 'MedicationAdministration', data=obs)
    if r.status_code != 201:
        print(r.status_code)
        print(obs)


# reading insulin

def allMAsforpat(patid, rxnorm, server):
    '''
    This method pulls all the procedures for a given patient for a given snomed code.
    It requires a string patientID, snomed, and server item as inputs.
    server item is the result of the server_connect(api_base) function.
    For example: if api_base = 'https://api-v8-stu3.hspconsortium.org/Diabetes/open/', use the following server result
    as input into the allprocsforpat() function
    server = serverconnect(api_base)

    allprocsforpat() returns a pandas dataframe
    '''
    #print("*** in function***")
    patient_id = 'Patient/' + patid
    search = MA.MedicationAdministration.where(struct={'subject': patient_id, 'code': rxnorm})
    fhir_obs = search.perform_resources(server)
    # create lists from all observations of dates and values
    listdates = []
    for date in fhir_obs:
        listdates.append(date.as_json()["effectiveDateTime"])
    listvals = []
    for val in fhir_obs:
        listvals.append(val.as_json()["dosage"]['dose']['value'])
    Medlist = []
    for i in fhir_obs:
        for a in i.as_json()["medicationCodeableConcept"]['coding']:
            Medlist.append(a['code'])
    # first make dictionary
    d = {'MA_Rsrc_Values': Medlist, 'Dates': listdates, 'Dose': listvals}
    # make pandas df from dictionary
    d = pd.DataFrame(d)
    d = d.sort_values('Dates', ascending=True)
    print("*** in function***")
    return d

#**************************************
# Patient ID: Patient/cf-1553130119529

# def store_and_fetch_data(patient):
#     patient = store_data(patient)
#     patient_1 = fetch_data()
#     return patient

def fetch_data(all_details):
    api_base = 'https://api-v8-stu3.hspconsortium.org/Diabetes/open/'
    server = serverconnect(api_base)
    loinc_g = "41653-7"  # glucose by glucometer
    loinc_c = "LP72222-0" # carbohydrate
    snomed = "183302000" # exercise
    rxnorm = "285018" #insulin
    patid = 'cf-1553130119529'
    df_g = allobsforpat(patid, loinc_g, server)
    df_c = allobsforpat(patid, loinc_c, server)
    df_e = allprocsforpat(patid, snomed, server)
    df_i = allMAsforpat(patid, rxnorm, server)
    add_glucose_to_table(df_g, all_details)
    add_carbs_to_table(df_c, all_details)
    add_exercise_to_table(df_e, all_details)
    add_insulin_to_table(df_i, all_details)

    #print(df_g.to_string())
    # print(df_c.to_string())
    # print(df_e.to_string())
    # print(df_i.to_string())

def add_glucose_to_table(df_g, all_details):
    # for row in df_g:
    #     print(row)
    #      print((df_g.loc[[0]]).loc[: , "Dates"])
    for row in df_g.head().itertuples():
        #print(index, len(df_g))
        # for row in df_g.head().itertuples():
        details = {'date': row.Dates,
               'data_type': 'glucose',
               'value': row.Obs_Rsrc_Values}
        all_details.append(details)
        # date = (df_g.loc[[index]]).loc[: , "Dates"]
        # print((df_g.loc[[index]]).loc[: , "Dates"])
        # print((df_g.loc[[index]]).loc[:, "Obs_Rsrc_Values"])

def add_carbs_to_table(df_c, all_details):
    for row in df_c.head().itertuples():
        details = {'date': row.Dates,
               'data_type': 'carbs',
               'value': row.Obs_Rsrc_Values}
        all_details.append(details)

def add_exercise_to_table(df_e, all_details):
    for row in df_e.head().itertuples():
        details = {'date': row.Dates,
               'data_type': 'exercise',
               'value': row.Proc_Rsrc_Values}
        all_details.append(details)

def add_insulin_to_table(df_i, all_details):
    for row in df_i.head().itertuples():
        details = {'date': row.Dates,
               'data_type': 'insulin',
               'value': row.Dose}
        all_details.append(details)

def store_data(patient):
    # write a function to store the data of the new record
    patid = '16952'
    server = 'https://api-v8-stu3.hspconsortium.org/Diabetes/open/'
    loinc = 'LP72222-0'
    # write a function to fetch all the details
    EnterCarbohydrates(server, patid, patient['carbs_'], "2019-04-01T21:14:10+01:00")
    EnterGlucometerReading(server, patid, patient['glucose_'], "2019-04-03T17:47:10+01:00")
    EnterExercise(server, patid, patient['exercise_'], "2019-04-01T21:14:10+01:00")
    EnterInsulin_Lantus100u_ml(server, patid, patient['insulin_'], "2019-04-01T21:14:10+01:00")
    return patient

def fetch_all_details(all_details):
    '''
       This currently is just hard-coded. Don't we need to add the input variable into each 'value' section?
    '''

    # details = {'date': '126464', 'data_type': 'carbs', 'value': 100}
    # details_2 = {'date': '123123', 'data_type': 'carbs', 'value': 1234}
    # details_3 = {'date': '123123', 'data_type': 'carbs', 'value': 1034}
    # details_4 = {'date': '123123', 'data_type': 'carbs', 'value': 1067}
    # all_details.append(details)
    # all_details.append(details_2)
    # all_details.append(details_3)
    # all_details.append(details_4)
    fetch_data(all_details)
    return all_details


def append_details(patient, all_details):
    '''
       This currently is just hard-coded. We will change to access the correct data based on where the values. This would be something like df_g[date] to get the date value.
    '''
    #print("*****************",patient)
    details_dict = {'date': '1324', 'data_type': 'glucose', 'value': patient['glucose_']}
    all_details.append(details_dict)
    details_dict = {'date': '1324', 'data_type': 'carbs', 'value':  patient['carbs_']}
    all_details.append(details_dict)
    details_dict = {'date': '1324', 'data_type': 'insulin', 'value': patient['insulin_']}
    all_details.append(details_dict)
    details_dict = {'date': '1324', 'data_type': 'exercise', 'value': patient['exercise_']}
    all_details.append(details_dict)
    return all_details