from flask import Flask, render_template, request, redirect, url_for, session, flash, abort
from werkzeug.security import generate_password_hash, check_password_hash
import re
import json
import os
import smtplib
from email.mime.text import MIMEText
from datetime import datetime, timedelta
from functools import wraps
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'luckyanjay'
app.permanent_session_lifetime = timedelta(minutes=5)

USERS_FILE = 'users.json'
SERVICE_FILE = 'services.json'
DIARY_FILE = 'diary.json'

# Validasi email

def valid_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)

# Fungsi kirim email login dan service

def send_login_alert(username):
    try:
        msg = MIMEText(f"Akun '{username}' berhasil login pada {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}.")
        msg['Subject'] = "Login Alert"
        msg['From'] = "franzackylucky@gmail.com"
        msg['To'] = "franzackylucky@gmail.com"

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login("franzackylucky@gmail.com", "sfxocchjxlmwzyvr")
            server.send_message(msg)
    except Exception as e:
        print("Email gagal:", e)

def send_service_done_email(email, nama, kerusakan):
    try:
        msg = MIMEText(f"Hai {nama}, HP kamu dengan kerusakan '{kerusakan}' telah selesai diperbaiki. Silakan ambil di tempat service.")
        msg['Subject'] = "Notifikasi Servis HP Selesai"
        msg['From'] = "franzackylucky@gmail.com"
        msg['To'] = email

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login("franzackylucky@gmail.com", "sfxocchjxlmwzyvr")
            server.send_message(msg)
    except Exception as e:
        print("Gagal kirim email:", e)

# Load & Save JSON

def load_users():
    if not os.path.exists(USERS_FILE) or os.stat(USERS_FILE).st_size == 0:
        return {}
    with open(USERS_FILE, 'r') as f:
        return json.load(f)

def save_users(users):
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=4)

def load_services():
    if not os.path.exists(SERVICE_FILE):
        return []
    with open(SERVICE_FILE, 'r') as f:
        return json.load(f)

def save_services(data):
    with open(SERVICE_FILE, 'w') as f:
        json.dump(data, f, indent=4)

def load_diary():
    if not os.path.exists(DIARY_FILE):
        return []
    with open(DIARY_FILE, 'r') as f:
        return json.load(f)

def save_diary(data):
    with open(DIARY_FILE, 'w') as f:
        json.dump(data, f, indent=4)

# Middleware

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        users = load_users()
        username = session.get('username')
        if not username or users[username].get('role') != 'admin' or username != 'Lucky':
            flash("Akses ditolak. Hanya admin Lucky yang bisa akses.")
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated

# Routes
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm = request.form['confirm_password']

        if not valid_email(email):
            return "Format email tidak valid."

        if password != confirm:
            return "Password tidak cocok."

        users = load_users()
        if username in users or any(user['email'] == email for user in users.values()):
            return "Username atau Email sudah terdaftar."

        users[username] = {
            'email': email,
            'password': generate_password_hash(password),
            'online': False,
            'role': 'user'
        }
        save_users(users)
        return redirect(url_for('login'))

    return render_template('register.html')

login_attempts = {}

@app.route('/', methods=['GET', 'POST'])
def login():
    ip = request.remote_addr
    if ip not in login_attempts:
        login_attempts[ip] = {'count': 0, 'last': datetime.now()}

    if request.method == 'POST':
        now = datetime.now()
        if (now - login_attempts[ip]['last']) > timedelta(minutes=5):
            login_attempts[ip] = {'count': 0, 'last': now}

        if login_attempts[ip]['count'] >= 5:
            return "Terlalu banyak percobaan login. Coba lagi nanti."

        username = request.form['username']
        password = request.form['password']
        users = load_users()

        if username in users and check_password_hash(users[username]['password'], password):
            session.permanent = True
            session['username'] = username
            users[username]['online'] = True
            save_users(users)
            send_login_alert(username)
            login_attempts[ip] = {'count': 0, 'last': now}
            return redirect(url_for('admin_dashboard') if users[username].get('role') == 'admin' else url_for('dashboard'))
        else:
            login_attempts[ip]['count'] += 1
            login_attempts[ip]['last'] = now
            return "Login gagal."

    return render_template('index.html')

@app.route('/dashboard')
@login_required
def dashboard():
    services = load_services()
    total = len(services)
    selesai = len([s for s in services if s['status'] == 'selesai'])
    pending = total - selesai
    return render_template("dashboard.html", total=total, selesai=selesai, pending=pending, username=session['username'])

@app.route('/admin_dashboard')
@login_required
@admin_required
def admin_dashboard():
    return render_template("admin_dashboard.html", username=session['username'])

@app.route('/lobi')
@login_required
def lobi():
    return render_template('buat/lobi.html')

@app.route("/pengguna")
@login_required
def pengguna_online():
    users = load_users()  # kalau kamu juga mau nampilin semua yang online
    online_users = [u for u, d in users.items() if d.get('online')]

    current_user_data = {
        'nama': users[session['username']].get('nama', session['username']),
        'email': users[session['username']].get('email', ''),
        'status': users[session['username']].get('role', 'user'),
        'foto': users[session['username']].get('foto', 'default.jpg'),
    }

    return render_template("pengguna.html", current_user=current_user_data, online_users=online_users)
    
