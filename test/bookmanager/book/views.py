from django.shortcuts import render
from django.http.request import HttpRequest
from django.http.response import HttpResponse

# Create your views here.
def index(request):
    data = {
        'show': "圣诞节快乐！～～～～"
            }
    # return HttpResponse(f"{data['show']}")
    return render(request, 'book/index.html', context=data)
