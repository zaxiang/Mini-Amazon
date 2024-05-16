import base64
from flask import render_template, redirect, url_for, flash, request, abort
from flask_login import current_user, login_required
from .models.inventory import Inventory
from .models.order import Order
from .models.category import Category

from flask import Blueprint
bp = Blueprint('order', __name__)


@bp.route('/order_history')
@login_required
def order():
    """
    Displays order history for a user based on filters such as seller ID, search terms, date range, and inventory name.
    """
    sid = request.args.get('seller_id', None)
    search_term = request.args.get('search_term', None)
    start_date = request.args.get('start_date', None)
    end_date = request.args.get('end_date', None)
    inventory_name = request.args.get('inventory_name', None)
    
    if isinstance(inventory_name, str):
        inventory_name = inventory_name.lower()
    
    order_history = Order.search_by_criteria(current_user.id, sid, search_term, start_date, end_date, inventory_name, 'buyer')
    order_summary = Order.get_order_history_with_summary([order['order_id'] for order in order_history])

    return render_template('order_history.html', order_history=order_history, order_summary=order_summary)


@bp.route('/order_stats')
@login_required
def order_stats():
    """
    Displays statistical data for orders filtered by categories selected by the user.
    """
    selected_categories = request.args.get('category_name', "All Categories")

    if isinstance(selected_categories, str):
        inventory_name = selected_categories.lower()
    
    order_history = Order.search_by_category(current_user.id, selected_categories, 'buyer')
    order_summary = Order.get_order_history_with_summary([order['order_id'] for order in order_history])

    return render_template('order_stats.html', order_history=order_history, order_summary=order_summary, categories=Category.get_user_ordered_product_category(current_user.id), selected_categories=selected_categories)


@bp.route('/order_details/<int:oid>')
@login_required
def search_order_details(oid):
    """
    Displays detailed information for a specific order, including product items and a summary of the order.
    """
    order = Order.getById(oid)
    
    if not order or order.uid != current_user.id:
        return redirect(url_for('index.index'))

    order_details = Inventory.get_order_products(oid)
    order_summary = Order.get_order_history_with_summary([oid])

    return render_template('order_details.html', order=order, order_details=order_details, order_summary=order_summary)