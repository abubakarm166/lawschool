from django.contrib import admin
from django.urls import path
from Law_school import views

urlpatterns = [
    path('', views.index, name="index"),
    path('register-request/', views.register_request, name="register_request"),
    path('login/', views.user_login, name="login"),
    path('logout/', views.user_logout, name="user_logout"),
    path('assignments/', views.assignments_list, name="assignments_list"),
    path('download-assignment/<int:assignment_id>/', views.download_assignment, name="download_assignment"),
]
