from django.utils import timezone
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.contrib.sessions.models import Session
from .serializers import PostSerializer, SavedCollectionSerializer, SavedItemSerializer, UsersSerializer
from .models import *
from django.contrib.auth.hashers import check_password
import re
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
@api_view(['POST'])
def getallposts(request):
    session_key=request.data["session_key"]

    if(not validation(session_key)):
        response={
                "success": False,
                "message": "Please login"
            }
        return Response(response,status=401)
    
    session = Session.objects.get(session_key=session_key)
    session_data = session.get_decoded()
    email=session_data['email']

    if(not Users.objects.filter(email=email)):
        return Response({"error":"User Does Not Exist"},status=400)

    user=Users.objects.filter(email=email)[0]
    posts = Post.objects.all().order_by("-create_time","-post_id")
    postSerializer = PostSerializer(posts, many=True)
    
    list=[]
    for i in postSerializer.data:
        this_post=Post.objects.get(post_id=i["post_id"])
        post_user=Users.objects.get(user_id=i["user"])
        i["post_username"]=post_user.user_name

        liked_post=LikedPost.objects.filter(user=user,post=this_post)
        if(liked_post):
            i['has_liked']="true"
        else:
            i['has_liked']="false"

        saved_collection=SavedCollection.objects.filter(user=user)[0]
        saved_post=SavedItem.objects.filter(saved_collection=saved_collection,post=this_post)
        if(saved_post):
            i['has_saved']="true"
        else:
            i['has_saved']="false"
        list.append(i)

    response={
        "Data": list,
    }
    return Response(response, status=200)

@csrf_exempt
@api_view(['POST'])
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

    if(not Users.objects.filter(email=email)):
        return Response({"error":"User Does Not Exist"},status=400)
    
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
        user.no_of_posts+=1
        user.save()
        return Response({"message":"Post uploaded successfully"},status=201)
    else:
        return Response({"error":postSerializer.errors},status=400)

@csrf_exempt
@api_view(['POST'])
def ownprofile(request):
    session_key=request.data["session_key"]

    if(not validation(session_key)):
        response={
                "success": False,
                "message": "Please login"
            }
        return Response(response,status=401)
    
    session = Session.objects.get(session_key=session_key)
    session_data = session.get_decoded()
    email=session_data['email']

    if(not Users.objects.filter(email=email)):
        return Response({"error":"User Does Not Exist"},status=400)
    
    user=Users.objects.filter(email=email)[0]
    
    usersSerializer = UsersSerializer(user)

    posts = Post.objects.filter(user=user).order_by("-create_time","-post_id")
    postSerializer = PostSerializer(posts, many=True)

    list=[]
    for i in postSerializer.data:
        this_post=Post.objects.get(post_id=i["post_id"])
        i["post_username"]=user.user_name

        liked_post=LikedPost.objects.filter(user=user,post=this_post)
        if(liked_post):
            i['has_liked']="true"
        else:
            i['has_liked']="false"

        saved_collection=SavedCollection.objects.filter(user=user)[0]
        saved_post=SavedItem.objects.filter(saved_collection=saved_collection,post=this_post)
        if(saved_post):
            i['has_saved']="true"
        else:
            i['has_saved']="false"

        list.append(i)

    response={
        "Data": {
            "profile_data" : usersSerializer.data,
            "posts_data" : list,
        }
    }
    return Response(response, status=200)

@csrf_exempt
@api_view(['PATCH'])
def editprofile(request):
    session_key=request.data["session_key"]
    
    if(not validation(session_key)):
        response={
                "success": False,
                "message": "Please login"
            }
        return Response(response,status=401)
    
    session = Session.objects.get(session_key=session_key)
    session_data = session.get_decoded()
    email=session_data['email']

    if(not Users.objects.filter(email=email)):
        return Response({"error":"User Does Not Exist"},status=400)
    user=Users.objects.filter(email=email)[0]

    # Extract individual fields
    if "formData" in request.data:
        formData = request.data["formData"]
    if "name" in formData:
        if(formData["name"] != "") :
            user.name = formData["name"]
    if "bio" in formData:
        if(formData["bio"] != "") :
            user.bio = formData["bio"]
    user.save()
    return Response({"message":"Profile updated successfully"}, status=201)

