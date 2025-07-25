from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, jwt_required
from flasgger import Swagger
from flask_migrate import Migrate
from flask_cors import CORS
import datetime

# Initialize app
app = Flask(__name__)
CORS(app)

# Config
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['JWT_SECRET_KEY'] = 'your_jwt_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:1234@localhost/pharma'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Init extensions
db = SQLAlchemy(app)
swagger = Swagger(app)
migrate = Migrate(app, db)
jwt = JWTManager(app)

# -----------------------------
# Models
# -----------------------------
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    manufacturer = db.Column(db.String(100))
    price = db.Column(db.Float)
    discount = db.Column(db.String(10))
    image_url = db.Column(db.Text)
    chemical_formulation = db.Column(db.String(100))
    generic_name = db.Column(db.String(100))
    salts = db.relationship('SaltContent', backref='product', lazy=True)
    reviews = db.relationship('Review', backref='product', lazy=True)
    descriptions = db.relationship('Description', backref='product', lazy=True)

class SaltContent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))
    salt_name = db.Column(db.String(100))
    quantity = db.Column(db.String(50))

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))
    rating = db.Column(db.Float)
    comment = db.Column(db.Text)

class Description(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))
    section_title = db.Column(db.String(100))
    content = db.Column(db.Text)

# -----------------------------
# Routes
# -----------------------------



@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if data.get('username') == 'admin' and data.get('password') == 'admin123':
        expires = datetime.timedelta(hours=1)
        token = create_access_token(identity='admin', expires_delta=expires)
        return jsonify(token=token), 200
    return jsonify({'msg': 'Invalid credentials'}), 401

# --------- Products ----------




# --------- Salts ----------
@app.route('/salts/<int:product_id>', methods=['GET'])
@jwt_required()
def get_salts(product_id):
    salts = SaltContent.query.filter_by(product_id=product_id).all()
    return jsonify([{'salt_name': s.salt_name, 'quantity': s.quantity} for s in salts])


# --------- Reviews ----------
@app.route('/reviews/<int:product_id>', methods=['GET'])
@jwt_required()
def get_reviews(product_id):
    reviews = Review.query.filter_by(product_id=product_id).all()
    return jsonify([{'rating': r.rating, 'comment': r.comment} for r in reviews])


# --------- Descriptions ----------
@app.route('/descriptions/<int:product_id>', methods=['GET'])
@jwt_required()
def get_descriptions(product_id):
    descs = Description.query.filter_by(product_id=product_id).all()
    return jsonify([{'section_title': d.section_title, 'content': d.content} for d in descs])


# -----------------------------
# Run App
# -----------------------------
if __name__ == '__main__':
    app.run(debug=True)
