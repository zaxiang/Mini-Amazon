import base64
from flask import render_template, redirect, url_for, request, abort, jsonify
from flask_login import current_user, login_required
from .models.image import Image
from .models.feedback import Feedback
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField, FileField
from flask_wtf.file import FileField, FileAllowed
from wtforms.validators import DataRequired, ValidationError

from flask import Blueprint
bp = Blueprint('feedback', __name__)

def feedback_image_update(files, feedback_id):
    """
    Processes image uploads for a feedback entry, saves the images, and updates the feedback record.
    
    Args:
        files (werkzeug.datastructures.FileStorage): List of file storage objects representing images.
        feedback_id (int): The ID of the feedback entry to associate the images with.
    
    Returns:
        bool: True if images were successfully updated, False otherwise.
    """
    added_images = []
    for file in files:
        if file:
            saved_image = Image.add_image(file)
            print(f'saved images: {saved_image.content}')
            added_images.append(saved_image.id)
    
    image_update = Feedback.add_images_to_feedback(feedback_id, added_images)
    return image_update


def get_current_feedback_images(feedback_history):
    """
    Retrieves images associated with each feedback entry in the feedback history.
    
    Args:
        feedback_history (list of Feedback objects): List of feedback entries.
    
    Returns:
        dict: A dictionary mapping feedback IDs to lists of associated images.
    """
    feedback_images = {}
    for feedback in feedback_history:
        images = Image.get_feedback_image(feedback.id)
        feedback_images[feedback.id] = images if images else None
    return feedback_images
    

class FeedbackForm(FlaskForm):
    rating = IntegerField('Rating', validators=[DataRequired()])
    review = StringField('Review', validators=[DataRequired()])
    images = FileField('Product Image', validators=[FileAllowed(['jpeg'], 'Images only!')], render_kw={"multiple": True})
    submit = SubmitField('Submit')

    def __init__(self, *args, **kwargs):
        super(FeedbackForm, self).__init__(*args, **kwargs)
        
    # Validate the rating is within 1 to 5
    def validate_rating(self, rating):
        if rating.data > 5 or rating.data < 1:
            raise ValidationError('Invalid rating: Has to be 1 - 5')
        
        
@bp.route('/feedback')
@login_required
def feedback():
    """
    Displays the feedback history for the current user.
    """
    feedback_history = Feedback.getByUser(current_user.id) or []
    feedback_images = get_current_feedback_images(feedback_history)
            
    return render_template('feedback_history.html', feedback_history=feedback_history, feedback_images=feedback_images)


@bp.route('/feedback_history/recent', methods=['POST'])
@login_required
def submit_feedback_history():
    """
    Displays a limited number of recent feedback entries based on user input.
    """
    k = request.form.get('k', type=int)
    
    # Server-side validation for 'k'
    if not k or k < 1:
        return redirect(url_for('feedback.feedback'))

    uid = current_user.id
    feedback_history = Feedback.get_most_recent_k_feedback(uid, k)
    feedback_images = get_current_feedback_images(feedback_history)
        
    return render_template('feedback_history.html', feedback_history=feedback_history, feedback_images=feedback_images)


@bp.route('/feedback/delete/<int:feedback_id>', methods=['POST'])
@login_required
def delete_feedback(feedback_id):
    """
    Deletes a feedback entry, checking that the current user is the owner of the feedback.
    """
    feedback_to_delete = Feedback.getById(feedback_id)

    if feedback_to_delete is None or feedback_to_delete.uid != current_user.id:
        return redirect(url_for('feedback.feedback'))

    success = Feedback.deleteById(feedback_id)

    return redirect(url_for('feedback.feedback'))


@bp.route('/feedback/edit/<int:feedback_id>', methods=['GET', 'POST'])
@login_required
def edit_feedback(feedback_id):
    """
    Edits an existing feedback entry, allowing image updates and content changes.
    """
    feedback = Feedback.getById(feedback_id)
    if not feedback or feedback.uid != current_user.id:
        return redirect(url_for('feedback.feedback'))
    
    form = FeedbackForm()
    if form.validate_on_submit():
        result = Feedback.update_feedback(feedback_id, int(form.rating.data), form.review.data)
        if result:
            files = request.files.getlist('images')
            if feedback_image_update(files, feedback_id):
                return redirect(url_for('feedback.feedback'))
    else:
        print("Form errors:", form.errors)
    
    return render_template('edit_feedback.html', form=form, feedback=feedback)


@bp.route('/feedback/new/<int:sid>', methods=['GET', 'POST'])
@login_required
def new_feedback(sid):
    """
    Submits new feedback for a seller, identified by the seller ID (`sid`), and potentially adds images.
    """
    if Feedback.feedback_exists_for_user_and_seller(current_user.id, sid):
        return redirect(url_for('feedback.feedback')) 

    form = FeedbackForm()
    if form.validate_on_submit():
        result = Feedback.add_feedback(uid=current_user.id, sid=sid, rating=int(form.rating.data), review_text=form.review.data)
        if result:
            files = request.files.getlist('images')
            if feedback_image_update(files, result.id):
                return redirect(url_for('feedback.feedback'))
    else:
        print("Form errors:", form.errors)
        
    return render_template('new_feedback.html', form=form, sid=sid)


@bp.route('/feedback/vote/<int:feedback_id>', methods=['POST'])
@login_required
def upvote_feedback(feedback_id):
    """
    Handles the upvoting of a feedback entry, ensuring that each user can only vote once per feedback.
    """
    # Check if the current user has already upvoted this feedback
    already_upvoted = Feedback.check_user_upvote(current_user.id, feedback_id)
    if already_upvoted:
        return jsonify({'error': 'You have already voted this feedback'}), 400

    if Feedback.add_upvote(feedback_id, current_user.id):
        return jsonify({'success': 'Upvote added'}), 200
    else:
        return jsonify({'error': 'Failed to upvote'}), 500
