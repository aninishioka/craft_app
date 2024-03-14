import os
from dotenv import load_dotenv
from flask import Flask, g, redirect, render_template, session, flash, request
from sqlalchemy.exc import IntegrityError
from models import db, connect_db, User, Project, Needle, Hook, Yarn, TimeLog
from forms import CSRFProtectForm, SignupForm, LoginForm, NewProjectForm, EditProjectForm, ProjectTimeLogForm, EditTimeLogForm
from functools import wraps
from utils import removeFieldListEntry


DEFAULT_NEEDLE_DATA = {'size': 'US 00000000 - 0.5 mm'}
DEFAULT_HOOK_DATA = {'size': '0.6 mm'}


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

@app.get('/users')
@login_required
def user_list():
    """Page listing users.
    Can take query param, 'q', to search by username."""

    search_term = request.args.get('q')

    if search_term:
        users = User.query.filter(User.username.ilike(f'%{search_term}%')).all()
    else:
        users = User.query.all()

    # TODO: add search

    return render_template('users/user_list.html', users=users)


@app.get('/users/<int:user_id>')
@login_required
def user_page(user_id):
    """Show user profile."""

    user = User.query.get_or_404(user_id)

    projects = Project.query.filter(
        Project.user_id == user_id
        ).order_by(
            Project.pinned.desc(), Project.created_at.desc()
        )

    return render_template('users/projects.html', user=user, projects=projects)


@app.get('/users/<int:user_id>/following')
@login_required
def user_following(user_id):
    """Show user profile."""

# TODO: n+1
    user = User.query.get_or_404(user_id)

    return render_template('users/following.html', user=user)


@app.get('/users/<int:user_id>/followers')
@login_required
def user_followers(user_id):
    """Show user profile."""

# TODO: n+1
    user = User.query.get_or_404(user_id)

    return render_template('users/followers.html', user=user)


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


@app.post('/users/<int:user_id>/follow')
@login_required
def follow_user(user_id):
    """Handle following user."""

    form = g.csrf_form

    user = User.query.get_or_404(user_id)

    if not form.validate_on_submit():
        flash('Unathorized', 'danger')
        return redirect("/")

    user.followers.append(g.user)
    db.session.commit()

    redirect_url = request.form.get("came_from", "/")

    flash(f'Now following {user.username}', 'success')
    return redirect(redirect_url)


@app.post('/users/<int:user_id>/unfollow')
@login_required
def unfollow_user(user_id):
    """Handle unfollowing user."""

    form = g.csrf_form

    user = User.query.get_or_404(user_id)

    if not form.validate_on_submit():
        flash('Unathorized', 'danger')
        return redirect("/")

    user.followers.remove(g.user)
    db.session.commit()

    redirect_url = request.form.get("came_from", "/")

    flash(f'Unfollowed {user.username}', 'success')
    return redirect(redirect_url)


##############################################################################
# Project routes:

