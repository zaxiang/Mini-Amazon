from flask import render_template, redirect, url_for, request, jsonify
from flask_login import current_user, login_required
from .models.image import Image
from .models.review import Review
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField, FileField
from flask_wtf.file import FileField, FileAllowed
from wtforms.validators import DataRequired, ValidationError
from flask import Blueprint

bp = Blueprint('review', __name__)


def review_image_update(files, review_id):
    """
    Handles image upload for reviews by saving new images and associating them with a review.
    """
    added_images = []
    for file in files:
        if file:
            saved_image = Image.add_image(file)
            print(f'saved images: {saved_image.content}')
            added_images.append(saved_image.id)
    
    image_update = Review.add_images_to_review(review_id, added_images)
    return image_update


def get_current_review_images(review_history):
    """
    Retrieves associated images for each review in the given history.
    """
    review_images = {}
    for review in review_history:
        images = Image.get_review_image(review.id)
        review_images[review.id] = images if images else None
    return review_images
    

class ReviewForm(FlaskForm):
    """
    Form class for creating or editing a review, including fields for rating, text review, and image uploads.
    """
    rating = IntegerField('Rating', validators=[DataRequired()])
    review = StringField('Review', validators=[DataRequired()])
    images = FileField('Product Image', validators=[FileAllowed(['jpeg'], 'Images only!')], render_kw={"multiple": True})
    submit = SubmitField('Submit')

    def __init__(self, *args, **kwargs):
        super(ReviewForm, self).__init__(*args, **kwargs)
        
    # Validate the rating is within 1 to 5
    def validate_rating(self, rating):
        if rating.data > 5 or rating.data < 1:
            raise ValidationError('Invalid rating: Has to be 1 - 5')


@bp.route('/review')
@login_required
def review():
    """
    Displays the history of reviews made by the current user.
    """
    review_history = Review.getByUser(current_user.id) or []
    review_images = get_current_review_images(review_history)
            
    return render_template('review_history.html', review_history=review_history, review_images=review_images)


@bp.route('/review/new/<int:invid>', methods=['GET', 'POST'])
@login_required
def new_review(invid):
    """
    Creates a new review for a specific inventory item, ensuring no duplicate reviews for the same item.
    """
    existing_review = Review.review_exists_for_user_and_inventory(current_user.id, invid)
    if existing_review:
        return redirect(url_for('review.review')) 
    form = ReviewForm()
    if form.validate_on_submit():
        result = Review.add_review(uid=current_user.id, invid=invid, rating=int(form.rating.data), review_text=form.review.data)
        if result:
            files = request.files.getlist('images')
            if review_image_update(files, result.id):
                return redirect(url_for('review.review'))
    else:
        print("Form errors:", form.errors)
        
    return render_template('new_review.html', form=form, invid=invid)


@bp.route('/review/delete/<int:review_id>', methods=['POST'])
@login_required
def delete_review(review_id):
    """
    Deletes a specific review, ensuring that only the creator of the review can delete it.
    """
    review_to_delete = Review.getById(review_id)
    if review_to_delete is None or review_to_delete.uid != current_user.id:
        return redirect(url_for('review.review'))

    success = Review.deleteById(review_id)

    return redirect(url_for('review.review'))


@bp.route('/review/edit/<int:review_id>', methods=['GET', 'POST'])
@login_required
def edit_review(review_id):
    """
    Edits an existing review, updating text, rating, and images.
    """
    review = Review.getById(review_id)
    if not review or review.uid != current_user.id:
        return redirect(url_for('review.review'))
    form = ReviewForm()
    if form.validate_on_submit():
        result = Review.update_review(review_id, int(form.rating.data), form.review.data)
        if result:
            files = request.files.getlist('images')
            if review_image_update(files, review_id):
                return redirect(url_for('review.review'))
    else:
        print("Form errors:", form.errors)
    
    return render_template('edit_review.html', form=form, review=review)


@bp.route('/review/inventory/<int:invid>')
@login_required
def inventory_reviews(invid):
    """
    Displays all reviews for a specific inventory item, calculating average ratings and providing associated images.
    """
    reviews = Review.getByInventory(invid)
    review_images = {}
    
    if reviews:
        # Calculate average rating
        average_rating = sum(review.rating for review in reviews) / len(reviews) if reviews else 0
        review_count = len(reviews)  # Calculate the number of reviews

        # Fetch images for each review
        for review in reviews:
            images = Image.get_review_image(review.id)
            review_images[review.id] = images if images else None
    else:
        average_rating = 0  # default value if no reviews
        review_count = 0

    return render_template('inventory_reviews.html', reviews=reviews, average_rating=average_rating, review_count=review_count, invid=invid, review_images=review_images)


@bp.route('/review/vote/<int:review_id>', methods=['POST'])
@login_required
def upvote_review(review_id):
    """
    Adds an upvote to a review, ensuring that a user can only upvote a review once.
    """
    # Check if the current user has already upvoted this review
    already_upvoted = Review.check_user_upvote(current_user.id, review_id)
    if already_upvoted:
        return jsonify({'error': 'You have already voted this review'}), 400

    if Review.add_upvote(review_id, current_user.id):
        return jsonify({'success': 'Upvote added'}), 200
    else:
        return jsonify({'error': 'Failed to upvote'}), 500
