import firebase_admin
from firebase_admin import auth, credentials
import MySQLdb
from config import Config
import sys

def create_admin(email, password, name="System Admin"):
    # 1. Initialize Firebase Admin
    try:
        if not firebase_admin._apps:
            cred = credentials.Certificate(Config.FIREBASE_SERVICE_ACCOUNT_KEY)
            firebase_admin.initialize_app(cred)
            print("✅ Firebase Admin Initialized")
    except Exception as e:
        print(f"❌ Firebase Auth failed: {e}")
        return

    # 2. Create User in Firebase
    try:
        user = auth.create_user(
            email=email,
            password=password,
            display_name=name
        )
        uid = user.uid
        print(f"✅ Firebase User Created: {uid}")
    except Exception as e:
        if 'EMAIL_EXISTS' in str(e):
            print("ℹ️ User already exists in Firebase, trying to sync with MySQL...")
            user = auth.get_user_by_email(email)
            uid = user.uid
        else:
            print(f"❌ Firebase Creation Error: {e}")
            return

    # 3. Create User in MySQL
    try:
        db = MySQLdb.connect(
            host=Config.MYSQL_HOST,
            user=Config.MYSQL_USER,
            passwd=Config.MYSQL_PASSWORD,
            db=Config.MYSQL_DB,
            port=Config.MYSQL_PORT
        )
        cursor = db.cursor()
        
        # Check if already exists in MySQL
        cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
        if cursor.fetchone():
            cursor.execute("UPDATE users SET role = 'admin' WHERE email = %s", (email,))
            print(f"✅ User role updated to 'admin' in MySQL")
        else:
            cursor.execute(
                "INSERT INTO users (name, email, password_hash, role, is_verified) VALUES (%s, %s, %s, %s, 1)",
                (name, email, uid, 'admin')
            )
            print(f"✅ Admin user created in MySQL database")
        
        db.commit()
        db.close()
    except Exception as e:
        print(f"❌ MySQL Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python create_admin.py <email> <password>")
    else:
        create_admin(sys.argv[1], sys.argv[2])
