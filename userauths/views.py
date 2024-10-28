from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from userauths.models import User, Profile
from userauths.forms import UserRegisterForm

def register_view(request):
    if request.user.is_authenticated:
        messages.warning(request, "You are already logged in.")
        return redirect("hotel:hotel_list")

    form = UserRegisterForm(request.POST or None)
    if form.is_valid():
        user = form.save(commit=False)
        full_name = form.cleaned_data.get('full_name')
        phone = form.cleaned_data.get('phone')
        email = form.cleaned_data.get('email')
        password = form.cleaned_data.get('password1')

        # Set the password for the user
        user.set_password(password)
        user.save()
        
        # Authenticate and log in the user
        user = authenticate(email=email, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f"Hey {full_name}, your account has been created successfully.")
            
            # Check if a profile already exists
            profile, created = Profile.objects.get_or_create(user=user)
            if created:
                # Profile was created
                profile.full_name = full_name
                profile.phone = phone
                profile.save()
                messages.success(request, "Profile created successfully.")
            else:
                # Profile already exists, update it if necessary
                profile.full_name = full_name
                profile.phone = phone
                profile.save()  # Save updates if necessary
            
            return redirect("hotel:hotel_list")

    context = {
        'form': form
    }
    return render(request, 'userauths/sign-up.html', context)


def login_view(request):
    if request.user.is_authenticated:
        messages.warning(request, "You are already logged in.")
        return redirect("hotel:hotel_list")

    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        
        # Authenticate the user
        user_auth = authenticate(request, email=email, password=password)
        
        if user_auth is not None:
            login(request, user_auth)
            messages.success(request, "You are logged in.")
            next_url = request.GET.get("next", "hotel:hotel_list")
            return redirect(next_url)
        else:
            messages.error(request, "Invalid email or password.")
            return redirect("userauths:sign-in")
    
    return render(request, 'userauths/sign-in.html')  # Adjust the template path as needed



def LogoutView(request):
    logout(request)
    messages.success(request, "you have been logged out")
    return redirect("userauths:sign-in")