from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
def index(request):
    return HttpResponse('Main Page')

def group(request, slug):
    return HttpResponse('Posts list')