GitLab repo: https://gitlab.oit.duke.edu/yl967/extensible-hasher.git
P.S. The Gradescope raised an error "server responded with 0 code" so we couldn't upload our CODE.zip.
     We have sent an email as well as an Ed post, and our files are attached to it.
     Could you take a look at it? Also, you could go to our gitlab repo, and the main branch is our final product.
     Thank you!
     Ed post: https://edstem.org/us/courses/52274/discussion/4891467

Link to the final project long demo video: 
	- https://drive.google.com/file/d/1P1HTYG8H7shJtt73JRQm73MqhLgoBkUm/view?usp=sharing
	- https://www.youtube.com/watch?v=3ZUkjsGLn2A
Link to the additional short video (extras): 
	- https://drive.google.com/file/d/1uKkhCZFhpQsn5nM0_-4PM0uK9g1LOG5a/view?usp=sharing
	- https://www.youtube.com/watch?v=STP-SKlkeUo

README.txt: list your team members and their roles, briefly summarize what each of you have done since the last milestone, and include a link to your repo

Team members:
- Zihan Cao: Products Guru - responsible for Products
  a. (extra) Added sorting product by rating and sales
  b. (extra) Allow sellers to add tags to a product
  c. Added seller list to the detailed product page
  d. Participate in the demo recording.

- Yuxuan Gu: Carts Guru - responsible for Cart / Order
  a. (extra) Added save for later in functionality cart
  b. Fixed product quantity in order
  c. Participate in the demo recording.

- Yang Li: Sellers Guru - responsible for Inventory / Order Fulfillment
  a. User guru: 
    - Balance top up/withdraw
    - User public view
    - (extra) Search/filter purchase history by item, by seller, by date, etc
  b. Product guru:
    - User create new products for sale & edit product information
    - (extra) Mixed filter/sort a list of products by average review rating, total sales, minimum rating, price range, keyword, seller, etc.
    - (extra) Maintain a set of "tags" for labeling products
    - (extra) "Standardize" products across seller with different inventory designs, images, and price
  c. Cart guru:
    - Mark the entire order as fulfilled if all items are fulfilled
  d. Seller guru:
    - Manage inventory (add/delete product within inventory list, view/change quantity and price)
    - Browse/search the history of orders & Provide a mechanism for marking a line item as fulfilled
  e. Social guru:
    - (extra) Include the ability to submit a limited number of images in the seller feedbacks, and make these easily available to users on the website
  f. (extra) Implement well-designed large testing database with real and/or realistic data
  g. (extra) Develop method for recommending products based on past purchase history as well as reviews
  h. Complete REPORT.pdf
  i. Participate in the demo recording.

- Carl Zhang: Social Guru - responsible for Feedback / Messaging
  a. Participate in the demo recording.
  b. Created review interface for products, displaying average rating and review counts
  c. Created feedback interface for sellers, displaying average rating and review counts
  d. (extra)Added functions to upvote reviews and feedbacks, users are not allowed to upvote twice
  e. (extra)Include the ability to submit a limited number of images in the review section and make these available through displaying review

- Emily Xiang: Users Guru - responsible for Account / Purchases
  a. Participate in the demo recording.
  b. Account Information Update Page Error Fixed
  c. (User extra) Add interactive visualization on spending amounts and quantity of purchases history by category
  d. (Seller extra) Add interactive visualization to show the popularity of one’s products in the order fulfillment page.


Where to find in your code the implementation of required items above:
- User guru:
1. allow user to update balance (top up/withdraw)
  - app/models/user.py: update_balance(user_id, new_balance)
  - app/users.py: balance()
  - app/templates/balance.html
2. implement user public view
  - app/models/image.py: get_feedback_image(fid)
  - app/users.py: user_public_view(uid)
  - app/templates/balance.html
3. (extra) search/filter purchase history by item, by seller, by date, etc.
  - app/models/order.py: search_by_criteria(uid, sid=None, order_id=None, start_date=None, end_date=None, inventory_name=None, role='buyer')
  - app/order.py: order()
  - app/templates/order_history.html
4. (extra) interactive visualization on spending amounts and quantity of purchases history by category
  - app/models/order.py: get_all_order(uid)
  - app/models/order.py: search_by_category(uid, category=None, role='seller')
  - app/order.py: order_stats()
  - app/templates/order_history.html
  - app/templates/order_stats.html

- Product guru:
5. allow user to create new products & edit product information
  - app/models/product.py: add_new_product(uid, name, description, file, sid, current_quantity, price), update_product(pid, name, description)
  - app/product.py: class ProductForm(FlaskForm), class ProductInfoForm(FlaskForm), add_product(), edit_product()
  - app/templates/new_product.html
  - app/templates/edit_product.html
6. (extra) allow user to filter/sort a list of products by multiple filters
  - app/models/inventory.py: search_inventory_by_form(sid=None, keyword=None, category=None, sort=None, rating_filter=None, price_min=None, price_max=None), getByRating(order='desc'), getBySales(order='desc')
  - app/inventory.py: search_inventory_form(), get_inventories_details(filter_type, filter_value=None, order=None, sid=None, keyword=None, category=None, sort=None, rating_filter=None, price_min=None, price_max=None)
  - app/templates/base.html
  - app/templates/search_results.html
