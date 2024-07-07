from django.test import TestCase

# Create your tests here.


# Dependencies:
# pip install pytest-mock
import pytest


class TestCheckout:

    # Checkout as authenticated user with valid cart and shipping address
    def test_checkout_authenticated_user_with_valid_cart_and_shipping_address(self, mocker):
        from mkt.payment.views import checkout
        from django.contrib.auth.models import User
        from django.test import RequestFactory
        from payment.models import ShippingAddress
        from cart.cart import Cart

        # Create a mock request with an authenticated user
        user = User(id=1, username='testuser')
        request = RequestFactory().post('/checkout')
        request.user = user
        # Mock session with cart items
        request.session = {'session_key': {'1': 2}}

        # Mock the ShippingAddress and Cart objects
        mocker.patch.object(ShippingAddress.objects, 'get',
                            return_value=ShippingAddress(user=user))
        mocker.patch.object(Cart, 'get_prods', return_value=['product1'])
        mocker.patch.object(Cart, 'get_quants', return_value={'1': 2})
        mocker.patch.object(Cart, 'cart_total', return_value=100)

        response = checkout(request)

        assert response.status_code == 200
        assert 'cart_products' in response.context
        assert 'quantities' in response.context
        assert 'totals' in response.context
        assert 'shipping_form' in response.context

    # Checkout with empty cart for authenticated user
    def test_checkout_authenticated_user_with_empty_cart(self, mocker):
        from mkt.payment.views import checkout
        from django.contrib.auth.models import User
        from django.test import RequestFactory
        from payment.models import ShippingAddress
        from cart.cart import Cart

        # Create a mock request with an authenticated user
        user = User(id=1, username='testuser')
        request = RequestFactory().post('/checkout')
        request.user = user
        request.session = {'session_key': {}}  # Mock session with empty cart

        # Mock the ShippingAddress and Cart objects
        mocker.patch.object(ShippingAddress.objects, 'get',
                            return_value=ShippingAddress(user=user))
        mocker.patch.object(Cart, 'get_prods', return_value=[])
        mocker.patch.object(Cart, 'get_quants', return_value={})
        mocker.patch.object(Cart, 'cart_total', return_value=0)

        response = checkout(request)

        assert response.status_code == 200
        assert 'cart_products' in response.context
        assert 'quantities' in response.context
        assert 'totals' in response.context
        assert 'shipping_form' in response.context


class TestBillingInfo:

    # Renders billing_info template with correct context when user is authenticated
    def test_renders_billing_info_template_with_correct_context_when_authenticated(self, mocker):
        from mkt.payment.views import billing_info
        from django.contrib.auth.models import User
        from django.test import RequestFactory
        from django.http import HttpRequest

        # Mock request and user
        request = RequestFactory().post('/')
        request.user = mocker.Mock(spec=User)
        request.user.is_authenticated = True
        request.session = {}

        # Mock Cart methods
        mock_cart = mocker.patch('mkt.payment.views.Cart')
        mock_cart.return_value.get_prods.return_value = []
        mock_cart.return_value.get_quants.return_value = {}
        mock_cart.return_value.cart_total.return_value = 0

        # Call the function
        response = billing_info(request)

        # Assertions
        assert response.status_code == 200
        assert 'payment/billing_info.html' in [
            t.name for t in response.templates]
        assert 'cart_products' in response.context_data
        assert 'quantities' in response.context_data
        assert 'totals' in response.context_data
        assert 'shipping_info' in response.context_data
        assert 'billing_form' in response.context_data

    # Handles empty POST request gracefully
    def test_handles_empty_post_request_gracefully(self, mocker):
        from mkt.payment.views import billing_info
        from django.test import RequestFactory
        from django.contrib import messages

        # Mock request and messages
        request = RequestFactory().get('/')
        request.session = {}
        mocker.patch('django.contrib.messages.success')

        # Call the function
        response = billing_info(request)

        # Assertions
        assert response.status_code == 302  # Redirect status code
        assert response.url == '/home'
        messages.success.assert_called_once_with(request, "Access Denied")
