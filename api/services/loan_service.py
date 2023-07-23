from api.models import LoanModel as Loan, User, LoanTransaction as Transaction
from api.constants import LoanType, LoanLimit
from rest_framework.exceptions import ValidationError
from datetime import date
from dateutil import relativedelta

from django.db import DatabaseError, IntegrityError, transaction

class LoanService():
    
    def __next_due_date(self) -> date:
        return date.today() + relativedelta.relativedelta(months=1, day=1)
    
    def __calculate_remaining_principal_remaining(self, tenure_completed:int, tenure:int, loan_amount:int)->int:
        return (loan_amount - (loan_amount/tenure)*tenure_completed)
    
    def __calculate_emi(self, loan_amount:int, interest_rate:int, tenure:int)->tuple:
        """_summary_

        Args:
            loan_data (dict): _description_

        Returns:
            int: _description_
        """
        
        monthly_interest = interest_rate/12/100
        emi = loan_amount*interest_rate*(pow(1+monthly_interest, tenure))/(pow(1+monthly_interest,tenure)-1)
        principal_due_monthly = loan_amount/tenure
        total_due = emi*tenure
        total_interest = total_due-loan_amount
        
        return emi,total_due,total_interest,principal_due_monthly
        
    
    def __validate_loan_request(self, loan_amount:int, loan_type:str, interest_rate:int, tenure, user:User)->bool:
        
        user_annual_salary = user.annual_income
        user_monthly_salary = user_annual_salary/12
        emi, total_due,total_interest, principal_due_monthly = self.__calculate_emi(loan_amount, interest_rate, tenure)
        
        if LoanLimit[loan_type] < loan_amount :
            return False
        elif interest_rate < 14:
            return False
        elif emi > (60 * user_monthly_salary)/100:
            return False
        elif user_annual_salary < 150000:
            return False
        elif total_interest <= 10000:
            return False         
        
        return True
    
    def __list_future_transactions(self, loan:Loan)->list:
        transactions = []
        
        next_date = loan.next_payment_date
        remaining_tenure = loan.term_period - loan.total_emi
        
        for i in range(remaining_tenure):
            emi_date = next_date + relativedelta.relativedelta(months=i, day=1)
            amount_due = loan.current_emi
            
            transactions.append({"emi_date":emi_date, "amount_due":amount_due})
        
        return transactions
    
    def get_loan(self, loan_id:str) -> Loan:
        return Loan.objects.get(slug=loan_id)
    
    @transaction.atomic
    def create_loan(self, loan_data:dict) -> Loan:
        try:
            user_slug = loan_data.get('user_id')
            user = User.objects.get(slug=user_slug)
            loan_amount = loan_data.get('loan_amount')
            loan_type = loan_data.get('loan_type')
            interest_rate = loan_data.get('interest_rate')
            tenure = loan_data.get('term_period')
            
            if self.__validate_loan_request(loan_amount, loan_type, interest_rate, tenure, user):
                loan = Loan.objects.create(**loan_data)
                emi, total_due,total_interest, principal_due_monthly = self.__calculate_emi(loan_amount, interest_rate, tenure)
                loan.next_payment_date = self.__next_due_date()
                loan.current_emi = emi
                loan.current_due = total_due
                loan.principal_due_monthly = principal_due_monthly
                loan.current_paid= 0
                loan.save()
            else :
                raise ValidationError("Invalid request to apply to loan")
            
            return loan
        except (DatabaseError, IntegrityError) as e:
            transaction.rollback()
            raise Exception("Cannot process loan")
            
    
    @transaction.atomic
    def pay_loan(self, loan_data:dict) -> None:
        try:
            loan_slug = loan_data.get("loan_id")
            amount = loan_data.get("amount")
            
            loan = Loan.objects.get(slug=loan_slug)
            due_date = loan.next_payment_date()
            loan.current_paid += amount
            loan.last_payment_date = date.today()
            loan.next_payment_date = self.__next_due_date()
            remaining_tenure = loan.term_period - loan.total_emi
            
            if amount == loan.current_emi:
                loan.current_due -= amount
                interest = loan.current_emi - loan.principal_due_monthly
            else:
                loan_amount = self.__calculate_remaining_principal_remaining(loan.loan_amount, loan.term_period, remaining_tenure)
                emi, total_due,total_interest, principal_due_monthly = self.__calculate_emi(loan_amount, loan.interest_rate, remaining_tenure)
                
                loan.current_emi = emi
                loan.principal_due_monthly = principal_due_monthly
                loan.current_due = total_due - amount
                interest = emi - principal_due_monthly
                
            remaining_tenure-=1
            loan_transaction = Transaction.objects.create(due_date=due_date, date_paid=date.today(), principal=loan.principal_due_monthly*remaining_tenure, interest=interest, amount_paid=amount, loan=loan)  
            loan.total_emi += 1  
            loan.save()
            return loan
        except (DatabaseError, IntegrityError) as e:
            transaction.rollback()
            raise Exception("cannot make payment")
    
    def get_statement(self, loan:Loan) -> tuple:
        loan_amount = loan.loan_amount
        past_transaction = Transaction.objects.filter(loan=loan)
        next_transaction = self.__list_future_transactions(loan)
        
        return past_transaction,next_transaction
        
        