# Loan Management System

Loan management system is used to register user and store the information about user. This system also provides api for :
1. user to apply for loan if the user satisfies certain conditions
2. user to make EMI payments for the loan 
3. user to get current statement of pending transaction and past transactions

## Data Sources 

The system has the following sources of data:

1.  A CSV file with three columns (id, aadhar_id, date, transaction type, amount)
    
**_NOTE:_**  Data files cannot be pushed due to lfs issue 
     
         #### Files structure 
         
         ```
            data/
            
              ├── transaction.csv
            ```

## System Requirements 


* The system should store the CSVs into a relevant
database and make API calls to get the data.

## Installation 

To install the required packages, run the following command in the project directory:
```
    pipenv shell
    pip install -r requirements.txt

```

To install rabbitmq management docker server
```
    docker run -d --hostname my-rabbit --name loan-manager rabbitmq:3-management

```

To install postgresql docker

```

    docker run -p 5431:5432 -e POSTGRES_PASSWORD=mysecretpassword -v /postgresql/data:/var/lib/postgresql/data -d postgres:15

```

## Usage

Start postgres docker container in interactive mode

```

    docker exec -it <container-id> bash

```

Create database and User in the container terminal
```

    psql -U postgres
    CREATE DATABASE bright_db
    CREATE USER bright_user WITH PASSWORD 'bright_password'
    ALTER USER bright_user WITH SUPERUSER
    GRANT ALL PRIVILEGES ON DATABASE bright_db TO 'bright_user'

```

Start rabbitmq:management server if container not running 

```

    docker ps -a
    docker run <container ID>

```

Start Celery worker in a new terminal
```

    cd path/to/project_directory
    pipenv shell
    C_FORCE_ROOT=1 celery -A config worker -l info --purge -Q register_user -P solo  -n config-1 

```

Make migrations in the Database

```

    python manage.py makemigrations 
    python manage.py migrate

```

To start the server, run the following command in the project directory:
```

    python manage.py runserver
    
```

The server will start running on http://localhost:8000

Note: Remember to add url prefix in the api like http://localhost:8000/api

## API Documentation

- ### api/register-user/

    This endpoint triggers the celery task to register user data provided (stored in the database).

    * Request
    ```
    POST /api/register HTTP/1.1

    ```
    * Response
    ```
        HTTP/1.1 200 OK
    Content-Type: application/json

    {
        'message': 'Success', 
        'error_code':201,
        "user_id": "unique user slug"
    }

    ```

- ### api/apply-loan/

    This endpoint returns the status of the report or the CSV.
    
    * Request
    ```
    POST /api/apply-loan HTTP/1.1

    {
       unique_user_id: Unique User Identifier (UUID)        
       loan_type: Loan type as supported above
       loan_amount: Amount of Loan in rupees
       interest_rate: Rate of interest in percentage
       term_period: time period of repayment in months
       disbursement_date: Date of disbursal
    }

    ```
    * Response
    ```
        HTTP/1.1 200 OK
        Content-Type: text/csv

        [

             Error: None if success. Error string in case ingestion was not successful stating apt reason.
             Loan_id: Unique identifier to identify the loan initiated.
             Due_dates: List containing objects of EMI dates and amount. Each object contains:
             Date: EMI date
             Amount_due: Amount due on that date
        
        ]


    ```
- ### api/make-payment/

    This endpoint returns the status of the report or the CSV.
    
    * Request
    ```
    POST /api/get_report HTTP/1.1

    {
        Loan_id: Unique identifier to identify the loan
        Amount (depends upon User)
    }

    ```
    * Response
    ```
        HTTP/1.1 200 OK
        Content-Type: text/csv

        [

            Error: None if no error. Error String in case of failure
        
        ]


    ```
- ### api/get-statement/<loan-id>/

    This endpoint returns the status of the report or the CSV.
    
    * Request
    ```
    GET /api/get-statement/<loan-id>/ HTTP/1.1

    ```
    * Response
    ```
        HTTP/1.1 200 OK
        Content-Type: text/csv

        [

            past_transaction: [
                {
                    - Date
                    - Principal
                    - Interest
                    - Amount_paid
                }
            ],
            next_transaction : [
                {
                    - Date: EMI date
                    - Amount_due: Amount due on that dat
                }
            ]
        
        ]


    ```

## Functionalities 

Used advance python features like -
 - atomic transactions
 - RabbitMQ queue for registering user
 - Celery worker for consuming task and updating db
 - Caching
