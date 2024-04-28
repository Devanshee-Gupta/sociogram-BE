from django.utils import timezone
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.contrib.sessions.models import Session
from .serializers import UsersSerializer
from .models import *
from django.contrib.auth.hashers import check_password
# from db_connection import user_collection
# Create your views here.

def validation(data):
    session_key=data
    if session_key=="":
        return False
    queryset=Session.objects.filter(session_key=session_key)
    if len(queryset)>0:
        temp=queryset[0]
        if queryset[0].expire_date<timezone.now():
            return False
        if temp.session_key==session_key:
            return True 
    return False

@csrf_exempt
@api_view(['POST'])
def signup(request):
    data = request.data
    serializer = UsersSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        return Response({"message":"User created successfully"},status=201)
    else:
        return Response({"error":serializer.errors},status=400)
    
@csrf_exempt
@api_view(['POST'])
def signin(request):
    response={}
    if request.data['email']=='':
        response['success']=False
        response['error']='Email Id required'
        return Response(response,status.HTTP_400_BAD_REQUEST)
    
    if request.data['password']=='':
        response['success']=False
        response['error']='Password required'
        return Response(response,status.HTTP_400_BAD_REQUEST)
    
    email=request.data['email']
    password=request.data['password']
    user=Users.objects.filter(email=email).first()
    if not user:
        response={
        "success": False,
        "error": "User does not exist",
        }
        return Response(response,status.HTTP_401_UNAUTHORIZED)
    
    if email == user.email and check_password(password, user.password):
        request.session['email'] = email
        request.session.create()
        session_key = request.session.session_key

        response={
            "success": True,
            "message": "User successfully authenticated",
            "session_key":session_key,
        }


        if(not SavedCollection.objects.filter(user=user)):
            SavedCollection.objects.create(user=user)

        return Response(response,status=200)
    
    else:
        response={
            "success": False,
            "error": "Invalid credentials",
        }
    return Response(response,status=401)


@api_view(['POST'])
def authenticate(request):
    session_key=request.data["session_key"]
    if(not validation(session_key)):
        response={
                "success": False,
                "error": "Please login"
            }
        return Response(response,status=401)
    response={
        "success":True,
    }
    return Response(response,status=200)



