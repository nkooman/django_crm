from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.forms import inlineformset_factory
from django.contrib import messages
from django.contrib.auth import authenticate, login as django_login, logout as django_logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from .models import *
from .forms import *
from .filters import *
from .decorators import *
# Create your views here.


@unauthenticated_user
def register(request):
    form = CreateUserForm()

    if request.method == 'POST':
        form = CreateUserForm(request.POST)

        if form.is_valid():
            user = form.save()

            customer = Group.objects.get(name='customer')
            user.groups.add(customer)

            username = form.cleaned_data.get('username')
            messages.success(request, 'Account was created for ' + username)

            return redirect('login')

    context = {'form': form}

    return render(request, 'accounts/register.html', context)


@unauthenticated_user
def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            django_login(request, user)

            return redirect('home') if any(group.name == 'admin' for group in request.user.groups.all()) else redirect('user')
        else:
            messages.info(request, 'Username or password is incorrect.')

    context = {}

    return render(request, 'accounts/login.html', context)


def logout(request):
    django_logout(request)

    return redirect('login')


@login_required(login_url='login')
@allowed_groups(allowed_groups=['admin'])
def home(request):
    orders = Order.objects.all()
    customers = Customer.objects.all()

    total_orders = orders.count()
    total_customers = customers.count()

    delivered = orders.filter(status="Delivered").count()
    pending = orders.filter(status="Pending").count()

    context = {
        'orders': orders,
        'customers': customers,
        'total_orders': total_orders,
        'total_customers': total_customers,
        'delivered': delivered,
        'pending': pending
    }

    return render(request, 'accounts/dashboard.html', context)


@allowed_groups(allowed_groups=['admin', 'customer'])
def user(request):
    context = {}

    return render(request, 'accounts/user.html')


@login_required(login_url='login')
@allowed_groups(allowed_groups=['admin'])
def products(request):
    products = Product.objects.all()

    return render(request, 'accounts/products.html', {'products': products})


@login_required(login_url='login')
@allowed_groups(allowed_groups=['admin'])
def customer(request, pk):
    customer = Customer.objects.get(id=pk)
    orders = customer.order_set.all()
    order_count = orders.count()

    order_filter = OrderFilter(request.GET, queryset=orders)
    orders = order_filter.qs

    context = {'customer': customer,
               'orders': orders,
               'order_count': order_count,
               'order_filter': order_filter}

    return render(request, 'accounts/customer.html', context)


@login_required(login_url='login')
@allowed_groups(allowed_groups=['admin'])
def create_order(request, pk):
    OrderFormSet = inlineformset_factory(
        Customer, Order, fields=('product', 'status'), extra=10)
    customer = Customer.objects.get(id=pk)
    formset = OrderFormSet(queryset=Order.objects.none(), instance=customer)

    if request.method == 'POST':
        formset = OrderFormSet(request.POST, instance=customer)

        if formset.is_valid():
            formset.save()

            return redirect('/')

    context = {'formset': formset}

    return render(request, 'accounts/order_form.html', context)


@login_required(login_url='login')
@allowed_groups(allowed_groups=['admin'])
def update_order(request, pk):
    order = Order.objects.get(id=pk)
    form = OrderForm(instance=order)

    if request.method == 'POST':
        form = OrderForm(request.POST, instance=order)

        if form.is_valid():
            form.save()

            return redirect('/')

    context = {'form': form, 'order': order}

    return render(request, 'accounts/order_form.html', context)


@login_required(login_url='login')
@allowed_groups(allowed_groups=['admin'])
def delete_order(request, pk):
    order = Order.objects.get(id=pk)

    if request.method == 'POST':
        order.delete()

        return redirect('/')

    context = {'order': order}

    return render(request, 'accounts/delete.html', context)
