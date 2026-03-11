from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models.db import mysql
from models.utils import haversine
import MySQLdb.cursors

shelter_bp = Blueprint('shelter', __name__)

@shelter_bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.role != 'shelter':
        return "Unauthorized", 403
    
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    # Get shelter info to check approval and location
    cursor.execute("SELECT * FROM shelters WHERE user_id = %s", (current_user.id,))
    shelter = cursor.fetchone()
    
    if not shelter['approved']:
        return render_template('shelter/pending.html')

    # Get nearby available donations
    cursor.execute("SELECT d.*, u.name as donor_name FROM donations d JOIN users u ON d.donor_id = u.id WHERE d.status = 'AVAILABLE'")
    all_donations = cursor.fetchall()
    
    for d in all_donations:
        if shelter['lat'] is not None and shelter['lng'] is not None and d['lat'] is not None and d['lng'] is not None:
            dist = haversine(shelter['lat'], shelter['lng'], d['lat'], d['lng'])
            d['distance'] = round(dist, 2)
        else:
            d['distance'] = None
            
    # Sort by distance (None values go to the end)
    nearby_donations = sorted(all_donations, key=lambda x: (x['distance'] is None, x['distance']))
            
    # Get incoming and history
    cursor.execute("""
        SELECT c.*, d.food_description, d.status as donation_status 
        FROM claims c 
        JOIN donations d ON c.donation_id = d.id 
        WHERE c.shelter_id = %s
    """, (shelter['id'],))
    claims = cursor.fetchall()
            
    return render_template('shelter/dashboard.html', donations=nearby_donations, claims=claims)

@shelter_bp.route('/claim/<int:donation_id>', methods=['POST'])
@login_required
def claim_donation(donation_id):
    if current_user.role != 'shelter':
        return "Unauthorized", 403
        
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM shelters WHERE user_id = %s", (current_user.id,))
    shelter = cursor.fetchone()
    
    # Check if already claimed
    cursor.execute("SELECT * FROM donations WHERE id = %s AND status = 'AVAILABLE'", (donation_id,))
    donation = cursor.fetchone()
    
    if donation:
        cursor.execute("UPDATE donations SET status = 'CLAIMED' WHERE id = %s", (donation_id,))
        cursor.execute("INSERT INTO claims (donation_id, shelter_id) VALUES (%s, %s)", (donation_id, shelter['id']))
        mysql.connection.commit()
        flash('Donation claimed successfully!', 'success')
    else:
        flash('Donation no longer available', 'danger')
        
    return redirect(url_for('shelter.dashboard'))
@shelter_bp.route('/receive/<int:donation_id>', methods=['POST'])
@login_required
def receive_donation(donation_id):
    if current_user.role != 'shelter':
        return "Unauthorized", 403
        
    cursor = mysql.connection.cursor()
    cursor.execute("UPDATE donations SET status = 'DELIVERED' WHERE id = %s", (donation_id,))
    cursor.execute("UPDATE claims SET status = 'RECEIVED' WHERE donation_id = %s", (donation_id,))
    mysql.connection.commit()
    
    flash('Donation marked as received! Thank you for your service.', 'success')
    return redirect(url_for('shelter.dashboard'))
