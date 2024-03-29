import os
from dotenv import load_dotenv
from flask import Flask, g, redirect, render_template, session, flash, request
from sqlalchemy.exc import IntegrityError, NoResultFound
from models import db, connect_db, User, Project, Needle, Hook, Yarn, TimeLog, Request, Participant, Message, Conversation
from forms import CSRFProtectForm, SignupForm, LoginForm, NewProjectForm, EditProjectForm, ProjectTimeLogForm, EditTimeLogForm, EditUserForm, MessageForm, NewConversationForm, ProgressForm
from functools import wraps
from utils import removeFieldListEntry


load_dotenv()


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
app.config['SECRET_KEY'] = os.environ['SECRET_KEY']


connect_db(app)


DEFAULT_NEEDLE_DATA = {'size': 'US 00000000 - 0.5 mm'}
DEFAULT_HOOK_DATA = {'size': '0.6 mm'}
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


def check_authorization(f):
    """Function decorator. Checks if user allowed to access a resource."""

    @wraps(f)
    def authorization_decorator(user_id):

        other_user = User.query.get_or_404(user_id)

        if other_user.private:
            if g.user != other_user and not g.user.is_following(other_user):
                return render_template('users/private.html', user=other_user)

        return f(user_id)

    return authorization_decorator



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
    - logged in: projects of followed users
    """

    if g.user:
        following_ids = [f.id for f in g.user.following] + [g.user.id]

        projects = (Project.query
                    .filter(Project.user_id.in_(following_ids))
                    .order_by(Project.created_at.desc())
                    .limit(100)
                    .all())

        return render_template('home.html', projects=projects)

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

            return redirect('/profile')

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
            return redirect('/profile')

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

    return render_template('users/user_list.html', users=users)


@app.get('/profile')
@login_required
def user_profile():
    """User profile."""

    user = User.query.get_or_404(g.user.id)

    projects = Project.query.filter(
        Project.user_id == user.id
        ).order_by(
            Project.pinned.desc(), Project.created_at.desc()
        )

    return render_template('users/projects.html', user=user, projects=projects)


@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    """Show user settings."""

    form = EditUserForm(obj=g.user)

    if form.validate_on_submit():
        user = User.query.get(g.user.id)

        user.username = form.username.data
        user.email = form.email.data
        user.image_url = form.image_url.data or None

        db.session.commit()

        flash('Changes saved.', 'success')

    return render_template('users/settings.html', form=form)


@app.get('/notifications')
@login_required
def notifications():
    """Show user notifications."""

    follow_requests = db.session.query(
        Request.user_requesting_id,
        User.username
    ).outerjoin(User, User.id == Request.user_requesting_id).filter(
        Request.user_being_requested_id == g.user.id
    ).all()

    return render_template('users/notifications.html', follow_requests = follow_requests)


@app.get('/users/<int:user_id>')
@login_required
@check_authorization
def user_page(user_id):
    """Show user profile."""

    user = User.query.get_or_404(user_id)

    projects = Project.query.filter(
        Project.user_id == user_id
        ).order_by(
            Project.pinned.desc(), Project.created_at.desc()
        )

    return render_template('users/projects.html', user=user, projects=projects)


@app.post('/settings/private')
@login_required
def private_account():
    """Handle privating account."""

    form = g.csrf_form

    if form.validate_on_submit():
        user = User.query.get(g.user.id)

        user.private = True
        db.session.commit()

        flash('Account now private.', 'success')

    return render_template('users/settings.html', form=form)


@app.post('/settings/unprivate')
@login_required
def unprivate_account():
    """Handle unprivating account."""

    form = g.csrf_form

    if form.validate_on_submit():
        user = User.query.get(g.user.id)

        user.private = False
        db.session.commit()

        flash('Account now public.', 'success')

    return render_template('users/settings.html', form=form)


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


@app.post('/users/delete')
@login_required
def delete_user():
    """Handle deleting user."""

    form = g.csrf_form

    if not form.validate_on_submit():
        flash('Unauthorized', 'danger')
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
        flash('Unauthorized', 'danger')
        return redirect("/")

    if user.private:
        user.requests_received.append(g.user)
        db.session.commit()
        flash(f'Request sent to {user.username}', 'success')

    else:
        user.followers.append(g.user)
        db.session.commit()
        flash(f'Now following {user.username}', 'success')

    redirect_url = request.form.get("came_from", "/")

    return redirect(redirect_url)


@app.post('/users/<int:user_id>/unfollow')
@login_required
def unfollow_user(user_id):
    """Handle unfollowing user."""

    form = g.csrf_form

    user = User.query.get_or_404(user_id)

    if not form.validate_on_submit():
        flash('Unauthorized', 'danger')
        return redirect("/")

    user.followers.remove(g.user)
    db.session.commit()

    redirect_url = request.form.get("came_from", "/")

    flash(f'Unfollowed {user.username}', 'success')
    return redirect(redirect_url)


@app.post('/users/<int:user_id>/cancel_request')
@login_required
def cancel_follow_request(user_id):
    """Handle canceling follow request user."""

    form = g.csrf_form

    user = User.query.get_or_404(user_id)

    if not form.validate_on_submit():
        flash('Unauthorized', 'danger')
        return redirect("/")

    user.requests_received.remove(g.user)
    db.session.commit()

    redirect_url = request.form.get("came_from", "/")

    flash(f'Canceled follow request.', 'success')
    return redirect(redirect_url)


##############################################################################
# Request routes:

@app.post('/requests/<int:requesting_user_id>/confirm')
@login_required
def confirm_request(requesting_user_id):
    """Confirm follow request."""

    form = g.csrf_form

    if not form.validate_on_submit():
        flash('Unauthorized', 'danger')
        return redirect("/")

    follow_request = Request.query.get_or_404((g.user.id, requesting_user_id))
    db.session.delete(follow_request)
    db.session.commit()

    other_user = User.query.get_or_404(requesting_user_id)
    g.user.followers.append(other_user)
    db.session.commit()

    flash(f'{other_user.username} is following you now.', 'success')
    return redirect('/notifications')


@app.post('/requests/<int:requesting_user_id>/delete')
@login_required
def delete_request(requesting_user_id):
    """Delete follow request."""

    form = g.csrf_form

    if not form.validate_on_submit():
        flash('Unauthorized', 'danger')
        return redirect("/")

    follow_request = Request.query.get_or_404((g.user.id, requesting_user_id))
    db.session.delete(follow_request)
    db.session.commit()

    flash('Deleted follow request.', 'success')
    return redirect('/notifications')


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
            progress = form.progress.data
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
        return redirect(f'/projects/{project.id}')

    return render_template('projects/create.html', form=form)

# TODO: add testing to check authorization
@app.get('/projects/<int:project_id>')
@login_required
def project_details(project_id):
    """Show project details."""

    project = Project.query.get_or_404(project_id)
    form = ProgressForm(obj=project)

    other_user = User.query.get_or_404(project.user_id)

    if other_user.private:
        if g.user != other_user and not g.user.is_following(other_user):
            return render_template('users/private.html', user=other_user)

    return render_template('projects/details.html', project=project, form=form)


@app.route('/projects/<int:project_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_project(project_id):
    """Handle editing project.
    If GET, show form.
    If form submission valid, update DB and redirect to user's profile"""

    project = Project.query.get_or_404(project_id)

    if g.user.id != project.user_id:
        flash('Unauthorized', 'danger')
        return redirect("/")

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
    elif form.validate_on_submit():
        project.title = form.title.data or None
        project.pattern = form.pattern.data
        project.designer = form.designer.data
        project.progress = form.progress.data

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


