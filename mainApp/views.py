from django.shortcuts import render
from users.models import Vendor, Consumer
from inventory.models import Product, ProductInventory, ProductAttribute, ProductAttributeValue, Category, Sub_Category, ProductAttributeValues, Rating, Review, Wishlist, WishlistItem, Cart, CartItem, Order, OrderItem, ShippingAddress, SalesRecord
from django.contrib.auth.decorators import login_required
import jwt
from django.conf import settings
import json
from django.http import JsonResponse, HttpResponse
from django.db.models import Avg
import bleach
from django.db.models import F
import os
from datetime import datetime, timedelta
import re
from chat.models import Chat, Message

from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags


'''
DONE search&filter
DONE user registration&login, password change
DONE product creation
DONE product detail page and rating&reviews
DONE wishlist
DONE product delete&update
DONE dashboard for consumers and for vendors
DONE add to cart & remove from cart & update cart
DONE checkout
DONE chat

anu xval moxval cotas ifiqreb ras gaaketeb checkoutis magivrad tu araferi vikideb da egreve viwyeb ro dokerizeba
gavuketo am proeqts

'''

def sanitize_input(user_input):
    cleaned_input = bleach.clean(user_input, tags=['p', 'strong', 'em'], attributes={'*': ['class']})
    return cleaned_input

def home(request):

    attr_dict = {}
    len_wish = 0
    wishlist_items = None
    cart_data = 'None'
    total_price = []

    try:
        if request.user.is_vendor:
            vendor = Vendor.objects.get(email=request.user)
        else:
            vendor = request.user
    except:
        vendor = request.user

    if request.method == 'GET':
        # Retrieve all ProductInventory instances
        
        try:
            cartData = Cart.objects.get(user=vendor)

            cart_data = cartData.items.all()

            for i in cart_data:
                total_price.append(i.product.retail_price * i.quantity)
        except:
            cart_data = 'None'

        try:
            wishlist12 = Wishlist.objects.get(user=vendor)

            wishlist_items = WishlistItem.objects.select_related('wishlist').filter(wishlist=wishlist12)

            len_wish = len(wishlist_items)
        except:
            wishlist_items = None
            len_wish = 0

        q = request.GET.get('search') if request.GET.get('search') != None else ''

        if q == '':
            product_inventories = ProductInventory.objects.select_related('product').all()
        else:
            product_inventories = ProductInventory.objects.filter(product__name__icontains=sanitize_input(q))

        categories = Category.objects.all()

        # Loop through each ProductInventory instance
        for product_inventory in product_inventories:
            # Retrieve all associated attribute values for this ProductInventory instance
            attribute_values = product_inventory.productattributevaluess.all().distinct()
            
            # Loop through each attribute value and print its name and value
            for attribute_value in attribute_values:
                # Check if the attribute name already exists in the reorganized data
                if attribute_value.attributevalues.attribute.name in attr_dict:
                    if attribute_value.attributevalues.value not in attr_dict[attribute_value.attributevalues.attribute.name]:
                        # If it's not in the list, append it
                        attr_dict[attribute_value.attributevalues.attribute.name].append(attribute_value.attributevalues.value)
                else:
                    # If it doesn't exist, create a new list with the value
                    attr_dict[attribute_value.attributevalues.attribute.name] = [attribute_value.attributevalues.value]

    chat_seen = 'You Have Unread Message In This Chat!' + " "
    chat_seen_bol = False

    if request.user.is_authenticated:
        all_chats = Chat.objects.filter(sender=vendor) | Chat.objects.filter(receiver=vendor)

        for i in all_chats:

            if i.sender_seen == False and i.sender == vendor:
                chat_seen += i.receiver.email + " "
                chat_seen_bol = True
            elif i.receiver_seen == False and i.receiver.email == vendor.email:
                chat_seen += i.sender.email + " "
                chat_seen_bol = True
    else:
        chat_seen = 'You Have Unread Message In This Chat!' + " "
        chat_seen_bol = False

    context = {'vendor': vendor, 'attrs': attr_dict.items(), 'product_inventories':product_inventories, 'categories': categories, 'q': q, 'len_wish': len_wish, "wishprods": wishlist_items, 'cart_data': cart_data, 'len_cart': len(cart_data), 'total_price': sum(total_price), "chat_seen": chat_seen, 'chat_seen_bol': chat_seen_bol}

    return render(request, 'mainApp/home.html', context)

def add_products(request):
    vendor = Vendor.objects.get(email=request.user)

    category = Category.objects.all()
    sub_category = Sub_Category.objects.all()

    categoryArr = []
    subCategoryArr = []

    for i in category:
        categoryArr.append(i.name)
    
    for k in sub_category:
        subCategoryArr.append(k.name)

    context = {'vendor': vendor, "category": categoryArr, "subCategory": subCategoryArr}

    return render(request, 'mainApp/add_product.html', context)

def product_detail(request, sku):

    try:
        if request.user.is_vendor:
            vendor = Vendor.objects.get(email=request.user)
        else:
            vendor = request.user
    except:
        vendor = request.user

    total_price = []
        
    try:
        cartData = Cart.objects.get(user=vendor)

        cart_data = cartData.items.all()

        for i in cart_data:
            total_price.append(i.product.retail_price * i.quantity)
    except:
        cart_data = 'None'

    try:
        wishlist12 = Wishlist.objects.get(user=vendor)

        wishlist_items = WishlistItem.objects.filter(wishlist=wishlist12)

        len_wish = len(wishlist_items)
    except:
        wishlist_items = None
        len_wish = 0

    product = ProductInventory.objects.filter(product__unique_id=sku)

    produ_name = ''

    for i in product:
        produ_name = i.product.name

    reorganized_data1 = {}
        
    # Identify the default product
    default_product = product.values('productattributevaluess__attributevalues__attribute__name', "productattributevaluess__attributevalues__value")
        
    for i in default_product:
        attribute_name = i["productattributevaluess__attributevalues__attribute__name"]
        attribute_value = i["productattributevaluess__attributevalues__value"]
        reorganized_data1[attribute_name] = [attribute_value]

    product32 = product[0].product

    reviews = product32.reviews.all().order_by('-created_at')
    rating_instance, _ = Rating.objects.get_or_create(product=product32)
    average_rating = rating_instance.average_rating
    num_ratings = rating_instance.num_ratings

    values = []

    for attr, values12 in reorganized_data1.items():
        for j in values12:
            values.append(j)
    
    context = {
        "product": product,
        "vendor": vendor,
        "produ_name": produ_name,
        'sku': sku,
        "rec_data": values, 
        "rec_data2": reorganized_data1.items(), 
        'reviews': reviews, 'average_rating': average_rating, 'num_ratings': num_ratings,
        'len_wish': len_wish, "wishprods": wishlist_items,
        'cart_data': cart_data, 'len_cart': len(cart_data), 'total_price': sum(total_price)
    }
    return render(request, 'mainApp/product_detail.html', context)