@csrf_exempt
@api_view(['POST'])
def changepassword(request):
    session_key=request.data["session_key"]
    
    if(not validation(session_key)):
        response={
                "success": False,
                "message": "Please login"
            }
        return Response(response,status=401)
    
    session = Session.objects.get(session_key=session_key)
    session_data = session.get_decoded()
    email=session_data['email']
    if(not Users.objects.filter(email=email)):
        return Response({"error":"User Does Not Exist"},status=400)
    user=Users.objects.filter(email=email)[0]

     # Extract individual fields

    regex = r'^(?=.*[A-Z])(?=.*[!@#$%^&*])(?=.*[0-9]).{5,}$'

    password = request.data["formData"]["password"]

    if re.match(regex, password):
        confirm_password = request.data["formData"]["confirm_password"]
        if password == confirm_password:
            if not password.startswith(('pbkdf2_sha256$', 'bcrypt$', 'argon2$')): 
                hash_pwd = make_password(password)
                user.password = hash_pwd
            else:
                user.password = password
            user.save()
            return Response({"message":"Password updated successfully"}, status=201)
        else:
            return Response({"error":"Re-entered Password is not same"}, status=400)
    else:
        return Response({"error":"Password must have minimum 5 characters, atleast 1 uppercase, 1 special character and 1 number"}, status=400)

@csrf_exempt
@api_view(['POST'])
def othersprofile(request,userid):
    session_key=request.data["session_key"]
    
    if(not validation(session_key)):
        response={
                "success": False,
                "message": "Please login"
            }
        return Response(response,status=401)
    session = Session.objects.get(session_key=session_key)
    session_data = session.get_decoded()
    email=session_data['email']

    if(not Users.objects.filter(email=email)):
        return Response({"error":"User Does Not Exist"},status=400)
    
    user=Users.objects.filter(user_id=userid)[0]
    usersSerializer = UsersSerializer(user)

    posts = Post.objects.filter(user=user).order_by("-create_time","-post_id")
    postSerializer = PostSerializer(posts, many=True)

    list=[]
    for i in postSerializer.data:
        this_post=Post.objects.get(post_id=i["post_id"])
        i["post_username"]=user.user_name

        liked_post=LikedPost.objects.filter(user=user,post=this_post)
        if(liked_post):
            i['has_liked']="true"
        else:
            i['has_liked']="false"

        saved_collection=SavedCollection.objects.filter(user=user)[0]
        saved_post=SavedItem.objects.filter(saved_collection=saved_collection,post=this_post)
        if(saved_post):
            i['has_saved']="true"
        else:
            i['has_saved']="false"
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
def addtolist(request):
    session_key=request.data["session_key"]
    post_id=request.data["post_id"]
    if(not validation(session_key)):
        response={
                "success": False,
                "error": "Please login"
            }
        return Response(response,status=401)
    session = Session.objects.get(session_key=session_key)
    session_data = session.get_decoded()
    email=session_data['email']

    if(not Users.objects.filter(email=email)):
        return Response({"error":"User Does Not Exist"},status=400)
    
    user=Users.objects.filter(email=email)[0]
    if(not Post.objects.filter(post_id=post_id)):
        return Response({"error":"Post Does Not Exist"},status=400)
    post=Post.objects.filter(post_id=post_id)[0]

    saved_collection=SavedCollection.objects.filter(user=user)[0]
    if(not SavedItem.objects.filter(saved_collection=saved_collection,post=post)):
        SavedItem.objects.create(saved_collection=saved_collection,post=post)
        saved_collection.no_of_posts+=1
        saved_collection.save()
        return Response({"message":"Post saved successfully"},status=201)
    else:
        return Response({"error":"Post is already saved"},status=400)

@csrf_exempt
@api_view(['DELETE'])
def deletefromlist(request):
    post_id=request.data["post_id"]
    session_key=request.data["session_key"]

    if(not validation(session_key)):
        response={
                "success": False,
                "error": "Please login"
            }
        return Response(response,status=401)
    
    session = Session.objects.get(session_key=session_key)
    session_data = session.get_decoded()
    email=session_data['email']

    if(not Users.objects.filter(email=email)):
        return Response({"error":"User Does Not Exist"},status=400)
    
    user=Users.objects.filter(email=email)[0]
    if(not Post.objects.filter(post_id=post_id)):
        return Response({"error":"Post Does Not Exist"},status=400)
    post=Post.objects.filter(post_id=post_id)[0]

    saved_collection=SavedCollection.objects.filter(user=user)[0]
    if(not SavedItem.objects.filter(saved_collection=saved_collection,post=post)):
        return Response({"error":"Post is already not saved"},status=400)
    else:
        SavedItem.objects.filter(saved_collection=saved_collection,post=post).delete()
        saved_collection.no_of_posts-=1
        saved_collection.save()
        return Response({"message":"Post removed successfully"},status=201)

