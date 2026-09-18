import json
from flask import Flask, render_template, send_from_directory, request, jsonify
from flask_cors import CORS
import os

app = Flask(__name__, static_folder='static', template_folder='templates')
CORS(app)

BASE_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(BASE_DIR, 'data')


def load_stadiums():
    stadiums_path = os.path.join(DATA_DIR, 'stadiums.geojson')
    
    try:
        with open(stadiums_path, 'r', encoding='utf-8') as fh:
            data = json.load(fh)
            return data.get('features', [])
    except FileNotFoundError:
        app.logger.warning('stadiums.geojson not found: %s', stadiums_path)
        return []
    except Exception as exc:
        app.logger.error('Unable to load stadiums.geojson: %s', exc)
        return []


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/data/<path:filename>')
def data_file(filename):
    # Serve geojson data from the repo `data/` directory
    return send_from_directory(DATA_DIR, filename)


@app.route('/api/country', methods=['POST'])
def country_click():
    payload = request.json or {}
    app.logger.info('Country clicked: %s', payload.get('id'))

    props = payload.get('properties', {}) if isinstance(payload, dict) else {}
    country_code = (props.get('SOV_A3') or props.get('country') or props.get('ISO_A3') or props.get('ADM0_A3') or '')
    country_code = country_code.strip().upper()

    stadiums = []
    if country_code:
        stadiums = [feature for feature in load_stadiums()
                    if (feature.get('properties', {}).get('country') or '').strip().upper() == country_code]

    return jsonify({'status': 'received', 'payload': payload, 'stadiums': stadiums}), 200


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)
