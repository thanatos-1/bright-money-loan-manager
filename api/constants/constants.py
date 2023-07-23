import uuid

from django.db import models


class LoanType(models.TextChoices):
    CAR = "CAR"
    HOME = "HOME"
    EDUCATIIONAL = "EDUCATIATIONAL"
    PERSONAL = "PERSONAL"
    
class LoanLimit(models.IntegerChoices):
    CAR = 750000
    HOME = 8500000
    EDUCATIIONAL = 5000000
    PERSONAL = 1000000
    
class TransactionType(models.TextChoices):
    DEBIT = "DEBIT"
    CREDIT = "CREDIT"