def cart(request):
    cart_items = None

    if request.user.is_authenticated:
        # Handle cart data for registered users
        try:
            if request.user.is_vendor:
                vendor = Vendor.objects.get(email=request.user)
            else:
                vendor = request.user
        except:
            vendor = request.user

        total_price = []
            
        try:
            cartData = Cart.objects.get(user=vendor)

            cart_data = cartData.items.all()

            for i in cart_data:
                total_price.append(i.product.retail_price * i.quantity)

            
        except:
            cart_data = 'None'

        try:
            wishlist12 = Wishlist.objects.get(user=vendor)

            wishlist_items = WishlistItem.objects.filter(wishlist=wishlist12)

            len_wish = len(wishlist_items)
        except:
            wishlist_items = None
            len_wish = 0

        page = 'cart' if request.path == '/cart/' else 'other'

        
        context = {
            "vendor": vendor,
            'len_wish': len_wish, "wishprods": wishlist_items,
            'cart_data': cart_data, 'len_cart': len(cart_data), 'total_price': sum(total_price),
            'page': page
        }
        return render(request, 'mainApp/cart.html', context)
    else:
        cart_items = request.COOKIES.get('cart_items')

        total_price = 0
        cart_data = []
        attr_values = []

        if cart_items:
            cart_items = eval(cart_items)  # Convert the string back to a list

            for cart_item in cart_items:
                product = ProductInventory.objects.get(sku=cart_item['sku'])
                price = product.retail_price * int(cart_item['quantity'])
                total_price += price

                attribute_values = product.productAttributes.all()
                if attribute_values.exists():
                    attr_values.append(attribute_values.first().value)
                
                cart_data.append({
                    'name': product.product.name,
                    'img_url': product.img_url.url,
                    'quantity': int(cart_item['quantity']),
                    'fullPrice': price,
                    'price': product.retail_price,
                    'sku': product.sku,
                    "stock": product.stock,
                    'attr_values': attr_values
                })

        page = 'cart' if request.path == '/cart/' else 'other'
        
        context = {"cart_data": cart_data, "total_price": total_price, 'page': page}

        return render(request, 'mainApp/cart.html', context=context)

def checkout_page(request):
    # Get the product information from the URL parameters
    products = []
    total_price = request.GET.get('total_price', '0.00')  # Default value if parameter is not provided

    # Loop through the URL parameters to extract product information
    for key, value in request.GET.items():
        if key.startswith('product'):
            parts = key.split('_')
            index = parts[1].replace('quantity', '')
            if len(parts) == 2 and value:
                product_info = {
                    'quantity': request.GET.get(f'product_quantity{index}', '0'),
                    'id': request.GET.get(f'product_id{index}', ''),
                    'price': request.GET.get(f'product_price{index}', '0.00')
                }
                if product_info["price"] != '0.00':
                    products.append(product_info)

    # Process the product information as needed
    # For example, you can render a template with this information

    products2 = []

    for i in products:
        product = ProductInventory.objects.filter(sku=i['id'])

        for j in product:
            product_info2 = {
                'name': j.product.name,
                'img_url': j.img_url.url,
                'price': j.retail_price,
                'quantity': i['quantity'],
                'sku': j.sku
            }
            
            products2.append(product_info2)

    consumer = 'None'
    if request.user.is_authenticated:
        consumer = Consumer.objects.get(email=request.user)
        shippingAdr = ShippingAddress.objects.get(costumer=consumer)

    context = {
        'products': products2,
        'total_price': total_price,
        'consumer': consumer,
        'shippingAdr': shippingAdr
    }
    return render(request, 'mainApp/checkout_page.html', context)

"""
the code below is for ajax requests,
i tried to separate functions for registered users and functions that are for guest users
"""

def filter_sub_products_forproduct_detail(request):
    if request.method == 'GET':
        sku = request.GET.get('sku_for_prod')

        product = ProductInventory.objects.get(sku=sku)

        reorganized_data1 = {}

        attribute_values = product.productattributevaluess.all().distinct()
                
        # Loop through each attribute value and print its name and value
        for attribute_value in attribute_values:
            # Check if the attribute name already exists in the reorganized data
            if attribute_value.attributevalues.attribute.name in reorganized_data1:
                if attribute_value.attributevalues.value not in reorganized_data1[attribute_value.attributevalues.attribute.name]:
                    # If it's not in the list, append it
                    reorganized_data1[attribute_value.attributevalues.attribute.name].append(attribute_value.attributevalues.value)
            else:
                # If it doesn't exist, create a new list with the value
                reorganized_data1[attribute_value.attributevalues.attribute.name] = [attribute_value.attributevalues.value]

        context = {
            'name':  product.product.name,
            'img_url': product.img_url.url,
            'price': product.retail_price,
            "desc": product.product.description,
            'stock': product.stock,
            'sku': product.sku,
            'rec_data': reorganized_data1
        }

        # Return the filtered products as HTML response
        return JsonResponse(context)
    else:
        # Handle invalid request method
        return JsonResponse({'error': 'Invalid request method'}, status=405)

