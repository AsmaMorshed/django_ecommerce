from decimal import Decimal

CART_SESSION_ID = 'cart'


class Cart:
    """
    Session-based shopping cart.
    Stores cart data in Django's server-side session — no database required.
    """

    def __init__(self, request):
        self.session = request.session
        cart = self.session.get(CART_SESSION_ID)
        if not cart:
            # Initialize an empty cart in the session
            cart = self.session[CART_SESSION_ID] = {}
        self.cart = cart

    # ------------------------------------------------------------------
    # ADD ITEM
    # ------------------------------------------------------------------
    def add_item(self, product, quantity=1, color=None, size=None, override_quantity=False):
        """
        Add a product to the cart or update its quantity.
        Uses the product's UUID pk (as string) as the cart key.
        If color/size variants are selected they are stored with the item.
        """
        product_id = str(product.id)  # UUID → string key

        if product_id not in self.cart:
            self.cart[product_id] = {
                'name':     str(product.name),
                'price':    str(product.get_price()),   # uses Member 2's dynamic pricing method
                'quantity': 0,
                'color':    color or '',
                'size':     size  or '',
                'image':    str(product.productimage_set.first().image.url)
                            if product.productimage_set.exists() else '',
            }

        if override_quantity:
            self.cart[product_id]['quantity'] = quantity
        else:
            self.cart[product_id]['quantity'] += quantity

        self.save()

    # ------------------------------------------------------------------
    # REMOVE ITEM
    # ------------------------------------------------------------------
    def remove_item(self, product):
        """Remove a product from the cart entirely."""
        product_id = str(product.id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    # ------------------------------------------------------------------
    # SAVE (mark session as modified so Django persists it)
    # ------------------------------------------------------------------
    def save(self):
        self.session.modified = True

    # ------------------------------------------------------------------
    # SUBTOTALS & TOTAL
    # ------------------------------------------------------------------
    def get_total_price(self):
        """Arithmetic summation loop — returns grand total as Decimal."""
        return sum(
            Decimal(item['price']) * item['quantity']
            for item in self.cart.values()
        )

    def get_item_count(self):
        """Returns total number of individual units in the cart."""
        return sum(item['quantity'] for item in self.cart.values())

    # ------------------------------------------------------------------
    # CLEAR
    # ------------------------------------------------------------------
    def clear(self):
        """Wipe cart from session (called after successful checkout)."""
        del self.session[CART_SESSION_ID]
        self.save()

    # ------------------------------------------------------------------
    # ITERATOR — lets templates do {% for item in cart %}
    # ------------------------------------------------------------------
    def __iter__(self):
        """
        Iterate over cart items and attach computed subtotal to each.
        """
        cart_copy = self.cart.copy()
        for item in cart_copy.values():
            item['subtotal'] = Decimal(item['price']) * item['quantity']
            yield item

    def __len__(self):
        return self.get_item_count()
