from django.shortcuts import render,redirect,HttpResponseRedirect
from django.http import HttpResponse
from django.contrib.auth.hashers import make_password,check_password
from .models.product import Product
from .models.category import Category
from .models.customer import Customer
from .models.order import Order
from .middlewares.auth import  auth_middleware
from django.views import View

# Create your views here.


def index(request):
    if request.method=='GET':
            cart=request.session.get('cart')
            if not cart:
                request.session['cart']={}
            product = None
            categories = Category.get_all_categories()

            categoryId = request.GET.get("category")

            if categoryId:
                product = Product.get_all_product_by_id(categoryId)
            else:
                product = Product.get_all_product()

            data = {}
            data['products'] = product
            data['categories'] = categories

            print(request.session.get('email'))
            # return render(request,'orders/order.html')
            return render(request, 'index.html', data)
    else:
        product=request.POST.get('product_id')
        remove=request.POST.get('remove')
        cart=request.session.get('cart')
        if cart:
            quantity=cart.get(product)
            if quantity:
                if remove:
                    if quantity<=1:
                        cart.pop(product)
                    else:
                        cart[product]=quantity-1
                else:
                    cart[product] = quantity+1
            else:
                cart[product]=1
        else:
            cart={}
            cart[product] = 1

        request.session['cart']=cart
        print(request.session['cart'])
        return redirect('homepage')


def validateuser(customer):
    error_msg = None
    if not customer.first_name:
        error_msg = "First name is required"
    elif not customer.last_name:
        error_msg = "Last name is required"
    elif not customer.password:
        error_msg = "Password is required"
    elif len(customer.password) < 6:
        error_msg = "Password should have more than 6 character"
    elif customer.isExist():
        error_msg = "Email id is already Exist"
    return error_msg


def registerUser(request):

    first_name = request.POST.get('firstname')
    last_name = request.POST.get('lastname')
    email = request.POST.get('email')
    password = request.POST.get('password')
    value = {
        'first_name': first_name,
        'last_name': last_name,
        'email': email
    }

    customer = Customer(first_name=first_name,
                        last_name=last_name,
                        email=email,
                        password=password)

    error_msg = None
    error_msg = validateuser(customer)

    if not error_msg:
        customer.password = make_password(customer.password)
        customer.register()
        return redirect('homepage')
    else:
        data = {
            'error': error_msg,
            'values': value

        }
        return render(request, 'signup.html', data)


def signup(request):
    if request.method == "GET":
        return render(request, 'signup.html')
    else:
        return registerUser(request)
#class based view

class Login(View):
    return_url=None
    def get(self,request):
        Login.return_url=request.GET.get('return_url')
        return render(request, 'login.html')

    def post(self,request):
        email = request.POST.get('email')
        password = request.POST.get('password')

        error_msg = None
        customer = Customer.get_customer_by_email(email)
        if customer:
            flag = check_password(password, customer.password)
            if flag:
                request.session['customer_id'] = customer.id
                request.session['email'] = customer.email
                if Login.return_url:
                    return HttpResponseRedirect(Login.return_url)
                else:
                    Login.return_url = None
                    return redirect('homepage')
            else:
                error_msg = "Email or Password Invalid !!"
        else:
            error_msg = "Email or Password Invalid !!"

        return render(request, 'login.html', {'error': error_msg})



def logout(request):
    request.session.clear()
    return redirect('login')

def cart(request):
    ids=list(request.session.get('cart').keys())
    products=Product.get_cart_products_by_id(ids)
    print(products)
    return render(request,'cart.html',{'products':products})


def checkout(request):
    if request.session.get('customer_id'):
        if request.method=='POST':
            address=request.POST.get('address')
            phone=request.POST.get('phone')
            customer=request.session.get('customer_id')
            cart=request.session.get('cart')
            products=Product.get_cart_products_by_id(list(cart.keys()))
            print(address,phone,customer,cart,products)
            for p in products:
                 order=Order(  customer=Customer(id=customer),
                                 product=p,
                                 price=p.price,
                                 address=address,
                                 phone=phone,
                                 quantity=cart.get(str(p.id))
                           )
                 order.placeOrder()
            request.session['cart']={}
            return redirect('cart')
    else:
        return redirect('login')

@auth_middleware
def orders(request):
    if request.method == "GET":
        customer=request.session.get('customer_id')
        orders=Order.get_orders_by_customer(customer)
        print(orders)
        return render(request, 'order.html',{'orders':orders})

