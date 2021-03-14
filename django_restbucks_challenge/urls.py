from django.contrib import admin
from django.urls import path, include

from restbuck_app import views

urlpatterns = [
    path('menu/', views.Menu.as_view()),
    path('client_order/', views.OrderView.as_view()),
    path('client_order/<int:pk>/', views.OrderView.as_view()),
    path('admin/doc/', include('django.contrib.admindocs.urls')),
    path('admin/', admin.site.urls),
    ]
