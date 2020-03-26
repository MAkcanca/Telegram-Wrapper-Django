"""telegramwrap URL Configuration
"""
from django.contrib import admin
from django.urls import path, include

from telegramwrap import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('settings/', include('livesettings.urls')),
    path('request_code/', views.RequestCodeView.as_view()),
    path('submit_code/', views.SubmitCodeView.as_view()),
    path('logout/', views.LogoutView.as_view()),
    path('send_message/', views.SendMessageView.as_view()),
    path('attach_webhook/', views.AttachWebhookView.as_view()),
    path('get_token/', views.RetrieveTokenView.as_view()),
]
