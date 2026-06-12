from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import os
import json
from werkzeug.utils import secure_filename
import time
import markdown
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session

# Создаем папку instance если её нет
os.makedirs('instance', exist_ok=True)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here-change-in-production'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///echo.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Настройки для загрузки файлов
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'admin_login'
login_manager.login_message = 'Требуется авторизация мастера'

# Модели базы данных
class NPC(db.Model):
    __tablename__ = 'npcs'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    title = db.Column(db.String(200))
    race = db.Column(db.String(50))
    description = db.Column(db.Text)
    full_info = db.Column(db.Text)
    category = db.Column(db.String(50))
    status = db.Column(db.String(20))
    image_url = db.Column(db.String(300))
    importance = db.Column(db.Integer, default=1)
    portrait_url = db.Column(db.String(300), default='/static/images/placeholders/npc.jpg')
    

class Location(db.Model):
    __tablename__ = 'locations'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    region = db.Column(db.String(100))
    description = db.Column(db.Text)
    dangers = db.Column(db.Text)
    quests = db.Column(db.Text)
    npc_ids = db.Column(db.String(200))
    map_x = db.Column(db.Integer, default=50)
    map_y = db.Column(db.Integer, default=50)

class Article(db.Model):
    __tablename__ = 'articles'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(50))
    content = db.Column(db.Text)
    is_spoiler = db.Column(db.Boolean, default=False)
    sort_order = db.Column(db.Integer, default=0)

class PartyMember(db.Model):
    __tablename__ = 'party_members'
    id = db.Column(db.Integer, primary_key=True)
    player_name = db.Column(db.String(100))
    char_name = db.Column(db.String(100), nullable=False)
    char_class = db.Column(db.String(50))
    race = db.Column(db.String(50))
    description = db.Column(db.Text)
    private_notes = db.Column(db.Text)
    player_password = db.Column(db.String(200))
    level = db.Column(db.Integer, default=1)
    portrait_url = db.Column(db.String(300), default='/static/images/placeholders/player.jpg')

class GalleryImage(db.Model):
    __tablename__ = 'gallery_images'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(50))
    image_filename = db.Column(db.String(300), nullable=False)
    uploaded_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    sort_order = db.Column(db.Integer, default=0)

class MusicTrack(db.Model):
    __tablename__ = 'music_tracks'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    character_theme = db.Column(db.String(100))
    audio_url = db.Column(db.String(500), nullable=False)
    sort_order = db.Column(db.Integer, default=0)
    cover_url = db.Column(db.String(500))

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    is_admin = db.Column(db.Boolean, default=True)

def save_uploaded_file(file, folder='characters'):
    if file and file.filename:
        upload_folder = os.path.join('static', 'uploads', folder)
        os.makedirs(upload_folder, exist_ok=True)
        
        filename = secure_filename(file.filename)
        unique_filename = f"{int(time.time())}_{filename}"
        filepath = os.path.join(upload_folder, unique_filename)
        file.save(filepath)
        return f'/static/uploads/{folder}/{unique_filename}'
    return None

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.template_filter('markdown')
def markdown_filter(text):
    if text:
        # Конвертируем Markdown в HTML с поддержкой таблиц и списков
        return markdown.markdown(text, extensions=['extra', 'nl2br'])
    return ''

# Основные маршруты
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/world')
def world():
    articles = Article.query.filter_by(category='world').all()
    return render_template('world.html', articles=articles)

@app.route('/npcs')
def npcs():
    npc_list = NPC.query.order_by(NPC.importance.desc()).all()
    categories = db.session.query(NPC.category).distinct().all()
    races = db.session.query(NPC.race).distinct().all()
    
    # Собираем уникальные расы для фильтра
    races_list = []
    for npc in npc_list:
        if npc.race and npc.race not in races_list:
            races_list.append(npc.race)
    
    return render_template('npcs.html', 
                        npcs=npc_list, 
                        categories=[c[0] for c in categories if c[0]],
                        races_list=races_list)

@app.route('/api/npcs')
def api_npcs():
    npcs = NPC.query.all()
    return jsonify([{
        'id': n.id,
        'name': n.name,
        'title': n.title,
        'race': n.race,
        'category': n.category,
        'status': n.status
    } for n in npcs])

