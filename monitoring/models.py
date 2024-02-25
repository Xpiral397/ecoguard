from django.db import models

class User(models.Model):
    id = models.AutoField(primary_key=True)
    user_id = models.CharField(max_length=255, unique = True)
    email = models.EmailField(max_length=50, unique = True)
    name = models.CharField(max_length = 50)
    date_joined = models.DateTimeField(auto_now_add=True)

class DataMonitored(models.Model):
    STATE_CHOICES = [('Processing', 'Processing'), ('Error', 'Error'), ('Success', 'Success')]
    user = models.ForeignKey(User, on_delete=models.CASCADE,  null = True)
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, unique =True)  
    coordinate = models.JSONField()
    start_date = models.DateField()
    end_date = models.DateField()
    last_check = models.DateTimeField(auto_now_add=True)
    last_saved  = models.DateTimeField(auto_now=True)
    analysis_made = models.JSONField()
    state = models.CharField(max_length=20, choices=STATE_CHOICES, default='Processing')

class Analysis(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    data = models.ForeignKey(DataMonitored, on_delete=models.CASCADE, related_name='analysis')
    NDVI = models.DecimalField(max_digits=10, decimal_places=2)
    NDWI = models.DecimalField(max_digits=10, decimal_places=2)
    SDVI = models.DecimalField(max_digits=10, decimal_places=2)
    NDBI = models.DecimalField(max_digits=10, decimal_places=2)
    SAVI = models.DecimalField(max_digits=10, decimal_places=2)
    MSAVI2 = models.DecimalField(max_digits=10, decimal_places=2)
    EVI = models.DecimalField(max_digits=10, decimal_places=2)
    MNDWI = models.DecimalField(max_digits=10, decimal_places=2)
    DeforestMeasure = models.DecimalField(max_digits=10, decimal_places=2)
    LMI = models.DecimalField(max_digits=10, decimal_places=2)

class Monitoring(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    analysis = models.ForeignKey(Analysis, on_delete=models.CASCADE)

