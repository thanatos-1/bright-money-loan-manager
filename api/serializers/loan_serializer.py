from rest_framework import serializers
from api.models.loan_model import LoanModel, LoanTransaction as Transaction
from api.constants import LoanType

class LoanSerializer(serializers.Serializer):
    user_id = serializers.CharField(max_length=255, allow_blank=False, allow_null=False)
    loan_type = serializers.ChoiceField(allow_null=False, allow_blank=False, choices=LoanType.choices)
    loan_amount = serializers.IntegerField(allow_null=False)
    interest_rate = serializers.DecimalField(allow_null=False, decimal_places=2, max_digits=12)
    term_period = serializers.IntegerField(allow_null=False)
    disbursement_date = serializers.DateField(allow_null=False)
    
class LoanPaymentSerializer(serializers.Serializer):
    amount = serializers.IntegerField(allow_null=False)
    loan_id = serializers.CharField(max_length=255, allow_blank=False, allow_null=False)
    
class TransactionSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Transaction
        fields = '__all__'
        