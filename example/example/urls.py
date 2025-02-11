"""example URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.urls import include, re_path
from django.contrib import admin
from django.shortcuts import render, redirect
from django.views.generic import RedirectView


def login(request):
    if not request.user.is_authenticated:
        return render(request, 'web3auth/login.html')
    else:
        return redirect('/admin/login')


def auto_login(request):
    if not request.user.is_authenticated:
        return render(request, 'web3auth/autologin.html')
    else:
        return redirect('/admin/login')


urlpatterns = [
    re_path(r'^admin/', admin.site.urls),
    re_path(r'^$', RedirectView.as_view(url='/login')),
    re_path(r'^login/', login, name='login'),
    re_path(r'^auto_login/', auto_login, name='autologin'),
    re_path(r'', include('web3auth.urls')),
]