def filter_products_for_collections(request):
    sort_option = request.GET.get('sort', 'low_to_high')
    filters_cat = request.GET.get('filters_cat')
    filters_attr = request.GET.get('filters_attr')
    search_q = request.GET.get('search_q')

    if filters_cat: 
        filters_cat_dict = json.loads(filters_cat)
    else:
        filters_cat_dict = None

    if filters_attr: 
        filters_attr_dict = json.loads(filters_attr)
    else:
        filters_attr_dict = None

    if search_q:
        products = ProductInventory.objects.filter(product__name__icontains=search_q, stock__gt=0).order_by('retail_price').distinct()
    else:
        products = ProductInventory.objects.filter(stock__gt=0).order_by('retail_price').distinct()

    if filters_cat_dict: 
        products = products.filter(product__category__name__in=filters_cat_dict)

    if filters_attr_dict: 
        products = products.filter(productattributevaluess__attributevalues__value__in=filters_attr_dict)

    # Apply sorting
    if sort_option == 'low_to_high':
        products = products.order_by('retail_price')
    elif sort_option == 'high_to_low':
        products = products.order_by('-retail_price') 

    serialized_products = [{
            'name': product.product.name,
            'price': product.retail_price,
            'unique_id': product.product.unique_id,
            'img_url': product.img_url.url,
            'pk_forWish': product.pk,
        
        } for product in products.distinct()]


    return JsonResponse({'products': serialized_products})

# these views are for comments and reviews
def delete_review(request):
    review_id = request.POST.get('reviewId')
    # Save the review
    review = Review.objects.get(pk=int(review_id))
    review.delete()

    return JsonResponse({
        "message": "Review deleted successfully!",
        "status": "success"
    })

def submit_review(request):
    if request.method == 'POST':
                # Access the JWT token from the Authorization header
        auth_header = request.headers.get('Authorization')
        
        if auth_header and auth_header.startswith('Bearer '):
            jwt_token = auth_header.split(' ')[1]
            
            try:
                # Decode the JWT token using the secret key
                decoded_data = jwt.decode(jwt_token, settings.SECRET_KEY, algorithms=['HS256'])
                
                # Access user information from the decoded token
                user_id = decoded_data.get('user_id')
                user = Consumer.objects.get(pk=user_id)

                # Access expiration time from the decoded token
                expiration_time = decoded_data.get('exp')
                
                # Convert expiration time from Unix timestamp to datetime object
                expiration_datetime = datetime.utcfromtimestamp(expiration_time)
                
                # Calculate remaining time until expiration
                current_datetime = datetime.utcnow()
                remaining_time = expiration_datetime - current_datetime
                
                print("Token expiration time:", expiration_datetime)
                print("Remaining time until expiration:", remaining_time)
            
                if request.POST.get('rating'):
                    rating = int(request.POST.get('rating'))    
                else:
                    rating = 0

                comment = request.POST.get('comment')
                user = request.user
                product_id = request.POST.get('product_id')

                product = Product.objects.get(unique_id=product_id)

                # Save the review
                review = Review.objects.create(product=product, user=user, rating=rating, comment=sanitize_input(comment))

                # Calculate average rating
                average_rating = Review.objects.filter(product=product).aggregate(Avg('rating'))['rating__avg']

                # Update or create rating instance for the product
                rating_instance, created = Rating.objects.get_or_create(product=product)
                rating_instance.average_rating = average_rating
                rating_instance.num_ratings = Review.objects.filter(product=product).count()
                rating_instance.save()

                return JsonResponse({
                    'user': user.username,
                    'rating': rating,
                    'comment': comment,
                    'average_rating': average_rating,
                    'num_ratings': rating_instance.num_ratings
                })
            
            except jwt.ExpiredSignatureError:
                return JsonResponse({'error25': 'Token has expired'}, status=401)
            except jwt.InvalidTokenError:
                return JsonResponse({'error': 'Invalid token'}, status=401)
            except Exception as e:
                traceback_str = traceback.format_exc()
                return JsonResponse({'error': f'An error occurred: {str(e)},\n Traceback: {traceback_str}'}, status=500)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)

