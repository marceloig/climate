import os
import sqlite3
from flask import Flask, request, g, jsonify

app = Flask(__name__)
app.config.from_object(__name__) # load config from this file , flaskr.py

# Load default config and override config from an environment variable
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'climate.db'),
    SECRET_KEY='development key',
    USERNAME='admin',
    PASSWORD='default'
))
app.config.from_envvar('FLASKR_SETTINGS', silent=True)

@app.route("/climate", methods=['GET'])
def list_climate():
    climates = []
    for row in query_db('select id, date, rainfall, temperature from climate order by id desc'):
        climates.append(create_climate(row))

    return jsonify({'climates': climates})

@app.route("/climate/<int:climate_id>", methods=['GET'])
def get_climate(climate_id):
    row = query_db('select id, date, rainfall, temperature from climate where id = ?', [climate_id], one=True)
    return jsonify(create_climate(row))

@app.route("/climate", methods=['POST'])
def save_climate():
    db = get_db()
    cursor = db.execute('insert into climate (date, rainfall, temperature) values (?, ?, ?)',
                 [request.json['date'], request.json['rainfall'], request.json['temperature']])
    db.commit()
    
    return jsonify({'id': cursor.lastrowid, 
                    'date': request.json['date'], 
                    'rainfall': request.json['rainfall'], 
                    'temperature': request.json['temperature'] 
                    }), 201

@app.route("/climate/<int:climate_id>", methods=['DELETE'])
def delete_climate(climate_id):
    db = get_db()
    cursor = db.execute('delete from climate where id = ?', [climate_id])
    db.commit()
    return jsonify({'message':"Success"}), 200

@app.route("/climate/predict", methods=['GET'])
def predict_climate():
    return 200

def create_climate(row):
    climate = {'id': row['id'], 
                'date': row['date'], 
                'rainfall': row['rainfall'], 
                'temperature': row['temperature'] 
                }
    return climate

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
    """Initializes the database."""
    init_db()
    print('Initialized the database.')

def connect_db():
    """Connects to the specific database."""
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv

def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db

@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()