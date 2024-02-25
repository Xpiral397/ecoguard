from django.contrib import admin
from .models import DataMonitored, Analysis, Monitoring, User

@admin.register(DataMonitored)
class DataMonitoredAdmin(admin.ModelAdmin):
    list_display = ('id',  'name', 'state', 'start_date', 'end_date', 'last_check', 'last_saved','coordinate', 'analysis_made',  'state')
    search_fields = ('name','id')  # Assuming User model has a 'username' field

@admin.register(Analysis)
class AnalysisAdmin(admin.ModelAdmin):
    list_display = ('user', 'data', 'NDVI', 'NDWI', 'SDVI', 'NDBI', 'SAVI', 'MSAVI2', 'EVI', 'MNDWI', 'DeforestMeasure', 'LMI')

@admin.register(Monitoring)
class MonitoringAdmin(admin.ModelAdmin):
    list_display = ('user', 'analysis')
    

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_id', 'name', 'email', 'date_joined')
    search_fields = ('id','user_id', 'email', 'name')
