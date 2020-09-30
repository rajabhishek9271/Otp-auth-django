from django.shortcuts import render
from django.http import HttpResponse
import http.client
from django.views.generic import View
# Create your views here.
import json
import requests
import ast

from rest_framework.views import APIView
from rest_framework.response import Response
# from rest_framework import permissions, status, generics
# from forms import UserForm
from .models import User, PhoneOTP
from django.shortcuts import get_object_or_404, redirect
import random
# from .serializer import CreateUserSerializer, LoginSerializer
# from knox.views import LoginView as KnoxLoginView
# from knox.auth import TokenAuthentication
# from rest_framework.authentication import SessionAuthentication, BasicAuthentication
# from rest_framework.permissions import IsAuthenticated
import mysql.connector
from django.db import connection

from django.contrib.auth import login,logout
import environ

env = environ.Env()
# reading .env file
environ.Env.read_env()


conn = http.client.HTTPConnection("2factor.in")


class Registration(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'register.html')

    def post(self, request, *args, **kwargs):
        form = request.POST
        phone_number = form.get('phone')
        password = form.get('password')
        username = form.get('username')
        email    = form.get('email')

        request.session['email'] = email
        request.session['username'] = username
        request.session['password'] = password
        request.session['phone'] = phone_number

        if phone_number:
            phone = str(phone_number)
            user = User.objects.filter(phone__iexact = phone)
            if user.exists():
                return Response({
                    'status' : False,
                    'detail' : 'Phone number already exists'
                })

            else:
                key = send_otp(phone)
                if key:
                    old = PhoneOTP.objects.filter(phone__iexact = phone)
                    if old.exists():
                        old = old.first()
                        count = old.count
                        if count > 10:
                            return Response({
                                'status' : False,
                                'detail' : 'Sending otp error. Limit Exceeded. Please Contact Customer support'
                            })

                        old.count = count +1
                        old.save()
                        print('Count Increase', count)
                        conn.request("GET", f"https://2factor.in/API/R1/?module=SMS_OTP&apikey={env('API_KEY')}&to=+91{str(phone)}&otpvalue={str(key)}&templatename=test")
                        res = conn.getresponse()

                        data = res.read()
                        data=data.decode("utf-8")
                        data=ast.literal_eval(data)


                        if data["Status"] == 'Success':
                            old.otp_session_id = data["Details"]
                            old.otp = str(key)
                            old.save()
                            print('In validate phone :'+old.otp_session_id)
                            return redirect('verify_true')
                        else:
                            return render(request, 'verify_false.html', context={
                                  'status' : False,
                                  'detail' : 'OTP sending Failed'
                                })


                    else:


                        conn.request("GET", f"https://2factor.in/API/R1/?module=SMS_OTP&apikey={env('API_KEY')}&to=+91{str(phone)}&otpvalue={str(key)}&templatename=test")
                        res = conn.getresponse()
                        data = res.read()
                        print(data.decode("utf-8"))
                        data=data.decode("utf-8")
                        data=ast.literal_eval(data)

                        if data["Status"] == 'Success':
                            obj=PhoneOTP.objects.create(
                            phone=phone,
                            otp = key,
                            email=email,
                            username=username,
                            password=password,
                            )
                            obj.otp_session_id = data["Details"]
                            obj.save()
                            print('In validate phone :'+obj.otp_session_id+"OTP IS: "+str(obj.otp))
                            return redirect('verify_true')
                        else:
                            return render(request, 'verify_false.html', context={
                                  'status' : False,
                                  'detail' : 'OTP sending Failed'
                                })


                else:
                     return render(request, 'verify_false.html', context={
                           'status' : False,
                            'detail' : 'Sending otp error'
                     })

        else:
            return render(request, 'verify_false.html', context={
                'status' : False,
                'detail' : 'Phone number is not given in post request'
            })




