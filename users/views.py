from django.contrib import messages
from django.contrib.auth import authenticate, get_user_model, login, logout
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.http.response import HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.views import View

from .forms import LoginForm, UserRegistrationForm
from .tokens import account_activation_token

User = get_user_model()


class LoginView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('homepage')
        form = LoginForm()
        return render(request, 'users/login.html', {'form': form})

    def post(self, request):
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(request, email=email, password=password)
            if user is not None:
                login(request, user)
                return redirect('homepage')
            else:
                messages.error(request, 'Invalid username or password')

        return render(request, 'users/login.html', {'form': form})


class LogoutView(View):
    def get(self, request):
        logout(request)
        return redirect('login')


class RegistrationView(View):
    def get(self, request):
        form = UserRegistrationForm()
        return render(request, 'users/register.html', {'form': form})

    def post(self, request):
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()

            to_address = form.cleaned_data.get('email')

            domain = get_current_site(request).domain

            uid = urlsafe_base64_encode(force_bytes(user.pk))

            token = account_activation_token.make_token(user)

            link = reverse('activate', kwargs={
                'uidb64': uid, 'token': token})

            email_subject = 'Activate your account'

            activation_url = f'http://{domain}{link}'

            email_body = f'Hi {user.username}, Please click on the link to confirm your registration \n{activation_url}'

            sender = 'sender@abc.com'

            email = EmailMessage(
                email_subject,
                email_body,
                sender,
                [to_address],
            )
            try:
                email.send()
            except Exception:
                user.delete()
                messages.error(
                    request, 'There was a problem in sending activation email, Please try again.')
            else:
                messages.success(
                    request, 'Account successfully created, Please check your email.')

        return render(request, 'users/register.html', {'form': form})


class ActivationView(View):
    def get(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except Exception:
            user = None

        if user is not None and account_activation_token.check_token(user, token):
            user.is_active = True
            user.save()
            messages.success(request, 'Account activated successfully.')
            return redirect('login')
        else:
            return HttpResponse('Invalid activation link')
