import base64
from flask import render_template, redirect, url_for, flash, request, abort, jsonify
from flask_login import current_user, login_required
from .models.inventory import Inventory
from .models.user import User
from .models.order import Order
from .models.cart import Cart
from .models.recommendation import Recommendation
import logging
from decimal import Decimal
from .inventory import get_inventories_details
from .inventory import get_inventories_details
from .index import get_all_products_details, get_all_inventories_details
from .models.category import Category

from flask import Blueprint
bp = Blueprint('cart', __name__)


def authenticated_user_cart():
    """
    Get user's cart entry. If doesn't have one, register a cart
    """
    if Cart.has_cart(current_user.id):
        cart = Cart.getByUser(current_user.id)
    else:
        cart = Cart.register(current_user.id)
    return cart


def check_authentication(recommend=False):
    """
    Check whether the user is authenticated or not. Display cart information
    """
    recommendation = None
    if current_user.is_authenticated:
        cart = authenticated_user_cart()
        if recommend:
            recommendation = Recommendation.recommend_products_based_on_history_and_reviews(current_user.id)
    else:
        cart = Cart.register()
    return cart, recommendation


def cart_summary(cart_details):
    """
    Get Cart summary information including quantity and price
    """
    total_price = 0
    total_items = 0

    # Calculate total price using a for loop
    for item in cart_details:
        total_price += Decimal(item['price']) * item['quantity']
        total_items += item['quantity']
        
    return total_price, total_items


@bp.route('/cart')
def cart():
    """
    Main cart view that displays cart product
    """
    total_price, total_items = None, None
    cart, recommendation = check_authentication(True)
    cid = cart.id
    cart_details = Inventory.get_cart_products(cid)
    if cart_details:
        total_price, total_items = cart_summary(cart_details)

    return render_template('cart.html', cart_details=cart_details, recommendation=recommendation, total_price=total_price, total_items=total_items)


"""
CRUD operations for cart_product database
"""
@bp.route('/add_to_cart', methods=['POST'])
def add_product_to_cart():
    invid = request.form['invid']
    originalId = request.form.get('originalId', False)
    recommend_add = request.form.get('recommend_page', False)
        
    try:
        cid = get_cart_id()
        item = Inventory.getById(invid)
        all_products = get_inventories_details('product', filter_value=invid)

        if item and originalId and Cart.add_to_cart(cid, item.id, item.price):
            details = get_inventories_details('inventory_id', filter_value=originalId)
            flash('Item added to cart!')
            return render_template("seller_product_detail.html", details=details[0], all_products=all_products)
        elif item and recommend_add and Cart.add_to_cart(cid, item.id, item.price):
            return redirect(url_for('cart.cart'))
        elif item and Cart.add_to_cart(cid, item.id, item.price):
            products_details = get_all_products_details()
            inventory_details = get_all_inventories_details()
            flash('Item added to cart!')
            return render_template('index.html', products_details=products_details, inventory_details=inventory_details, top_products=None, categories = Category.getExistCategories())
        else:
            return jsonify({'error': 'Not Enough Inventories'}), 400
    except Exception as e:
        logging.error(f"Failed to add product to cart: {str(e)}")
        return jsonify({'error': 'Internal Server Error'}), 500


@bp.route('/delete_item', methods=['POST'])
def delete_item_from_cart():
    cart, recommendation = check_authentication(True)
    cid = cart.id
    invid = request.form.get('invid')
    save_page = request.form.get('save_for_later', False)
    total_price, total_items = None, None

    if save_page and Cart.remove_product_by_invid(cid, invid):
        return redirect(url_for('cart.save_for_later'))
    elif Cart.remove_product_by_invid(cid, invid):
        # Item successfully removed from save_for_later page
        cart_details = Inventory.get_cart_products(cid)
        if cart_details:
            total_price, total_items = cart_summary(cart_details)
        return render_template('cart.html', cart_details=cart_details, recommendation=recommendation, total_price=total_price, total_items=total_items)
    

"""
CRUD operations for save-for-later items.
Change products' status within the cart
"""
@bp.route('/save_for_later')
def save_for_later():
    cart, recommendation = check_authentication(False)
    cid = cart.id
    cart_details = Inventory.get_cart_products(cid, in_cart=False)

    return render_template('save_for_later.html', cart_details=cart_details)


