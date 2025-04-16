"""
URL configuration for municipal_data project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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

from django.urls import path, include

from django.conf import settings

from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('accounts.urls')),
    path('billing/', include('billing.urls')),  # Add this line for billing app
    path('accounts/', include('accounts.urls')),  # Ensures accounts/ is the base path
    path('helpdesk/', include('helpdesk.urls')),  # Add this line for billing app
    path('distance_calculator/', include('distance_calculator.urls')),
    path('portal/', include('customer_portal.urls')),  # External user interface
    path('services/', include('services.urls')),  # External user interface
] 
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)



