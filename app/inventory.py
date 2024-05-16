import base64
from flask import render_template, redirect, url_for, flash, request
from flask_login import current_user, login_required
from .models.seller import Seller 
from .models.inventory import Inventory
from .models.user import User
from .models.product import Product
from .models.image import Image
from .models.order import Order
from .models.tag import Tag
from .models.category import Category
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SelectField, SubmitField, FloatField, FileField
from flask_wtf.file import FileField, FileAllowed
from wtforms.validators import DataRequired, NumberRange

from flask import Blueprint
bp = Blueprint('inventory', __name__)

class InventoryForm(FlaskForm):
    """
    Form used to update inventory items with validation for quantity and price.
    """
    current_quantity = IntegerField('Current Quantity', validators=[DataRequired(), NumberRange(min=0)])
    price = FloatField('Price', validators=[DataRequired(), NumberRange(min=0)])
    submit = SubmitField('Submit')

    def __init__(self, *args, **kwargs):
        super(InventoryForm, self).__init__(*args, **kwargs)


def get_inventories_details(filter_type, filter_value=None, order=None, sid=None, keyword=None, category=None, sort=None, rating_filter=None, price_min=None, price_max=None):
    """
    Retrieves detailed information about inventories based on different filtering criteria such as seller, category, and sorting preferences.
    """
    inventories_details = []
    check = True
    
    # Determine the source of inventories based on the filter_type
    if filter_type == "seller":
        inventories = Inventory.getBySeller(filter_value)
    elif filter_type == "keyword":
        inventories = Inventory.getByKeyword(filter_value)
    elif filter_type == "category":
        inventories = Inventory.getByCategory(filter_value)
    elif filter_type == "sorted":
        if order == "price_asc":
            inventories = Inventory.getByPrice()
        else:
            inventories = Inventory.getByPrice('desc')
    elif filter_type == "sorted_by_rating":
        if order == "rating_desc":
            inventories = Inventory.getByRating()
        else:
            inventories = Inventory.getByRating('asc')
    elif filter_type == "sorted_by_sales":
        if order == "sales_desc":
            inventories = Inventory.getBySales()
        else:
            inventories = Inventory.getBySales('asc')
    elif filter_type == "inventory_id":
        inventories = [Inventory.getById(filter_value)] if Inventory.getById(filter_value) else []
        check = False
    elif filter_type == "product":
        inventories = Inventory.getSameProductById(filter_value)
        inventories.sort(key=lambda x: x.price)
    elif filter_type == "mixed":
        inventories = Inventory.search_inventory_by_form(
            sid=sid,
            keyword=keyword,
            category=category,
            sort=sort,
            rating_filter=rating_filter,
            price_min=price_min,
            price_max=price_max
        )
        print(f'reach here - inventories: {inventories} {sid} sid, {keyword} keyword, {category} category, {sort} sort, {rating_filter} rating, {price_min} - {price_max}')
    else:
        return []

    for inventory in inventories:
        if not inventory:
            continue
        related_products = Product.get_inventory_products(inventory.id)
        images = Image.get_inventory_image(inventory.id, check) if Image.has_inventory_images(inventory.id) else Image.get_product_image(related_products.id)
        designs = Inventory.get_inventory_designs(inventory.id)
        
        inventories_details.append({
            'inventory': inventory,
            'products': related_products,
            'images': images,
            'designs': designs[0] if designs else None  
        })

    return inventories_details


@bp.route('/inventory')
@login_required
def inventory():
    """
    Main inventory view that displays inventories based on user role. Registers user as seller if not already registered.
    """
    inventories_details = []
    # Check if the current user is a seller
    if not Seller.is_seller(current_user.id):
        # If not, register them as a seller
        result = Seller.register(current_user.id)
    else:
        # If the user is a seller, find their inventory
        sid = Seller.getByUid(current_user.id).id
        inventories_details = get_inventories_details('seller', filter_value=sid)

    # Render the page by adding information to the inventory.html file
    return render_template('inventory.html', inventories_details=inventories_details)