import traceback
@login_required
def ajax_viewFor_CreteProducts(request):
    if request.method == 'POST':
        # Access the JWT token from the Authorization header
        auth_header = request.headers.get('Authorization')
        
        if auth_header and auth_header.startswith('Bearer '):
            jwt_token = auth_header.split(' ')[1]
            
            try:
                # Decode the JWT token using the secret key
                decoded_data = jwt.decode(jwt_token, settings.SECRET_KEY, algorithms=['HS256'])
                
                # Access user information from the decoded token
                user_id = decoded_data.get('user_id')
                user = Vendor.objects.get(pk=user_id)

                # Access the product_obj and sub_prod_obj as JSON strings
                product_obj_str = request.POST.get('product_obj')
                sub_prod_obj_str = request.POST.get('sub_prod_obj')

                lent = 1
                fine1 = False
                fine2 = False
                
                if request.POST.get('lent'):
                    lent = request.POST.get('lent')
                else:
                    lent = 1

                # Parse the JSON strings into Python objects
                product_data = json.loads(product_obj_str)
                sub_product_data = json.loads(sub_prod_obj_str)

                category = None
                sub_category = None
                product = None

                if int(lent) == 1:                                  
                    try:
                        check_sku = ProductInventory.objects.get(sku=sub_product_data['product_id_1']['product_sku']+f'-{user}')

                        if check_sku:
                            fine1 = False
                            return JsonResponse({'message12521': f"please choose different SKU, because one of your product already have it '{sub_product_data['product_id_1']['product_sku']}' "})
                    except:
                        category = Category.objects.get_or_create(name=product_data['category'].title())
                        sub_category = Sub_Category.objects.get_or_create(name=product_data['product_sub_category'].title(), parent=category[0])
                        product = Product.objects.get_or_create(name=product_data["product_name"], vendor=user, description=product_data["product_desc"], category=sub_category[0])

                        if product[1]:
                            product[0].unique_id = product[0].slug + f"-{product[0].pk}"
                            product[0].save()
                    
                        fine1 = True
                if int(lent) > 1:
                    try:
                        for i_for_product_id in range(int(lent)):
                            for j in sub_product_data[i_for_product_id].keys():
                                if int(j.split(sep="_")[2]) == i_for_product_id:

                                    check_sku = ProductInventory.objects.get(sku=sub_product_data[i_for_product_id][f'product_id_{i_for_product_id}']['product_sku']+f'-{user}')

                                    if check_sku:
                                        fine2 = False
                                        return JsonResponse({'message12521': f"please choose different SKU, because one of your product already have it '{sub_product_data[i_for_product_id][f'product_id_{i_for_product_id}']['product_sku']}' "})
                    except:
                        category = Category.objects.get_or_create(name=product_data['category'].title())
                        sub_category = Sub_Category.objects.get_or_create(name=product_data['product_sub_category'].title(), parent=category[0])
                        product = Product.objects.get_or_create(name=product_data["product_name"], vendor=user, description=product_data["product_desc"], category=sub_category[0])

                        if product[1]:
                            product[0].unique_id = product[0].slug + f"-{product[0].pk}"
                            product[0].save()

                        fine2 = True

                if int(lent) == 1 and fine1:
                        request.FILES.get('image').name = sub_product_data['product_id_1']['product_sku'] + request.FILES.get('image').name

                        sub_product = ProductInventory.objects.get_or_create(
                            sku=sub_product_data['product_id_1']['product_sku']+f'-{user}',
                            retail_price=float(sub_product_data['product_id_1']['product_price']),
                            is_default=True,
                            img_url=request.FILES.get('image'),
                            stock=int(sub_product_data['product_id_1']['product_stock']),
                            product=product[0]
                        )

                        arr1 = []

                        for i in sub_product_data['product_id_1'].keys():
                            if i.startswith('attr'):
                                arr1.append(i.split(sep='_')[1])
                        
                        for v in arr1:
                            attr = ProductAttribute.objects.get_or_create(name=v.title())
                            attr_value = ProductAttributeValue.objects.get_or_create(
                                attribute=attr[0], 
                                value=sub_product_data['product_id_1'][f"attr_{v}"].title()
                            )

                            trgh_attr_value = ProductAttributeValues.objects.get_or_create(
                                attributevalues=attr_value[0], 
                                productinventory=sub_product[0]
                            )

                        if sub_product[1]:
                            sub_product[0].save()
                elif int(lent) > 1 and fine2:
                    for i_for_product_id in range(int(lent)):
                        for j in sub_product_data[i_for_product_id].keys():
                            if int(j.split(sep="_")[2]) == i_for_product_id:
                                request.FILES.getlist('image')[i_for_product_id].name = sub_product_data[i_for_product_id][f'product_id_{i_for_product_id}']['product_sku'] + request.FILES.getlist('image')[i_for_product_id].name

                                sub_product = ProductInventory.objects.get_or_create(
                                    sku=sub_product_data[i_for_product_id][f'product_id_{i_for_product_id}']['product_sku']+f'-{user}',
                                    retail_price=float(sub_product_data[i_for_product_id][f'product_id_{i_for_product_id}']['product_price']),
                                    is_default=sub_product_data[i_for_product_id][f'product_id_{i_for_product_id}']['form_check_input'],
                                    img_url=request.FILES.getlist('image')[i_for_product_id],
                                    product=product[0],
                                    stock=int(sub_product_data[i_for_product_id][f'product_id_{i_for_product_id}']['product_stock'])
                                )

                                arr1 = []

                                for i in sub_product_data[i_for_product_id][f'product_id_{i_for_product_id}'].keys():
                                    if i.startswith('attr'):
                                        arr1.append(i.split(sep='_')[1])
                                
                                for v in arr1:
                                    if v is not None:
                                        attr = ProductAttribute.objects.get_or_create(name=v.title())
                                        attr_value = ProductAttributeValue.objects.get_or_create(
                                            attribute=attr[0], 
                                            value=sub_product_data[i_for_product_id][f'product_id_{i_for_product_id}'][f"attr_{v}"].title()
                                        )

                                    #'product_id_attr_Size'

                                        trgh_attr_value = ProductAttributeValues.objects.get_or_create(
                                            attributevalues=attr_value[0], 
                                            productinventory=sub_product[0]
                                        )

                                if sub_product[1]:
                                    sub_product[0].save()

                if int(lent) == 1:
                    # For demonstration purposes, let's just return a simple response
                    response_data = {'product': {
                       "product_id": product[0].unique_id,
                    },
                        "message": "Product Created Successfully"
                    }
                elif int(lent) > 1:
                    response_data = {'product': {
                        "product_id": product[0].unique_id,
                    },
                        "message": "Product Created Successfully"
                    }

                return JsonResponse(response_data)
            
            except jwt.ExpiredSignatureError:
                return JsonResponse({'error': 'Token has expired'}, status=401)
            except jwt.InvalidTokenError:
                return JsonResponse({'error': 'Invalid token'}, status=401)
            except Exception as e:
                traceback_str = traceback.format_exc()
                return JsonResponse({'error': f'An error occurred: {str(e)},\n Traceback: {traceback_str}'}, status=500)
            
from datetime import datetime
@login_required
def deleteProduct(request):
    if request.method == 'POST':
        # Access the JWT token from the Authorization header
        auth_header = request.headers.get('Authorization')
        
        if auth_header and auth_header.startswith('Bearer '):
            jwt_token = auth_header.split(' ')[1]
            
            try:
                # Decode the JWT token using the secret key
                decoded_data = jwt.decode(jwt_token, settings.SECRET_KEY, algorithms=['HS256'])
                
                # Access user information from the decoded token
                user_id = decoded_data.get('user_id')
                user = Vendor.objects.get(pk=user_id)

                # Access expiration time from the decoded token
                expiration_time = decoded_data.get('exp')
                
                # Convert expiration time from Unix timestamp to datetime object
                expiration_datetime = datetime.utcfromtimestamp(expiration_time)
                
                # Calculate remaining time until expiration
                current_datetime = datetime.utcnow()
                remaining_time = expiration_datetime - current_datetime
                
                print("Token expiration time:", expiration_datetime)
                print("Remaining time until expiration:", remaining_time)

                delete_product = request.POST.get('sku')
                default = request.POST.get('default')
                uniqueId = request.POST.get('uniqueId')

                if default == "True":
                    product = Product.objects.get(unique_id=uniqueId)
                    # Find the default sub-product associated with the default product
                    default_sub_product = ProductInventory.objects.filter(product=product, is_default=True).first()

                    if default_sub_product:
                        # Prepare the list of alternative sub-products
                        alternative_sub_products = ProductInventory.objects.filter(product=product, is_default=False)

                        if  len(alternative_sub_products) == 0:
                            # Proceed with deleting the product
                            ProductAttributeValues.objects.filter(productinventory=default_sub_product).delete()
                            
                            # Retrieve the path of the photo associated with the sub-product
                            photo_path = default_sub_product.img_url.url

                            # Delete the photo file from the storage
                            if os.path.exists(f'static{photo_path}'):
                                os.remove(f'static{photo_path}')

                            default_sub_product.delete()
                            
                            return JsonResponse({'success': 'Product deleted successfully'})
                        else:
                            alternative_products = [{"sku": sub_product.sku, "name": sub_product.product.name} for sub_product in alternative_sub_products]
                            return JsonResponse({'warning': 'You are deleting the default product. Please choose the next default product.', 'alternatives': alternative_products, 'delete_product': delete_product})
                    else:
                        return JsonResponse({'error': 'Something went wrong, try again'})
                        
                else:
                    product = Product.objects.get(unique_id=uniqueId)
                    # Proceed with deleting the product
                    delete_sub_product = ProductInventory.objects.get(product=product, sku=delete_product)

                    ProductAttributeValues.objects.filter(productinventory=delete_sub_product).delete()
                    
                    # Retrieve the path of the photo associated with the sub-product
                    photo_path = delete_sub_product.img_url.url

                    # Delete the photo file from the storage
                    if os.path.exists(f'static{photo_path}'):
                        os.remove(f'static{photo_path}')

                    delete_sub_product.delete()
                    
                    return JsonResponse({'success': 'Product deleted successfully'})
            
            except jwt.ExpiredSignatureError:
                return JsonResponse({'error25': 'Token has expired'}, status=401)
            except jwt.InvalidTokenError:
                return JsonResponse({'error': 'Invalid token'}, status=401)
            except Exception as e:
                traceback_str = traceback.format_exc()
                return JsonResponse({'error': f'An error occurred: {str(e)},\n Traceback: {traceback_str}'}, status=500)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)

