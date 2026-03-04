from django.urls import path
from .import views

urlpatterns=[
    path('', views.index, name='index'),
    path('add/',views.add_person, name='add_personne'),
    path('recognize/', views.recognize_person, name='recognize'),
]