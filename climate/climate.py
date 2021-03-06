import os
import sqlite3
import werkzeug
from datetime import datetime
from flask import Flask, request, g, jsonify

app = Flask(__name__)
app.config.from_object(__name__) # load config from this file , climate.py

# Load default config and override config from an environment variable
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'climate.db')
))
app.config.from_envvar('FLASKR_SETTINGS', silent=True)
FORMAT_DATE = '%Y-%m-%d'

@app.route("/climate", methods=['GET'])
def list_climate():
    climates = []
    query_sql = 'select id, date, rainfall, temperature from climate where 1=1 {} order by id desc'.format(query_filter(request.args))
    for row in query_db(query_sql):
        climates.append(create_climate(row))

    return jsonify({'climates': climates})

@app.route("/climate/<climate_id>", methods=['GET'])
def get_climate(climate_id):
    row = query_db('select id, date, rainfall, temperature from climate where id = ?', [climate_id], one=True)
    if row is None: 
        return jsonify({'message':"Not found"}), 404

    return jsonify(create_climate(row))

@app.route("/climate", methods=['POST'])
def save_climate():
    if not request.is_json:
        return jsonify({'message':"Bad Gateway"}), 502

    db = get_db()
    climate = request.get_json()
    if not valid_climate(climate):
        return jsonify({'message':"Bad Gateway"}), 502

    cursor = db.execute('insert into climate (date, rainfall, temperature) values (?, ?, ?)',
                 [climate['date'], climate['rainfall'], climate['temperature']])
    db.commit()
    
    return jsonify({'id': cursor.lastrowid, 
                    'date': climate['date'], 
                    'rainfall': climate['rainfall'], 
                    'temperature': climate['temperature']
                    }), 201

@app.route("/climate/<climate_id>", methods=['DELETE'])
def delete_climate(climate_id):
    db = get_db()
    cursor = db.execute('delete from climate where id = ?', [climate_id])
    db.commit()
    return jsonify({'message':"Success"}), 200

@app.route("/climate/predict", methods=['GET'])
def predict_climate():
    predict = datetime.now().strftime(FORMAT_DATE)
    row = query_db('select id, date, rainfall, temperature from climate where date = ?', [predict], one=True)
    if row is None: 
        return jsonify({'message':"Not found"}), 404

    return jsonify(create_climate(row))

@app.errorhandler(werkzeug.exceptions.BadRequest)
def handle_bad_request(e):
    return jsonify({'message':"Bad Request"}), 400

def query_filter(params):
    query = ""
    query_params = {'period':"and (date between date('now') and date('now', '{}'))"}
    query_value = {'week':"+7 day",
                    'month':"+1 month"}
    for key, value in params.iteritems():
        if key in query_params: 
            query = query.join(query_params[key].format(query_value.get(value, "+0 day")))
    return query

def create_climate(row):
    climate = {'id': row['id'], 
                'date': row['date'], 
                'rainfall': row['rainfall'], 
                'temperature': row['temperature'] 
                }
    return climate

def valid_climate(climate):
    if ('date' in climate and 'rainfall' in climate and 'temperature' in climate):
        if (not is_number(climate['rainfall'])) or (not is_number(climate['temperature'])):
            return False
        try:
            datetime.strptime(climate['date'], FORMAT_DATE)
        except ValueError:
            return False

        return True
    else:
        return False

def is_number(num):
    return isinstance(num, (int, long, float))

def init_db():
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()

def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

@app.cli.command('initdb')
def initdb_command():
    init_db()
    print('Initialized the database.')

def connect_db():
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv

def get_db():
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db

@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()