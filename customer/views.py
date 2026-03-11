from pyexpat.errors import messages
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect, render
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.decorators import login_required

# Create your views here.


@login_required
def customer_dashboard(request):
    
    return render(request, 'customer/customer_dashboard.html')

@login_required
def password_change(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            logout(request)
            # Update the session to prevent logout
           
            messages.success(request, 'Your password was successfully updated!')
            return redirect('login')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'customer/password_change.html', {'form': form})