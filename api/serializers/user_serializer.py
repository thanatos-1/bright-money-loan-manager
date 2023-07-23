from rest_framework import serializers

class RegisterUserSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=255, allow_blank=False, allow_null=False)
    aadhar_id = serializers.CharField(max_length=255, allow_blank=False, allow_null=False)
    email = serializers.EmailField(max_length=255, allow_blank=False, allow_null=False)
    annual_income = serializers.IntegerField(required=True, allow_null=False)