from datetime import datetime

from django.contrib.auth import authenticate, login, logout
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from rango.forms import CategoryForm, PageForm
from rango.forms import UserForm, UserProfileForm
from rango.models import Category, Page
from rango.webhose_search import run_query

def index(request):
    # A helper method
    # A helper method
    def get_server_side_cookie(request, cookie, default_val=None):
        val = request.session.get(cookie)
        if not val:
            val = default_val
        return val

    # Updated the function definition
    def visitor_cookie_handler(request):
        visits = int(get_server_side_cookie(request, 'visits', '1'))

        last_visit_cookie = get_server_side_cookie(request,
                                               'last_visit',
                                               str(datetime.now()))
        last_visit_time = datetime.strptime(last_visit_cookie[:-7],
                                            '%Y-%m-%d %H:%M:%S')
        # If it's been more than a day since the last visit...
        if (datetime.now() - last_visit_time).seconds > 0:
            visits = visits + 1
    # update the last visit cookie now that we have updated the count
            request.session['last_visit'] = str(datetime.now())
        else:
    # set the last visit cookie
            request.session['last_visit'] = last_visit_cookie
    # Update/set the visits cookie
        request.session['visits'] = visits


    request.session.set_test_cookie()
    category_list = Category.objects.order_by('-likes')[:5]
    page_list = Page.objects.order_by('-views')[:5]
    context_dict = {'categories': category_list, 'pages': page_list}
    # Obtain our Response object early so we can add cookie information.
    # Call function to handle the cookies
    visitor_cookie_handler(request)
    context_dict['visits'] = request.session['visits']

    response = render(request, 'rango/index.html', context_dict)
    # Return response back to the user, updating any cookies that need changed.
    return response

def about(request):
    request.session.delete_test_cookie()
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


def register(request):
    # A boolean value for telling the template
    # whether the registration was successful.
    # Set to False initially. Code changes value to
    # True when registration succeeds.
    registered = False
    # If it's a HTTP POST, we're interested in processing form data.
    if request.method == 'POST':
    # Attempt to grab information from the raw form information.
    # Note that we make use of both UserForm and UserProfileForm.
        user_form = UserForm(data=request.POST)
        profile_form = UserProfileForm(data=request.POST)
        # If the two forms are valid...
        if user_form.is_valid() and profile_form.is_valid():
    # Save the user's form data to the database.
            user = user_form.save()
    # Now we hash the password with the set_password method.
    # Once hashed, we can update the user object.
            user.set_password(user.password)
            user.save()
    # Now sort out the UserProfile instance.
    # Since we need to set the user attribute ourselves,
    # we set commit=False. This delays saving the model
    # until we're ready to avoid integrity problems.
            profile = profile_form.save(commit=False)
            profile.user = user
    #Did the user provide a profile picture?
    # If so, we need to get it from the input form and
    #put it in the UserProfile model.
            if 'picture' in request.FILES:
                profile.picture = request.FILES['picture']
    # Now we save the UserProfile model instance.
            profile.save()
    # Update our variable to indicate that the template
    # registration was successful.
            registered = True
        else:
    # Invalid form or forms - mistakes or something else?
    # Print problems to the terminal.
            print(user_form.errors, profile_form.errors)
    else:
    # Not a HTTP POST, so we render our form using two ModelForm instances.
    # These forms will be blank, ready for user input.
        user_form = UserForm()
        profile_form = UserProfileForm()
    # Render the template depending on the context.
        return render(request,'rango/register.html',
            {'user_form': user_form,
            'profile_form': profile_form,
             'registered': registered})


def user_login(request):
    # If the request is a HTTP POST, try to pull out the relevant information
    if request.method == 'POST':
    # Gather the username and password provided by the user.
    # This information is obtained from the login form.
    # We use request.POST.get('<variable>') as opposed
    # to request.POST['<variable>'], because the
    # request.POST.get('<variable>') returns None if the
    # value does not exist, while request.POST['<variable>']
    # will raise a KeyError exception.
        username = request.POST.get('username')
        password = request.POST.get('password')

    # Use Django's machinery to attempt to see if the username/password
    # combination is valid - a User object is returned if it is.
        user = authenticate(username=username, password=password)
    # If we have a User object, the details are correct.
    # If None (Python's way of representing the absence of a value), no user
    # with matching credentials was found.
        if user:
        # Is the account active? It could have been disabled.
            if user.is_active:
        # If the account is valid and active, we can log the user in.
        # We'll send the user back to the homepage.
                login(request,user)
                return HttpResponseRedirect(reverse('index'))
            else:
        # An inactive account was used - no logging in
                return HttpResponse("Your Rango account is disabled.")
        else:
        # Bad login details were provided. So we can't log the user in.
             print("Invalid login details: {0}, {1}".format(username, password))
             return HttpResponse("Invalid login details supplied.")
    # The request is not a HTTP POST, so display the login form.
    # This scenario would most likely be a HTTP GET.
    else:
    # No context variables to pass to the template system, hence the
    # blank dictionary object...
        return render(request, 'rango/login.html', {})

# Use the login_required() decorator to ensure only those logged in can access the view.
@login_required
def user_logout(request):
    # Since we know the user is logged in, we can now just log them out.
    logout(request)
    # Take the user back to the homepage.
    return HttpResponseRedirect(reverse('index'))
@login_required
def restricted(request):
        return HttpResponse("Since you're logged in, you can see this text!")

def search(request):
    result_list = []

    if request.method =='POST':
        query = request.POST['query'].strip()
        if query:
            result_list = run_query(query)

    return render(request, 'rango/search.html', {'result_list': result_list})
