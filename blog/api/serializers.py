from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Blog

class UserSerializer(serializers.ModelSerializer):
    confirm_password=serializers.CharField(write_only=True)
    email=serializers.EmailField(required=True)
    username=serializers.CharField(required=True)
    class Meta:
        model=User
        fields=['id','username','email','password','confirm_password'] # '__all__'
        extra_kwargs = {
            "password": {"write_only": True},
            "confirm_password": {"write_only": True},   
        }
    def validate(self,data):
        if data['password']!=data['confirm_password']:
            raise serializers.ValidationError({"password":"Passwords do not match"})
        return data
    def create(self,validation_data):
        validation_data.pop('confirm_password')
        user=User.objects.create_user(**validation_data)
        return user

class BlogSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True) 
    class Meta:
        model=Blog
        fields=['title','content','date','author']
        extra_kwargs={
            'author':{"read_only":True},
            'date':{'read_only':True}
        }
        
    def create(self, validated_data):
        validated_data['author'] = self.context['request'].user  # Set author to the logged-in user
        return super().create(validated_data)