@bp.route('/search_inventory', methods=['POST'])
def search_inventory():
    """
    Searches and displays inventory based on seller identifier input.
    """
    inventories_details = []
    sid = request.form.get('seller_identifier')
    
    if Seller.is_seller(sid):
        inventories_details = get_inventories_details('seller', filter_value=sid)
        seller = User.get_seller_account(sid)
        
        # Render a template to display the search results
        return render_template('search_results.html', inventories_details=inventories_details, seller=seller)
    else:
        error_msg = "No such seller!"
        return render_template('error_msg.html', msg=error_msg)


@bp.route('/inventory/<int:invid>')
def seller_product_detail(invid, check=False):
    """
    Displays detailed view of a single inventory item, accessible only to the inventory's seller.
    """
    editable = False
    details = get_inventories_details('inventory_id', filter_value=invid)
    all_products = get_inventories_details('product', filter_value=invid)
    if current_user.is_authenticated:
        inventory = Inventory.getById(invid)
        current_seller = Seller.getByUid(current_user.id)
        check = inventory.sid == current_seller.id
        editable = Product.get(inventory.pid).uid == current_user.id
    if len(details) > 0:
        return render_template('seller_product_detail.html', details=details[0], check=check, editable=editable, all_products=all_products)
    else:
        error_msg = "No such inventory!"
        return render_template('error_msg.html', msg=error_msg)


@bp.route('/search_inventory_form', methods=['POST'])
def search_inventory_form():
    """
    Search and display inventory based on multiple filters and sorting criteria entered through a web form.
    """
    # Handle the form submission
    sid = request.form.get('sid')
    sid = None if not sid else int(sid)
    
    keyword = request.form.get('keyword')
    keyword = None if keyword == '' else keyword
    
    category = request.form.get('category')
    sort = request.form.getlist('sort[]')  
    rating_filter = request.form.get('rating_filter', type=float)
    price_min = request.form.get('price_min', type=float)
    price_max = request.form.get('price_max', type=float)

    inventories_details = get_inventories_details(
        filter_type='mixed', 
        sid=sid,
        keyword=keyword,
        category=category,
        sort=sort,
        rating_filter=rating_filter,
        price_min=price_min,
        price_max=price_max
    )
    seller = Seller.getById(sid)
    
    # Render the page with the search results
    return render_template('search_results.html', inventories_details=inventories_details, seller=seller, mixed=True, keyword=keyword, category=category, price_min=price_min, price_max=price_max, rating_filter=rating_filter, sort=sort)


"""
Search and displays inventories based on user-selected criteria like keyword or category, etc.
"""
@bp.route('/search_inventory_by_keyword', methods=['POST'])
def search_inventory_by_keyword():
    inventories_details = []
    keyword = request.form.get('keyword_identifier')
    
    inventories_details = get_inventories_details('keyword', filter_value=keyword)
    
    return render_template('search_results.html', inventories_details=inventories_details, keyword=keyword)


@bp.route('/browse_category/<int:categoryId>', methods=['GET', 'POST'])
def browse_category(categoryId):
    category_details = get_inventories_details('category', filter_value=categoryId)

    return render_template('search_results.html', inventories_details=category_details, category=True)


"""
Sorts and displays inventories based on user-selected criteria like price or rating, etc.
"""
@bp.route('/sort_inventory', methods=['POST'])
def sort_inventory():
    sort_order = request.form.get('sort_order')
    inventories_details = get_inventories_details('sorted', order=sort_order)

    return render_template('search_results.html', inventories_details=inventories_details, sort=True)


@bp.route('/sort_inventory_by_rating', methods=['POST'])
def sort_inventory_by_rating():
    sort_order = request.form.get('sort_order')
    inventories_details = get_inventories_details('sorted_by_rating', order=sort_order)

    return render_template('search_results.html', inventories_details=inventories_details, sort=True)


