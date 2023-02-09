from django.http import request
from django.http.response import HttpResponseRedirect
from django.shortcuts import render, HttpResponse, redirect, get_object_or_404
from datetime import datetime
from django.contrib.sites.shortcuts import get_current_site
from django.urls.base import reverse
from django.utils.encoding import force_text
from Myapp.models import Contact  # , register
from django.contrib import messages
from django.contrib.auth.models import User
# from django.contrib.auth.forms import UserModelForm
from django.db import connections
import mysql.connector
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes
from .tokens import account_activation_token
from django.template.loader import render_to_string
from .forms import SignUpForm
from django.db import IntegrityError
from operator import itemgetter
from django.contrib.auth import logout, login, authenticate
from django.contrib.auth.forms import UserCreationForm, forms
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView
from django.core.mail import EmailMessage
import smtplib
from django.core.mail import send_mail
from .forms import PostForm, CommentForm
from django.views.generic import (TemplateView, ListView,
                                  DetailView, CreateView,
                                  UpdateView, DeleteView)
from django.utils import timezone
from django.core.mail import send_mail
from Myapp.models import Posting, Comment
from django.urls import reverse_lazy


# Create your views here.


def homePage(request):
    return render(request, 'index.html')
    # return HttpResponse("this is home page")


def activation_sent(request):
    return render(request, 'activation_sent.html')


def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.profile.signup_confirmation = True
        user.save()
        login(request, user)
        return render(request, 'index.html')
    else:
        return HttpResponse('activation_invalid')


def registration(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.refresh_from_db()
            user.profile.first_name = form.cleaned_data.get('first_name')
            user.profile.last_name = form.cleaned_data.get('last_name')
            user.profile.email = form.cleaned_data.get('email')
            user.is_active = False
            user.save()
            messages.success(request, 'Your Data has been Accepted!')
            current_site = get_current_site(request)
            subject = 'Please Activate Your Account'
            message = render_to_string('activation_request.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user),
            })
            to_email = form.cleaned_data.get('email')
            email = EmailMessage(subject, message, to=[to_email])
            email.send()
            return render(request, 'activation_sent.html')
        else:
            messages.warning(request, 'Credentials Invalid Please Try Again!.')
    else:
        form = SignUpForm()
    return render(request, 'register.html')


def aboutPage(request):
    return render(request, 'about.html')


def service(request):
    return render(request, 'service.html')


def contact(request):
    if request.method == "POST":
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        desc = request.POST.get('desc')
        contact = Contact(name=name, email=email, phone=phone,
                          desc=desc, date=datetime.today())
        contact.save()
        messages.success(request, 'Your messages has been Send!')
    return render(request, 'contact.html')


def loginUser(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user:
            if user.is_active:
                login(request, user)
                return render(request, 'index.html')
            else:
                # If account is not active:
                return HttpResponse("Your account is not active.")
        else:
            messages.warning(request, 'Credentials Invalid Please Try Again!.')
            print("Someone tried to login and failed.")
            print("They used username: {} and password: {}".format(
                username, password))
            return render(request, 'login.html')

    else:
        # Nothing has been provided for username or password.
        return render(request, 'login.html', {})


@login_required
def logoutUser(request):
    logout(request)
    return redirect('/login')


class PostHomeView(ListView):
    model = Posting
    template_name= 'post_list.html'
    ordering = ['-published_date']
    
    # def get_queryset(self):
    #     return Posting.objects.filter(published_date__lte=timezone.now()).order_by('-published_date')
    
class PostDetailView(DetailView):
    model = Posting
    template_name = 'blog-data.html'
  
    
class CreatePostView(CreateView): 
    model = Posting
    form_class = PostForm
    template_name = 'post_form.html'
    success_url = reverse_lazy('Myapp:post_list_blog') 
    success_message = 'Post Has Been Posted!'
    
    
class PostUpdateView(UpdateView):
    model = Posting
    fields= ["title", "text"]
    template_name = 'update_form.html'
    success_url = reverse_lazy('Myapp:post_list_blog')
    
class PostDeleteView(DeleteView):
    model = Posting
    template_name = 'posting_confirm_delete.html'
    success_url = reverse_lazy('Myapp:post_list_blog')


class DraftListView(ListView):
    model = Posting
    template_name = 'post_draft_list.html'    

    def get_queryset(self):
        return Posting.objects.filter(published_date__isnull=True).order_by('created_date')
    
   
    
    
#######################################
## Functions that require a pk match ##
#######################################   
@login_required   
def post_publish(request, pk):
    post = get_object_or_404(Posting, pk=pk)
    post.publish()
    return HttpResponse("You Publish a Post! Thankyou!")

@login_required
def add_comment_to_post(request, pk):
    post = get_object_or_404(Posting, pk=pk)
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.save()
        return redirect('Myapp:post_detail_blog', pk=post.pk)
    else:
        form = CommentForm()
    return render(request, 'comments_form.html', {'form': form})

@login_required
def comment_approve(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    comment.approve()
    return redirect('Myapp:post_detail_blog', pk=comment.post.pk)

@login_required
def comment_remove(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    post_pk = comment.post.pk
    comment.delete()
    return redirect('Myapp:post_detail_blog', pk=post_pk)
    
