import asyncio
from asgiref.sync import async_to_sync, sync_to_async
from GeeAnalysis.Analysis.analyze import ConcurrencyAnalyzer


from .seriailzers import *
from channels.db import database_sync_to_async
from datetime import datetime, timedelta
from channels.db import database_sync_to_async
from .models import DataMonitored
from .seriailzers import DataMonitoredSerializer

from django.utils import timezone 
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from datetime import datetime, timedelta
from channels.db import database_sync_to_async
import os
import dotenv

dotenv.load_dotenv()

def Runing(request):
    return HttpResponse("Hello, world!")

class MakeAnalysisView(APIView):
    def get(self, request, user_id, analysis_name):
        print('Hello', user_id)
        try:
            # Retrieve the DataMonitored instance based on user_id and name
            data_monitored = DataMonitored.objects.get(name=analysis_name) 
            # Serialize the DataMonitored instance
            serializer = DataMonitoredSerializer(data_monitored)
            print(serializer.data)
            # Return the serialized data as a response
            return Response(serializer.data, status=status.HTTP_200_OK)
        except DataMonitored.DoesNotExist:
            return Response({"error": "DataMonitored not found"}, status=status.HTTP_404_NOT_FOUND)

class MakeAnalysisPostView(APIView):

    @sync_to_async
    def create_data_monitored(self, user_id, user_name, email, coordinate, start_date, end_date, analysis_name):
        monitoredData = DataMonitored.objects.create(
            user=get_object_or_404(User, user_id=user_id, name=user_name, email=email),
            coordinate=coordinate,
            start_date=start_date,
            end_date=end_date,
            name=analysis_name,
            state='Processing',
            analysis_made={}
        )
        self.send_processing_email(monitoredData, '/dashboard')
        return monitoredData

    @database_sync_to_async
    def get_user(self, user_id):
        return User.objects.get(user_id=user_id)

    @database_sync_to_async
    def validate_analysis(self, user, username, email, coordinate, analysis_name):
        if user.name != username or user.email != email:
            return {'error': f'Analysis with user_id: {user.user_id} once exists, with {user.email}, {user.name} but now has changed to "{email}" "{username}" ', 'status': '409', }
        existing_analysis = DataMonitored.objects.filter(user=user, name=analysis_name).first()
        print(existing_analysis)
        if existing_analysis:
            return {'error': f'Analysis with name "{analysis_name}" already exists for this user', 'status': '409'}

        # Check if the user has made another analysis in the last 15 days with the same coordinate
        recent_analysis = DataMonitored.objects.filter(
            user=user,
            coordinate__exact=coordinate,
            last_check__gt=timezone.now() - timedelta(days=15)
        )
        print(recent_analysis)

        if recent_analysis:
            return {'error': 'You can only make another analysis of the same area in the next 15 days', 'status': '429'}
        return None

    @database_sync_to_async
    def run_analysis(self, data_monitored, coordinate, start_date, end_date):
        print(data_monitored, 'Tr')
        try:
            data = ConcurrencyAnalyzer(cordinate=coordinate, start=start_date, end=end_date).execute()
            data_monitored.state = 'Success'
            data_monitored.analysis_made = data
            data_monitored.last_saved = timezone.now()
            data_monitored.save()
            self.send_success_email(data_monitored)
        except Exception as e:
            print(e)
            data_monitored.state = 'Error'
            data_monitored.save()
            self.send_error_email(data_monitored, e)

    @async_to_sync
    async def post(self, request, userId, analysisName):
        user = await self.get_user(userId)
        coordinate = request.data.get('coordinate')
        email = request.data.get('email')
        userName = request.data.get('username')
        start_date = request.data.get('start_date')
        end_date = request.data.get('end_date')

        validate_result = await self.validate_analysis(user, userName, email, coordinate=coordinate, analysis_name=analysisName)

        if validate_result:
            return Response(validate_result['error'], status=status.HTTP_429_TOO_MANY_REQUESTS if validate_result['status'] == '429' else status.HTTP_409_CONFLICT)

        data_monitored = await self.create_data_monitored(userId, userName, email, coordinate, start_date, end_date, analysisName)
        await asyncio.create_task(self.run_analysis(data_monitored, coordinate, start_date, end_date))

        return Response({'status': 'Processing'}, status=status.HTTP_202_ACCEPTED)

    def send_success_email(self, data_monitored, total_time_used='3.6 minutes', dashboard_link='?slah'):
        subject = 'Analysis Success'
        message = render_to_string('email/index.html', {
            "analysis_name": data_monitored.user.name,
            'coordinate': data_monitored.coordinate,
            'user': data_monitored.user,
            'total_time_used':total_time_used,
            'start_date': data_monitored.start_date,
            'end_date': data_monitored.end_date,
            'start_time': data_monitored.last_check,
            'end_time': data_monitored.last_saved,
            'status': 'success',
            'dashboard_link': dashboard_link
        })

        plain_message = strip_tags(message)
        self.send_email(data_monitored, subject, message, plain_message)

    def send_error_email(self, data_monitored, total_time_used='10 minutes', error =None ):
        subject = 'Analysis Error'
        message = render_to_string('email/index.html', {
            'errors': error,
            "analysis_name": data_monitored.name,
            'user': data_monitored.user.name,
            'total_time_used':total_time_used,
            'start_date': data_monitored.start_date,
            'end_date': data_monitored.end_date,
            'status': 'error'
        })

        plain_message = strip_tags(message)
        self.send_email(data_monitored, subject, message, plain_message)

    def send_processing_email(self, data_monitored, total_time_used ='10 minuts' , dashboard_link='/dashboard'):
        subject = 'Analysis Processing'
        message = render_to_string('email/index.html', {
            "analysis_name": data_monitored.name,
            'coordinate': data_monitored.coordinate,
            'user': data_monitored.user.name,
            'total_time_used':total_time_used,
            'start_date': data_monitored.start_date,
            'end_date': data_monitored.end_date,
            'start_time': data_monitored.last_check,
            'end_time': data_monitored.last_saved,
            'status': 'processing',
            'dashboard_link': dashboard_link
        })

        plain_message = strip_tags(message)
        self.send_email(data_monitored, subject, message, plain_message)

    def send_email(self, data_monitored, subject, message, plain_message):
        recipient_email = data_monitored.user.email
        print(os.environ.get('SMTP_USER'), recipient_email, 'address')

        send_mail(
            subject,
            plain_message,
            from_email=os.environ.get('SMTP_USER'),
            recipient_list=[recipient_email],
            html_message=message,
            fail_silently=False
        )
