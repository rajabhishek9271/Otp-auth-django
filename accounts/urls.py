from django.urls import path, include, re_path
from .views import *
app_name = 'accounts'

urlpatterns = [
    re_path('vlidate_phone/', ValidatePhoneSendOTP.as_view()),
]
