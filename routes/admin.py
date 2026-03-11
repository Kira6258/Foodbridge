from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models.db import mysql
import MySQLdb.cursors

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/login')
def login():
    if current_user.is_authenticated and current_user.role == 'admin':
        return redirect(url_for('admin.dashboard'))
    return render_template('admin/login.html')

@admin_bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.role != 'admin':
        return "Unauthorized", 403
    
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    
    # Stats
    cursor.execute("SELECT COUNT(*) as count FROM donations")
    total_donations = cursor.fetchone()['count']
    cursor.execute("SELECT COUNT(*) as count FROM shelters")
    total_shelters = cursor.fetchone()['count']
    cursor.execute("SELECT COUNT(*) as count FROM users WHERE role = 'volunteer'")
    total_volunteers = cursor.fetchone()['count']
    
    # Pending Shelters
    cursor.execute("SELECT * FROM shelters WHERE approved = 0")
    pending_shelters = cursor.fetchall()
    
    # All Users
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    
    return render_template('admin/dashboard.html', 
                          total_donations=total_donations, 
                          total_shelters=total_shelters, 
                          total_volunteers=total_volunteers,
                          pending_shelters=pending_shelters,
                          users=users)

@admin_bp.route('/approve_shelter/<int:shelter_id>', methods=['POST'])
@login_required
def approve_shelter(shelter_id):
    if current_user.role != 'admin':
        return "Unauthorized", 403
        
    cursor = mysql.connection.cursor()
    cursor.execute("UPDATE shelters SET approved = 1 WHERE id = %s", (shelter_id,))
    mysql.connection.commit()
    
    flash('Shelter approved successfully!', 'success')
    return redirect(url_for('admin.dashboard'))
