from flask_mysqldb import MySQL
from flask_login import UserMixin
import MySQLdb.cursors

mysql = MySQL()

class User(UserMixin):
    def __init__(self, user_data):
        self.id = user_data['id']
        self.name = user_data['name']
        self.email = user_data['email']
        self.role = user_data.get('role')
        self.lat = user_data.get('lat')
        self.lng = user_data.get('lng')
        self.phone = user_data.get('phone')
        self.is_verified = user_data.get('is_verified', 0) # Default to 0 (False)

    @staticmethod
    def get(user_id):
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        user_data = cursor.fetchone()
        if user_data:
            return User(user_data)
        return None

    @staticmethod
    def find_by_email(email):
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user_data = cursor.fetchone()
        if user_data:
            return user_data
        return None
