from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models.db import mysql
from models.utils import haversine
import MySQLdb.cursors

volunteer_bp = Blueprint('volunteer', __name__)

@volunteer_bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.role != 'volunteer':
        return "Unauthorized", 403
    
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    
    # Get available delivery tasks (donations that are CLAIMED but not yet picked up)
    cursor.execute("""
        SELECT d.*, u.name as donor_name, s.name as shelter_name, s.address as shelter_address
        FROM donations d 
        JOIN users u ON d.donor_id = u.id
        JOIN claims c ON d.id = c.donation_id
        JOIN shelters s ON c.shelter_id = s.id
        WHERE d.status = 'CLAIMED'
    """)
    all_tasks = cursor.fetchall()
    
    for t in all_tasks:
        if current_user.lat is not None and current_user.lng is not None and t['lat'] is not None and t['lng'] is not None:
            dist = haversine(current_user.lat, current_user.lng, t['lat'], t['lng'])
            t['distance'] = round(dist, 2)
        else:
            t['distance'] = None
            
    # Sort by proximity (None values go to the end)
    nearby_tasks = sorted(all_tasks, key=lambda x: (x['distance'] is None, x['distance']))
            
    # Get current and past deliveries for this volunteer
    cursor.execute("""
        SELECT del.*, d.food_description, s.name as shelter_name, s.address as shelter_address
        FROM deliveries del
        JOIN donations d ON del.donation_id = d.id
        JOIN claims c ON d.id = c.donation_id
        JOIN shelters s ON c.shelter_id = s.id
        WHERE del.volunteer_id = %s
    """, (current_user.id,))
    deliveries = cursor.fetchall()
            
    return render_template('volunteer/dashboard.html', tasks=nearby_tasks, deliveries=deliveries)

@volunteer_bp.route('/accept_delivery/<int:donation_id>', methods=['POST'])
@login_required
def accept_delivery(donation_id):
    if current_user.role != 'volunteer':
        return "Unauthorized", 403
        
    cursor = mysql.connection.cursor()
    cursor.execute("INSERT INTO deliveries (donation_id, volunteer_id) VALUES (%s, %s)", (donation_id, current_user.id))
    mysql.connection.commit()
    
    flash('Delivery task accepted!', 'success')
    return redirect(url_for('volunteer.dashboard'))

@volunteer_bp.route('/update_status/<int:delivery_id>', methods=['POST'])
@login_required
def update_status(delivery_id):
    if current_user.role != 'volunteer':
        return "Unauthorized", 403
        
    new_status = request.form.get('status')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    
    cursor.execute("UPDATE deliveries SET status = %s WHERE id = %s", (new_status, delivery_id))
    
    # Sync donation status
    cursor.execute("SELECT donation_id FROM deliveries WHERE id = %s", (delivery_id,))
    deliv = cursor.fetchone()
    if new_status == 'PICKED UP':
        cursor.execute("UPDATE donations SET status = 'PICKED UP' WHERE id = %s", (deliv['donation_id'],))
    elif new_status == 'DELIVERED':
        cursor.execute("UPDATE donations SET status = 'DELIVERED' WHERE id = %s", (deliv['donation_id'],))
        
    mysql.connection.commit()
    flash(f'Status updated to {new_status}', 'success')
    return redirect(url_for('volunteer.dashboard'))