@bp.route('/sort_inventory_by_sales', methods=['POST'])
def sort_inventory_by_sales():
    sort_order = request.form.get('sort_order')
    inventories_details = get_inventories_details('sorted_by_sales', order=sort_order)

    return render_template('search_results.html', inventories_details=inventories_details, sort=True)


class NewInventoryForm(FlaskForm):
    """
    Form used to create new inventory items
    """
    pid = SelectField('Product', coerce=int, validators=[DataRequired()])
    current_quantity = IntegerField('Current Quantity', validators=[DataRequired(), NumberRange(min=0)])
    price = FloatField('Price', validators=[DataRequired(), NumberRange(min=0)])
    submit = SubmitField('Submit')

    def __init__(self, seller_id=None, current_pid=None, *args, **kwargs):
        super(NewInventoryForm, self).__init__(*args, **kwargs)
        if seller_id is not None:
            excluded_product_ids = Seller.get_seller_product_ids(seller_id)
            products = [product for product in Product.get_all() if product.id not in excluded_product_ids]
        else:
            products = Product.get_all()
        
        self.pid.choices = [(product.id, product.name) for product in products]


"""
CRUD operations for inventory database
"""
@bp.route('/inventory/add', methods=['GET', 'POST'])
@login_required
def add_inventory():
    sid = Seller.getByUid(current_user.id).id
    form = NewInventoryForm(seller_id=sid)
    msg = None
    
    if form.validate_on_submit():
        # standardize products across seller:
        # price has to be at least 0.8 * original inventory
        product = Product.get(form.pid.data)
        creator_sid = Seller.getByUid(product.uid).id
        original_inventory = Inventory.traceCreatorInventory(creator_sid, product.id)
        min_price = int(float(original_inventory.price) * 0.8) + 1 if original_inventory else 0.01
        msg = f"min price has to be {min_price}"
        if form.price.data < min_price:
            return render_template('new_inventory.html', form=form, msg=msg)
        
        result = Inventory.addNewInventory(
            sid=sid, 
            pid=form.pid.data,
            current_quantity=form.current_quantity.data,
            price=form.price.data
        )
        if result:
            return redirect(url_for('inventory.inventory'))
        else:
            print('Failed to add new inventory.', 'error')
    
    return render_template('new_inventory.html', form=form, msg=msg)


@bp.route('/inventory/edit', methods=['GET', 'POST'])
@login_required
def edit_inventory():
    invid = request.args.get('invid') if request.method == 'GET' else request.form.get('invid')
    inventory = Inventory.getById(invid)
    product = Product.get(inventory.pid)
    original_tags = Tag.getByProducts(product.id)
    tag_labels = [Category.get(tag.cid).label for tag in original_tags]
    
    # standardize products across seller:
    # price has to be at least 0.8 * original inventory
    creator_sid = Seller.getByUid(product.uid).id
    original_inventory = Inventory.traceCreatorInventory(creator_sid, product.id)
    min_price = int(float(original_inventory.price) * 0.8) + 1 if original_inventory else 0.01
    
    form = InventoryForm()
    if form.validate_on_submit():
        new_info = {
            'current_quantity': form.current_quantity.data,
            'price': form.price.data,
        }
        # if Inventory.update_inventory(invid, new_info) and Inventory.update_design(invid, new_info):
        if Inventory.update_inventory(invid, new_info):
            return redirect(url_for('inventory.inventory'))
    else:
        print("Form errors:", form.errors)

    designs = Inventory.get_inventory_designs(invid)
    return render_template('edit_inventory.html', form=form, product=product, min_price=min_price, tags=tag_labels, inventory=inventory, designs=designs)


