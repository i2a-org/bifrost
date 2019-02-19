
# Bifrost

## What is IsItAlzheimers.org?

IsItAlzheimers.org (I2A) is where caregivers and at risk people will go to see if they may have a treatable dementia or really have Alzheimer's Disease. We will have an augmented intelligence system (code has been in development for 3 years) powering the backend. Tools include a polypharmacy engine, anticholinergenic engine, essential nutrient engine and others. There will also be a community forum.

## What is Bifrost?

To be able to evaluate patient data, IsItAlzheimers.org is required to collect anonymous health data. To do so, we have created an extendable open source API. Bifrost is designed to guide patients through the process of completing all the information that is required for up-to-date health reports. The system then processes the information and allows the frontend to display results to the patient.

All of the services that are provided through Bifrost are based on publicly available research papers. Bifrost is an implementation to bring all this research together in one simple and useful hub. We believe that by making this information public, we can assist patients and caretakers who are overwhelmed by the challenges of dementia.

## Use

To run bifrost locally:

 1) Run `./startup`: starts DynamoDBLocal (https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/DynamoDBLocal.html) and dynamodb-admin (https://github.com/aaronshaf/dynamodb-admin) to make local development easier -> compatible alternatives can be used as well
 2) Run `./runlocal`: starts bifrost (requires a local dynamodb resource to be run)

## Endpoints

### GET "/v0/search/variable"

Defined in: ./api/endpoints/search/Search_Variable.py

Description: Searches the system for matching variables.

Parameters:
- `s` : search for matching variable by keyword
- `id` : search for matching variable by ID

Errors:
- "Could not find any variables." : no matching variables were found

Result: list, contains all the matching variables

### GET "/search/report"

Defined in: ./api/endpoints/search/Search_Report.py

Description: Searches for matching reports.

Parameters:
- `s` : search for matching reports by keyword

Errors:
- "Could not find any reports." : no matching reports were found

Result: list, contains all the matching reports

### POST "/patient/create"

Defined in: ./api/endpoints/patient/Patient_Create.py

Description: Creates a new user in the system.

Parameters:
- `hash` : the password hash to be used for future user login

Errors:
- "This is not correct." : `hash` parameters not given
- "Could not create patient." : patient could not be created at the moment

Result: string, unique `patient_id`

### POST "/patient/login"

Defined in: ./api/endpoints/patient/Patient_Login.py

Description: Creates a new session for given user. This call checks if the user is registered for an I2A account (spam prevention).

Parameters:
- `hash` : the password hash to be used for future user login
- `patient_id` : the patient ID that was returned during the patient creation

Errors:
- "This is not correct." :  : `hash` or `patient_id` parameters not given
- "Credentials not correct." : patient could not be found based on given `patient_id`
- "Credentials not correct." : `hash` does not match the patient
- "Could not create session." : session could not be created at the moment

Result: string, unique `session_id`

### GET "/patient/variable"

Defined in: ./api/endpoints/patient/Patient_Variable.py

Description: Return patient's variable data, based on given identifier.

Parameters:
- `id` : unique `variable_id` (can be obtained from variable search endpoint)

Errors:
- "Parameter 'id' required." : `variable_id` parameter not given
- "Variable '[...]' is not a valid variable." : the given `variable_id` could not be found
- "Patient has no submitted variable '[...]'." : no value for this variable was submitted

Result: dict

`{ "values": [ {"value": [value], "timestamp": [time_submitted]}, ... ], "data_type": [data_type] }`

### POST "/patient/variable"

Defined in: ./api/endpoints/patient/Patient_Variable.py

Description: Add a new value to a patient's variable data.

Parameters:
- `id` : unique `variable_id` (can be obtained from variable search endpoint)
- `value` : the value to be set (data_type will be enforced by bifrost, when possible)

Errors:
- "Parameters 'id' and 'value' are required." : `variable_id` and `value` are not given
- "Variable '[...]' is not a valid variable." : `variable_id` has not been defined in systemm (suggests that `variable_id` is incorrect)
- "'[...]' can only be populated automatically." : `variable_id` can not be populated by the patient
- "'[...]' does not accept multiple values." : `variable_id` is defined to only accept a value once
- "The last submission for '[...]' is still active." : the last value set for `variable_id` has not yet expired
- "Value contained invalid data type." : unable to convert given value to defined data_type
- "Variable '[...]' could not be saved." : value could not be saved at the moment

Result: list (all the `variable_id` values that can be found in the DB)

`[ { "value": [value], "timestamp": [time_submitted] }, ... ]`

### GET "/patient/order"

Defined in: ./api/endpoints/patient/Patient_Order.py

Description: Get information on orderable, and previously ordered reports.

Paramters:
- `todos` : include the reports that a patient can complete, based on bifrost's condition system

Result: dict

`{ "queue": queue, "reports": reports, "todo": todos }`

### POST "/patient/order"

Defined in: ./api/endpoints/patient/Patient_Order.py

Description: Create a new order for a report.

Parameters:
- `id` : the `report_id` to be ordered

Errors:
- "Parameter 'id' required." : the `id` parameter not given
- "Report '[...]' is not valid." : the given `report_id` could not be found
- "Report is already being processed." : the given `report_id` is already in the queue
- "A report is already being processed." : there is already a report in the queue
- "Additional variables required." : some variables require (re-)submission (details are given in the result's `missing` field)
- "Could not add report to queue." : order could not be saved at the moment

Result: string, the unique `queue_id`

### GET "/patient/report"

Defined in: ./api/endpoints/patient/Patient_Report.py

Description: Get all the patient's report information.

Parameters:
- `id` : the `report_id` to be returned

Errors:
- "Parameter 'id' required." : the `id` parameter not given
- "Report '[...]' is not valid." : the given `report_id` could not be found

Result: dict

`{
    "report_id": [...], 
    "name": [...], 
    "description": [...], 
    "refresh": [false OR rate],
    "order": [false OR position of report],
    "values": [ {'mmse_language_praxis_writing': [1.0, 'numeric'], 'mmse_attention_calculation': [1.0, 'numeric'], }, ... ]
}`

### POST "/processing/queue" *DEPRECATED*

Defined in: ./api/endpoints/processing/Processing_Queue.py

Description: Process all elements in queue. This call will be moved to a patient specific call, or a new system will be created for processing queues.

## Database

[prefix] = "dev", "staging", or "production"

### [prefix].org.i2a.actions *DEPRECATED*

Possibly removed in future versions.

### [prefix].org.i2a.logs

Description: Contains system logs, based on requests and library defined output.

Fields: timestamp (numeric), name (string), log (string), status (string)

### [prefix].org.i2a.patients

Description: Contains all patient information.

Fields: patient_id (string), reports (dict), variables (dict), hash (string), queue (dict)

Example:
`{
  "reports": { "report_id": 1549814804, ... },
  "variables": { "variable_id": [ { "value": 5, "timestamp": 1549814302 }, ... ], ... },
  "hash": "[...]",
  "queue": { "report_id": "queue_id" },
  "patient_id": "[...]"
}`

### [prefix].org.i2a.queue

### [prefix].org.i2a.reports

### [prefix].org.i2a.rules

### [prefix].org.i2a.sessions

### [prefix].org.i2a.variables

