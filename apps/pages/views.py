from django.shortcuts import render

def home_page(request):
    ctx = {

    }
    return render(request, 'home/home.html', ctx)