@app.route('/logout')
def logout():
    users = load_users()
    if 'username' in session:
        username = session['username']
        users[username]['online'] = False
        save_users(users)
        session.pop('username')
    return redirect(url_for('login'))

@app.route('/input', methods=['GET', 'POST'])
@login_required
def input_service():
    services = load_services()

    if request.method == 'POST':
        nama = request.form['nama']
        nohp = request.form['nohp']
        kerusakan = request.form['kerusakan']
        status = request.form['status']
        email = request.form['email']

        # Validasi input
        if not all([nama, nohp, kerusakan, email, status]):
            flash("Semua kolom wajib diisi!", "warning")
            # Hanya tampilkan yang pending
            pending_services = [s for s in services if s['status'] == 'pending']
            return render_template('admin_input.html', services=pending_services)

        services.append({
            "nama": nama,
            "nohp": nohp,
            "kerusakan": kerusakan,
            "status": status,
            "email": email
        })
        save_services(services)

        if status == "selesai":
            send_service_done_email(email, nama, kerusakan)

        flash("Data berhasil ditambahkan!", "success")
        return redirect(url_for('input_service'))

    # Filter hanya data yang masih pending
    pending_services = [s for s in services if s['status'] == 'pending']
    return render_template('admin_input.html', services=pending_services)

@app.route('/update_status', methods=['GET', 'POST'])
@login_required
def update_status():
    services = load_services()

    if request.method == 'POST':
        index = int(request.form['index'])
        new_status = request.form['status']
        services[index]['status'] = new_status
        save_services(services)

        # Kirim email kalau selesai
        if new_status == "selesai":
            send_service_done_email(services[index]['email'], services[index]['nama'], services[index]['kerusakan'])

        flash("Status berhasil diperbarui.", "success")
        return redirect(url_for('update_status'))

    return render_template('update_status.html', services=services)

@app.route('/riwayat')
@login_required
def riwayat():
    services = load_services()
    selesai_services = [s for s in services if s['status'] == 'selesai']
    return render_template('riwayat.html', services=selesai_services)

@app.route('/admin/diary', methods=['GET', 'POST'])
@admin_required
def admin_diary():
    entries = load_diary()

    if request.method == 'POST':
        new_entry = request.form.get('entry')
        new_title = request.form.get('title')
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        if new_entry and new_title:
            new_id = max([e.get('id', 0) for e in entries], default=0) + 1
            entries.append({'id': new_id, 'timestamp': timestamp, 'entry': new_entry, 'title': new_title})
            save_diary(entries)
            flash("Entry baru berhasil ditambahkan!")
        else:
            flash("Judul dan isi tidak boleh kosong!")

        return redirect(url_for('admin_diary'))

    return render_template('admin_diary.html', entries=reversed(entries))

@app.route('/form_service', methods=['GET', 'POST'])
def form_service():
    if request.method == 'POST':
        nama = request.form['nama'].strip()
        nohp = request.form['nohp'].strip()
        kerusakan = request.form['kerusakan'].strip()
        email = request.form['email'].strip()
        status = "pending"

        # Validasi input kosong
        if not nama or not nohp or not kerusakan or not email:
            flash("Semua field harus diisi!", "error")
            return redirect(url_for('form_service'))

        # Validasi format email
        if not valid_email(email):
            flash("Format email tidak valid!", "error")
            return redirect(url_for('form_service'))

        services = load_services()
        services.append({
            "nama": nama,
            "nohp": nohp,
            "kerusakan": kerusakan,
            "status": status,
            "email": email
        })
        save_services(services)

        flash("Data berhasil dikirim! Kami akan menghubungi Anda setelah servis selesai.", "success")
        return redirect(url_for('form_service'))

    return render_template('input.html')

#settings
UPLOAD_FOLDER = 'static/profil'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

  # Pengaturan
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
app.config['UPLOAD_FOLDER'] = 'static/foto_profil'

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/pengaturan', methods=['GET', 'POST'])
@login_required
def settings():
    users = load_users()
    username = session['username']
    user_data = users.get(username)

    if not user_data:
        flash("Akun tidak ditemukan.", "danger")
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        # Ganti nama
        nama_baru = request.form.get('nama')
        if nama_baru:
            user_data['nama'] = nama_baru

        # Ganti password
        pass_lama = request.form.get('password_lama')
        pass_baru = request.form.get('password_baru')
        confirm_pass = request.form.get('konfirmasi')

        if pass_lama and pass_baru and confirm_pass:
            if check_password_hash(user_data['password'], pass_lama):
                if pass_baru == confirm_pass:
                    user_data['password'] = generate_password_hash(pass_baru)
                    flash("Password berhasil diganti", "success")
                else:
                    flash("Konfirmasi password tidak cocok", "warning")
            else:
                flash("Password lama salah", "danger")

        # Upload foto profil
        if 'foto' in request.files:
            foto = request.files['foto']
            if foto and allowed_file(foto.filename):
                filename = secure_filename(f"{username}_{foto.filename}")
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                foto.save(filepath)
                user_data['foto'] = filename

        # Toggle dark mode
        dark_mode = request.form.get('dark_mode') == 'on'
        user_data['dark_mode'] = dark_mode

        # Simpan perubahan
        users[username] = user_data
        save_users(users)
        flash("Pengaturan berhasil diperbarui", "success")
        return redirect(url_for('settings'))

    # Kirim data user ke template
    user = {
        "username": username,
        "email": user_data.get("email", ""),
        "foto": user_data.get("foto", "default.jpg"),
        "dark_mode": user_data.get("dark_mode", False),
        "nama": user_data.get("nama", "")
    }

    return render_template("settings.html", user=user)