def delete_default_product(request):
    if request.method == 'POST':
        new_default = request.POST.get('selectedSku')
        product_for_delete = request.POST.get('product_for_delete')

        new_default_prod = ProductInventory.objects.get(sku=new_default)

        new_default_prod.is_default = True

        new_default_prod.save()

        prod_to_del = ProductInventory.objects.get(sku=product_for_delete)

        ProductAttributeValues.objects.filter(productinventory=prod_to_del).delete()
                    
        # Retrieve the path of the photo associated with the sub-product
        photo_path = prod_to_del.img_url.url

        # Delete the photo file from the storage
        if os.path.exists(f'static{photo_path}'):
            os.remove(f'static{photo_path}')

        prod_to_del.delete()

        return JsonResponse({'success': 'Product deleted successfully'})
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)

def update_product(request, sku):
    vendor = Vendor.objects.get(email=request.user)

    product = Product.objects.get(unique_id = sku)

    sub_products = ProductInventory.objects.filter(product=product).order_by('created_at')

    attr_dict = {}

    # Loop through each ProductInventory instance
    for product_inventory in sub_products:
        # Retrieve all associated attribute values for this ProductInventory instance
        attribute_values = product_inventory.productattributevaluess.all().distinct()

        attr_dict[product_inventory.pk] = {}
                
        # Loop through each attribute value and print its name and value
        for attribute_value in attribute_values:
            # Check if the attribute name already exists in the reorganized data
            if attribute_value.attributevalues.attribute.name in attr_dict:
                if attribute_value.attributevalues.value not in attr_dict[product_inventory.pk][attribute_value.attributevalues.attribute.name]:
                    # If it's not in the list, append it
                    attr_dict[product_inventory.pk][attribute_value.attributevalues.attribute.name].append(attribute_value.attributevalues.value)
            else:
                # If it doesn't exist, create a new list with the value
                attr_dict[product_inventory.pk][attribute_value.attributevalues.attribute.name] = [attribute_value.attributevalues.value]

    category = Category.objects.all()
    sub_category = Sub_Category.objects.all()

    categoryArr = []
    subCategoryArr = []

    for i in category:
        categoryArr.append(i.name)
    
    for k in sub_category:
        subCategoryArr.append(k.name)

    context = {
        'vendor': vendor,
        "category": categoryArr,
        "subCategory": subCategoryArr,
        'product': product,
        'sku': sku,
        'sub_products': sub_products,
        'attr_dict': attr_dict.items(),
        'sub_length': len(sub_products),
    }

    return render(request, 'mainApp/update_product.html', context)

