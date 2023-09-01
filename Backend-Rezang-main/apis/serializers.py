from rest_framework import serializers
from .models import *


# phone number and otp serializers


class PhoneNumberSerializer(serializers.Serializer):
    phone_number = serializers.CharField()


class OtpVerificationSerializer(serializers.Serializer):
    otp = serializers.CharField()


# Questionaires serializers


class OptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Option
        fields = ('text', 'option_id')

class QuestionSerializer(serializers.ModelSerializer):
    options = OptionSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = ('id', 'text', 'options')

class UserResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserResponse
        fields = '__all__'


# skin analysis serializers 


class SkinAnalyzerSerializer(serializers.Serializer):
    image = serializers.ImageField()


# image serializers


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ('base64_data',)