from store.models import Product


class Cart():
    def __init__(self, request):
        self.session = request.session

        # Get the current session key if it exists
        cart = self.session.get('session_key')

        # if the user is new, no session key
        if 'session_key' not in request.session:
            cart = self.session['session_key'] = {}

        # make sure cart is available in all pages of the website
        self.cart = cart

    def add(self, product, quantity):
        product_id = str(product.id)
        product_qty = str(quantity)

        # logic
        if product_id in self.cart:
            pass
        else:
            # self.cart[product_id] = {'price': str(product.price)}
            self.cart[product_id] = int(product_qty)

        self.session.modified = True

    def cart_total(self):
        # Get product IDS
        product_ids = self.cart.keys()
        # lookup keys in our db model
        products = Product.objects.filter(id__in=product_ids)
        # Get quantities
        quantities = self.cart
        # start counting at 0
        total = 0
        for key, value in quantities.items():
            # Convert int string into int so we can do math
            key = int(key)
            for product in products:
                if product.id == key:
                    total = total + (product.price * value)
        return total

    def __len__(self):
        return len(self.cart)

    def get_prods(self):
        # get ids from cart
        product_ids = self.cart.keys()

        # use ids to lookup products in database model
        products = Product.objects.filter(id__in=product_ids)

        # Return those lokkedup products
        return products

    def get_quants(self):
        quantities = self.cart
        return quantities

    def update(self, product, quantity):
        product_id = str(product)
        product_qty = int(quantity)

        # Get cart
        ourcart = self.cart
        # Update Dictionary/cart
        ourcart[product_id] = product_qty

        self.session.modified = True

        thing = self.cart
        return thing
