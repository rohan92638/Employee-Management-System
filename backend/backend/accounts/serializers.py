from rest_framework import serializers
from .models import User

class RegisterSerializer(serializers.ModelSerializer):
    confirm_password= serializers.CharField(write_only=True)
    
    class Meta:
        model= User
        fields = ['full_name', 'email', 'mobile', 'password', 'confirm_password']
        extra_kwargs = {'password': {'write_only': True}}
        
    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError("Passwords do not match.")
        return data
    
    def create(self, validated_data):
        validated_data.pop('confirm_password')  # remove confirm_password
        user = User.objects.create_user(**validated_data)
        return user