def update_product_ajax(request):
    if request.method == 'POST':
        sub_prod_obj_str = request.POST.get('sub_prod_obj')
        product_obj_str = request.POST.get('product_obj')
        unique_id_prod = request.POST.get('unique_id_prod')
        sub_product_data = json.loads(sub_prod_obj_str)
        product_data = json.loads(product_obj_str)

        user = Vendor.objects.get(email=request.user)

        print(sub_product_data)

        main_product = None
        main_product2 = Product.objects.get(unique_id=unique_id_prod)

        lent = 1
        fine1 = False
        fine2 = False
                
        if request.POST.get('lent'):
            lent = request.POST.get('lent')
        else:
            lent = 1
        
        # checking if SKU is already used by another product of the same vendor
        if int(lent) == 1:
            main_product = ProductInventory.objects.get(product__unique_id=unique_id_prod)
            try:
                if main_product.sku == sub_product_data[0]['product_id_0']['product_sku']+f'-{user}':
                    category = Category.objects.get_or_create(name=product_data['category'].title())
                    sub_category = Sub_Category.objects.get_or_create(name=product_data['product_sub_category'].title(), parent=category[0])
                    main_product2.category = sub_category[0]
                    main_product2.name = product_data["product_name"]
                    main_product2.description = product_data["product_desc"]

                    main_product2.unique_id = main_product2.slug + f"-{main_product2.pk}"
                    main_product2.save()

                    fine1 = True
                else:
                    check_sku = ProductInventory.objects.get(sku=sub_product_data['product_id_1']['product_sku']+f'-{user}')

                    if check_sku:
                        fine1 = False
                        return JsonResponse({'message12521': f"please choose different SKU, because one of your product already have it '{sub_product_data['product_id_1']['product_sku']}' "})

            except:
                category = Category.objects.get_or_create(name=product_data['category'].title())
                sub_category = Sub_Category.objects.get_or_create(name=product_data['product_sub_category'].title(), parent=category[0])

                main_product2.category = sub_category[0]
                main_product2.name = product_data["product_name"]
                main_product2.description = product_data["product_desc"]

                main_product2.unique_id = main_product2.slug + f"-{main_product2.pk}"
                main_product2.save()
            
                fine1 = True

        # same here
        if int(lent) > 1:
            main_product = ProductInventory.objects.filter(product__unique_id=unique_id_prod)
            try:
                for i_for_product_id in range(int(lent)):
                    for j in sub_product_data[i_for_product_id].keys():
                        if int(j.split(sep="_")[2]) == i_for_product_id:

                            if main_product[i_for_product_id].sku == sub_product_data[i_for_product_id][f'product_id_{i_for_product_id}']['product_sku']+f'-{user}':
                                category = Category.objects.get_or_create(name=product_data['category'].title())
                                sub_category = Sub_Category.objects.get_or_create(name=product_data['product_sub_category'].title(), parent=category[0])

                                main_product2.category = sub_category[0]
                                main_product2.name = product_data["product_name"]
                                main_product2.description = product_data["product_desc"]

                                if main_product2:
                                    main_product2.unique_id = main_product2.slug + f"-{main_product2.pk}"
                                    main_product2.save()

                                fine2 = True
                            else:
                                check_sku = ProductInventory.objects.get(sku=sub_product_data[i_for_product_id][f'product_id_{i_for_product_id}']['product_sku']+f'-{user}')

                                if check_sku:
                                    fine2 = False
                                    return JsonResponse({'message12521': f"please choose different SKU, because one of your product already have it '{sub_product_data[i_for_product_id][f'product_id_{i_for_product_id}']['product_sku']}' "})

            except:
                category = Category.objects.get_or_create(name=product_data['category'].title())
                sub_category = Sub_Category.objects.get_or_create(name=product_data['product_sub_category'].title(), parent=category[0])
                main_product2.category = sub_category[0]
                main_product2.name = product_data["product_name"]
                main_product2.description = product_data["product_desc"]

                if main_product2:
                    main_product2.unique_id = main_product2.slug + f"-{main_product2.pk}"
                    main_product2.save()

                fine2 = True


        # updating product
        if int(lent) == 1 and fine1:
                main_product = ProductInventory.objects.get(product__unique_id=unique_id_prod)
                if request.FILES.get('image'):
                    # Retrieve the path of the photo associated with the sub-product
                    photo_path = main_product.img_url.url

                    # Delete the photo file from the storage
                    if os.path.exists(f'static{photo_path}'):
                        os.remove(f'static{photo_path}')

                    image_file = request.FILES.get('image')
                    # Rename image file if necessary
                    image_file.name = sub_product_data[0]['product_id_0']['product_sku'] + image_file.name
                    main_product.img_url = image_file
                else:
                    print('No image file provided')

                main_product.sku = sub_product_data[0]['product_id_0']['product_sku']+f'-{user}'
                main_product.retail_price = float(sub_product_data[0]['product_id_0']['product_price'])
                main_product.is_default = sub_product_data[0]['product_id_0']['form_check_input']
                main_product.stock = sub_product_data[0]['product_id_0']['product_stock']
                main_product.product=main_product2

                # Retrieve the product inventory object
                product_inventory = main_product

                # Get the old attribute values associated with the product inventory
                old_attribute_values = product_inventory.productattributevaluess.all()

                # Delete the old attribute values
                old_attribute_values.delete()

                # Update attributes
                for key, value in sub_product_data[0]['product_id_0'].items():
                    if key.startswith('attr'):
                        attr_name = key.split('_')[1]
                        attr_value = value.title()
                        # Update or create the attribute value
                        attr = ProductAttribute.objects.get_or_create(name=attr_name)[0]
                        attr_value_instance, _ = ProductAttributeValue.objects.get_or_create(attribute=attr, value=attr_value)
                        # Create a new ProductAttributeValues instance
                        ProductAttributeValues.objects.create(attributevalues=attr_value_instance, productinventory=product_inventory)

                # Save changes to the product inventory
                product_inventory.save()

        # Updating sub-products
        elif int(lent) > 1 and fine2:
            main_products = ProductInventory.objects.filter(product__unique_id=unique_id_prod)

            for i_for_product_id in range(int(lent)):
                sub_product = main_products[i_for_product_id]

                # Update image
                if request.FILES.get(f'image-{i_for_product_id}', None):
                    image_file = request.FILES.get(f'image-{i_for_product_id}')

                    # Delete existing image if it exists
                    if sub_product.img_url:
                        if os.path.exists(sub_product.img_url.path):
                            os.remove(sub_product.img_url.path)

                    # Save new image
                    image_file.name = sub_product_data[i_for_product_id][f'product_id_{i_for_product_id}']['product_sku'] + image_file.name
                    sub_product.img_url = image_file
                else:
                    print('No image file provided')

                # Update other fields
                sub_product.sku = sub_product_data[i_for_product_id][f'product_id_{i_for_product_id}']['product_sku']+f'-{user}'
                sub_product.retail_price = float(sub_product_data[i_for_product_id][f'product_id_{i_for_product_id}']['product_price'])
                sub_product.is_default = sub_product_data[i_for_product_id][f'product_id_{i_for_product_id}']['form_check_input']
                sub_product.stock = int(sub_product_data[i_for_product_id][f'product_id_{i_for_product_id}']['product_stock'])
                sub_product.product = main_product2

                # Retrieve the product inventory object
                product_inventory = main_product[i_for_product_id]

                # Get the old attribute values associated with the product inventory
                old_attribute_values = product_inventory.productattributevaluess.all()

                # Delete the old attribute values
                old_attribute_values.delete()

                # Update attributes
                for key, value in sub_product_data[i_for_product_id][f'product_id_{i_for_product_id}'].items():
                    if key.startswith('attr'):
                        attr_name = key.split('_')[1]
                        attr_value = value.title()
                        # Update or create the attribute value
                        attr = ProductAttribute.objects.get_or_create(name=attr_name)[0]
                        attr_value_instance, _ = ProductAttributeValue.objects.get_or_create(attribute=attr, value=attr_value)
                        # Create a new ProductAttributeValues instance
                        ProductAttributeValues.objects.create(attributevalues=attr_value_instance, productinventory=product_inventory)

                # Save changes to the product inventory
                product_inventory.save()


        if int(lent) == 1:
            # For demonstration purposes, let's just return a simple response
            response_data = {'product': {
                "product_id": main_product.product.unique_id,
            },
                "message": "Product Created Successfully"
            }
        elif int(lent) > 1:
            response_data = {'product': {
                "product_id": main_product[0].product.unique_id,
            },
                "message": "Product Created Successfully"
            }

        return JsonResponse(response_data)
    