@bp.route('/save_product_for_later', methods=['POST'])
def save_product_for_later():
    total_price, total_items = None, None
    cart, recommendation = check_authentication(False)
    cid = cart.id
    invid = request.form.get('invid')
    if Cart.save_product_for_later(cid, invid):
        cart_details = Inventory.get_cart_products(cid)
        recommendation = Recommendation.recommend_products_based_on_history_and_reviews(current_user.id)
        if cart_details:
            total_price, total_items = cart_summary(cart_details)
        return render_template('cart.html', cart_details=cart_details, recommendation=recommendation, total_price=total_price, total_items=total_items)
 
    
@bp.route('/move_product_to_cart', methods=['POST'])
def move_product_to_cart():
    cart, recommendation = check_authentication(False)
    cid = cart.id
    invid = request.form.get('invid')
    if Cart.move_product_to_cart(cid, invid):
        cart_details = Inventory.get_cart_products(cid, in_cart=False)
        return render_template('save_for_later.html', cart_details=cart_details)


@bp.route('/update_quantity', methods=['POST'])
def update_quantity():
    """
    Update cart product quantity
    """
    total_price, total_items = None, None
    cart, recommendation = check_authentication(True)
    cid = cart.id
    invid = request.form.get('invid')
    quantity = request.form.get('quantity')

    if int(quantity) > 0:
        if Cart.edit_quantity_by_invid(cid, invid, int(quantity)):
            cart_details = Inventory.get_cart_products(cid)
            if cart_details:
                total_price, total_items = cart_summary(cart_details)
            return render_template('cart.html', cart_details=cart_details, error=False, recommendation=recommendation, total_price=total_price, total_items=total_items)
        else:
            cart_details = Inventory.get_cart_products(cid)
            if cart_details:
                total_price, total_items = cart_summary(cart_details)
            return render_template('cart.html', cart_details=cart_details, error=True, recommendation=recommendation, total_price=total_price, total_items=total_items)


@login_required
def get_cart_id():
    """
    Get current cart id
    """
    try:
        cart = authenticated_user_cart()
        return cart.id
    except Exception as e:
        logging.error(f"Failed to add product to cart: {str(e)}")
        return False


@bp.route('/checkout_summary', methods=['GET'])
@login_required
def checkout_summary():
    """
    Generate checkout summary including total items and total price, etc
    """
    total_price, total_items = None, None
    cart = authenticated_user_cart()
    cart_details = Inventory.get_cart_products(cart.id, in_cart=True)

    if cart_details:
        total_price, total_items = cart_summary(cart_details)

    return render_template('checkout.html', cart_details=cart_details, total_price=total_price, total_items=total_items)


@bp.route('/process_checkout', methods=['POST'])
@login_required
def process_checkout():
    """
    Process checkout: Update buyer/seller balance and inventory
    """
    # buyer's balance
    user = User.get(current_user.id)
    user_balance = user.balance
    
    # cart_products
    cart = authenticated_user_cart()
    cart_items = Inventory.get_cart_products(cart.id)
    if not cart_items:
        error_msg = "Your cart is empty."
        return render_template('error_msg.html', msg=error_msg)
    total_price = sum(item['quantity'] * item['price'] for item in cart_items)
    
    # Create new order, Decrease buyer balance & Increase seller balance
    if user_balance >= total_price:
        try:
            # Create a new order
            oid = Order.add_new_order(user.id)
            if oid is None: 
                raise Exception("Failed to create order")
            
            # Add cart_products to order_products
            for item in cart_items:
                # Add to order_products
                Order.add_to_order(oid, item['invid'], item['price'], item['quantity'])
                
                # Decrease seller's inventory quantity
                quantity = Inventory.getById(item['invid']).current_quantity
                if quantity < item['quantity']:
                    raise Exception("Failed to create order")
                new_quantity = quantity - item['quantity']
                Inventory.updateQuantity(item['invid'], new_quantity)
                
                # Increase seller balance
                seller_account = User.get_seller_account(item['sid'])
                new_seller_balance = item['quantity'] * item['price'] + seller_account.balance
                User.update_balance(seller_account.id, new_seller_balance)
                
            # Decrease buyer balance
            new_buyer_balance = user_balance - total_price
            User.update_balance(user.id, new_buyer_balance)

            return redirect(url_for('cart.thank_you'))
        except Exception as e:
            return render_template('error_msg.html', msg=e) 
            
    else:
        error_msg = "Not enough balance."
        return render_template('error_msg.html', msg=error_msg)


@bp.route('/thank_you')
@login_required
def thank_you():
    """
    Display thank you note
    """
    Cart.delete_cart_items(current_user.id)
    return render_template('thank_you.html')