from flask_login import UserMixin
from flask import current_app as app
from werkzeug.security import generate_password_hash, check_password_hash
from flask import jsonify
import logging
from .. import login


class User(UserMixin):
    """Define the User class with UserMixin to utilize Flask-Login functionalities"""
    def __init__(self, id, email, firstname, lastname, address="", balance=0):
        self.id = id
        self.email = email
        self.firstname = firstname
        self.lastname = lastname
        self.address = address
        self.balance = balance


    @staticmethod
    def get_by_auth(email, password):
        """Authenticate user by email and password"""
        rows = app.db.execute("""
            SELECT password, id, email, firstname, lastname
            FROM Users
            WHERE email = :email
            """, email=email)
        if not rows:  # email not found
            return None
        elif not check_password_hash(rows[0][0], password):
            # incorrect password
            return None
        else:
            return User(*(rows[0][1:]))


    @staticmethod
    def email_exists(email, update=False, uid=None):
        """Check if email already exists in the database"""
        rows = app.db.execute("""
            SELECT id, email
            FROM Users
            WHERE email = :email
            """, email=email)
        if update:
            return not ((len(rows) == 1 and int(rows[0][0]) == uid) or len(rows) == 0)
        else:
            return len(rows) > 0


    @staticmethod
    def register(email, password, firstname, lastname):
        """Register a new user with email and password"""
        try:
            rows = app.db.execute("""
                INSERT INTO Users(email, password, firstname, lastname)
                VALUES(:email, :password, :firstname, :lastname)
                RETURNING id
                """, email=email,
                     password=generate_password_hash(password),
                     firstname=firstname, lastname=lastname)
            id = rows[0][0]
            return User.get(id)
        except Exception as e:
            return None


    @staticmethod
    @login.user_loader
    def get(id):
        """Fetch user by ID for login management"""
        rows = app.db.execute("""
            SELECT id, email, firstname, lastname, address, balance
            FROM Users
            WHERE id = :id
            """, id=id)
        return User(*(rows[0])) if rows else None
    
    
    @staticmethod
    def get_seller_account(sid):
        """Retrieve a user account that is a seller"""
        rows = app.db.execute('''
            SELECT u.id, u.email, u.firstname, u.lastname, u.address, u.balance
            FROM users u
            JOIN sellers s ON u.id = s.uid
            WHERE s.id = :sid
            ''', sid=sid)
        return User(*(rows[0])) if rows is not None else None


    @staticmethod
    def update_information(new_info):
        """Update user information (without balance)"""
        try:
            query = f"UPDATE Users SET firstname = '{new_info['firstname']}', lastname = '{new_info['lastname']}', email = '{new_info['email']}', address = '{new_info['address']}', password = '{generate_password_hash(new_info['password'])}' WHERE id = '{new_info['id']}'"
            print("execute this update info query")
            app.db.execute(query)
            return True
        except Exception as e:
            logging.error(f"Failed to update user information: {str(e)}")
            return None

    
    @staticmethod
    def update_balance(user_id, new_balance):
        """Update the user's balance in the database"""
        try:
            app.db.execute(
                """
                UPDATE Users
                SET balance = :new_balance
                WHERE id = :user_id
                """,
                new_balance=new_balance,
                user_id=user_id
            )
            return True
        except Exception as e:
            return False