def add_to_wishlist(request):
    if request.method == 'POST' and request.user.is_authenticated:
        product_id = request.POST.get('product_id')
        product = ProductInventory.objects.get(pk=product_id)
        wishlist, created = Wishlist.objects.get_or_create(user=request.user)
        
        # Check if the product is already in the wishlist
        if wishlist.products.filter(pk=product_id).exists():
            return JsonResponse({'success': False, 'message': 'Product already in wishlist'})

        # Add the product to the wishlist
        wishlist_item = WishlistItem.objects.create(wishlist=wishlist, product=product)

        product_name = product.product.name
        img = product.img_url
        product_price = product.retail_price
        product_pk = product.pk
        product_unique_id = product.product.unique_id
        
        return JsonResponse({
            'success': True,
            'message': 'Product added to wishlist',              
            'product_name': product_name,
            'image': img.url,
            'price': product_price,
            'product_id': product_pk,
            'product_unique_id': product_unique_id
        })
    
    return JsonResponse({'success': False, 'message': 'User not authenticated or method not allowed'})

def delete_to_wishlist(request):
    if request.method == 'POST' and request.user.is_authenticated:
        product_id = request.POST.get('product_id')

        wishlist12 = Wishlist.objects.get(user=request.user)

        if WishlistItem.objects.filter(product=int(product_id), wishlist=wishlist12):
            WishlistItem.objects.filter(product=int(product_id), wishlist=wishlist12).delete()
            return JsonResponse({'success': True, 'message': 'Product Deleted From wishlist'})
        else:
            return JsonResponse({'success': False, 'message': 'Error Please Try Again'})
    
    return JsonResponse({'success': False, 'message': 'User not authenticated or method not allowed'})

def add_to_cart(request):
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity'))
        sku = request.POST.get('sku')

        # Initialize an empty list to store cart items
        cart_items = request.COOKIES.get('cart_items')
        if cart_items:
            cart_items = json.loads(cart_items)  # Convert the JSON string back to a list
        else:
            cart_items = []

        # Check if the product is already in the cart
        for item in cart_items:
            if item['sku'] == sku:
                response = JsonResponse({'message_already': 'already in cart'})
                return response

        # Get product details
        product = ProductInventory.objects.get(sku=sku)
        price = product.retail_price * quantity
        total_price = price

        # Add the new item to the cart
        cart_items.append({'sku': sku, 'quantity': quantity})

        # Set the expiration time to 1 day from now
        expiration_time = datetime.now() + timedelta(days=1)

        # Prepare JSON response
        response_data = {
            "price": product.retail_price,
            "sku": product.sku,
            'quantity': quantity,
            "name": product.product.name,
            "img_url": str(product.img_url.url),
            'total_price': total_price,
            'unique_id': product.product.unique_id
        }

        # Set the updated cart data in cookies
        response = JsonResponse(response_data)
        response.set_cookie('cart_items', json.dumps(cart_items), expires=expiration_time)
        return response
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)

def add_to_cart_users(request):
    if request.method == 'POST':

        # Access the JWT token from the Authorization header
        auth_header = request.headers.get('Authorization')
        
        if auth_header and auth_header.startswith('Bearer '):
            jwt_token = auth_header.split(' ')[1]
            
            try:
                # Decode the JWT token using the secret key
                decoded_data = jwt.decode(jwt_token, settings.SECRET_KEY, algorithms=['HS256'])
                
                # Access user information from the decoded token
                user_id = decoded_data.get('user_id')
                user = Consumer.objects.get(pk=user_id)

                # Access expiration time from the decoded token
                expiration_time = decoded_data.get('exp')
                
                # Convert expiration time from Unix timestamp to datetime object
                expiration_datetime = datetime.utcfromtimestamp(expiration_time)
                
                # Calculate remaining time until expiration
                current_datetime = datetime.utcnow()
                remaining_time = expiration_datetime - current_datetime
                
                print("Token expiration time:", expiration_datetime)
                print("Remaining time until expiration:", remaining_time)

                quantity = request.POST.get('quantity')
                sku = request.POST.get('sku')
                quantity_cookie = request.POST.get('quantity_cookie')
                sku_cookie = request.POST.get('sku_cookie')

                cart, created = Cart.objects.get_or_create(user=user)

                total_price = 0   

                if sku_cookie != '[]' and sku_cookie is not None:
                    sku_cookie = json.loads(sku_cookie)
                    quantity_cookie = json.loads(quantity_cookie)
                    skuLen = len(sku_cookie)

                    for i in range(skuLen):
                        product = ProductInventory.objects.get(sku=sku_cookie[i])

                        cart_item, created2 = CartItem.objects.get_or_create(cart=cart, product=product, quantity=int(quantity_cookie[i]))

                        if not created2:
                            response = JsonResponse({'message_already': 'already in cart'})
                            return response

                        price = product.retail_price * int(quantity_cookie[i])
                        total_price += price

                    return JsonResponse({"good_message": "Your Products Are Added to Cart Please Refresh To see them"})
                else:
                    product = ProductInventory.objects.get(sku=sku)

                    alreadyIn_cart = False

                    cart_item6 = CartItem.objects.filter(cart=cart)

                    for item in cart_item6:
                        if item.product.sku == product.sku:
                            alreadyIn_cart = True
                    
                    if alreadyIn_cart:
                        response = JsonResponse({'message_already': 'already in cart'})
                        return response

                    cart_item, created2 = CartItem.objects.get_or_create(cart=cart, product=product, quantity=int(quantity))

                    if cart_item:
                        cart_item.save()

                    price = product.retail_price * int(quantity)
                    total_price += price

                    # Set the updated cart data in cookies
                    response = JsonResponse({"price": product.retail_price, "sku": product.sku, 'quantity': int(quantity), "name": product.product.name, "img_url": str(product.img_url.url), 'total_price': total_price, 'unique_id': product.product.unique_id})
                    return response
            
            except jwt.ExpiredSignatureError:
                return JsonResponse({'error25': 'Token has expired'}, status=401)
            except jwt.InvalidTokenError:
                return JsonResponse({'error': 'Invalid token'}, status=401)
            except Exception as e:
                traceback_str = traceback.format_exc()
                return JsonResponse({'error': f'An error occurred: {str(e)},\n Traceback: {traceback_str}'}, status=500)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)

