from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Product, CartItem, Order
from django.contrib.auth.models import User
from django.contrib import messages



def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        # login if anthenticate success
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            message = 'Incorrect Username or Password Entered'
            messages.error(request, message)
            return render(request, 'login.html')
    else:
        return render(request, 'login.html')



def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        email = request.POST.get('email')
        # throw error when user exists
        try:
            user = User.objects.create_user(username=username, password=password, email=email)
            login(request, user)
            return redirect('home')
        except IntegrityError:
            messages.error(request, 'Username Already Exists')
            return redirect('register')
    else:
        return render(request, 'register.html')
        

def logout_view(request):
    logout(request)
    messages.success(request, 'User Logged Out')
    return redirect('login')


def home_view(request):
    products = Product.objects.all()
    context = {'products': products}
    return render(request, 'home.html', context)


@login_required(login_url='login')
def add_to_cart(request, product_id):
    product = Product.objects.get(pk=product_id)
    cart_item, created = CartItem.objects.get_or_create(user=request.user, product=product)
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    message = 'Added ' + product.title + ' to the Cart'
    messages.success(request, message)
    return redirect('home')




@login_required(login_url='login')
def cart_view(request):
    cart_items = CartItem.objects.filter(user=request.user)
    cart_total = 0
    for item in cart_items:
        cart_total += item.product.price
    context = {
        'cart_items': cart_items,
        'cart_total': cart_total,
    }
    return render(request, 'cart.html', context)


@login_required(login_url='login')
def checkout_view(request):
    cart_items = CartItem.objects.filter(user=request.user)
    total = 0
    for cart_item in cart_items:
        total += cart_item.product.price * cart_item.quantity
    order = Order.objects.create(user=request.user, total=total)
    products = set()
    for cart_item in cart_items:
        products.add(cart_item.product)
    order.products.set(products)
    cart_items.delete()
    message = 'Checkout Success'
    messages.success(request, message)
    return redirect('home')

@login_required(login_url='login')
def delete_cart_item_view(request, cart_item_id):
    cart_item = get_object_or_404(CartItem, pk=cart_item_id)
    if request.method == 'POST':
        cart_item.delete()
    return redirect('cart')

@login_required(login_url='login')
def order_history_view(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    context = {'orders': orders}
    return render(request, 'order_history.html', context)