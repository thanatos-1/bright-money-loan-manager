from django.urls import path, include
from .views import UserLoanView, UserRegisterView, UserPaymentView

urlpatterns = [
    path('register-user/', UserRegisterView.as_view()),
    path('apply-loan/', UserLoanView.as_view()),
    path('make-payment/', UserPaymentView.as_view()),
    path('get-statement/<str:loan_id>/', UserPaymentView.as_view())
]