@app.route('/locations')
def locations():
    locations = Location.query.all()
    return render_template('locations.html', locations=locations)

@app.route('/location/<int:id>')
def location_detail(id):
    location = Location.query.get_or_404(id)
    return render_template('location_detail.html', location=location)

@app.route('/pantheon')
def pantheon():
    gods = Article.query.filter_by(category='pantheon').all()
    return render_template('pantheon.html', gods=gods)

@app.route('/codex')
def codex():
    rules = Article.query.filter_by(category='rule').all()
    return render_template('codex.html', rules=rules)

@app.route('/party')
def party():
    members = PartyMember.query.all()
    return render_template('party.html', members=members)

@app.route('/gallery')
def gallery():
    images = GalleryImage.query.order_by(GalleryImage.sort_order, GalleryImage.uploaded_at.desc()).all()
    return render_template('gallery.html', images=images)

"""
# Админ маршруты
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('admin_dashboard'))
        flash('Неверные учетные данные', 'danger')
    
    return render_template('admin/login.html')
"""
"""
@app.route('/admin/logout')
@login_required
def admin_logout():
    logout_user()
    return redirect(url_for('index'))
"""

@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    npc_count = NPC.query.count()
    location_count = Location.query.count()
    article_count = Article.query.count()
    party_count = PartyMember.query.count()
    image_count = GalleryImage.query.count()
    music_count = MusicTrack.query.count()
    
    return render_template('admin/dashboard.html', 
                        npc_count=npc_count,
                        location_count=location_count,
                        article_count=article_count,
                        party_count=party_count,
                        image_count=image_count,
                        music_count=music_count)

def save_portrait(file, folder='npcs'):
    if file and file.filename:
        # Создаем папку если её нет
        upload_folder = os.path.join('static', 'uploads', folder)
        os.makedirs(upload_folder, exist_ok=True)
        
        # Создаем уникальное имя файла
        filename = secure_filename(file.filename)
        name_parts = filename.rsplit('.', 1)
        unique_filename = f"{int(time.time())}_{name_parts[0]}.{name_parts[1]}"
        
        # Сохраняем файл
        filepath = os.path.join(upload_folder, unique_filename)
        file.save(filepath)
        
        # Возвращаем URL для доступа
        return f'/static/uploads/{folder}/{unique_filename}'
    return None

# Маршруты для управления NPC
@app.route('/admin/npcs')
@login_required
def admin_npcs():
    npcs = NPC.query.all()
    return render_template('admin/npcs.html', npcs=npcs)

@app.route('/admin/npc/add', methods=['GET', 'POST'])
@login_required
def add_npc():
    if request.method == 'POST':
        # Обработка фото
        portrait_url = None
        if 'image' in request.files and request.files['image'].filename:
            portrait_url = save_portrait(request.files['image'], 'npcs')
        
        npc = NPC(
            name=request.form['name'],
            title=request.form['title'],
            race=request.form['race'],
            description=request.form['description'],
            full_info=request.form['full_info'],
            category=request.form['category'],
            status=request.form['status'],
            portrait_url=portrait_url or '/static/images/placeholders/npc.jpg'
        )
        db.session.add(npc)
        db.session.commit()
        flash('NPC добавлен', 'success')
        return redirect(url_for('admin_npcs'))
    return render_template('admin/edit_npc.html', npc=None)

