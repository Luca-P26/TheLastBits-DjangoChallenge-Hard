"""
URL configuration for coderrun_prob3 project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from units import views as unit_views
from django.views.generic.base import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('simulate', unit_views.simulate_challenge, name='simulate-challenge-no-slash'),
    path('simulate/', unit_views.simulate_challenge, name='simulate-challenge'),
    path('register-people/', unit_views.register_challenge_roster, name='register-challenge-roster'),
    path('unit', unit_views.create_unit, name='unit-create'),
    path('unit/', unit_views.create_unit, name='unit-create-slash'),
    path('unit/', include('units.urls')),
    path('', RedirectView.as_view(url='/unit/', permanent=False)),

]
