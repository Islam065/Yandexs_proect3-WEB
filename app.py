from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import random

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///records.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Record(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False, default='Игрок')
    time = db.Column(db.Integer, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/get_delay')
def get_delay():
    return jsonify({'delay': random.uniform(1, 5)})


@app.route('/save_result', methods=['POST'])
def save_result():
    data = request.json
    time = data['time']
    username = data.get('username', 'Игрок')

    new_record = Record(username=username, time=time)
    db.session.add(new_record)
    db.session.commit()

    # Расчет процентиля
    all_times = [r.time for r in Record.query.all()]
    percentile = int((sum(1 for t in all_times if t > time) / len(all_times)) * 100) if all_times else 0

    return jsonify({
        'status': 'success',
        'stats': {
            'your_time': time,
            'percentile': percentile,
            'total_players': len(all_times)
        }
    })


@app.route('/records')
def records():
    records = Record.query.order_by(Record.time.asc()).all()
    return render_template('records.html', records=records)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000)
