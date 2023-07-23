from api.models import User

class UserService():
    
    def create_user(self, data:dict) -> User:
        user = User.objects.create(**data)
        return user
    
    def get_user(self, aadhar_id:str)->User:
        return User.objects.get(aadhar_id=aadhar_id)