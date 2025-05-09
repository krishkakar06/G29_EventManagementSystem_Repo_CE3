from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_jwt_extended import JWTManager, jwt_required, create_access_token
import os
from datetime import datetime
from werkzeug.utils import secure_filename
from flask_migrate import Migrate
from flask import send_from_directory

app = Flask(__name__)
CORS(app)

# Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///db.sqlite3')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'your-secret-key-here')
app.config['UPLOAD_FOLDER'] = 'uploads'
app.static_folder='uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db = SQLAlchemy(app)
migrate = Migrate(app, db)
jwt = JWTManager(app)

# Models
class Event(db.Model):
    __tablename__ = 'Eventmanage1_event'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    type = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Float, nullable=False)
    date = db.Column(db.String(50))  # ISO format string
    location = db.Column(db.String(200))
    image = db.Column(db.String(500), nullable=True)
    organizer_id = db.Column(db.Integer)

    def to_dict(self):
        image_url = None
        if self.image:
            if self.image.startswith('/uploads'):
                image_url = self.image
            elif self.image.startswith('uploads/'):
                image_url = f"/{self.image}"
            else:
                # Prevent double /uploads/ prefix
                if self.image.startswith('/uploads/'):
                    image_url = self.image
                else:
                    image_url = f"/uploads/{self.image}"
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'type': self.type,
            'price': self.price,
            'date': self.date,
            'location': self.location,
            'image': image_url,
            'organizer_id': self.organizer_id
        }

# Routes
import logging

logger = logging.getLogger(__name__)

@app.route('/api/events', methods=['GET'])
def get_events():
    events = Event.query.all()
    event_dicts = [e.to_dict() for e in events]
    for event in event_dicts:
        logger.debug(f"Event ID: {event['id']}, Image URL: {event['image']}")
    return jsonify(event_dicts)

@app.route('/api/events/<int:event_id>', methods=['GET'])
def get_event(event_id):
    event = Event.query.get_or_404(event_id)
    return jsonify(event.to_dict())

@app.route('/api/events', methods=['POST'])
def create_event():
    data = request.get_json()
    image_value = data.get('image')
    app.logger.debug(f"Received image field in create_event: {image_value}")
    # Validate image field to avoid malformed paths
    if image_value and (image_value.startswith('http://') or image_value.startswith('https://') or image_value.startswith('/uploads')):
        image_field = image_value
    else:
        image_field = f"/uploads/{image_value}" if image_value else ''

    event = Event(
        title=data['title'],
        description=data['description'],
        type=data['type'],
        price=data['price'],
        date=data.get('date'),
        location=data.get('location'),
        image=image_field,
        organizer_id=data.get('organizer_id')
    )
    db.session.add(event)
    db.session.commit()
    return jsonify(event.to_dict()), 201

@app.route('/api/events/<int:event_id>', methods=['PUT'])
def update_event(event_id):
    event = Event.query.get_or_404(event_id)
    data = request.get_json()

    image_value = data.get('image')
    if image_value and (image_value.startswith('http') or image_value.startswith('/uploads')):
        image_field = image_value
    else:
        image_field = f"/uploads/{image_value}" if image_value else event.image

    event.title = data.get('title', event.title)
    event.description = data.get('description', event.description)
    event.type = data.get('type', event.type)
    event.price = data.get('price', event.price)
    event.date = data.get('date', event.date)
    event.location = data.get('location', event.location)
    event.image = image_field

    db.session.commit()
    return jsonify(event.to_dict())

@app.route('/api/events/<int:event_id>', methods=['DELETE'])
def delete_event(event_id):
    event = Event.query.get_or_404(event_id)
    db.session.delete(event)
    db.session.commit()
    return jsonify({'message': 'Event deleted'}), 200

@app.route('/api/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        return jsonify({'image': f'/uploads/{filename}'}), 201

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', debug=True, port=5000)