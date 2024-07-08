from django.test import TestCase

# Create your tests here.


import pytest


class TestCartSummary:

    # Renders cart_summary.html with correct context when cart has products
    def test_renders_cart_summary_with_products(self, mocker, rf):
        # Mock the request and session
        request = rf.get('/cart_summary')
        request.session = mocker.MagicMock()

        # Mock the Cart methods
        mock_cart = mocker.patch('mkt.cart.views.Cart', autospec=True)
        mock_cart_instance = mock_cart.return_value
        mock_cart_instance.get_prods.return_value = ['product1', 'product2']
        mock_cart_instance.get_quants.return_value = {'1': 2, '2': 3}
        mock_cart_instance.cart_total.return_value = 100

        # Call the view
        response = cart_summary(request)

        # Assert the response
        assert response.status_code == 200
        assert 'cart_summary.html' in [t.name for t in response.templates]
        assert response.context_data['cart_products'] == [
            'product1', 'product2']
        assert response.context_data['quantities'] == {'1': 2, '2': 3}
        assert response.context_data['totals'] == 100

    # Renders cart_summary.html with empty context when cart is empty
    def test_renders_cart_summary_with_empty_cart(self, mocker, rf):
        # Mock the request and session
        request = rf.get('/cart_summary')
        request.session = mocker.MagicMock()

        # Mock the Cart methods
        mock_cart = mocker.patch('mkt.cart.views.Cart', autospec=True)
        mock_cart_instance = mock_cart.return_value
        mock_cart_instance.get_prods.return_value = []
        mock_cart_instance.get_quants.return_value = {}
        mock_cart_instance.cart_total.return_value = 0

        # Call the view
        response = cart_summary(request)

        # Assert the response
        assert response.status_code == 200
        assert 'cart_summary.html' in [t.name for t in response.templates]
        assert response.context_data['cart_products'] == []
        assert response.context_data['quantities'] == {}
        assert response.context_data['totals'] == 0


class TestCartAdd:

    # Successfully adds a product to the cart when valid product_id and product_qty are provided
    def test_adds_product_to_cart(self, mocker):
        from django.http import HttpRequest
        from store.models import Product
        from mkt.cart.views import cart_add

        # Create a mock request with POST data
        request = HttpRequest()
        request.method = 'POST'
        request.POST['action'] = 'post'
        request.POST['product_id'] = '1'
        request.POST['product_qty'] = '2'

        # Mock the Product model and Cart class
        mock_product = mocker.patch('store.models.Product')
        mock_product.objects.get.return_value = Product(
            id=1, name='Test Product', price=10.00)

        mock_cart = mocker.patch('mkt.cart.views.Cart')
        mock_cart_instance = mock_cart.return_value

        # Call the function under test
        response = cart_add(request)

        # Assertions
        mock_cart_instance.add.assert_called_once_with(
            product=mock_product.objects.get.return_value, quantity=2)
        assert response.status_code == 200
        assert response.json() == {'qty: ': 1}

    # Handles the case when product_id does not exist in the database
    def test_product_id_does_not_exist(self, mocker):
        from django.http import HttpRequest
        from django.http import Http404
        from mkt.cart.views import cart_add

        # Create a mock request with POST data
        request = HttpRequest()
        request.method = 'POST'
        request.POST['action'] = 'post'
        request.POST['product_id'] = '999'
        request.POST['product_qty'] = '2'

        # Mock the get_object_or_404 to raise Http404
        mocker.patch('mkt.cart.views.get_object_or_404', side_effect=Http404)

        # Call the function under test and assert it raises Http404
        with pytest.raises(Http404):
            cart_add(request)


class TestCartUpdate:

    # Successfully updates cart when valid product_id and product_qty are provided
    def test_successful_cart_update(self, mocker):
        from django.http import HttpRequest
        from django.contrib.messages.storage.fallback import FallbackStorage
        from mkt.cart.views import cart_update
        from store.models import Product

        # Create a mock request
        request = HttpRequest()
        request.method = 'POST'
        request.POST['action'] = 'post'
        request.POST['product_id'] = '1'
        request.POST['product_qty'] = '2'
        request.session = {}

        # Mock the Product model
        mocker.patch('store.models.Product.objects.get',
                     return_value=Product(id=1, price=10))

        # Mock messages framework
        setattr(request, 'session', 'session')
        messages_storage = FallbackStorage(request)
        setattr(request, '_messages', messages_storage)

        # Call the function
        response = cart_update(request)

        # Assertions
        assert response.status_code == 200
        assert response.json() == {'qty': 2}

    # Handles non-integer product_id gracefully
    def test_non_integer_product_id(self, mocker):
        from django.http import HttpRequest
        from django.contrib.messages.storage.fallback import FallbackStorage
        from mkt.cart.views import cart_update

        # Create a mock request
        request = HttpRequest()
        request.method = 'POST'
        request.POST['action'] = 'post'
        request.POST['product_id'] = 'abc'  # Non-integer product_id
        request.POST['product_qty'] = '2'
        request.session = {}

        # Mock messages framework
        setattr(request, 'session', 'session')
        messages_storage = FallbackStorage(request)
        setattr(request, '_messages', messages_storage)

        # Call the function and expect it to handle the error gracefully
        try:
            response = cart_update(request)
            assert False, "Expected ValueError"
        except ValueError:
            pass  # Expected outcome
