import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
# db_drop_and_create_all()

# ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks')
def get_drinks():
    drinks = [drink.short() for drink in Drink.query.all()]

    return jsonify({
        'success': True,
        'drinks': drinks}), 200


'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''


@requires_auth(permission='get:drinks-detail')
@app.route('/drinks-detail')
def get_drinks_detail():
    drinks = [drink.long() for drink in Drink.query.all()]

    return jsonify({
        'success': True,
        'drinks': drinks}), 200


'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''


@requires_auth(permission='post:drinks')
@app.route('/drinks')
@app.route('/drinks', methods=['POST'])
def post_drinks():
    try:
        body = request.get_json()
        title = body.get('title')
        recipe = body.get('recipe')
    except:
        abort(422, 'Incorect body of the request')

    is_new_drink = Drink.query.filter_by(
        title=title).one_or_none()

    if is_new_drink is None:
        drink = Drink(title=title, recipe=json.dumps(recipe))
        drink.insert()
    else:
        abort(409, f'Drink with name {title} already exist')

    return jsonify({
        'success': True,
        'drinks': drink.long()}), 200


'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''


@requires_auth(permission='patch:drinks')
@app.route('/drinks/<int:id>', methods=['PATCH'])
def patch_drinks(id):
    drink = Drink.query.filter_by(id=id).one_or_none()
    if drink is None:
        abort(404, f'There is no drink with id {id}')

    body = request.get_json()
    title = body.get('title')
    recipe = body.get('recipe')

    drink.title = title
    drink.recipre = recipe
    drink.update()

    return jsonify({
        'success': True,
        'drinks': drink}), 200


'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''


@requires_auth(permission='delete:drinks')
@app.route('/drinks/<int:id>', methods=['DELETE'])
def delete_drinks(id):
    drink = Drink.query.filter_by(id=id).one_or_none()
    if drink is None:
        abort(404, f'There is no drink with id {id}')

    drink.delete()

    return jsonify({
        'success': True,
        'delete': id}), 200


# Error Handling
'''
Example error handling for unprocessable entity
'''


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": error.description
    }), 422


'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False, 
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''

'''
@TODO implement error handler for 404
    error handler should conform to general task above 
'''


@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": error.description
    }), 404


@app.errorhandler(409)
def already_exist(error):
    return jsonify({
        "success": False,
        "error": 409,
        "message": error.description
    }), 409


'''
@TODO implement error handler for AuthError
    error handler should conform to general task above 
'''
