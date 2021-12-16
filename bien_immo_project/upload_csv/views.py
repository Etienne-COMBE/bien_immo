from django.shortcuts import render, redirect
from django.contrib.auth import authenticate

# Create your views here.
def login(request):
    username = request.POST.get('username')
    password = request.POST.get('password')
    user = authenticate(username = username, password = password)
    if user is not None:
        return render(request, "upload_csv/index.html")
    return redirect("/")