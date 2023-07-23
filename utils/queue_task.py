from kombu import Connection
from django.conf import settings
from api.models import LoanModel as Loan

def send_task_to_queue(aadhar_id:str) -> None:
    message = {
        "id": aadhar_id,
        "task":"api.tasks.register_user",
        "kwargs":{
            "aadhar_id": aadhar_id
        }
    }
    
    with Connection(settings.BROKER_URL) as connection:
        queue = connection.SimpleQueue("register_user")
        queue.put(message, serializer="json")