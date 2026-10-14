from django.urls import path

from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home, name='home'),
    path('practices/', views.practices, name='practices'),
    path('team/', views.team, name='team'),
    path('team/<slug:slug>/', views.lawyer, name='lawyer'),
    path('cases/', views.cases, name='cases'),
    path('ip-centre/', views.ip_centre, name='ip'),
    path('press/', views.press, name='press'),
    path('contacts/', views.contacts, name='contacts'),
]
