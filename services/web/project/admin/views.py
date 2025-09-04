from flask import render_template, redirect, request, session, url_for
from . import admin_blueprint  # Move this import here
from project.models import db, User


@admin_blueprint.route('/admin')
def admin_panel():
    if session:
        username = session.get('username')
        print(username, flush=True)
        frog = User.query.filter_by(username=username).first()
        if frog.is_admin:
            users = User.query.all()
            return render_template('admin.html', users=users)
    return "Access Denied"


@admin_blueprint.route('/admin/update', methods=['POST'])
def update_admin_status():
    for key, value in request.form.items():
        if key.startswith('user_id_'):
            user_id = value  # Extract user ID from the key
            print(user_id)
            is_admin = request.form.get(f"is_admin_{value}") == 'on'
            user = User.query.get(user_id)
            if user:
                user.is_admin = is_admin
                db.session.commit()
    return redirect(url_for("admin.admin_panel"))
