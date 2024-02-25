from django.urls import path
from .views import Runing, MakeAnalysisView,MakeAnalysisPostView

app_name = 'GeeAnalysis'

urlpatterns = [
    path('',Runing),
    path('get-analysis/<str:user_id>/<str:analysis_name>/',  MakeAnalysisView.as_view(), name='get'),
    path('make-analysis/<str:userId>/<str:analysisName>/', MakeAnalysisPostView.as_view(), name='post'),
]
