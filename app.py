from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import random
import os

# Инициализация Flask и базы данных
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///reaction.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Модель для хранения результатов
class Record(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False, default='Аноним')
    reaction_time = db.Column(db.Integer, nullable=False)
    date = db.Column(db.String(20), default=lambda: datetime.now().strftime("%Y-%m-%d %H:%M"))

# Создание таблиц
with app.app_context():
    db.create_all()

# Основные маршруты
@app.route('/')
def index():
    return render_template('index.html')

# Генерация случайной задержки
@app.route('/get_delay')
def get_delay():
    return jsonify({'delay': random.uniform(1.0, 3.0)})

# Сохранение результата и расчет статистики
@app.route('/save_result', methods=['POST'])
def save_result():
    data = request.json
    time_ms = int(data['time'])
    username = data.get('username', 'Аноним').strip()[:20] or 'Аноним'

    new_record = Record(username=username, reaction_time=time_ms)
    db.session.add(new_record)
    db.session.commit()

    # Расчет позиции среди других игроков
    total_players = Record.query.count()
    faster_players = Record.query.filter(Record.reaction_time < time_ms).count()
    percentile = round((1 - faster_players / total_players) * 100) if total_players > 0 else 100

    return jsonify({
        'status': 'success',
        'stats': {
            'your_time': time_ms,
            'percentile': percentile,
            'total_players': total_players
        }
    })

# Показ таблицы рекордов
@app.route('/records')
def records():
    records = Record.query.order_by(Record.reaction_time.asc()).limit(20).all()
    return render_template('records.html', records=records)

# Запуск приложения
if __name__ == '__main__':
    if not os.path.exists('instance'):
        os.makedirs('instance')
    app.run(debug=True)
