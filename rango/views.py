from django.http import HttpResponse
from django.shortcuts import render
from rango.models import Category, Page
from rango.forms import CategoryForm, PageForm

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

def add_category(request):
    form = CategoryForm()

    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():

        #have we been provided with a valid form?
            form.save(commit=True)
        # Now that the category is saved
        # We could give a confirmation message
        # But since the most recent category added is on the index page
        # Then we can direct the user back to the index page.

            return index(request)
        else:
            print(form.errors)

    return render(request, 'rango/add_category.html', {'form':form})

def add_page(request, category_name_slug):
    try:
        category = Category.objects.get(slug=category_name_slug)
    except Category.DoesNotExist:
        category = None

    form = PageForm()
    if request.method == 'POST':
        form = PageForm(request.POST)
        if form.is_valid():
            if category:
                page = form.save(commit=False)
                page.category = category
                page.views = 0
                page.save()
                return show_category(request, category_name_slug)
            else:
                print(form.errors)

    context_dict = {'form':form,'category':category}
    return render (request, 'rango/add_page.html',context_dict)