class ValidatePhoneSendOTP(APIView):

    def post(self, request, *args, **kwargs):
        phone_number = request.data.get('phone')
        password = request.data.get('password', False)
        username = request.data.get('username', False)
        email    = request.data.get('email', False)

        if phone_number:
            phone = str(phone_number)
            user = User.objects.filter(phone__iexact = phone)
            if user.exists():
                return Response({
                    'status' : False,
                    'detail' : 'Phone number already exists'
                })

            else:
                key = send_otp(phone)
                if key:
                    old = PhoneOTP.objects.filter(phone__iexact = phone)
                    if old.exists():
                        old = old.first()
                        count = old.count
                        if count > 10:
                            return Response({
                                'status' : False,
                                'detail' : 'Sending otp error. Limit Exceeded. Please Contact Customer support'
                            })

                        old.count = count +1
                        old.save()
                        print('Count Increase', count)

                        conn.request("GET", "https://2factor.in/API/R1/?module=SMS_OTP&apikey=1028fcd9-3158-11ea-9fa5-0200cd936042&to="+phone+"&otpvalue="+str(key)+"&templatename=WomenMark1")
                        res = conn.getresponse()

                        data = res.read()
                        data=data.decode("utf-8")
                        data=ast.literal_eval(data)


                        if data["Status"] == 'Success':
                            old.otp_session_id = data["Details"]
                            old.save()
                            print('In validate phone :'+old.otp_session_id)
                            return Response({
                                   'status' : True,
                                   'detail' : 'OTP sent successfully'
                                })
                        else:
                            return Response({
                                  'status' : False,
                                  'detail' : 'OTP sending Failed'
                                })




                    else:

                        obj=PhoneOTP.objects.create(
                            phone=phone,
                            otp = key,
                            email=email,
                            username=username,
                            password=password,
                        )
                        conn.request("GET", "https://2factor.in/API/R1/?module=SMS_OTP&apikey=1028fcd9-3158-11ea-9fa5-0200cd936042&to="+phone+"&otpvalue="+str(key)+"&templatename=WomenMark1")
                        res = conn.getresponse()
                        data = res.read()
                        print(data.decode("utf-8"))
                        data=data.decode("utf-8")
                        data=ast.literal_eval(data)

                        if data["Status"] == 'Success':
                            obj.otp_session_id = data["Details"]
                            obj.save()
                            print('In validate phone :'+obj.otp_session_id)
                            return Response({
                                   'status' : True,
                                   'detail' : 'OTP sent successfully'
                                })
                        else:
                            return Response({
                                  'status' : False,
                                  'detail' : 'OTP sending Failed'
                                })


                else:
                     return Response({
                           'status' : False,
                            'detail' : 'Sending otp error'
                     })

        else:
            return Response({
                'status' : False,
                'detail' : 'Phone number is not given in post request'
            })



def send_otp(phone):
    if phone:
        key = random.randint(999,9999)
        print(key)
        return key
    else:
        return False

class VerifyOTP(View):
    def get(self, request, *args, **kwargs):

        return render(request, 'verify_true.html')

    def post(self, request, *args, **kwargs):
        form = request.POST
        otp = form.get('otp')

        print(otp)
        old = PhoneOTP.objects.filter(otp__iexact = otp)
        if old.exists():
            old = old.first()
            otp_session_id = old.otp_session_id
            conn.request("GET", f"https://2factor.in/API/V1/{env('API_KEY')}/SMS/VERIFY/{otp_session_id}/{otp}")
            res = conn.getresponse()
            data = res.read()
            print(data.decode("utf-8"))
            data=data.decode("utf-8")
            data=ast.literal_eval(data)



            if data["Status"] == 'Success':
                old.validated = True
                old.save()
                email = request.session['email']
                username = request.session['username']
                password = request.session['password']
                phone_number = request.session['phone']

                with connection.cursor() as cursor:
                    # TODO: Password is getting stored as string in database rather than hashed.
                    cursor.execute("INSERT INTO ACCOUNTS_USER(USERNAME, EMAIL, PASSWORD, PHONE, IS_SUPERUSER, IS_STAFF, IS_ACTIVE, FIRST_NAME, LAST_NAME, LAST_LOGIN, DATE_JOINED) VALUES(%s, %s, %s, %s, 0, 0, 0, 'Abhi', 'Raj', '2020-09-30 07:34:38.551108', '2020-09-28 13:03:21.539822');",[username, email, password, phone_number])
                return render(request, 'welcome.html')

            else:
                return render(request, 'failed.html', context={'status':'Wrong OTP entered!'})



        else:
            return render(request, 'failed.html', context={'status':'OTP was not sent to you.'})
