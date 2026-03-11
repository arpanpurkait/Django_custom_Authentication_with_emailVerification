from pyexpat.errors import messages
from django.shortcuts import render, redirect,reverse
from accounts.forms import RegistrationForm,PasswordResetForm
from django.contrib import messages
from django.conf import settings
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.urls import reverse

from accounts.utils import send_activation_email,send_password_reset_email

from customer.views import customer_dashboard
from seller.views import seller_dashboard
from accounts.models import User
from django.contrib.auth import authenticate, login, logout

def home(request):
    user = request.user

    return render(request, 'accounts/home.html', {'username':user })
def logout_view(request):
    logout(request)
    return redirect('home')



# Create your views here.
def login_view(request):
    if request.user.is_authenticated:
        if request.user.is_seller:
            return redirect("seller_dashboard")
        # Handle login logic here
        elif request.user.is_customer:
            return redirect("customer_dashboard")
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        if not email or not password:
            messages.error(request, "Please enter both email and password.")
            return redirect('login')
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            messages.error(request, "Invalid email or password.")
            return redirect('login')

        if not user.is_active:
            messages.error(request, "Account is not active. Please wait for activation.")
            return redirect('login')
        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            if user.is_seller:
                return redirect("seller_dashboard")
            elif user.is_customer:
                return redirect("customer_dashboard")
        else:
            messages.error(request, "Invalid email or password.")
            return redirect('customer_dashboard')

    return render(request,'accounts/login.html')  # Redirect to home page after successful login



def register_view(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.set_password(form.cleaned_data["password"])
            user.is_active = True  # Set user as active after registration
            user.save()
            print("Data saved....")
            uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            activation_link = reverse('', kwargs={'uidb64': uidb64, 'token': token})
            activation_url = f"{settings.SITE_DOMAIN}{activation_link}"
            
            send_activation_email(user.email, activation_url)


            messages.success(request, "Registration successful. Please wait for account activation.")
            return redirect("customer_dashboard")  # Redirect to customer dashboard after successful registration
        else:
            print("Not saving the data....")
    else:
        form = RegistrationForm()
    return render(request, 'accounts/register.html', {'form': form})



def activate_account(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
        if user.is_active:
            messages.info(request, "Account already activated.")
            return redirect("login")
        if default_token_generator.check_token(user, token):
            user.is_active = True
            user.save()
            messages.success(request, "Account activated successfully. You can now log in.")
            return redirect("login")
        else:
            messages.error(request, "Invalid activation link.")
            return redirect("login")
    except:
        (TypeError, ValueError, OverflowError, User.DoesNotExist)
        messages.error(request, "Invalid activation link.")
        return redirect("login")


def password_reset_view(request):
    # Implement password reset logic here
    if request.method == "POST":
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            user = User.objects.filter(email=email).first()
            if user:
                uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
                token = default_token_generator.make_token(user)
                reset_link = reverse('password_reset_confirm', kwargs={'uidb64': uidb64, 'token': token})
                reset_url = f"{request.build_absolute_uri(reset_link)}"
                send_password_reset_email(user.email, reset_url)
            
            messages.success(request, "If an account with that email exists, a password reset link has been sent.")
            # Implement password reset logic here, such as sending a password reset email
            return redirect('login')
    else:
        form = PasswordResetForm()
        return render(request, 'accounts/password_reset.html', {'form': form})


def password_reset_confirm_view(request, uidb64, token):
    # Implement password reset confirmation logic here
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
        if not default_token_generator.check_token(user, token):
            messages.error(request, "Expired password reset link.")
            return redirect("login")

        if request.method == "POST":
            form = PasswordResetForm(request.POST)
            if form.is_valid():
                form.save()

                messages.success(request, "Password reset successful. You can now log in with your new password.")
                return redirect("login")
        else:
            form = PasswordResetForm()
            return render(request, 'password_reset_confirm.html')
            
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        messages.error(request, "Invalid password reset link.")
        return redirect("login")