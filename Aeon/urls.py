"""Aeon URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
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
from django.urls import path
from . import views
from . import settings
from django.conf.urls.static import static
from . import Ajax_Code

from django.conf.urls import url

urlpatterns = [

    path('admin_access/', admin.site.urls),
    path('bookings', views.booking_pageshow),
    path('roomSummary', views.roomSummary_pageshow),
    path('paymentGateway', views.payment_check),
    path('receipt/OrderID=<str:orderID>/', views.print_pageshow, name='receipt'),

    # STATIC PAGES
    path('', views.home_pageshow),
    path('aboutUs', views.aboutUs_pageshow),
    path('facility', views.facility_pageshow),
    path('contactUs', views.contactUs_pageshow),

    # ROOMS
    path('HomeStay', views.homeStay_pageshow),
    path('DeluxeRoom', views.deluxeRoom_pageshow),
    path('PremiumRoom', views.premiumRoom_pageshow),

    # PAYTM URLS
    path('handlerequest/', views.handlerequest, name='HandleRequest'),

    # AJAX URLS
    path('ajax_login_credentialsCheck', Ajax_Code.ajax_login_credentialsCheck, name='ajax_login_credentialsCheck'),
    path('ajax_login_accountCreate', Ajax_Code.ajax_login_accountCreate, name='ajax_login_accountCreate'),
    path('ajax_login_guestCreate', Ajax_Code.ajax_login_guestCreate, name='ajax_login_guestCreate'),

]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
handler404 = 'Aeon.views.error_404'