@bp.route('/inventory/delete', methods=['POST'])
@login_required
def delete_inventory():
    invid = request.form['invid']
    try:
        if Inventory.deleteById(invid):
            return '', 204  
        else:
            return 'Deletion failed', 400  
    except Exception as e:
        return str(e), 500 


@bp.route('/inventory/seller_order_list')
@login_required
def seller_order_list():
    """
    Displays a list of all orders associated with the current seller, optionally filtered by search terms and date range.
    """
    sid = Seller.getByUid(current_user.id).id
    search_term = request.args.get('search_term', None)
    start_date = request.args.get('start_date', None)
    end_date = request.args.get('end_date', None)
    inventory_name = request.args.get('inventory_name', None)
    
    if isinstance(inventory_name, str):
        inventory_name = inventory_name.lower()
      
    # order_details = Order.get_by_seller(sid) 
    order_details = Order.search_by_criteria(current_user.id, sid, search_term, start_date, end_date, inventory_name, 'seller')
    
    return render_template('seller_order_list.html', order_details=order_details)


@bp.route('/inventory/seller_order_vis')
@login_required
def seller_order_vis():
    """
    Visualizes all orders for the current seller to provide an overview of sales data.
    """
    sid = Seller.getByUid(current_user.id).id
    order_details = Order.get_all_order_products_by_seller(sid)
    
    return render_template('seller_order_vis.html', order_details=order_details)


@bp.route('/inventory/seller_order_detail/<int:order_id>')
@login_required
def seller_order_detail(order_id):
    """
    Displays detailed information for a specific order, accessible only to the seller of the order.
    """
    sid = Seller.getByUid(current_user.id).id
    order_details = Order.get_order_products_by_seller(order_id, sid)
    
    return render_template('seller_order_detail.html', order_details=order_details, order_id=order_id)


@bp.route('/inventory/mark_fulfilled', methods=['POST'])
@login_required
def mark_fulfilled():
    """
    Marks an order as fulfilled based on the provided order and inventory IDs, updating the status accordingly.
    """
    order_id = request.form.get('order_id')
    invid = request.form.get('invid')
    success = Order.mark_as_fulfilled(order_id, invid) 
    if success:
        check = Order.update_order_status(order_id)
    return redirect(url_for('inventory.seller_order_detail', order_id=order_id))


class InventoryDesignForm(FlaskForm):
    """
    Form class for managing inventory design data including name, description, and associated images.
    """
    name = StringField('Name', validators=[DataRequired()])
    description = StringField('Description', validators=[DataRequired()])
    images = FileField('Product Image', validators=[FileAllowed(['jpeg'], 'Images only!')], render_kw={"multiple": True})
    submit = SubmitField('Submit')

    def __init__(self, *args, **kwargs):
        super(InventoryDesignForm, self).__init__(*args, **kwargs)
        

@bp.route('/inventory/edit_design/<int:invid>', methods=['GET', 'POST'])
@login_required
def edit_design(invid):
    """
    Allows editing of inventory design details, including updating or adding new design information and associated images.
    """
    inventory = Inventory.getById(invid)
    
    form = InventoryDesignForm()
    if form.validate_on_submit():
        # Add or Update inventory design
        exist_design = Inventory.check_exist_design(invid)
        design_update = Inventory.add_or_update_design(exist_design, invid, form.name.data, form.description.data)
        
        files = request.files.getlist('images')  
        
        added_images = []
        for file in files:
            if file and allowed_file(file.filename):
                saved_image = Image.add_image(file)
                print(f'saved images: {saved_image.content}')
                added_images.append(saved_image.id)

        image_update = Inventory.add_images_to_inventory(invid, added_images)
        if design_update and image_update:
            return redirect(url_for('inventory.inventory'))
    else:
        print("Form errors:", form.errors)
        
    return render_template('edit_inventory_design.html', form=form, inventory=inventory)


def allowed_file(filename):
    """
    Determines if the uploaded file has an allowed file extension.
    """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() == 'jpeg'
