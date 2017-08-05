"""my-gem URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
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
from django.conf.urls import url
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import password_reset, password_reset_done, password_reset_confirm, password_reset_complete

from my-gem.core.views import home, upload_contra_cheque, edit_user, list_user, register_user, change_password, check_upload

urlpatterns = [
    url(r'^$', home, name='home'),
    url(r'^upload/$', upload_contra_cheque, name='upload_contra_cheque'),
    url(r'^check_upload/$', check_upload, name='check_upload'),

    url(r'^edit_user/$', edit_user, name='edit_user'),
    url(r'^edit_user/(?P<pk>\d+)/$', edit_user, name='edit_user'),
    url(r'^list_user/$', list_user, name='list_user'),
    url(r'^register_user/$', register_user, name='register_user'),
    url(r'^change_password/(?P<pk>\d+)/$', change_password, name='change_password'),

    url(r'^login/$', auth_views.login, name='login'),
    url(r'^logout/$', auth_views.logout, {'next_page': 'login'}, name='logout'),
    url(r'^admin/', admin.site.urls),

    url(r'^user/password/reset/$', password_reset, {'post_reset_redirect' : '/user/password/reset/done/'},name="password_reset"),
    url(r'^user/password/reset/done/$',password_reset_done),
    url(r'^reset/(?P<uidb64>[0-9A-Za-z]+)/(?P<token>.+)/$', password_reset_confirm,name='password_reset_confirm'),
    url(r'^user/password/done/$',password_reset_complete, name='password_reset_complete'),
]