@app.route('/projects/new', methods=['POST', 'GET'])
@login_required
def add_project():
    """Handle new project creation.
    If GET, show form.
    If form submission valid, update DB and redirect to user's profile."""

    form = NewProjectForm()

    if form.add_yarn.data:
        form.yarns.append_entry({})
    elif form.add_needles.data:
        form.needles.append_entry({})
    elif form.add_hooks.data:
        form.hooks.append_entry({})
    elif removeFieldListEntry(form.yarns):
        pass
    elif removeFieldListEntry(form.needles):
        pass
    elif removeFieldListEntry(form.hooks):
        pass
    elif form.validate_on_submit():
        project = Project(
            user_id = g.user.id,
            title = form.title.data or form.pattern.data or None,
            pattern = form.pattern.data,
            designer = form.designer.data,
            content = form.content.data,
        )

        for needle in form.needles.entries:
            needle = Needle.query.get(needle.data['size'])
            if needle:
                project.needles.append(needle)

        for hook in form.hooks.entries:
            hook = Hook.query.get(hook.data['size'])
            if hook:
                project.hooks.append(hook)

        for yarn in form.yarns.entries:
            project.yarns.append(
                Yarn(
                    yarn_name = yarn.data['yarn_name'],
                    color = yarn.data['color'],
                    dye_lot = yarn.data['dye_lot'],
                    weight = yarn.data['weight'],
                    skein_weight = yarn.data['skein_weight'],
                    skein_weight_unit = yarn.data['skein_weight_unit'],
                    skein_length = yarn.data['skein_length'],
                    skein_length_unit = yarn.data['skein_length_unit'],
                    num_skeins = yarn.data['num_skeins']
                )
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

    if form.add_yarn.data:
        form.yarns.append_entry({})
    elif form.add_needles.data:
        form.needles.append_entry(DEFAULT_NEEDLE_DATA)
    elif form.add_hooks.data:
        form.hooks.append_entry(DEFAULT_HOOK_DATA)
    elif removeFieldListEntry(form.yarns):
        pass
    elif removeFieldListEntry(form.needles):
        pass
    elif removeFieldListEntry(form.hooks):
        pass
    elif g.user.id == project.user.id and form.validate_on_submit():
        project.title = form.title.data or None
        project.pattern = form.pattern.data
        project.designer = form.designer.data
        project.content = form.content.data

        project.needles = []
        for needle in form.needles.entries:
            needle = Needle.query.get(needle.data['size'])
            if needle:
                project.needles.append(needle)

        project.hooks = []
        for hook in form.hooks.entries:
            hook = Hook.query.get(hook.data['size'])
            if hook:
                project.hooks.append(hook)

        project.yarns = []
        for yarn in form.yarns.entries:
            project.yarns.append(
                Yarn(
                    yarn_name = yarn.data['yarn_name'],
                    color = yarn.data['color'],
                    dye_lot = yarn.data['dye_lot'],
                    weight = yarn.data['weight'],
                    skein_weight = yarn.data['skein_weight'],
                    skein_weight_unit = yarn.data['skein_weight_unit'],
                    skein_length = yarn.data['skein_length'],
                    skein_length_unit = yarn.data['skein_length_unit'],
                    num_skeins = yarn.data['num_skeins']
                )
            )

        db.session.commit()

        flash('Project edited.', 'success')
        return redirect(f'/projects/{project_id}')

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


@app.post('/projects/<int:project_id>/pin')
@login_required
def pin_project(project_id):
    """Handle pinning project."""

    project = Project.query.get_or_404(project_id)

    form = g.csrf_form

    if g.user.id != project.user.id and not form.validate_on_submit():
        flash('Unathorized', 'danger')
        return redirect("/")

    project.pinned=True
    db.session.commit()

    redirect_url = request.form.get("came_from", "/")

    flash('Project pinned', 'success')
    return redirect(redirect_url)


@app.post('/projects/<int:project_id>/unpin')
@login_required
def unpin_project(project_id):
    """Handle unpinning project."""

    project = Project.query.get_or_404(project_id)

    form = g.csrf_form

    if g.user.id != project.user.id and not form.validate_on_submit():
        flash('Unathorized', 'danger')
        return redirect("/")

    project.pinned=False
    db.session.commit()

    redirect_url = request.form.get("came_from", "/")

    flash('Project unpinned', 'success')
    return redirect(redirect_url)


@app.route('/projects/log_time', methods=['GET', 'POST'])
@login_required
def time_log_form():
    """Display project time logging form."""

    form = ProjectTimeLogForm()

    projects = Project.query.filter(Project.user_id == g.user.id).all()
    form.project.choices = [(p.id, p.title) for p in projects]

    if form.validate_on_submit():
        project_id = form.project.data
        project = Project.query.get(project_id)

        if project.user_id != g.user.id:
            flash('Unathorized', 'danger')
            return redirect("/")

        log = TimeLog(
            project_id=project.id,
            date=form.date.data,
            hours=form.hours.data,
            minutes=form.minutes.data,
            notes=form.notes.data
        )

        project.time_logs.append(log)
        db.session.commit()

        flash('Project log created.', 'success')
        return redirect(f'/projects/{log.project_id}')

    return render_template('projects/time-log.html',form=form)


@app.get('/projects/<int:project_id>/log_time')
@login_required
def selected_project_time_log_form(project_id):
    """Display project time logging form."""

    form = ProjectTimeLogForm()

    project = Project.query.get(project_id)

    if project.user_id != g.user.id:
        flash('Unathorized', 'danger')
        return redirect("/")

    form.project.choices = [(project.id, project.title)]
    form.project.data = project.id

    return render_template('projects/time-log.html',form=form)


@app.route('/logs/<int:log_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_time_log(log_id):
    """Display project time logging form."""

    log = TimeLog.query.get_or_404(log_id)
    form = EditTimeLogForm(obj=log)

    if log.project.user_id != g.user.id:
        flash('Unathorized', 'danger')
        return redirect("/")

    if form.validate_on_submit():
        log.date = form.date.data
        log.hours = form.hours.data
        log.minutes = form.minutes.data
        log.notes = form.notes.data

        db.session.commit()

        flash('Project log edited.', 'success')
        return redirect(f'/projects/{log.project_id}')

    return render_template('projects/edit-log.html',form=form, log=log)