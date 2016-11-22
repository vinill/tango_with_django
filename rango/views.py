from django.http import HttpResponse
from django.shortcuts import render
from rango.models import Category, Page

def index(request):
    context_list = Category.objects.order_by('-likes')[:5]
    context_pages = Page.objects.order_by('-views')[:10]
    context_dict={'categories': context_list,
                  'pages':context_pages}
    return render(request, 'rango/index.html', context_dict)

def about(request):
    return HttpResponse("rango says hello in about page!")

def show_category(request, category_name_slug):
    context_dict = {}

    try:
    # Can we find a category name slug with the given name?
    # If we can't, the .get() method raises a DoesNotExist exception.
    # So the .get() method returns one model instance or raises an exception.
        category = Category.objects.get(slug=category_name_slug)

    # Retrieve all of the associated pages.
    # Note that filter() will return a list of page objects or an empty list
        pages = Page.objects.filter(category=category)

        context_dict['pages']=pages
        context_dict['category']=category
    except Category.DoesNotExist:
        context_dict['category']= None
        context_dict['pages']= None

    return render(request, 'rango/category.html', context_dict)