@app.route('/admin/npc/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_npc(id):
    npc = NPC.query.get_or_404(id)
    if request.method == 'POST':
        # Обработка нового фото
        if 'image' in request.files and request.files['image'].filename:
            portrait_url = save_portrait(request.files['image'], 'npcs')
            if portrait_url:
                npc.portrait_url = portrait_url
        
        npc.name = request.form['name']
        npc.title = request.form['title']
        npc.race = request.form['race']
        npc.description = request.form['description']
        npc.full_info = request.form['full_info']
        npc.category = request.form['category']
        npc.status = request.form['status']
        
        db.session.commit()
        flash('NPC обновлен', 'success')
        return redirect(url_for('admin_npcs'))
    return render_template('admin/edit_npc.html', npc=npc)

@app.route('/admin/npc/delete/<int:id>')
@login_required
def delete_npc(id):
    npc = NPC.query.get_or_404(id)
    db.session.delete(npc)
    db.session.commit()
    flash('NPC удален', 'warning')
    return redirect(url_for('admin_npcs'))

# Маршруты для управления локациями
@app.route('/admin/locations')
@login_required
def admin_locations():
    locations = Location.query.all()
    return render_template('admin/locations.html', locations=locations)

@app.route('/admin/location/add', methods=['GET', 'POST'])
@login_required
def add_location():
    if request.method == 'POST':
        location = Location(
            name=request.form['name'],
            region=request.form['region'],
            description=request.form['description'],
            dangers=request.form['dangers'],
            quests=request.form['quests'],
            map_x=int(request.form.get('map_x', 50)),
            map_y=int(request.form.get('map_y', 50))
        )
        db.session.add(location)
        db.session.commit()
        flash('Локация добавлена', 'success')
        return redirect(url_for('admin_locations'))
    return render_template('admin/edit_location.html', location=None)

@app.route('/admin/location/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_location(id):
    location = Location.query.get_or_404(id)
    if request.method == 'POST':
        location.name = request.form['name']
        location.region = request.form['region']
        location.description = request.form['description']
        location.dangers = request.form['dangers']
        location.quests = request.form['quests']
        location.map_x = int(request.form.get('map_x', 50))
        location.map_y = int(request.form.get('map_y', 50))
        db.session.commit()
        flash('Локация обновлена', 'success')
        return redirect(url_for('admin_locations'))
    return render_template('admin/edit_location.html', location=location)

@app.route('/admin/location/delete/<int:id>')
@login_required
def delete_location(id):
    location = Location.query.get_or_404(id)
    db.session.delete(location)
    db.session.commit()
    flash('Локация удалена', 'warning')
    return redirect(url_for('admin_locations'))

# Маршруты для управления статьями
@app.route('/admin/articles')
@login_required
def admin_articles():
    articles = Article.query.all()
    return render_template('admin/articles.html', articles=articles)

@app.route('/admin/article/add', methods=['GET', 'POST'])
@login_required
def add_article():
    if request.method == 'POST':
        article = Article(
            title=request.form['title'],
            category=request.form['category'],
            content=request.form['content'],
            is_spoiler='is_spoiler' in request.form
        )
        db.session.add(article)
        db.session.commit()
        flash('Статья добавлена', 'success')
        return redirect(url_for('admin_articles'))
    return render_template('admin/edit_article.html', article=None)

@app.route('/admin/article/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_article(id):
    article = Article.query.get_or_404(id)
    if request.method == 'POST':
        article.title = request.form['title']
        article.category = request.form['category']
        article.content = request.form['content']
        article.is_spoiler = 'is_spoiler' in request.form
        db.session.commit()
        flash('Статья обновлена', 'success')
        return redirect(url_for('admin_articles'))
    return render_template('admin/edit_article.html', article=article)

@app.route('/admin/article/delete/<int:id>')
@login_required
def delete_article(id):
    article = Article.query.get_or_404(id)
    db.session.delete(article)
    db.session.commit()
    flash('Статья удалена', 'warning')
    return redirect(url_for('admin_articles'))

@app.route('/admin/article/update_order/<int:id>', methods=['POST'])
@login_required
def update_article_order(id):
    article = Article.query.get_or_404(id)
    try:
        new_order = int(request.form.get('sort_order', 0))
        article.sort_order = new_order
        db.session.commit()
        flash(f'Порядок статьи «{article.title}» изменен на {new_order}', 'success')
    except ValueError:
        flash('Ошибка: порядок должен быть числом', 'danger')
    except Exception as e:
        flash(f'Ошибка при сохранении: {e}', 'danger')
    
    return redirect(url_for('admin_articles'))

# Маршруты для управления игроками
@app.route('/admin/party')
@login_required
def admin_party():
    members = PartyMember.query.all()
    return render_template('admin/party.html', members=members)

@app.route('/admin/party/add', methods=['GET', 'POST'])
@login_required
def add_party_member():
    if request.method == 'POST':
        # Обработка фото
        portrait_url = None
        if 'image' in request.files and request.files['image'].filename:
            portrait_url = save_portrait(request.files['image'], 'players')
        
        member = PartyMember(
            player_name=request.form['player_name'],
            char_name=request.form['char_name'],
            char_class=request.form['char_class'],
            race=request.form['race'],
            description=request.form['description'],
            private_notes=request.form.get('private_notes', ''),
            level=int(request.form.get('level', 1)),
            portrait_url=portrait_url or '/static/images/placeholders/player.jpg'
        )
        db.session.add(member)
        db.session.commit()
        flash('Игрок добавлен', 'success')
        return redirect(url_for('admin_party'))
    return render_template('admin/edit_party.html', member=None)

@app.route('/admin/party/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_party_member(id):
    member = PartyMember.query.get_or_404(id)
    if request.method == 'POST':
        # Обработка нового фото
        if 'image' in request.files and request.files['image'].filename:
            portrait_url = save_portrait(request.files['image'], 'players')
            if portrait_url:
                member.portrait_url = portrait_url
        
        member.player_name = request.form['player_name']
        member.char_name = request.form['char_name']
        member.char_class = request.form['char_class']
        member.race = request.form['race']
        member.description = request.form['description']
        member.private_notes = request.form.get('private_notes', '')
        member.level = int(request.form.get('level', 1))
        
        db.session.commit()
        flash('Игрок обновлен', 'success')
        return redirect(url_for('admin_party'))
    return render_template('admin/edit_party.html', member=member)

@app.route('/admin/party/delete/<int:id>')
@login_required
def delete_party_member(id):
    member = PartyMember.query.get_or_404(id)
    db.session.delete(member)
    db.session.commit()
    flash('Игрок удален', 'warning')
    return redirect(url_for('admin_party'))

# Маршруты для управления галереей
@app.route('/admin/gallery')
@login_required
def admin_gallery():
    images = GalleryImage.query.order_by(GalleryImage.sort_order, GalleryImage.uploaded_at.desc()).all()
    return render_template('admin/gallery.html', images=images)

@app.route('/admin/gallery/add', methods=['GET', 'POST'])
@login_required
def add_gallery_image():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        category = request.form.get('category')
        sort_order = request.form.get('sort_order', 0)
        
        if 'image' not in request.files:
            flash('Не выбран файл', 'danger')
            return redirect(request.url)
        
        file = request.files['image']
        if file.filename == '':
            flash('Не выбран файл', 'danger')
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            unique_filename = f"{int(time.time())}_{filename}"
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], unique_filename))
            
            image = GalleryImage(
                title=title,
                description=description,
                category=category,
                image_filename=unique_filename,
                sort_order=int(sort_order)
            )
            db.session.add(image)
            db.session.commit()
            flash('Изображение добавлено в галерею', 'success')
            return redirect(url_for('admin_gallery'))
        else:
            flash('Недопустимый формат файла. Разрешены: png, jpg, jpeg, gif, webp', 'danger')
    
    return render_template('admin/edit_gallery.html', image=None)

@app.route('/admin/gallery/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_gallery_image(id):
    image = GalleryImage.query.get_or_404(id)
    
    if request.method == 'POST':
        image.title = request.form.get('title')
        image.description = request.form.get('description')
        image.category = request.form.get('category')
        image.sort_order = int(request.form.get('sort_order', 0))
        
        if 'image' in request.files and request.files['image'].filename != '':
            file = request.files['image']
            if file and allowed_file(file.filename):
                old_file_path = os.path.join(app.config['UPLOAD_FOLDER'], image.image_filename)
                if os.path.exists(old_file_path):
                    os.remove(old_file_path)
                
                filename = secure_filename(file.filename)
                unique_filename = f"{int(time.time())}_{filename}"
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], unique_filename))
                image.image_filename = unique_filename
        
        db.session.commit()
        flash('Изображение обновлено', 'success')
        return redirect(url_for('admin_gallery'))
    
    return render_template('admin/edit_gallery.html', image=image)

