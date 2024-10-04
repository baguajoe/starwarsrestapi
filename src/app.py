"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Character, Planet, Favorite

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)


@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code


@app.route('/')
def sitemap():
    return generate_sitemap(app)


@app.route('/character', methods=['GET'])
def get_all_characters():
    characters = Character.query.all()
    return jsonify([character.serialize()for character in characters]), 200


@app.route('/character/<int:character_id>', methods=['GET'])
def get_character(character_id):
    character = Character.query.get(character_id) 
    if character:
        return jsonify(character.serialize()), 200
    return jsonify({"error": "character not found"}), 404

@app.route('/planet', methods=['GET'])
def get_all_planets():
    planets = Planet.query.all()
    return jsonify([planet.serialize()for planet in planets]), 200


@app.route('/planet/<int:planet_id>', methods=['GET'])
def get_planet(planet_id):
    planet = Planet.query.get(planet_id) 
    if planet:
        return jsonify(planet.serialize()), 200
    return jsonify({"error": "planet not found"}), 404

@app.route('/users', methods=['GET'])
def get_all_users():
    users = User.query.all()
    return jsonify([user.serialize() for user in users]), 200


@app.route('/users/favorites', methods=['GET'])
def get_user_favorites():
    user_id = 1  
    user = User.query.get(user_id)
    if user:
        favorites = user.favorites
        return jsonify([favorite.serialize() for favorite in favorites]), 200
    return jsonify({"error": "User not found"}), 404

@app.route('/favorite/character/<int:character_id>', methods=['POST'])
def add_favorite_character(character_id):
    favorite = Favorite(user_id=1, character_id=character_id)
    
    if favorite:
        db.session.add(favorite)
        db.session.commit()
        return jsonify({"message": "Favorite character added"}), 200
    return jsonify({"error": "Favorite character not found"}), 404


@app.route('/favorite/planet/<int:planet_id>', methods=['POST'])
def add_favorite_planet(planet_id):
    favorite = Favorite(user_id=1, planet_id=planet_id)
    
    if favorite:
        db.session.add(favorite)
        db.session.commit()
        return jsonify({"message": "Favorite planet added"}), 200
    return jsonify({"error": "Favorite planet not found"}), 404





@app.route('/favorite/planet/<int:planet_id>', methods=['DELETE'])
def delete_favorite_planet(planet_id):
    user_id = 1  
    favorite = Favorite.query.filter_by(user_id=user_id, planet_id=planet_id).first()
    if favorite:
        db.session.delete(favorite)
        db.session.commit()
        return jsonify({"message": "Favorite planet deleted"}), 200
    return jsonify({"error": "Favorite planet not found"}), 404


@app.route('/favorite/character/<int:character_id>', methods=['DELETE'])
def delete_favorite_character(character_id):
    user_id = 1
    favorite = Favorite.query.filter_by(user_id=user_id, character_id=character_id).first()
    if favorite:
        db.session.delete(favorite)
        db.session.commit()
        return jsonify({"message": "Favorite character deleted"}), 200
    return jsonify({"error": "Favorite character not found"}), 404

# This only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
