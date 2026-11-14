from django.urls import path

from . import views

urlpatterns = [
    path('', views.create_unit, name='unit-create'),
    path('all/', views.unit_list, name='unit-list'),
    path('fight/', views.simulate_fight, name='fight-simulate'),
    path('fights/<int:pk>/', views.fight_result, name='fight-result'),
    path('<int:pk>/', views.unit_detail, name='unit-detail'),
    path('<int:pk>/heal/', views.heal_unit, name='unit-heal'),
]