7. (extra) maintain a set of tags for labeling products (no create by seller, like amazon)
  - app/models/tag.py: add_new_tag(pid, cid), delete_product_tag(pid)
  - app/product.py: add_product(), edit_product(invid)
  - app/templates/new_product.html
  - app/templates/edit_product.html
8. (extra) "standardize" products across seller with different inventory designs, images, and price
  - app/models/inventory.py: check_exist_design(invid), add_or_update_design(existing_design, invid, name, description), add_images_to_inventory(invid, image_ids)
  - app/inventory.py: add_inventory(), edit_inventory()
  - app/templates/new_inventory.html
  - app/templates/edit_inventory.html
9. (extra) Added seller list to the detailed product page
  - app/cart.py: add_product_to_cart()
  - app/models/inventory.py: getSameProductById(id)
  - app/templates/index.html
  - app/templates/new_product.html
  - app/templates/seller_product_detail.html 

- Cart guru:
10. automatically mark the entire order as fulfilled if all items are fulfilled
  - app/models/order.py: check_order_products_fulfilled(oid), update_order_status(oid)
  - app/inventory.py: mark_fulfilled(), sort_inventory_by_rating(), sort_inventory_by_sales()
11. (extra) Added save for later in functionality cart
  - app/cart.py: save_for_later()
  - app/models/cart.py: save_product_for_later(cid, invid)
  - app/templates/cart.html
  - app/templates/save_for_later.html 


- Seller guru:
12. allow seller to manage inventory
  - app/models/inventory.py: get_inventory_designs(invid), update_inventory(invid, new_info), traceCreatorInventory(sid, pid), check_exist_design(invid), add_or_update_design(check, invid, name, description), add_images_to_inventory(invid, image_ids), addNewInventory(sid, pid, current_quantity, price)
  - app/inventory.py: class InventoryForm(FlaskForm), class NewInventoryForm(FlaskForm), class InventoryDesignForm(FlaskForm), add_inventory(), edit_inventory(), edit_design(invid) 
  - app/templates/edit_inventory_design.html
  - app/templates/edit_inventory.html
  - app/templates/new_inventory.html
13. allow seller to browse/search order history & mark a line items as fulfilled
  - app/models/order.py: get_order_history_with_summary(order_ids), search_by_criteria(uid, sid, search_term, start_Date, end_date, inventory_name, 'seller')
  - app/inventory.py: seller_order_list(), mark_fulfilled()
  - app/templates/seller_order_list.html
  - app/templates/seller_order_detail.html
14. (extra) interactive visualization to show the popularity of one’s products in the order fulfillment page.
  - app/inventory.py: seller_order_vis()
  - app/models/inventory.py: get_all_order_products(sid)
  - app/models/order.py: get_all_order_products_by_seller(sid)
  - app/templates/seller_order_list.html
  - app/templates/seller_order_vis.html

- Social guru:
15. (extra) allow user to submit a limited number of images in the seller feedbacks
  - app/models/feedback.py: add_images_to_feedback(fid, image_ids)
  - app/models/image.py: get_feedback_image(fid)
  - app/feedback.py: feedback_image_update(files, feedback_id), get_current_feedback_images(feedback_history), class FeedbackForm(FlaskForm), feedback(), edit_feedback(fid), new_feedback(sid) 
  - app/users.py: user_public_view(uid)
  - app/templates/edit_feedback.html
  - app/templates/new_feedback.html
  - app/templates/_feedback_list.html
  - app/templates/user_public_view.html
  - app/templates/feedback_history.html
16.（extra) allow user to submit a limited number of images in the inventory reviews
  - app/models/review.py: add_images_to_review(rid, image_ids)
  - app/models/image.py: get_review_image(rid)
  - app/review.py: review_image_update(files, review_id), get_current_review_images(review_history), class ReviewForm(FlaskForm), review(), edit_review(rid), new_review(invid) 
  - app/templates/edit_review.html
  - app/templates/new_review.html
  - app/templates/_review_list.html
  - app/templates/review_history.html
  - app/templates/inventory_reviews.html
17. Review and feedback interface
  - app/models/feedback.py: add_upvote(feedback_id, user_id),check_user_upvote(user_id, feedback_id)
  - app/feedback.py: upvote_feedback
  - app/templates/_feedback_list.html
  - app/templates/user_public_view.html
  - app/review.py: inventory_reviews(invid), upvote_review(review_id)
  - app/models/review.py:add_upvote(review_id, user_id), check_user_upvote(user_id, review_id)
  - app/templates/seller_product_detail.html
  - app/templates/_review_list.html
  - app/templates/inventory_reviews.html

- Additional Features
18. (extra) Well-designed large testing database with real and/or realistic data:
  - db/generated/generate.py: a data generator for larger database
  - db/data/*.csv: large size database with realistic data
  - app/static/images/*.jpeg: realistic image data
19. (extra) provide personalized recommendation based on user's past purchase history and reviews
  - app/models/recommendation.py: recommend_products_based_on_history_and_reviews(user_id)
  - app/cart.py: check_authentication(recommend=False), cart()
  - app/templates/cart.html
