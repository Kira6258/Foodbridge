from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user
from models.db import mysql, User
import MySQLdb.cursors
from firebase_admin import auth as firebase_auth

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if request.is_json:
            return jsonify({"success": True, "redirect": redirect_dashboard(current_user.role).location})
        return redirect_dashboard(current_user.role)
    
    if request.method == 'POST':
        id_token = request.json.get('idToken') if request.is_json else None
        
        if id_token:
            try:
                decoded_token = firebase_auth.verify_id_token(id_token)
                email = decoded_token['email']
                
                user_data = User.find_by_email(email)
                if user_data:
                    user = User(user_data)
                    login_user(user)
                    return jsonify({"success": True, "redirect": redirect_dashboard(user.role).location})
                else:
                    return jsonify({"success": False, "error": "User not found in database. Please register first."})
            except Exception as e:
                return jsonify({"success": False, "error": str(e)})
            
    return render_template('login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Unified registration: Firebase token + Form data
        if request.is_json:
            data = request.json
            id_token = data.get('idToken')
            name = data.get('name')
            role = data.get('role')
            phone = data.get('phone')
            lat = data.get('lat')
            lng = data.get('lng')
            
            try:
                decoded_token = firebase_auth.verify_id_token(id_token)
                email = decoded_token['email']
                uid = decoded_token['uid']
                
                if User.find_by_email(email):
                    return jsonify({"success": False, "error": "Email already exists"})
                
                # Defensive check for empty lat/lng
                if not lat or lat == '': lat = None
                if not lng or lng == '': lng = None
                
                cursor = mysql.connection.cursor()
                cursor.execute("INSERT INTO users (name, email, password_hash, phone, role, lat, lng, is_verified) VALUES (%s, %s, %s, %s, %s, %s, %s, 1)",
                               (name, email, uid, phone, role, lat, lng))
                
                user_id = cursor.lastrowid
                
                if role == 'shelter':
                    address = data.get('address')
                    capacity = data.get('capacity')
                    contact = data.get('contact')
                    cursor.execute("INSERT INTO shelters (user_id, name, address, lat, lng, capacity, contact) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                                   (user_id, name, address, lat, lng, capacity, contact))
                
                mysql.connection.commit()
                return jsonify({"success": True})
                
            except Exception as e:
                return jsonify({"success": False, "error": str(e)})
        
    return render_template('register.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

def redirect_dashboard(role):
    if role == 'donor':
        return redirect(url_for('donor.dashboard'))
    elif role == 'shelter':
        return redirect(url_for('shelter.dashboard'))
    elif role == 'volunteer':
        return redirect(url_for('volunteer.dashboard'))
    elif role == 'admin':
        return redirect(url_for('admin.dashboard'))
    return redirect(url_for('auth.login'))

@auth_bp.route('/profile')
@login_required
def profile():
    return render_template('profile.html')

@auth_bp.route('/profile/edit', methods=['POST'])
@login_required
def edit_profile():
    name = request.form.get('name')
    phone = request.form.get('phone')
    
    cursor = mysql.connection.cursor()
    cursor.execute("UPDATE users SET name = %s, phone = %s WHERE id = %s", (name, phone, current_user.id))
    mysql.connection.commit()
    
    flash('Profile updated successfully!', 'success')
    return redirect(url_for('auth.profile'))

@auth_bp.route('/profile/delete', methods=['POST'])
@login_required
def delete_account():
    cursor = mysql.connection.cursor()
    cursor.execute("DELETE FROM users WHERE id = %s", (current_user.id,))
    mysql.connection.commit()
    logout_user()
    flash('Your account has been permanently deleted.', 'info')
    return redirect(url_for('index'))
