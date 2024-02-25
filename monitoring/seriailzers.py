# serializers.py

from rest_framework import serializers
from .models import Analysis, Monitoring, DataMonitored, User

class MonitoringSerializer(serializers.ModelSerializer):
    class Meta:
        model = Monitoring
        fields = '__all__'

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

class DataMonitoredSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = DataMonitored
        fields = '__all__'

class AnalysisSerializer(serializers.ModelSerializer):
    data = DataMonitoredSerializer()

    class Meta:
        model = Analysis
        fields = '__all__'
