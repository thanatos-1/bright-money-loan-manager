import logging

from django.core.exceptions import ValidationError
from django.db import IntegrityError
from rest_framework import status
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.views import APIView
from api.serializers import RegisterUserSerializer, LoanSerializer, LoanPaymentSerializer, TransactionSerializer
from api.services import LoanService, UserService
from django.core.exceptions import ObjectDoesNotExist
from django.db import DatabaseError, IntegrityError, transaction

from utils.queue_task import send_task_to_queue

class UserRegisterView(APIView):
    """_summary_

    Args:
        APIView (_type_): _description_
        
        
    """
    def post(self, request:Request) -> Response:
        
        try:
            user_service = UserService()
            register_user_serializer = RegisterUserSerializer(data=request.data)
            if register_user_serializer.is_valid(raise_exception=True):
                print("e2")
                data = register_user_serializer.validated_data
                print("e5", data, request.data)
                user = user_service.create_user(data)
                user.refresh_from_db()
                
            send_task_to_queue(user.aadhar_id)
            
            return Response({
                "status": "success",
                "user_id": user.slug
            }, status=status.HTTP_201_CREATED)
            
        except IntegrityError as e:
            print(e)
            return Response({
                "status":"error",
                "message":"Caould not register user as data already exists"
            }, status=status.HTTP_409_CONFLICT)
        except ValidationError as e:
            print(e)
            return Response({
                "status":"error",
                "message":e.message
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(e)
            return Response({
                "status":"error",
                "message":"some error occurred during registration"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            
            
        
        

class UserLoanView(APIView):
    """_summary_

    Args:
        APIView (_type_): _description_
    """
    
    def post(self, request:Request) -> Response:
        try:
            loan_service = LoanService()
            loan_serializer = LoanSerializer(data=request.data)
            
            if loan_serializer.is_valid(raise_exception=True):
                data = loan_serializer.validated_data
            
            loan = loan_service.create_loan(data)
            due_dates = loan_service.get_statement(loan)
            
            return Response({
                "status": "success",
                "loan_id": loan.slug,
                "due_dates":due_dates,
            }, status=status.HTTP_201_CREATED)
        
        except ValidationError as e:
            return Response({
                "status":"error",
                "message":e.message
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(e)
            return Response({
                "status":"error",
                "message":"some error occurred during registration"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            


class UserPaymentView(APIView):
    """_summary_

    Args:
        APIView (GET): Get statement and future dues
    """
    
    
    def get(self, loan_id:str) -> Response:
        try:
            loan_service = LoanService()
            loan = loan_service.get_loan(loan_id) 
            past_transaction, next_transaction = loan_service.get_statement(loan)
            
            past_transaction_serializer = TransactionSerializer(past_transaction, many=True)
            
            
            return Response({
                "status":"success",
                "past_transactions":past_transaction_serializer.data,
                "next_transaction":next_transaction
            }, status= status.HTTP_200_OK)
            
        except ObjectDoesNotExist as e:
            return Response({
                "status":"error",
                "message":f"Loan with ID {loan_id} does not exist"
            }, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        except Exception as e:
            return Response({
                "status":"error",
                "message":"some error occurred during registration"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    def post(self, request:Request) -> Response:
        try:
            loan_service = LoanService()
            payment_serializer = LoanPaymentSerializer(data=request.data)
            
            if payment_serializer.is_valid(raise_exception=True):
                data = payment_serializer.validated_data
            
            loan = loan_service.pay_loan(data)
            
            transaction.commit()
            
            return Response({
                "status": "success",
                "message":f"EMI for loan {loan.slug} has been paid successfully."
            }, status=status.HTTP_200_OK)
            
        
        except ValidationError as e:
            transaction.rollback()
            return Response({
                "status":"error",
                "message":e.message
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            transaction.rollback()
            return Response({
                "status":"error",
                "message":"some error occurred during registration"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
 