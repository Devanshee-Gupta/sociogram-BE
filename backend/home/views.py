import pwd
from django.utils import timezone
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.contrib.sessions.models import Session
from .serializers import CommentSerializer, PostSerializer, UsersSerializer
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

@csrf_exempt
@api_view(['Post'])
def getallposts(request):
    session_key=request.data["session_key"]

    if(not validation(session_key)):
        response={
                "success": False,
                "message": "Please login"
            }
        return Response(response,status=401)

    posts = Post.objects.all().order_by("-create_time","-post_id")
    postSerializer = PostSerializer(posts, many=True)
    
    list=[]
    for i in postSerializer.data:
        this_post=Post.objects.get(post_id=i["post_id"])
        post_user=Users.objects.get(user_id=i["user"])
        comments=Comment.objects.filter(post=this_post)[:3]
        commentSerializer = CommentSerializer(comments, many=True)
        comments_list=[]
        for j in commentSerializer.data:
            comment_user=Users.objects.get(user_id=j["commented_user"])
            j["comment_username"]=comment_user.user_name
            comments_list.append(j)
        
        i["comments"]=comments_list
        i["post_username"]=post_user.user_name
        list.append(i)

    response={
        "Data": list,
    }
    return Response(response, status=200)

@csrf_exempt
@api_view(['Post'])
def addnewpost(request):
    session_key=request.data["session_key"]

    # Extract individual fields from FormData
    caption = request.data.get("formData[caption]")
    tags = request.data.get("formData[tags]")
    image = request.FILES.get("formData[image]")
    if(not validation(session_key)):
        response={
                "success": False,
                "message": "Please login"
            }
        return Response(response,status=401)
    
    session = Session.objects.get(session_key=session_key)
    session_data = session.get_decoded()
    email=session_data['email']
    user=Users.objects.filter(email=email)[0]

    user_id=user.user_id

    if not image:
        return Response({"error": "Image file is required."}, status=400)

    data={
        "caption": caption,
        "tags":tags,
        "image":image,
        "user":user_id
    }

    postSerializer = PostSerializer(data=data)

    if postSerializer.is_valid():
        postSerializer.save()
        return Response({"message":"Post uploaded successfully"},status=201)
    else:
        return Response({"error":postSerializer.errors},status=400)

@csrf_exempt
@api_view(['Post'])
def ownprofile(request):
    session_key=request.data["session_key"]
    session = Session.objects.get(session_key=session_key)
    session_data = session.get_decoded()
    email=session_data['email']

    if(not validation(session_key)):
        response={
                "success": False,
                "message": "Please login"
            }
        return Response(response,status=401)
    
    user=Users.objects.filter(email=email)[0]
    
    usersSerializer = UsersSerializer(user)

    posts = Post.objects.filter(user=user).order_by("-create_time","-post_id")
    postSerializer = PostSerializer(posts, many=True)

    list=[]
    for i in postSerializer.data:
        this_post=Post.objects.get(post_id=i["post_id"])
        comments=Comment.objects.filter(post=this_post)[:3]
        commentSerializer = CommentSerializer(comments, many=True)
        comments_list=[]
        for j in commentSerializer.data:
            comment_user=Users.objects.get(user_id=j["commented_user"])
            j["comment_username"]=comment_user.user_name
            comments_list.append(j)
        
        i["comments"]=comments_list
        i["post_username"]=user.user_name
        list.append(i)

    response={
        "Data": {
            "profile_data" : usersSerializer.data,
            "posts_data" : list,
        }
    }
    return Response(response, status=200)


@csrf_exempt
@api_view(['POST'])
def editprofile(request):
    session_key=request.data["session_key"]
    session = Session.objects.get(session_key=session_key)
    session_data = session.get_decoded()
    email=session_data['email']

    if(not validation(session_key)):
        response={
                "success": False,
                "message": "Please login"
            }
        return Response(response,status=401)
    
    user=Users.objects.filter(email=email)[0]

    # Extract individual fields
    name = request.data["formData"]["name"]
    bio = request.data["formData"]["bio"]
    user.name = name
    user.bio = bio
    user.save()
    return Response({"message":"Profile updated successfully"}, status=200)

@csrf_exempt
@api_view(['POST'])
def changepassword(request):
    session_key=request.data["session_key"]
    session = Session.objects.get(session_key=session_key)
    session_data = session.get_decoded()
    email=session_data['email']

    if(not validation(session_key)):
        response={
                "success": False,
                "message": "Please login"
            }
        return Response(response,status=401)
    
    user=Users.objects.filter(email=email)[0]

     # Extract individual fields
    password = request.data["formData"]["password"]
    confirm_password = request.data["formData"]["confirm_password"]

    if not password.startswith(('pbkdf2_sha256$', 'bcrypt$', 'argon2$')):
        hash_pwd = make_password(password)
        user.password = hash_pwd
    else:
        user.password = password
    user.save()
    return Response({"message":"Password updated successfully"}, status=200)

@csrf_exempt
@api_view(['POST'])
def othersprofile(request,userid):
    session_key=request.data["session_key"]
    session = Session.objects.get(session_key=session_key)
    session_data = session.get_decoded()
    email=session_data['email']

    if(not validation(session_key)):
        response={
                "success": False,
                "message": "Please login"
            }
        return Response(response,status=401)
    
    user=Users.objects.filter(user_id=userid)[0]
    usersSerializer = UsersSerializer(user)

    posts = Post.objects.filter(user=user).order_by("-create_time","-post_id")
    postSerializer = PostSerializer(posts, many=True)

    list=[]
    for i in postSerializer.data:
        this_post=Post.objects.get(post_id=i["post_id"])
        comments=Comment.objects.filter(post=this_post)[:3]
        commentSerializer = CommentSerializer(comments, many=True)
        comments_list=[]
        for j in commentSerializer.data:
            comment_user=Users.objects.get(user_id=j["commented_user"])
            j["comment_username"]=comment_user.user_name
            comments_list.append(j)
        
        i["comments"]=comments_list
        i["post_username"]=user.user_name
        list.append(i)

    response={
        "Data": {
            "profile_data" : usersSerializer.data,
            "posts_data" : list,
        }
    }
    return Response(response, status=200)


@csrf_exempt
@api_view(['POST'])
def logout(request):
    
    session=Session.objects.get(session_key=request.data["session_key"])
    response={
        "success": True,
        "message": "Session Deleted succesfully!"
    }
    if session is None:
        response['success']=False,
        response['error']='User not found!'
        return Response(response,status.HTTP_404_NOT_FOUND)
    session.delete()
    return Response(response,status.HTTP_204_NO_CONTENT)