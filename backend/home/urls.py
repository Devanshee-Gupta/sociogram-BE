from django.urls import path
from . import views

urlpatterns = [
    path("signin/",views.signin),
    path("signup/",views.signup),
    path("authenticate/",views.authenticate),
]