from django.contrib import admin
from django.contrib.auth import login, logout
from django.urls import path
from django.conf.urls import url
from django.urls.conf import re_path
from Myapp import views
from django.http import HttpResponseRedirect
from django.views.generic import View
from .views import activation_sent, activate, PostHomeView, PostDetailView, CreatePostView, PostUpdateView, DraftListView, PostDeleteView
app_name = 'Myapp'
urlpatterns = [

    path('', views.homePage, name='index'),
    path('contact/', views.contact, name='contact'),
    path('service/', views.service, name='service'),
    path('about/', views.aboutPage, name='about'),
    # path('login/', views.loginUser, name='login'),
    path('login/', views.loginUser, name='login'),
    path('logout/', views.logoutUser, name='logout'),
    path('register/', views.registration, name='register'),
    path('sent/', activation_sent, name="activation_sent"),
    path('activate/<slug:uidb64>/<slug:token>/', views.activate, name='activate'),
    path('blog/', PostHomeView.as_view(), name='post_list_blog'),
    path('blog/<int:pk>', PostDetailView.as_view(), name='post_detail_blog'),
    path('post/new/', CreatePostView.as_view(), name='post_new_blog'),
    path('post/<int:pk>/edit/', PostUpdateView.as_view(), name='post_edit'),
    path('drafts/', DraftListView.as_view(), name='post_draft_list'),
    path('post/<int:pk>/remove/', PostDeleteView.as_view(), name='post_remove'),
    path('post/<int:pk>/publish/', views.post_publish, name='publish_post'),
    path('blog/<int:pk>/comment/', views.add_comment_to_post, name='add-comment'),
    path('comment/<int:pk>/approve/', views.comment_approve,name='comment_approve'),
    path('comment/<int:pk>/remove/', views.comment_remove, name='comment_remove'),

]
