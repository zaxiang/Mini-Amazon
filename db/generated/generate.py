from werkzeug.security import generate_password_hash
import csv
from faker import Faker
import random

num_users = 100
num_products = 500
num_images = 100
num_carts = 100
num_sellers = 100
num_inventories = 500
num_orders = 200
num_categories = 200
num_design = 30
num_feedbacks = 300
num_reviews = 200


Faker.seed(0)
fake = Faker()


def get_csv_writer(f):
    return csv.writer(f, dialect='unix')

def gen_images(num_images):
    with open('Images.csv', 'w') as f:
        writer = get_csv_writer(f)
        print('Images...', end=' ', flush=True)
        for imgid in range(10, num_images):
            if imgid % 100 == 0:
                print(f'{imgid}', end=' ', flush=True)
            content = f'{imgid}.jpeg'
            writer.writerow([imgid, content])
        print(f'{num_images} generated')
    return 


def gen_users(num_users):
    with open('Users.csv', 'w') as f:
        writer = get_csv_writer(f)
        print('Users...', end=' ', flush=True)
        for uid in range(7, num_users):
            if uid % 10 == 0:
                print(f'{uid}', end=' ', flush=True)
            profile = fake.profile()
            email = profile['mail']
            plain_password = f'test123'
            password = generate_password_hash(plain_password)
            name_components = profile['name'].split(' ')
            firstname = name_components[0]
            lastname = name_components[-1]
            address = profile['address']
            balance = random.randint(0, 2000)
            writer.writerow([uid, email, password, firstname, lastname, address, balance])
        print(f'{num_users} generated')
    return


def gen_products(num_products):
    available_pids = []
    with open('Products.csv', 'w') as f:
        writer = get_csv_writer(f)
        print('Products...', end=' ', flush=True)
        for pid in range(7, num_products):
            if pid % 100 == 0:
                print(f'{pid}', end=' ', flush=True)
            uid = fake.random_int(min=0, max=num_users-1)
            name = fake.sentence(nb_words=4)[:-1]
            description = fake.sentence()
            imgid = random.randint(1, num_images)
            available_pids.append(pid)
            writer.writerow([pid, uid, name, description, imgid])
        print(f'{num_products} generated; {len(available_pids)} available')
    return available_pids

def gen_categories(num_categories):
    categories = [
        "Ice Cream", "Beer", "Eggs", "Painting", "Books", 
        "Electronics", "Clothing", "Jewelry", "Furniture", "Toys",
        "Games", "Sports", "Outdoor", "Gardening", "Appliances",
        "Shoes", "Bags", "Watches", "Sunglasses", "Cosmetics"
    ]
    
    # Generate more categories to reach 100
    while len(categories) < num_categories:
        category = fake.unique.word().capitalize()
        if category not in categories:
            categories.append(category)
            
    with open('Categories.csv', 'w') as f:
        writer = get_csv_writer(f)
        print('Categories...', end=' ', flush=True)
        for idx, category in enumerate(categories, start=1):
            if idx % 100 == 0:
                print(f'{idx}', end=' ', flush=True)
            writer.writerow([idx, category])
        print(f'{num_categories} generated')
    return 

def gen_tags(num_products, num_categories):
    with open('Tags.csv', 'w') as f:
        writer = get_csv_writer(f)
        print('Tags...', end=' ', flush=True)
        for pid in range(1, num_products):
            num_tags = random.randint(1, 5)
            assigned_categories = random.sample(range(1, num_categories+1), num_tags)
            for cid in assigned_categories:
                writer.writerow([pid, cid])
        print(f'All tags generated')
    return 

def gen_carts(num_carts):
    with open('Carts.csv', 'w') as f:
        writer = get_csv_writer(f)
        print('Carts...', end=' ', flush=True)
        for cid in range(0, num_carts):
            if cid % 100 == 0:
                print(f'{cid}', end=' ', flush=True)
            uid = cid
            writer.writerow([cid, uid])
        print(f'{num_carts} generated')
    return 

def gen_orders(num_orders):
    with open('Orders.csv', 'w') as f:
        writer = get_csv_writer(f)
        print('Orders...', end=' ', flush=True)
        for oid in range(9, num_orders):
            if oid % 100 == 0:
                print(f'{oid}', end=' ', flush=True)
            uid = fake.random_int(min=0, max=10)
            time_created = fake.date_time_this_year()
            fulfillment_status = 'pending'
            time_fulfilled = None
            writer.writerow([oid, uid, time_created, fulfillment_status, time_fulfilled])
        print(f'{num_orders} generated')
    return 

def gen_sellers(num_sellers):
    with open('Sellers.csv', 'w') as f:
        writer = get_csv_writer(f)
        print('Sellers...', end=' ', flush=True)
        for sid in range(6, num_sellers):
            if sid % 100 == 0:
                print(f'{sid}', end=' ', flush=True)
            uid = sid
            writer.writerow([sid, uid])
        print(f'{num_sellers} generated')
    return 

