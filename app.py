from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

app = Flask(__name__)
app.config['SECRET_KEY'] = 'supersecretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Ініціалізація бази даних та компонентів
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"

# 📌 Модель товару
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text, nullable=False)

# 📌 Модель користувача
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

# Завантаження користувача для Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# 📌 Головна сторінка: якщо авторизований → профіль, якщо ні → список товарів
@app.route('/')
def home():
    if current_user.is_authenticated:
        return render_template('profile.html', user=current_user)
    products = Product.query.all()
    return render_template('index.html', products=products)

# 📌 Додавання товару
@app.route('/add_product', methods=['GET', 'POST'])
@login_required
def add_product():
    if request.method == 'POST':
        name = request.form['name']
        price = request.form['price']
        description = request.form['description']

        product = Product(name=name, price=price, description=description)
        db.session.add(product)
        db.session.commit()
        flash('Товар додано успішно!', 'success')
        return redirect(url_for('home'))

    return render_template('add_product.html')

# 📌 Реєстрація користувача
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        user = User(username=username, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Реєстрація успішна! Тепер увійдіть у систему.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

# 📌 Вхід у систему

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            flash('Вхід успішний!', 'success')
            return redirect(url_for('home'))  # 🔥 Переадресація на головну
        else:
            flash('Неправильний логін або пароль!', 'danger')
    return render_template('login.html')

# 📌 Вихід з облікового запису
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Ви вийшли з облікового запису.', 'info')
    return redirect(url_for('home'))

# 📌 Запуск сервера
if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Створюємо базу даних
    app.run(debug=True)