@app.post('/projects/<int:project_id>/edit_progress')
@login_required
def edit_project_progress(project_id):
    """Handle editing project.
        If GET, show form.
        If form submission valid, update DB and redirect to user's profile"""

    project = Project.query.get_or_404(project_id)

    if g.user.id != project.user_id:
        flash('Unauthorized', 'danger')
        return redirect("/")

    form = ProgressForm()

    if form.validate_on_submit():
        project.progress = form.progress.data

        db.session.commit()

        flash('Project progress edited.', 'success')
        return redirect(f'/projects/{project_id}')

    return render_template('projects/edit.html', project=project, form=form)

@app.post('/projects/<int:project_id>/delete')
@login_required
def delete_project(project_id):
    """Handle deleting project."""

    project = Project.query.get_or_404(project_id)

    form = g.csrf_form

    if g.user.id != project.user_id or not form.validate_on_submit():
        flash('Unauthorized', 'danger')
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

    if g.user.id != project.user_id or not form.validate_on_submit():
        flash('Unauthorized', 'danger')
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

    if g.user.id != project.user_id or not form.validate_on_submit():
        flash('Unauthorized', 'danger')
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
            flash('Unauthorized', 'danger')
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
        flash('Unauthorized', 'danger')
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
        flash('Unauthorized', 'danger')
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


