# Volteras API
## Description
Volteras API is a FastAPI-based project that provides an API for retrieving and manipulating electric vehicle data. This README file provides instructions on setting up and running the project, as well as information about the project architecture and endpoints.

## Setup
You will need Docker to run this application.
To set up the project locally, follow these steps:

Clone the repository to your local machine.

### Optional
If you clone the repository in your local machine, you may need to run the following command to set the PYTHONPATH environment variable:
```
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

### Docker

Build the Docker image:
```
docker build -t volteras_image .
```
Run the Docker container:

```
docker run --rm -p 8000:8000 --name volteras-container volteras_image
```

Once the Volteras API is up and running, you can access it at http://localhost:8000/. For a more user-friendly experience, you can navigate to http://localhost:8000/docs, which will provide you with an interactive API documentation interface.

(Optional) To add data to the database from CSV files, run the following command **in a new terminal**:

```
docker exec volteras-container python scripts/import_data.py
```
**The script drop the database and import the data from the CSV files**


### Tests
To run the tests, run the following command **in a new terminal**:

```
docker exec volteras-container pytest --color=yes tests/
```


# Architecture :
## Directories

- app/: Contains the main application code.
  - api/endpoints/: Contains the API endpoints.
  - api/models/: Contains the Pydantic models used in the API.
  - api/services/: Contains the services used in the API.
- core/database/: Contains the database code.
- main.py: Contains the FastAPI application object.
- data/: Contains CSV files used to populate the database.
- scripts/: Contains a Python script to populate the database with data.
-  tests/: Contains unit tests for the application.

## Files:

- Dockerfile: Defines the Docker image used to run the application.
- main.py: Contains the entry point for the application.
- README.md: Contains documentation on how to set up and run the application.
    

# Endpoints:
- GET /api/v1/vehicle_data/: 
  - Retrieves a list of vehicle data filtered by query parameters, and optionally exports the data in the specified format. The query parameters include export-format, vehicle_id, initial-timestamp, final-timestamp, sort-by, limit, and skip. The response can be either a list of VehicleModel objects or the exported data in the specified format.
- GET /api/v1/vehicle_data/{id}/:
  - Retrieves a particular vehicle data by ID. This endpoint requires the ID of the vehicle data to be passed as a parameter, and returns a single VehicleModel object.
- POST /api/v1/vehicle_data/: 
  - Adds a new vehicle data. This endpoint requires a VehicleModel object to be passed in the request body, and returns the newly created VehicleModel object.


  
Bonus: 

- There is a POST endpoint to add a vehicle model.
- To add the data from the CSV files, you must run the script named import_data.py.
- You can export the data in CSV or JSON from /api/v1/vehicle_data/ endpoint by specifying the parameter export_format in the endpoint /api/v1/vehicle_data.
- Screenshots 

## Screenshot:

The following screenshots demonstrate the functionality and output of the Volteras API:
- Endpoints
![docs](https://user-images.githubusercontent.com/7033942/223859238-ba2864e7-b5dc-4756-92ec-e96ffd0f5019.jpg)


This screenshot shows the data exported in CSV format using the /api/v1/vehicle_data endpoint with the export_format=csv query parameter.
- CSV
![CSV](https://user-images.githubusercontent.com/7033942/223859236-e0251ac5-dc76-4ce9-8097-1c880a44ca2b.jpg)

This is the output for the /api/v1/vehicle_data endpoint
![vehicle_data](https://user-images.githubusercontent.com/7033942/223859239-a3ecb56c-be13-4f34-bcf5-e61ec0eca57c.jpg)

