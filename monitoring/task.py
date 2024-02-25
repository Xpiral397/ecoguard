# tasks.py
from django_background_tasks import background

@background(schedule=60)  # Schedule the task to run every 60 seconds
def your_analysis_function(data_monitored_id):
    # Your analysis logic here
    data_monitored = DataMonitored.objects.get(id=data_monitored_id)
    
    # Update the DataMonitored instance with analysis result, end_date, state, etc.
    # ...

    data_monitored.save()