def get_cart_data(request):
    cart_items = request.COOKIES.get('cart_items')

    if request.user.is_authenticated:
        if cart_items:
            cart_items = eval(cart_items)  # Convert the string back to a list
            cart_products = []

            for cart_item in cart_items:
                product = ProductInventory.objects.get(sku=cart_item['sku'])
                
                cart_products.append({"sku": product.sku, 'quantity': cart_item['quantity']})

            return JsonResponse({'cart_products': cart_products})
        else:
            return JsonResponse({'message': 'Cart is empty'})
    else:
        if cart_items:
            cart_items = eval(cart_items)  # Convert the string back to a list

            total_price = 0
            cart_products = []

            for cart_item in cart_items:
                product = ProductInventory.objects.get(sku=cart_item['sku'])
                price = product.retail_price * int(cart_item['quantity'])
                total_price += price
                
                cart_products.append({"prod_price": product.retail_price, "sku": product.sku, 'quantity': int(cart_item['quantity']), "name": product.product.name, "img_url": str(product.img_url.url), 'unique_id': product.product.unique_id})

            return JsonResponse({'total_price': total_price, 'cart_products': cart_products})
        else:
            return JsonResponse({'message': 'Cart is empty'})

def remove_product_from_cart(request):
    """
    View to remove a product from the user's cart via AJAX request.
    """

    # Get the product ID from the POST data
    product_id = request.POST.get('product_id')

    # Find the cart item associated with the product and the user's cart
    try:
        cart_item = CartItem.objects.get(cart__user=request.user, product__sku=product_id)
        decreased_price = cart_item.product.retail_price * cart_item.quantity
        cart_item.delete()
        return JsonResponse({'success': True, 'decreased_price': decreased_price})
    except:
        return JsonResponse({'success': False, 'message': 'Product not found in the cart'}, status=404)

def updateCart(request):
    if request.method == 'POST':
        updated_quantities = json.loads(request.POST.get('updated_quantities'))

        try:
            cart_item = CartItem.objects.get(cart__user=request.user, product__sku=updated_quantities['sku'])
            cart_item.quantity = int(updated_quantities['quantity'])
            cart_item.save()
            return JsonResponse({'success': True, 'success_message': "Cart Item Update!!"})
        except:
            return JsonResponse({'success': False, 'message': 'Product not found in the cart'}, status=404)

def update_cart_guest(request):
    if request.method == 'POST':
        # Get the cart items from the cookies
        cart_items_json = request.COOKIES.get('cart_items')
        
        if cart_items_json:
            # Parse the JSON string to retrieve the cart items list
            cart_items = json.loads(cart_items_json)
        else:
            # If cart_items is not present, return an empty cart message
            return JsonResponse({'success': False, 'message': 'Cart is empty'})
        
        # Get the updated quantities and SKUs from the POST request
        updated_quantities = json.loads(request.POST.get('updated_quantities'))
        
        # Update the quantities of the specified products in the cart
        for item in cart_items:
            sku = item['sku']
            if sku in updated_quantities:
                item['quantity'] = updated_quantities[sku]
        
        # Convert the updated cart items list back to JSON string
        updated_cart_json = json.dumps(cart_items)
        
        # Set the updated cart items in the cookies
        response = JsonResponse({'success': True, 'message': 'Cart Item Update!!'})
        response.set_cookie('cart_items', updated_cart_json)
        return response
    else:
        # If the request method is not POST, return an error message
        return JsonResponse({'success': False, 'message': 'Invalid request method'})

def processOrder(request):
    transaction_id = datetime.now().timestamp()
    cart_items = request.COOKIES.get('cart_items')

    if request.method == 'POST':
        email = request.POST.get('email')
        name = request.POST.get('full_name')
        number = request.POST.get('number')
        city = request.POST.get('city')
        postalCode = request.POST.get('postalCode')
        address = request.POST.get('address')
        product_sku = request.POST.get('sku')

        costumer, created = Consumer.objects.get_or_create(email=request.user)

        costumer.full_name = name
        costumer.save()
            
        order = Order.objects.create(
            costumer=costumer,
            complete=False,
        )

        total_price = 0

        user_cart = Cart.objects.get(user=request.user)

        user_cartItem = user_cart.items.filter(product__sku__in=json.loads(product_sku))

        for item in user_cartItem:
            product = ProductInventory.objects.get(sku=item.product.sku)

            item.delete()

            orderItem = OrderItem.objects.create(
                order=order,
                product=product,
                quantity=int(item.quantity),
            )

            price = product.retail_price * int(item.quantity)
            total_price += price

            stock_item = int(product.stock)
            stock_item -= int(item.quantity)
            product.save()

            # Create a SalesRecord for the sold product
            salesrcrd = SalesRecord.objects.create(
                vendor=product.product.vendor,
                product=product,
                quantity_sold=int(item.quantity),
            )

            # Create chat conversation between consumer and vendor
            curChat = Chat.objects.get_or_create(
                sender=request.user,  # Consumer
                receiver=product.product.vendor,  # Vendor
            )

            Message.objects.create(
                content=f"New order placed: {item.quantity} x {product.product.name}, SKU: {product.sku}",
                chat=curChat[0],
                sender=request.user,
            )

            # Send email notification to the vendor
            vendor_email = product.product.vendor.email  # Assuming vendor has an email field
            subject = 'New Order Placed'
            message = render_to_string('mainApp/new_order_notification.html', {
                'quantity': item.quantity,
                'product_name': product.product.name,
                'product_sku': product.sku,
                'phone': number,
                'address': address,
                'full_name': name
            })
            plain_message = strip_tags(message)
            send_mail(subject, plain_message, settings.EMAIL_HOST_USER, [vendor_email], html_message=message)

            
        total321 = total_price + 5
        total4321 = float(order.get_all_total) + 5

        order.transaction_id = transaction_id

        if float(total321) == total4321:
            order.complete = True
        order.save()
        
        shipadr = ShippingAddress.objects.get_or_create(
            costumer=request.user,
        )

        shipadr[0].order = order
        shipadr[0].address = address
        shipadr[0].city = city
        shipadr[0].Postal_code = postalCode
        shipadr[0].full_name = name
        shipadr[0].phone_number = number
        shipadr[0].email = email

        shipadr[0].save()

        response = JsonResponse({'success': True, 'message': "Thanks For Buying!!"})

        return response