@app.route('/admin/gallery/delete/<int:id>')
@login_required
def delete_gallery_image(id):
    image = GalleryImage.query.get_or_404(id)
    
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], image.image_filename)
    if os.path.exists(file_path):
        os.remove(file_path)
    
    db.session.delete(image)
    db.session.commit()
    flash('Изображение удалено', 'warning')
    return redirect(url_for('admin_gallery'))

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session

# Музыкальные маршруты
@app.route('/music')
def music():
    tracks = MusicTrack.query.order_by(MusicTrack.sort_order, MusicTrack.id).all()
    return render_template('music.html', tracks=tracks)

@app.route('/admin/music')
@login_required
def admin_music():
    tracks = MusicTrack.query.order_by(MusicTrack.sort_order, MusicTrack.id).all()
    return render_template('admin/music.html', tracks=tracks)

@app.route('/admin/music/add', methods=['GET', 'POST'])
@login_required
def add_music_track():
    if request.method == 'POST':
        track = MusicTrack(
            title=request.form['title'],
            description=request.form['description'],
            character_theme=request.form['character_theme'],
            audio_url=request.form['audio_url'],
            cover_url=request.form.get('cover_url', ''),
            sort_order=int(request.form.get('sort_order', 0))
        )
        db.session.add(track)
        db.session.commit()
        flash('Трек добавлен', 'success')
        return redirect(url_for('admin_music'))
    return render_template('admin/edit_music.html', track=None)

