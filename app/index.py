from flask import Blueprint, render_template, request, jsonify, url_for, redirect, flash
from flask_login import current_user
from .models.product import Product
from .models.image import Image
from .models.inventory import Inventory
from .models.category import Category
from .models.seller import Seller

bp = Blueprint('index', __name__)

def get_all_products_details():
    """
    Retrieves details for all products including related images.
    """
    products_details = []
    products = Product.get_all()
    if products:
        for product in products:
            # Retrieve the associated image for each product
            images = Image.get_product_image(product.id)
            products_details.append({
                'products': product,
                'images': images
            })
    return products_details


def get_all_inventories_details():
    """
    Retrieves details for all inventories including related products, images, and designs.
    """
    inventories_details = []
    inventories = Inventory.get_all()
    if inventories:
        for inventory in inventories:
            # For each inventory, get related products and designs
            related_products = Product.get_inventory_products(inventory.id)
            images = Image.get_inventory_image(inventory.id) if Image.has_inventory_images(inventory.id) else Image.get_product_image(related_products.id)
            designs = Inventory.get_inventory_designs(inventory.id)
            inventories_details.append({
                'inventory': inventory,
                'products': related_products,
                'images': images,
                'designs': designs[0] if designs else None
            })
    return inventories_details


@bp.route('/', methods=['GET', 'POST'])
def index():
    """
    Main index route which displays products and inventories along with an option to view top priced products if requested via POST.
    """
    products_details = get_all_products_details()
    inventory_details = get_all_inventories_details()
    check = False  # Flag to check if the current user is a seller
    
    top_products = None
    if request.method == 'POST':
        k = request.form.get('k', type=int)
        if k is not None and k > 0:
            top_products = Inventory.get_top_k_highest_priced_products(k)
            
    if current_user.is_authenticated:
        check = Seller.is_seller(current_user.id)
    
    return render_template('index.html', check=check, products_details=products_details, inventory_details=inventory_details, top_products=top_products, categories=Category.getExistCategories())
