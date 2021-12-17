from django.shortcuts import render, redirect
from django.contrib.auth import authenticate

# Create your views here.
def login(request):
    username = request.POST.get('username')
    password = request.POST.get('password')
    user = authenticate(username = username, password = password)
    if (user is not None) and user.has_perm('upload'):
        return render(request, "upload_csv/index.html")
    elif user is not None:
        message = "Wrong permissions"
        return redirect(f"stats/?message={message}")
    return redirect("/")