from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordResetForm
from django.contrib.auth import login as auth_login, logout as auth_logout, authenticate
from django.contrib import messages
import requests


def sign_up(request):
        """
        Handles user registration. If the request method is POST, it processes the 
        form data. If the form is valid, it creates a new user, logs them in, and 
        redirects to the home page. Otherwise, it displays the registration form.
        """
        if request.method == 'POST':
            form = UserCreationForm(request.POST)
            if form.is_valid():
                user = form.save()  
                auth_login(request, user)  
                messages.success(request, 'Registration successful.')

                fastapi_url = 'https://api.fut-tracker.co.uk/users/'
                try:

                    response = requests.post(fastapi_url, json={
                        'email': request.POST.get('username'),
                        'password': request.POST.get('password1')
                    })
                    print(f"ressonse status code = {response.status_code}")

                except Exception as e:
                    print(f"error: {e}")

                return redirect('home')
            else:
                messages.error(request, 'Please correct the errors below.')
                print(form.errors)
        else:
            form = UserCreationForm()  
            
        return render(request, 'users/sign_up.html', 
                      {'form': form,
                       "title": "Sign Up",
                       "form_message": "Sign up to the FUT Tracker community",
                       "username_tooltip": "Please enter a valid email address",
                       "password1_tooltip": "Password must contain 6 characters, at least one number and at least one lowercase (a-z) letter",
                       })
    

def login(request):
    """
    Handles user login. If the request method is POST, it processes the form 
    data. If the form is valid, it logs the user in and redirects to the home page.
    Otherwise, it displays the login form.
    """
    
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            return redirect('home')
    else:
        form = AuthenticationForm()
        
    return render(request, 'users/login.html', 
                  {"form": form,
                   "title": "Log In",
                   "form_message": "Log in using your email and password"
                   })
    
    
def logout_view(request):
    """
    Handles user logout
    """
    auth_logout(request)
    return redirect('login')

    
def password_reset(request):
    """
    Handles password reset requests. If the request method is POST, it processes 
    the form data. If the form is valid, it initiates the password reset process 
    and redirects to a confirmation page. Otherwise, it displays the password 
    reset form.
    """
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            form.save(request=request)  
            return redirect('password_reset_done')  
    else:
        form = PasswordResetForm()  
    return render(request, 'users/password_reset.html', 
                  {'form': form,
                   "title": "Log In",
                   "form_message": "Please enter the Email address your registered with in order to reset your password"
                   })
