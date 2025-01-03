from flask import Blueprint, render_template, redirect, url_for, request, session, flash
from app.models import User, db
from app.forms import RegistrationForm, LoginForm, UserForm
from functools import wraps

main = Blueprint('main', __name__, template_folder='../templates')

# Middleware untuk memastikan login
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Silakan login terlebih dahulu.', 'warning')
            return redirect(url_for('main.login'))
        return f(*args, **kwargs)
    return decorated_function

# Rute default
@main.route('/')
def index():
    if 'user_id' in session:
        if session.get('role') == 'Admin':
            return redirect(url_for('main.dashboard'))
        else:
            return redirect(url_for('main.user_dashboard'))
    return redirect(url_for('main.login'))

# Rute registrasi
@main.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        try:
            existing_user = User.query.filter(
                (User.username == form.username.data) | (User.email == form.email.data)
            ).first()
            if existing_user:
                flash('Username atau email sudah terdaftar!', 'danger')
                return redirect(url_for('main.register'))
            
            new_user = User(
                username=form.username.data,
                email=form.email.data,
                role=form.role.data
            )
            new_user.set_password(form.password.data)
            db.session.add(new_user)
            db.session.commit()
            flash('Registrasi berhasil! Silakan login.', 'success')
            return redirect(url_for('main.login'))
        except Exception as e:
            db.session.rollback()
            flash(f'Terjadi kesalahan saat registrasi: {e}', 'danger')
    return render_template('register.html', form=form)

# Rute login
@main.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            session['user_id'] = user.id
            session['username'] = user.username
            session['role'] = user.role
            flash(f'Login berhasil! Selamat datang, {user.username}.', 'success')
            
            # Arahkan berdasarkan role
            if user.role == 'Admin':
                return redirect(url_for('main.dashboard'))
            elif user.role == 'User':
                return redirect(url_for('main.user_dashboard'))
        flash('Username atau password salah.', 'danger')
    return render_template('login.html', form=form)

# Dashboard admin
@main.route('/dashboard')
@login_required
def dashboard():
    if session.get('role') != 'Admin':
        flash('Anda tidak memiliki akses ke halaman ini.', 'danger')
        return redirect(url_for('main.index'))
    
    page = request.args.get('page', 1, type=int)
    users = User.query.paginate(page=page, per_page=5)
    return render_template('dashboard.html', users=users)

# Dashboard user
@main.route('/user_dashboard')
@login_required
def user_dashboard():
    if session.get('role') != 'User':
        flash('Anda tidak memiliki akses ke halaman ini.', 'danger')
        return redirect(url_for('main.index'))
    return render_template('index.html')

# Rute logout
@main.route('/logout')
def logout():
    session.clear()
    flash('Anda telah logout.', 'info')
    return redirect(url_for('main.login'))

# Tambah user (Admin saja)
@main.route('/user/add', methods=['GET', 'POST'])
@login_required
def add_user():
    if session.get('role') != 'Admin':
        flash('Anda tidak memiliki akses ke halaman ini.', 'danger')
        return redirect(url_for('main.index'))
    
    form = UserForm()
    if form.validate_on_submit():
        try:
            existing_user = User.query.filter(
                (User.username == form.username.data) | (User.email == form.email.data)
            ).first()
            if existing_user:
                flash('Username atau email sudah terdaftar!', 'danger')
                return redirect(url_for('main.add_user'))
            
            new_user = User(
                username=form.username.data,
                email=form.email.data,
                role=form.role.data
            )
            new_user.set_password('defaultpassword')
            db.session.add(new_user)
            db.session.commit()
            flash('User berhasil ditambahkan!', 'success')
            return redirect(url_for('main.dashboard'))
        except Exception as e:
            db.session.rollback()
            flash(f'Terjadi kesalahan saat menambahkan user: {e}', 'danger')
    return render_template('user_form.html', form=form)

# Edit user (Admin saja)
@main.route('/user/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_user(id):
    if session.get('role') != 'Admin':
        flash('Anda tidak memiliki akses ke halaman ini.', 'danger')
        return redirect(url_for('main.index'))
    
    user = User.query.get_or_404(id)
    form = UserForm(obj=user)
    if form.validate_on_submit():
        try:
            user.username = form.username.data
            user.email = form.email.data
            user.role = form.role.data
            db.session.commit()
            flash('Data user berhasil diperbarui!', 'success')
            return redirect(url_for('main.dashboard'))
        except Exception as e:
            db.session.rollback()
            flash(f'Terjadi kesalahan saat memperbarui user: {e}', 'danger')
    return render_template('user_form.html', form=form)

# Hapus user (Admin saja)
@main.route('/user/delete/<int:id>')
@login_required
def delete_user(id):
    if session.get('role') != 'Admin':
        flash('Anda tidak memiliki akses ke halaman ini.', 'danger')
        return redirect(url_for('main.index'))
    
    user = User.query.get_or_404(id)
    try:
        db.session.delete(user)
        db.session.commit()
        flash('User berhasil dihapus!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Terjadi kesalahan saat menghapus user: {e}', 'danger')
    return redirect(url_for('main.dashboard'))


@main.app_errorhandler(404)
def page_not_found(e):
    return render_template('errors/404.html'), 404

@main.app_errorhandler(500)
def internal_server_error(e):
    return render_template('errors/500.html'), 500
