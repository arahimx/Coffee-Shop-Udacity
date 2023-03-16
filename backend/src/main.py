import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from database.models import db_drop_and_create_all, setup_db, Drink
from auth.auth import AuthError, requires_auth, get_token_auth_header

app = Flask(__name__)
setup_db(app)
CORS(app)


db_drop_and_create_all()


@app.route('/allDrinks', methods=['GET'])
def get_drinks():

    drinks = Drink.query.all()

    return jsonify({
        'success': True,
        'drinks': [d.short() for d in drinks]
    }), 200


@app.route('/drink-detail', methods=['GET'])
@requires_auth('get:drink-detail')
def get_drink_detail(payload):

    drinks = Drink.query.all()


    return jsonify({
        'success': True,
        'drinks': [d.long() for d in drinks]
    }), 200


@app.route('/addDrink', methods=['POST'])
@requires_auth('post:drink')
def create_drink(payload):
    req = request.get_json()
    try:

        drink = Drink()
        drink.title = req['title']

        drink.recipe = json.dumps(req['recipe'])
        drink.insert()

    except Exception:
        abort(400)

    return jsonify({'success': True, 'drinks': [drink.long()]})


@app.route('/EditDrink/<int:id>', methods=['PATCH'])
@requires_auth('patch:drink')
def update_drink(payload, id):
    req = request.get_json()

    drink = Drink.query.filter(Drink.id == id).one_or_none()

    if not drink:
        abort(404)

    try:

        req_title = req.get('title')
        req_recipe = req.get('recipe')

        if req_title:
            drink.title = req_title

        if req_recipe:
            drink.recipe = json.dumps(req['recipe'])

        drink.update()
    except Exception:
        abort(400)

    return jsonify({'success': True, 'drinks': [drink.long()]}), 200


@app.route('/deleteDrink/<int:id>', methods=['DELETE'])
@requires_auth('delete:drink')
def delete_drink(payload, id):

    drink = Drink.query.filter(Drink.id == id).one_or_none()

    if not drink:
        abort(404)

    try:
        drink.delete()
    except Exception:
        abort(400)

    return jsonify({'success': True, 'delete': id}), 200



@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404


@app.errorhandler(AuthError)
def auth_error(error):
    print(error)
    return jsonify({
        "success": False,
        "error": error.status_code,
        "message": error.error['description']
    }), error.status_code


@app.errorhandler(401)
def unauthorized(error):
    print(error)
    return jsonify({
        "success": False,
        "error": 401,
        "message": 'Unathorized'
    }), 401


@app.errorhandler(500)
def internal_server_error(error):
    print(error)
    return jsonify({
        "success": False,
        "error": 500,
        "message": 'Internal Server Error'
    }), 500


@app.errorhandler(400)
def bad_request(error):
    print(error)
    return jsonify({
        "success": False,
        "error": 400,
        "message": 'Bad Request'
    }), 400


@app.errorhandler(405)
def method_not_allowed(error):
    print(error)
    return jsonify({
        "success": False,
        "error": 405,
        "message": 'Method Not Allowed'
    }), 405


if __name__ == "__main__":
    app.debug = True
    app.run()
