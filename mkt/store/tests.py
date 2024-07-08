from django.test import TestCase

# Create your tests here.


import pytest


class TestUpdateUser:
    # TODO:Update tests
    # User updates their profile successfully when authenticated
    def test_user_updates_profile_successfully_when_authenticated(self, mocker, rf):
        from mkt.store.views import update_user
        from django.contrib.auth.models import User
        from django.urls import reverse

        # Create a mock user and authenticate
        user = User.objects.create_user(username='testuser', password='12345')
        user.save()
        rf.user = user

        # Mock the request
        request = rf.post(reverse('update_user'), {
                          'username': 'newusername', 'first_name': 'New', 'last_name': 'Name', 'email': 'newemail@example.com'})
        request.user = user

        # Mock the login and messages functions
        mocker.patch('mkt.store.views.login')
        mocker.patch('mkt.store.views.messages.success')

        response = update_user(request)

        # Assertions
        assert response.status_code == 302  # Redirects to 'home'
        assert User.objects.get(id=user.id).username == 'newusername'

    # User tries to update profile without being authenticated
    def test_user_tries_to_update_profile_without_being_authenticated(self, mocker, rf):
        from mkt.store.views import update_user
        from django.urls import reverse

        # Mock the request
        request = rf.post(reverse('update_user'), {
                          'username': 'newusername', 'first_name': 'New', 'last_name': 'Name', 'email': 'newemail@example.com'})
        request.user = mocker.Mock(is_authenticated=False)

        # Mock the messages function
        mocker.patch('mkt.store.views.messages.success')

        response = update_user(request)

        # Assertions
        assert response.status_code == 302  # Redirects to 'home'


class TestUpdateInfo:

    # Authenticated user updates profile information successfully
    def test_authenticated_user_updates_profile_successfully(self, mocker, rf):
        from mkt.store.views import update_info
        from django.contrib.auth.models import User
        from mkt.store.models import Profile
        from payment.models import ShippingAddress
        from django.contrib.messages.storage.fallback import FallbackStorage

        # Create a mock user and profile
        user = User.objects.create_user(username='testuser', password='12345')
        profile = Profile.objects.create(user=user)
        shipping_address = ShippingAddress.objects.create(user=user, shipping_full_name='Test User', shipping_email='test@example.com',
                                                          shipping_address1='123 Test St', shipping_city='Test City', shipping_country='Test Country')

        # Mock the request
        request = rf.post('/update_info/', {
            'phone': '1234567890',
            'address1': '123 Test St',
            'city': 'Test City',
            'country': 'Test Country',
            'shipping_full_name': 'Test User',
            'shipping_email': 'test@example.com',
            'shipping_address1': '123 Test St',
            'shipping_city': 'Test City',
            'shipping_country': 'Test Country'
        })
        request.user = user

        # Add messages middleware to the request
        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)

        response = update_info(request)

        # Check if the profile and shipping address were updated
        profile.refresh_from_db()
        shipping_address.refresh_from_db()

        assert profile.phone == '1234567890'
        assert profile.address1 == '123 Test St'
        assert profile.city == 'Test City'
        assert profile.country == 'Test Country'
        assert shipping_address.shipping_full_name == 'Test User'
        assert shipping_address.shipping_email == 'test@example.com'
        assert shipping_address.shipping_address1 == '123 Test St'
        assert shipping_address.shipping_city == 'Test City'
        assert shipping_address.shipping_country == 'Test Country'
        assert response.status_code == 302  # Redirects to home

    # Unauthenticated user attempts to access the update page
    def test_unauthenticated_user_redirected_to_home(self, mocker, rf):
        from mkt.store.views import update_info
        from django.contrib.messages.storage.fallback import FallbackStorage

        # Mock the request
        request = rf.get('/update_info/')
        request.user = mocker.Mock(is_authenticated=False)

        # Add messages middleware to the request
        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)

        response = update_info(request)

        # Check if the user is redirected to home
        assert response.status_code == 302  # Redirects to home


class TestCategory:

    # create a category with a valid name
    def test_create_category_with_valid_name(self):
        category = Category(name="Electronics")
        assert category.name == "Electronics"

    # create a category with an empty name
    def test_create_category_with_empty_name(self):
        with pytest.raises(ValueError):
            Category(name="")


class TestCustomer:

    # Creating a customer with valid data
    def test_create_customer_with_valid_data(self):
        customer = Customer(
            first_name="John",
            last_name="Doe",
            phone="1234567890",
            email="john.doe@example.com",
            password="securepassword123"
        )
        assert customer.first_name == "John"
        assert customer.last_name == "Doe"
        assert customer.phone == "1234567890"
        assert customer.email == "john.doe@example.com"
        assert customer.password == "securepassword123"

    # Creating a customer with missing first name
    def test_create_customer_with_missing_first_name(self):
        with pytest.raises(ValueError):
            Customer(
                first_name="",
                last_name="Doe",
                phone="1234567890",
                email="john.doe@example.com",
                password="securepassword123"
            )


class TestProduct:

    # Creating a product with all required fields
    def test_create_product_with_all_required_fields(self, mocker):
        category = Category.objects.create(name="Electronics")
        product = Product.objects.create(
            name="Laptop",
            price=999.99,
            category=category,
            image="uploads/product/laptop.jpg"
        )
        assert product.name == "Laptop"
        assert product.price == 999.99
        assert product.category == category
        assert product.image == "uploads/product/laptop.jpg"

    # Creating a product with missing optional fields
    def test_create_product_with_missing_optional_fields(self, mocker):
        category = Category.objects.create(name="Electronics")
        product = Product.objects.create(
            name="Smartphone",
            price=499.99,
            category=category,
            image="uploads/product/smartphone.jpg"
        )
        assert product.name == "Smartphone"
        assert product.price == 499.99
        assert product.category == category
        assert product.image == "uploads/product/smartphone.jpg"
        assert product.desc == ""
        assert product.description is None
        assert product.is_sale is False
        assert product.sale_price == 0