def gen_inventories(num_inventories):
    with open('Inventories.csv', 'w') as f:
        writer = get_csv_writer(f)
        print('Inventories...', end=' ', flush=True)
        for invid in range(13, num_inventories):
            if invid % 100 == 0:
                print(f'{invid}', end=' ', flush=True)
            sid = fake.random_int(min=0, max=10)
            pid = fake.random_int(min=1, max=num_products-1)
            current_quantity = random.randint(1, 100)
            price = f'{str(fake.random_int(max=20))}.{fake.random_int(max=99):02}'
            writer.writerow([invid, sid, pid, current_quantity, price])
        print(f'{num_inventories} generated')
    return 

def gen_inventories_designs(num_design):
    with open('Inventory_Designs.csv', 'w') as f:
        writer = get_csv_writer(f)
        print('Inventory_Designs...', end=' ', flush=True)
        for _ in range(num_design):
            invid = random.randint(1, 100)
            name = fake.sentence(nb_words=4)[:-1]
            description = fake.sentence()
            writer.writerow([invid, name, description])
        print(f'{num_design} generated')
    return 

def gen_inventories_images():
    with open('Inventory_Images.csv', 'w') as f:
        writer = get_csv_writer(f)
        print('Inventory_Images...', end=' ', flush=True)
        for _ in range(20):
            num_images = random.randint(1, 5)
            for _ in range(num_images):
                invid = random.randint(1, 10)
                imgid = random.randint(1, 100)
                writer.writerow([invid, imgid])
        print(f'inventory images generated')
    return 

def gen_orders_products():
    with open('Order_Products.csv', 'w') as f:
        writer = get_csv_writer(f)
        print('Order_Products...', end=' ', flush=True)
        for oid in range(num_orders):
            if oid % 100 == 0:
                print(f'{oid}', end=' ', flush=True)
            num_requested = random.randint(1, 5)
            for _ in range(num_requested):
                invid = fake.random_int(min=1, max=92)
                quantity = random.randint(1, 3)
                # price = f'{str(fake.random_int(max=10))}.{fake.random_int(max=99):02}'
                price = 0
                fulfillment_status = 'pending'
                time_fulfilled = None
                writer.writerow([oid, invid, quantity, price, fulfillment_status, time_fulfilled])
    return 

def gen_cart_products():
    with open('Cart_Products.csv', 'w') as f:
        writer = get_csv_writer(f)
        print('Cart_Products...', end=' ', flush=True)
        for cid in range(num_carts):
            if cid % 100 == 0:
                print(f'{cid}', end=' ', flush=True)
            num_requested = random.randint(1, 5)
            for _ in range(num_requested):
                invid = fake.random_int(min=1, max=199)
                quantity = random.randint(1, 3)
                unit_price = f'{str(fake.random_int(max=10))}.{fake.random_int(max=99):02}'
                in_cart = "TRUE"
                writer.writerow([cid, invid, quantity, unit_price, in_cart])
    return

def gen_reviews(num_reviews):
    with open('Reviews.csv', 'w') as f:
        writer = get_csv_writer(f)
        print('Reviews...', end=' ', flush=True)
        for rid in range(4, num_reviews):
            if rid % 100 == 0:
                print(f'{rid}', end=' ', flush=True)
            uid = fake.random_int(min=0, max=10)
            invid = fake.random_int(min=30, max=100)
            rating = random.randint(1, 5)
            review = fake.sentence()
            time_created = fake.date_time_this_year()
            upvote = fake.random_int(min=0, max=100)
            writer.writerow([rid, uid, invid, rating, review, time_created, upvote])
        print(f'{num_reviews} generated')
    return  

def gen_feedback(num_feedbacks):
    with open('Feedbacks.csv', 'w') as f:
        writer = get_csv_writer(f)
        print('Feedbacks...', end=' ', flush=True)
        for fid in range(12, num_feedbacks):
            if fid % 100 == 0:
                print(f'{fid}', end=' ', flush=True)
            uid = fake.random_int(min=1, max=99)
            sid = fake.random_int(min=1, max=98)
            if uid == sid: 
                sid += 1
            rating = random.randint(1, 5)
            review = fake.sentence()
            time_created = fake.date_time_this_year()
            upvote = fake.random_int(min=0, max=100)
            writer.writerow([fid, uid, sid, rating, review, time_created, upvote])
        print(f'{num_feedbacks} generated')
    return 


# gen_images(num_images)
# gen_users(num_users)
# available_pids = gen_products(num_products)
# gen_sellers(num_sellers)
# gen_categories(num_categories)
# gen_carts(num_carts)
# gen_tags(num_products, num_categories)
# gen_orders(num_orders)
# gen_inventories(num_inventories)
# gen_inventories_designs(num_design)
# gen_inventories_images()
# gen_orders_products()
# gen_cart_products()
# gen_reviews(num_reviews)
gen_feedback(num_feedbacks)