from django.http import HttpResponse
from django.shortcuts import render

def index(request):
    context_dict={'boldmessage': "boldmessage!!"}
    return render(request, 'rango/index.html', context=context_dict)
def about(request):
    return HttpResponse("rango says hello in about page!")