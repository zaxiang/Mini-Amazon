import base64
from flask import render_template, redirect, url_for, flash, request
from flask_login import current_user, login_required
from .models.seller import Seller 
from .models.inventory import Inventory
from .models.product import Product
from .models.image import Image
from .models.category import Category
from .models.tag import Tag
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SelectMultipleField, SubmitField, HiddenField, FloatField, FileField
from flask_wtf.file import FileField, FileAllowed
from wtforms.validators import DataRequired, NumberRange, InputRequired
from werkzeug.utils import secure_filename
from flask import Blueprint

bp = Blueprint('product', __name__)


class ProductForm(FlaskForm):
    """
    Form class for adding new products with fields for name, description, image upload, quantity, price, and categories.
    """
    name = StringField('Name', validators=[DataRequired()])
    description = StringField('Description', validators=[DataRequired()])
    image = FileField('Product Image', validators=[FileAllowed(['jpeg'], 'Images only!'), DataRequired()])
    current_quantity = IntegerField('Current Quantity', validators=[DataRequired(), NumberRange(min=0)])
    price = FloatField('Price', validators=[DataRequired(), NumberRange(min=0)])
    categories = SelectMultipleField('Categories', choices=[], coerce=str, validators=[DataRequired()])
    submit = SubmitField('Submit')

    def __init__(self, *args, **kwargs):
        super(ProductForm, self).__init__(*args, **kwargs)
        self.setup_categories()

    def setup_categories(self):
        """
        Sets up the category choices for the select field using available categories from the database.
        """
        category_choices = [(str(cat.id), cat.label) for cat in Category.get_all()]
        self.categories.choices = category_choices


@bp.route('/add_product', methods=['GET', 'POST'])
@login_required
def add_product():
    """
    Adds a new product to the database. If the form validation is successful, it saves the product,
    uploads the image, and redirects to the home page.
    """
    form = ProductForm()
    if form.validate_on_submit():
        file = form.image.data
        if file:
            filename = secure_filename(file.filename)
            print("reach here: ", filename)
            sid = Seller.getByUid(current_user.id).id
            result = Product.add_new_product(current_user.id, form.name.data, form.description.data, file, sid, form.current_quantity.data, form.price.data)
            if result:
                selected_categories = form.categories
                for category in selected_categories.data:
                    Tag.add_new_tag(result['product'].id, category)
                return redirect(url_for('index.index'))
    else:
        print('Form is invalid:', form.errors)
    
    return render_template('new_product.html', form=form)


class ProductInfoForm(FlaskForm):
    """
    Form class for editing existing product information with fields for name, description, image, and categories.
    """
    name = StringField('Name', validators=[DataRequired()])
    description = StringField('Description', validators=[DataRequired()])
    image = FileField('Product Image', validators=[FileAllowed(['jpeg'], 'Images only!')])
    categories = SelectMultipleField('Categories', choices=[], coerce=str, validators=[DataRequired()])
    submit = SubmitField('Submit')

    def __init__(self, *args, **kwargs):
        super(ProductInfoForm, self).__init__(*args, **kwargs)
        self.setup_categories()

    def setup_categories(self):
        """
        Refreshes the category choices for the form each time it is instantiated.
        """
        category_choices = [(str(cat.id), cat.label) for cat in Category.get_all()]
        self.categories.choices = category_choices
        
        
@bp.route('/product/edit/<int:invid>', methods=['GET', 'POST'])
@login_required
def edit_product(invid):
    """
    Handles the editing of product details for a specific inventory item identified by 'invid'.
    Ensures that the current user is the owner of the product before allowing edits.
    """
    inventory = Inventory.getById(invid)
    product = Product.get(inventory.pid)  
    # make sure no sneaking change product information
    if product.uid != current_user.id:
        return redirect(url_for('index.index'))
    
    original_tags = Tag.getByProducts(product.id)
    tag_labels = [Category.get(tag.cid).label for tag in original_tags]
    
    form = ProductInfoForm()
    
    if form.validate_on_submit():
        file = form.image.data
        if file:
            Image.save_image(file, product.imgid)
            
        # Update the product details
        product_update = Product.update_product(product.id, form.name.data, form.description.data)
        if product_update and Tag.delete_product_tag(product.id):
            selected_categories = form.categories
            for category in selected_categories.data:
                Tag.add_new_tag(product.id, category)
            return redirect(url_for('inventory.inventory'))
    else:
        print("Form errors:", form.errors)

    return render_template('edit_product.html', form=form, product=product, tags=tag_labels, inventory=inventory)