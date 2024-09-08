from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user, login_required
from app import db
from app.models import User, Event, RSVP  # Import models directly from app.models
from app.forms import LoginForm, RegistrationForm, EventForm, RSVPForm  # Import forms from app.forms

from . import app  # Assuming your Flask app instance is named 'app'

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        return redirect(url_for('index'))
    return render_template('login.html', title='Sign In', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data, role=form.role.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route('/dashboard')
@login_required
def dashboard():
    events = Event.query.all()
    return render_template('dashboard.html', title='Dashboard', events=events)

@app.route('/create_event', methods=['GET', 'POST'])
@login_required
def create_event():
    form = EventForm()
    if form.validate_on_submit():
        event = Event(title=form.title.data, description=form.description.data, organizer_id=current_user.id)
        db.session.add(event)
        db.session.commit()
        flash('Your event has been created!')
        return redirect(url_for('dashboard'))
    return render_template('create_event.html', title='Create Event', form=form)

@app.route('/rsvp/<int:event_id>', methods=['GET', 'POST'])
@login_required
def rsvp(event_id):
    form = RSVPForm()
    if form.validate_on_submit():
        rsvp = RSVP(user_id=current_user.id, event_id=event_id, status=form.status.data)
        db.session.add(rsvp)
        db.session.commit()
        flash('Your RSVP has been recorded!')
        return redirect(url_for('dashboard'))
    return render_template('rsvp.html', title='RSVP', form=form)