@csrf_exempt
@api_view(['POST'])
def getlistelements(request):
    session_key=request.data["session_key"]

    if(not validation(session_key)):
        response={
                "success": False,
                "message": "Please login"
            }
        return Response(response,status=401)
    
    session = Session.objects.get(session_key=session_key)
    session_data = session.get_decoded()
    email=session_data['email']

    if(not Users.objects.filter(email=email)):
        return Response({"error":"User Does Not Exist"},status=400)
    
    user=Users.objects.filter(email=email)[0]
    saved_collection=SavedCollection.objects.filter(user=user)[0]
    alllistelement = SavedItem.objects.filter(saved_collection=saved_collection)
    itemSerializer = SavedItemSerializer(alllistelement, many=True)
    
    for i in itemSerializer.data:
        temp_post_id=i['post_id']
        temp_post=Post.objects.filter(post_id=temp_post_id)[0]
        postSerializer=PostSerializer(temp_post)
        i['post_id']=postSerializer.data

    collectionSerializer=SavedCollectionSerializer(saved_collection)
    response={
        "postData": itemSerializer.data,
        "collectionData": collectionSerializer.data,
    }
    return Response(response,status=200)   

@csrf_exempt
@api_view(['POST'])
def likepost(request):
    session_key=request.data["session_key"]
    post_id=request.data["post_id"]
    if(not validation(session_key)):
        response={
                "success": False,
                "error": "Please login"
            }
        return Response(response,status=401)
    session = Session.objects.get(session_key=session_key)
    session_data = session.get_decoded()
    email=session_data['email']

    if(not Users.objects.filter(email=email)):
        return Response({"error":"User Does Not Exist"},status=400)
    
    user=Users.objects.filter(email=email)[0]
    if(not Post.objects.filter(post_id=post_id)):
        return Response({"error":"Post Does Not Exist"},status=400)

    post=Post.objects.filter(post_id=post_id)[0]

    if(not LikedPost.objects.filter(user=user,post=post)):
        LikedPost.objects.create(user=user,post=post)
        post.no_of_likes+=1
        post.save()
        return Response({"message":"Post liked successfully"},status=201)
    else:
        return Response({"error":"Post is already liked"},status=400)

@csrf_exempt
@api_view(['DELETE'])
def unlikepost(request):
    session_key=request.data["session_key"]
    post_id=request.data["post_id"]
    if(not validation(session_key)):
        response={
                "success": False,
                "error": "Please login"
            }
        return Response(response,status=401)
    session = Session.objects.get(session_key=session_key)
    session_data = session.get_decoded()
    email=session_data['email']

    if(not Users.objects.filter(email=email)):
        return Response({"error":"User Does Not Exist"},status=400)
    
    user=Users.objects.filter(email=email)[0]
    if(not Post.objects.filter(post_id=post_id)):
        return Response({"error":"Post Does Not Exist"},status=400)

    post=Post.objects.filter(post_id=post_id)[0]

    if(not LikedPost.objects.filter(user=user,post=post)):
        return Response({"error":"Post is already not liked"},status=400)
    else:
        LikedPost.objects.filter(user=user,post=post).delete()
        post.no_of_likes-=1
        post.save()
        return Response({"message":"Post is unliked successfully"},status=201)

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

@csrf_exempt
@api_view(['DELETE'])
def deleteaccount(request):
    
    session=Session.objects.get(session_key=request.data["session_key"])
    response={}
    if session is None:
        response['success']=False,
        response['error']='User not found!'
        return Response(response,status.HTTP_404_NOT_FOUND)

    session_data = session.get_decoded()
    email=session_data['email']
    if(not Users.objects.filter(email=email)):
        return Response({"error":"User Does Not Exist"},status=400)
    
    user=Users.objects.filter(email=email)[0]
    all_liked_posts=LikedPost.objects.filter(user=user)
    for i in all_liked_posts:
        post = Post.objects.filter(post_id=i.post_id)[0]
        post.no_of_likes-=1
        post.save()
    
    saved_collection=SavedCollection.objects.filter(user=user)[0]
    user.delete()
    saved_collection.delete()
    session.delete()
    return Response({"message": "Account deleted successfully!"},status.HTTP_204_NO_CONTENT)
