from django.conf.urls import url
from core import views

app_name='core'

urlpatterns=[
    url(r'^register/$',views.register,name='register'),
    url(r'^user_login/$',views.user_login,name='user_login'),
    url(r'^aboutus/$',views.aboutus,name='aboutus'),
    url(r'^contactus/$',views.contactus,name='contactus'),
    url(r'^explore/$',views.explore,name='explore'),
    url(r'^profile/$',views.profile,name='profile'),
    url(r'^donate/$',views.donate,name='donate'),
    url(r'^findabenefactor/$',views.findabenefactor,name='findabenefactor'),
    url(r'^user_logout/$',views.user_logout,name='user_logout'),
]