@app.route('/change_password', methods=['POST'])
@login_required
def change_password():
    users = load_users()
    username = session['username']
    current_pw = request.form['current_password']
    new_pw = request.form['new_password']

    if not check_password_hash(users[username]['password'], current_pw):
        flash("Password lama salah!", "warning")
        return redirect(url_for('settings'))

    users[username]['password'] = generate_password_hash(new_pw)
    save_users(users)
    flash("Password berhasil diubah.", "success")
    return redirect(url_for('settings'))

@app.route('/edit_nama', methods=['GET', 'POST'])
@login_required
def edit_nama():
    users = load_users()
    username = session['username']

    if request.method == 'POST':
        nama_baru = request.form.get('nama')
        if nama_baru:
            users[username]['nama'] = nama_baru
            save_users(users)
            flash("Nama berhasil diperbarui", "success")
            return redirect(url_for('settings'))
        else:
            flash("Nama tidak boleh kosong", "warning")

    nama_sekarang = users[username].get('nama', username)
    return render_template("edit_nama.html", nama=nama_sekarang)


@app.route('/profil')
@login_required
def profil():
    users = load_users()
    username = session['username']
    user_data = users.get(username, {})
    return render_template("profil.html", user=user_data)

@app.route('/akun', methods=['GET', 'POST'])
@login_required
def akun():
    username = session.get('username')
    users = load_users()
    user = users.get(username)

    if request.method == 'POST':
        new_name = request.form['name']
        new_email = request.form['email']

        user['email'] = new_email
        user['nama'] = new_name
        users[username] = user
        save_users(users)
        flash("Akun berhasil diperbarui!", "success")
        return redirect(url_for('akun'))

    return render_template('akun.html', user=user)

# foto
app.config['UPLOAD_FOLDER'] = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/ubah_foto', methods=['GET', 'POST'])
@login_required
def ubah_foto():
    users = load_users()
    username = session['username']
    user = users[username]

    if request.method == 'POST':
        if 'foto' not in request.files:
            flash('Tidak ada file foto.', 'warning')
            return redirect(request.url)
        
        file = request.files['foto']
        if file and allowed_file(file.filename):
            filename = secure_filename(f"{username}_{file.filename}")
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            user['foto'] = filename
            save_users(users)
            flash('Foto profil berhasil diperbarui!', 'success')
            return redirect(url_for('settings'))

        flash('Format file tidak didukung.', 'danger')
        return redirect(request.url)

    return render_template('ubah_foto.html', user=user)

@app.route('/ganti_password', methods=['GET', 'POST'])
@login_required
def ganti_password():
    username = session['username']
    users = load_users()

    if request.method == 'POST':
        password_lama = request.form.get('password_lama')
        password_baru = request.form.get('password_baru')
        konfirmasi = request.form.get('konfirmasi')

        if not all([password_lama, password_baru, konfirmasi]):
            flash("Semua kolom wajib diisi!", "warning")
            return redirect(url_for('ganti_password'))

        if not check_password_hash(users[username]['password'], password_lama):
            flash("Password lama salah!", "danger")
            return redirect(url_for('ganti_password'))

        if password_baru != konfirmasi:
            flash("Konfirmasi password tidak cocok!", "warning")
            return redirect(url_for('ganti_password'))

        users[username]['password'] = generate_password_hash(password_baru)
        save_users(users)
        flash("Password berhasil diubah!", "success")
        return redirect(url_for('settings'))

    return render_template("ganti_password.html")

@app.route('/tema')
@login_required
def tema():
    users = load_users()
    username = session['username']
    user = users.get(username, {})
    return render_template('tema.html', user=user)

# Fungsi ambil data user dari session
def get_user():
    users = load_users()
    username = session.get('username')
    if username in users:
        return {
            "username": username,
            "email": users[username].get("email", ""),
            "foto": users[username].get("foto", "default.jpg"),
            "nama": users[username].get("nama", ""),
            "dark_mode": users[username].get("dark_mode", False)
        }
    return {}

# Register fungsi ke Jinja (HARUS DI BAWAHNYA)
app.jinja_env.globals.update(get_user=get_user)

@app.context_processor
def inject_user_theme():
    users = load_users()
    username = session.get('username')
    dark_mode = False
    if username and username in users:
        dark_mode = users[username].get('dark_mode', False)
    return dict(dark_mode=dark_mode)

if __name__ == '__main__':
    app.run(debug=True)
