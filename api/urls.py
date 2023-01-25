from django.urls import path

from api.views import *

urlpatterns = [
    path('bbs/', bbs),
    path('bbs/<int:pk>', BBDetailView.as_view()),
    path('bbs/<int:pk>/comments/', comments),
]
