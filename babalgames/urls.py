"""
URL configuration for babalgames project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
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
from django.contrib.auth.decorators import login_required, user_passes_test
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

def is_admin(user):
    return user.is_authenticated and user.is_staff

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('backend/', include('game.urls')),
    path('auth/', include('account.urls')),
    path('dashboard/', include('dashboard.urls')),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)