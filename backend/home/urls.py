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
    path(":userid/profile/",views.othersprofile),
    path("logout/",views.logout),
]