from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user
from app import db
from app.models import User
from app.forms import LoginForm, RegistrationForm, ResetPasswordRequestForm, ResetPasswordForm
# Import for password reset token generation and email sending (if implementing full feature)
# from app.email import send_password_reset_email


bp = Blueprint('auth', __name__)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index')) # Assuming a main blueprint with an index route
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('auth.login'))
        login_user(user, remember=form.remember_me.data)
        
        next_page = request.args.get('next')
        # Prevent open redirect vulnerability
        from urllib.parse import urlparse
        if next_page and urlparse(next_page).netloc == '':
            # Further check: ensure it's not trying to use //example.com which urlparse might miss
            if next_page.startswith('//'):
                next_page = url_for('main.index')
        elif not next_page: # if next_page is None or empty
             next_page = url_for('main.index')
        else: # if next_page has a netloc (external domain)
            next_page = url_for('main.index')
            
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)

@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index')) # Assuming a main blueprint with an index route

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('auth.login'))
    return render_template('register.html', title='Register', form=form)

@bp.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            # In a real application, you would generate a token and send an email here
            # For now, we'll just flash a message.
            # send_password_reset_email(user)
            flash('Check your email for the instructions to reset your password')
        else:
            # Flash message even if user not found to avoid enumeration
            flash('Check your email for the instructions to reset your password')
        return redirect(url_for('auth.login'))
    return render_template('reset_password_request.html',
                           title='Reset Password', form=form)

@bp.route('/reset_password/<token>', methods=['GET', 'POST']) # This route would be used if email token system was in place
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    # user = User.verify_reset_password_token(token) # This would verify the token
    # if not user:
    #     return redirect(url_for('main.index'))
    # For now, this is a placeholder as token verification is not implemented.
    # In a real app, you'd get the user from the token.
    # For this example, we'll assume the token is the user ID for simplicity (NOT SECURE FOR PRODUCTION)
    user = User.query.get(token) # Placeholder - NOT SECURE
    if not user:
         flash('Invalid or expired token.')
         return redirect(url_for('auth.reset_password_request'))

    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been reset.')
        return redirect(url_for('auth.login'))
    return render_template('reset_password.html', title='Reset Password', form=form)
