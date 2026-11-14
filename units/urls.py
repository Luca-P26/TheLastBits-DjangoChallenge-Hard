from django.urls import path

from . import views

urlpatterns = [
    path('', views.create_unit, name='unit-create'),
    path('all/', views.unit_list, name='unit-list'),
    path('<int:pk>/', views.unit_detail, name='unit-detail'),
    path('<int:pk>/heal/', views.heal_unit, name='unit-heal'),
]
