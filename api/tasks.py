from celery import shared_task
import time
import json
from api.models import User
from api.constants import TransactionType
import pandas as pd
import os
import functools

def calculate_credit_score(amount:int)->int:
    credit = max(300,min(900,300 + 10*(amount//15000)))
    return credit

@functools.lru_cache(maxsize=1, typed=False)
@shared_task(max_retries=10, default_retry_delay=10)
def register_user(aadhar_id:str)->None:
    """shared task consumig queue and generating report

    Args:
        report_id (_type_): _description_
    """
    
    #  Create new report object and add it to the database
    
    try:
        user = User.objects.get(aadhar_id=aadhar_id)
        transaction_df = pd.read_csv('data/transaction.csv')
        user_df = transaction_df.loc[transaction_df["user"] == user.aadhar_id]
        total_amount = 0
        
        for transaction in user_df.iterrows():
            transaction_type = transaction[1]["transaction_type"]
            amount = transaction[1]["amount"]
            
            if transaction_type == TransactionType.DEBIT:
                total_amount -= amount
            elif transaction_type == TransactionType.CREDIT:
                total_amount += amount
            else:
                raise ValueError("unknown transaction type: %s" % transaction_type)
            
        
        user.total_balance = total_amount
        user.credit_score = calculate_credit_score(total_amount)
        print("total amount", total_amount)
        user.save()
        
    except ValueError as e:
        print("unprocessable transaction")                
        
    except Exception as e:
        print(str(e))
 
    
    
    