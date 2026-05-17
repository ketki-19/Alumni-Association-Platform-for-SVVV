from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
from functools import wraps

app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = 'svvv_super_secret_key_2026'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///alumni.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ==========================================
# DATABASE MODELS
# ==========================================
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    enrollment_number = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), default='alumni') # student, alumni, admin
    batch_year = db.Column(db.Integer, nullable=True)
    department = db.Column(db.String(100), nullable=True)
    current_company = db.Column(db.String(100), nullable=True)

class Job(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    company = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    posted_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

# ==========================================
# JWT MIDDLEWARE
# ==========================================
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
        try:
            # Format expected: "Bearer <token>"
            token = token.split(" ")[1]
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = User.query.filter_by(id=data['user_id']).first()
        except:
            return jsonify({'message': 'Token is invalid!'}), 401
        return f(current_user, *args, **kwargs)
    return decorated

# ==========================================
# API ROUTES
# ==========================================
@app.route('/api/setup', methods=['GET'])
def setup_db():
    """Initializes DB and creates dummy users for testing"""
    db.create_all()
    
    # Create test user if not exists
    if not User.query.filter_by(enrollment_number='EN001').first():
        hashed_pw = generate_password_hash('password', method='pbkdf2:sha256')
        new_user = User(
            enrollment_number='EN001', 
            password_hash=hashed_pw,
            full_name='Rahul Sharma',
            role='alumni',
            batch_year=2018,
            department='Computer Science',
            current_company='Google'
        )
        db.session.add(new_user)
        db.session.commit()
        return jsonify({'message': 'Database initialized & Test User Created'})
    return jsonify({'message': 'Database already setup'})

@app.route('/api/login', methods=['POST'])
def login():
    """Authenticates user and returns JWT token"""
    data = request.get_json()
    
    if not data or not data.get('enrollment_number') or not data.get('password'):
        return jsonify({'message': 'Could not verify', 'error': 'Missing credentials'}), 400
        
    user = User.query.filter_by(enrollment_number=data.get('enrollment_number')).first()
    
    if user and check_password_hash(user.password_hash, data.get('password')):
        token = jwt.encode({
            'user_id': user.id,
            'role': user.role,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
        }, app.config['SECRET_KEY'], algorithm="HS256")
        
        return jsonify({'token': token, 'full_name': user.full_name, 'role': user.role})
        
    return jsonify({'message': 'Invalid enrollment number or password'}), 401

@app.route('/api/directory', methods=['GET'])
@token_required
def get_directory(current_user):
    """Returns list of alumni (Protected Route)"""
    alumni = User.query.filter_by(role='alumni').all()
    result = []
    for alum in alumni:
        result.append({
            'name': alum.full_name,
            'batch': alum.batch_year,
            'department': alum.department,
            'company': alum.current_company
        })
    return jsonify({'data': result})

@app.route('/api/jobs', methods=['POST', 'GET'])
@token_required
def manage_jobs(current_user):
    if request.method == 'POST':
        data = request.get_json()
        new_job = Job(
            title=data['title'],
            company=data['company'],
            description=data['description'],
            posted_by=current_user.id
        )
        db.session.add(new_job)
        db.session.commit()
        return jsonify({'message': 'Job posted successfully!'}), 201
        
    elif request.method == 'GET':
        jobs = Job.query.all()
        result = [{'title': j.title, 'company': j.company, 'desc': j.description} for j in jobs]
        return jsonify({'jobs': result})

@app.route('/api/events', methods=['POST'])
@token_required
def create_event(current_user):
    data = request.get_json()
    return jsonify({
        'message': f"Event '{data.get('title')}' created successfully!",
        'status': 'pending_approval'
    }), 201

if __name__ == '__main__':
    # Run the Flask app on localhost (127.0.0.1:5000)
    app.run(debug=True, port=5000)
