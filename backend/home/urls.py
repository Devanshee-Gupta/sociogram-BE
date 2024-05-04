from django.urls import path
from . import views

urlpatterns = [
    path("signin/",views.signin),
    path("signup/",views.signup),
    path("authenticate/",views.authenticate),
    path("getallposts/",views.getallposts),
    path("addnewpost/",views.addnewpost),
    path("ownprofile/",views.ownprofile),
    path("editprofile/",views.editprofile),
    path("changepassword/",views.changepassword),
    path("<str:userid>/profile/", views.othersprofile),
    path("addtolist/",views.addtolist),
    path("getlistelements/",views.getlistelements),
    path("deletefromlist/",views.deletefromlist),
    path("likepost/",views.likepost),
    path("unlikepost/",views.unlikepost),
    path("logout/",views.logout),
]