@app.route('/admin/music/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_music_track(id):
    track = MusicTrack.query.get_or_404(id)
    if request.method == 'POST':
        track.title = request.form['title']
        track.description = request.form['description']
        track.character_theme = request.form['character_theme']
        track.audio_url = request.form['audio_url']
        track.cover_url = request.form.get('cover_url', '')
        track.sort_order = int(request.form.get('sort_order', 0))
        db.session.commit()
        flash('Трек обновлен', 'success')
        return redirect(url_for('admin_music'))
    return render_template('admin/edit_music.html', track=track)

@app.route('/admin/music/delete/<int:id>')
@login_required
def delete_music_track(id):
    track = MusicTrack.query.get_or_404(id)
    db.session.delete(track)
    db.session.commit()
    flash('Трек удален', 'warning')
    return redirect(url_for('admin_music'))

# Секретный пользователь (Тифлинг)
SECRET_USER = {
    'username': 'TheTifling',
    'password': 'MyEnemyMyIdol'
}

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Проверка на Админа
        admin_user = User.query.filter_by(username=username).first()
        if admin_user and check_password_hash(admin_user.password_hash, password):
            login_user(admin_user)
            flash('Добро пожаловать, Мастер!', 'success')
            return redirect(url_for('admin_dashboard'))
        
        # Проверка на Тифлинга
        if username == SECRET_USER['username'] and password == SECRET_USER['password']:
            session['secret_user'] = username
            flash('Добро пожаловать, великий Тифлинг!', 'success')
            return redirect(url_for('secret_archive'))
        
        # Если ни то, ни другое
        flash('Неверный логин или пароль!', 'danger')
    
    return render_template('admin/login.html')

@app.route('/admin/logout')
@login_required
def admin_logout():
    logout_user()
    flash('Вы вышли из панели мастера', 'info')
    return redirect(url_for('index'))

@app.route('/secret/logout')
def secret_logout():
    session.pop('secret_user', None)
    flash('Вы вышли из секретного архива', 'info')
    return redirect(url_for('index'))

@app.route('/secret/archive')
def secret_archive():
    if not session.get('secret_user'):
        flash('Сначала войдите в систему!', 'warning')
        return redirect(url_for('login'))
    return render_template('secret_archive.html')

@app.route('/alternate-reality')
def alternate_reality():
    # Проверяем, авторизован ли секретный пользователь
    if not session.get('secret_user'):
        flash('Сначала войдите в секретный архив!', 'warning')
        return redirect(url_for('login'))
    return render_template('alternate_reality.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        if not User.query.first():
            admin = User(
                username='admin',
                password_hash=generate_password_hash('voidmaster'),
                is_admin=True
            )
            db.session.add(admin)
            db.session.commit()
            print("Администратор создан: admin / voidmaster")
    app.run(debug=True, host='0.0.0.0', port=5000)