##############################################################################
# Conversation routes:

@app.get('/conversations')
@login_required
def conversations_page():
    """Display conversations page."""

    conversations = g.user.get_conversations()

    return render_template('conversations/no_conversation_selected.html', conversations = conversations)

@app.get('/conversations/<int:conversation_id>')
@login_required
def show_converation(conversation_id):
    """Display conversation."""

    form = MessageForm()

    try:
        Participant.query.filter(
        Participant.user_id == g.user.id,
        Participant.conversation_id == conversation_id
        ).one()
    except NoResultFound:
        flash('Unauthorized', 'danger')
        return redirect('/')

    conversations = g.user.get_conversations()

    participants = db.session.query(User).outerjoin(
        Participant
    ).filter(
        Participant.conversation_id == conversation_id,
        g.user.id != Participant.user_id
    ).all()

    messages = db.session.query(
        Message.user_id,
        Message.text
    ).filter(
        Message.conversation_id == conversation_id
    ).all()

    return render_template(
        'conversations/conversation.html',
        participants=participants,
        conversation_id=conversation_id,
        conversations=conversations,
        messages=messages,
        form=form
        )

@app.post('/conversations/<int:conversation_id>/new_message')
@login_required
def send_message(conversation_id):
    """Send new message."""

    form = MessageForm()

    try:
        Participant.query.filter(
        Participant.user_id == g.user.id,
        Participant.conversation_id == conversation_id
        ).one()

    except NoResultFound:
        flash('Unauthorized', 'danger')
        return redirect('/')

    if form.validate_on_submit():
        message = Message(
            user_id=g.user.id,
            conversation_id=conversation_id,
            text=form.message.data,
        )

        db.session.add(message)
        db.session.commit()

        return redirect(f'/conversations/{conversation_id}')

    return render_template('conversations/conversation.html', form=form)

@app.route('/conversations/new', methods=['POST', 'GET'])
def new_conversation():
    """Handle creating new conversation"""

    conversations = g.user.get_conversations()

    form = NewConversationForm()

    form.user.choices = [(user.id, user.username) for user in User.query.filter(User.id != g.user.id).all()]

    if form.validate_on_submit():
        conversation = Conversation()
        db.session.add(conversation)
        db.session.commit()

        user_id = form.user.data
        user = User.query.get_or_404(user_id)
        user.conversations.append(conversation)
        g.user.conversations.append(conversation)
        db.session.commit()

        message = Message(
            user_id = g.user.id,
            conversation_id = conversation.id,
            text = form.message.data
        )
        db.session.add(message)
        db.session.commit()

        return redirect(f'/conversations/{conversation.id}')

    return render_template('conversations/new_conversation.html',  form= form, conversations=conversations)
