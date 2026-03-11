from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models.db import mysql
from models.utils import haversine
import MySQLdb.cursors
import os

donor_bp = Blueprint('donor', __name__)

@donor_bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.role != 'donor':
        return "Unauthorized", 403
    
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    # Get donor's donations
    cursor.execute("SELECT * FROM donations WHERE donor_id = %s ORDER BY posted_at DESC", (current_user.id,))
    donations = cursor.fetchall()
    
    # Get nearby shelters
    cursor.execute("SELECT * FROM shelters WHERE approved = 1")
    all_shelters = cursor.fetchall()
    
    for s in all_shelters:
        if current_user.lat is not None and current_user.lng is not None and s['lat'] is not None and s['lng'] is not None:
            dist = haversine(current_user.lat, current_user.lng, s['lat'], s['lng'])
            s['distance'] = round(dist, 2)
        else:
            s['distance'] = None
            
    # Sort by distance (None values go to the end)
    nearby_shelters = sorted(all_shelters, key=lambda x: (x['distance'] is None, x['distance']))
    
    return render_template('donor/dashboard.html', donations=donations, shelters=nearby_shelters)

@donor_bp.route('/post_donation', methods=['POST'])
@login_required
def post_donation():
    if current_user.role != 'donor':
        return "Unauthorized", 403
        
    food_desc = request.form.get('food_description')
    quantity = request.form.get('quantity')
    available_until = request.form.get('available_until')
    
    # Handle photo upload (simplified for now)
    photo_path = ""
    if 'photo' in request.files:
        file = request.files['photo']
        if file.filename != '':
            filename = f"donation_{current_user.id}_{int(os.path.getmtime('.'))}.jpg"
            file.save(os.path.join('static/uploads', filename))
            photo_path = filename

    cursor = mysql.connection.cursor()
    cursor.execute("""
        INSERT INTO donations (donor_id, food_description, quantity, photo, lat, lng, available_until)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (current_user.id, food_desc, quantity, photo_path, current_user.lat, current_user.lng, available_until))
    mysql.connection.commit()
    
    flash('Donation posted successfully!', 'success')
    return redirect(url_for('donor.dashboard'))
