import os
from dotenv import load_dotenv
from flask import Flask, g, redirect, render_template, session, flash
from sqlalchemy.exc import IntegrityError
from models import db, connect_db, User, Project
from forms import CSRFProtectForm, SignupForm, LoginForm, NewProjectForm, EditProjectForm
from functools import wraps


load_dotenv()


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
app.config['SECRET_KEY'] = os.environ['SECRET_KEY']


connect_db(app)


CURR_USER_KEY = 'user'


@app.before_request
def add_user_to_g():
    """If logged in, add current user to request."""

    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])
    else:
        g.user = None


@app.before_request
def add_csrf_form_to_g():
    """Add CSRF-only form so every route can access"""

    g.csrf_form = CSRFProtectForm()


def login_required(f):
    """Function decorator. Checks user is logged in."""

    @wraps(f)
    def login_decorator(*args, **kwargs):

        if not g.user:
            flash('Unauthorized.', 'danger')
            return redirect('/')

        return f(*args, **kwargs)

    return login_decorator


def login_user(user):
    """Save user to session."""

    session[CURR_USER_KEY] = user.id


def logout_user():
    """Remove user from session."""

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]


@app.get('/')
def homepage():
    """Show homepage.

    - anon users: login page
    - logged in: user profile
    """

    if g.user:
        return redirect(f'/users/{g.user.id}')

    return render_template('home-anon.html')


##############################################################################
# User signup/login/logout


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    """Handle user sign up.

    Create new user and add to DB.

    If form invalid, re-render form.
    """

    form = SignupForm()

    if form.validate_on_submit():
        try:
            user = User.signup(
                username=form.username.data,
                email=form.email.data,
                image_url=form.image_url.data or None,
                password=form.password.data
            )
            db.session.commit()

            login_user(user)

            return redirect(f'/users/{user.id}')

        except IntegrityError:
            flash('Username or email already in use.', 'danger')

    return render_template('users/signup.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login.

    If form invalid, re-render form.
    """

    form = LoginForm()

    if form.validate_on_submit():
        user = User.login(
            username=form.username.data,
            password=form.password.data
        )

        if user:
            login_user(user)
            flash(f'Hello, {user.username}', 'success')
            return redirect(f'/users/{user.id}')

        flash('Invalid credentials.', 'danger')

    return render_template('users/login.html', form=form)

@app.post('/logout')
def logout():
    """Handle user logout.

    If form invalid, re-render form.
    """

    if not g.csrf_form.validate_on_submit() or not g.user:
        flash('Unauthorized', 'danger')
        return redirect('/')

    logout_user()

    flash('Logged out', 'success')
    return redirect('/login')


##############################################################################
# General user routes:

@app.get('/users/<int:user_id>')
@login_required
def user_page(user_id):
    """Show user profile."""

    user = User.query.get_or_404(user_id)

    return render_template('users/profile.html', user=user)


@app.route('/users/profile', methods=['GET', 'POST'])
@login_required
def edit_user():
    # TODO:
    return

@app.post('/users/delete')
@login_required
def delete_user():
    """Handle deleting user."""

    form = g.csrf_form

    if not form.validate_on_submit():
        flash('Unathorized', 'danger')
        return redirect("/")

    db.session.delete(g.user)
    db.session.commit()

    flash('User deleted', 'success')
    return redirect(f'/signup')


##############################################################################
# Project routes:

@app.route('/projects/new', methods=['POST', 'GET'])
@login_required
def add_project():
    """Handle new project creation.
    If GET, show form.
    If form submission valid, update DB and redirect to user's profile."""

    form = NewProjectForm()

    if form.validate_on_submit():
        project = Project(
            user_id = g.user.id,
            title = form.title.data or form.pattern.data or None,
            pattern = form.pattern.data,
            designer = form.designer.data,
            needles = form.needles.data,
            content = form.content.data
        )

        db.session.add(project)
        db.session.commit()

        flash('New project added', 'success')
        return redirect(f'/users/{g.user.id}')

    return render_template('projects/create.html', form=form)


@app.get('/projects/<int:project_id>')
@login_required
def project_details(project_id):
    """Show project details."""

    project = Project.query.get_or_404(project_id)

    return render_template('projects/details.html', project=project)


@app.route('/projects/<int:project_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_project(project_id):
    """Handle editing project.
    If GET, show form.
    If form submission valid, update DB and redirect to user's profile"""

    project = Project.query.get_or_404(project_id)

    form = EditProjectForm(obj=project)

    if g.user.id == project.user.id and form.validate_on_submit():
        project.title = form.title.data or None
        project.pattern = form.pattern.data
        project.designer = form.designer.data
        project.needles = form.needles.data
        project.content = form.content.data

        db.session.commit()

        flash('Project edited.', 'success')
        return redirect(f'/users/{g.user.id}')

    return render_template('projects/edit.html', form=form, project_id=project.id)


@app.post('/projects/<int:project_id>/delete')
@login_required
def delete_project(project_id):
    """Handle deleting project."""

    project = Project.query.get_or_404(project_id)

    form = g.csrf_form

    if g.user.id != project.user.id and not form.validate_on_submit():
        flash('Unathorized', 'danger')
        return redirect("/")


    db.session.delete(project)
    db.session.commit()

    flash('Project deleted', 'success')
    return redirect(f'/users/{g.user.id}')