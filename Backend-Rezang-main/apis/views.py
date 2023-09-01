from django.conf import settings
from .serializers import *
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.parsers import MultiPartParser, FormParser
from twilio.rest import Client
from .models import *
import random
import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import base64


# Phone number and otp view


stored_otp_dict = {}


class SendOtpView(APIView):
    def post(self, request):
        serializer = PhoneNumberSerializer(data=request.data)
        if serializer.is_valid():
            phone_number = serializer.validated_data['phone_number']
            otp = str(random.randint(1000, 9999))

            print(otp)

            stored_otp_dict[phone_number] = otp
            client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
            message = client.messages.create(
                body=f"Your OTP is: {otp}",
                from_=settings.TWILIO_PHONE_NUMBER,
                to=phone_number
            )
            return Response({'message': 'OTP sent successfully'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VerifyOtpView(APIView):
    def post(self, request):
        entered_otp = request.data.get('otp')
        phone_number = request.data.get('phone_number')
        stored_otp = stored_otp_dict.get(phone_number)
        if stored_otp and entered_otp == stored_otp:
            return Response({'message': 'OTP verified successfully'}, status=status.HTTP_200_OK)
        else:
            return Response({'message': 'Invalid OTP'}, status=status.HTTP_400_BAD_REQUEST)


# Questionaire view


class QuestionList(APIView):
    def get(self, request):
        questions = Question.objects.all()
        serializer = QuestionSerializer(questions, many=True)
        return Response(serializer.data)

    def post(self, request):
        data = request.data
        
        for question_data in data:
            question_text = question_data['text']
            options_data = question_data.get('options', [])
            
            question = Question.objects.create(text=question_text)
            
            for option_id, option_text in enumerate(options_data, start=1):
                Option.objects.create(question=question, text=option_text, option_id=option_id)
            
        return Response(status=status.HTTP_201_CREATED)

class UserResponseView(APIView):
    def post(self, request):
        data = request.data
        
        for response_data in data:
            question_id = response_data['question']
            selected_option_id = response_data.get('selected_option', None)
            
            question = Question.objects.get(pk=question_id)
            selected_option = Option.objects.get(question=question, option_id=selected_option_id) if selected_option_id else None
            
            UserResponse.objects.create(question=question, selected_option=selected_option)
            
        return Response(status=status.HTTP_201_CREATED)


# Skin api view


@csrf_exempt
def analyze_image(request):
    if request.method == 'POST' and 'image' in request.FILES:
        image_file = request.FILES['image']
        # url = "https://skin-analyze.p.rapidapi.com/facebody/analysis/skinanalyze"
        # headers = {
        #     "X-RapidAPI-Key": "5b653917cdmshc1fa1a8fe967a1fp141b72jsn1ee1e89a9294",
        #     "X-RapidAPI-Host": "skin-analyze.p.rapidapi.com"
        # }
        files = {'image': (image_file.name, image_file.read(), 'image/jpeg')}

        response = requests.post(url, files=files, headers=headers)
        api_response = response.json()

        keys_to_include = ["acne", "dark_circle", "blackhead", "skin_type"]

        filtered_response = {key: api_response["result"].get(key, {}) for key in keys_to_include}

        for key, data in filtered_response.items():
            value = data.get("value", None)
            confidence = data.get("confidence", None)

            if value == 1:
                data["value"] = "True"
            else:
                data["value"] = "False"

            if confidence is not None:
                data["confidence"] = f"{int(confidence * 100)}%"

        skin_type_value = filtered_response.get("skin_type", {}).get("skin_type")
        skin_type_label = {
            0: "Oily skin",
            1: "Dry skin",
            2: "Neutral skin",
            3: "Combination skin"
        }
        
        skin_type_confidence = filtered_response.get("skin_type", {}).get("details", [])[skin_type_value].get("confidence", None)

        if skin_type_value in skin_type_label and skin_type_confidence is not None:
            filtered_response["skin_type"] = {
                "Confidence": f"{int(skin_type_confidence * 100)}%",
                "value": skin_type_label[skin_type_value]
            }

        return JsonResponse(filtered_response)
    
    return JsonResponse({"error": "Invalid request"})


# image view


@api_view(['POST'])
def image(request):
    if request.method == 'POST':

        image_files = request.FILES.getlist('images')

        if not image_files:
            return Response({"error": "No images provided."}, status=status.HTTP_400_BAD_REQUEST)

        saved_images = []

        for image_file in image_files:
            base64_data = base64.b64encode(image_file.read()).decode('utf-8')
            image = Image(base64_data=base64_data)
            image.save()
            saved_images.append({"id": image.id})

        return Response({"message": "Images uploaded successfully.", "saved_images": saved_images}, status=status.HTTP_201_CREATED)
