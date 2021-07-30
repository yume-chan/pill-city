import os
from os import urandom
from pymongo.uri_parser import parse_uri
from flask import Flask, request, jsonify
from flask_mongoengine import MongoEngine, MongoEngineSessionInterface
from flask_restful import Api
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token
from mini_gplus.resources import Users, Me, Posts, Comments, NestedComments, Circles, Circle, CircleMember, \
    Followings, Following, Profile
from mini_gplus.models import User


app = Flask(__name__)
app.secret_key = urandom(24)
mongodb_uri = os.environ['MONGODB_URI']
mongodb_db = parse_uri(mongodb_uri)['database']
app.config['MONGODB_SETTINGS'] = {
    'db': mongodb_db,
    'host': mongodb_uri
}
db = MongoEngine(app)
app.session_interface = MongoEngineSessionInterface(db)


##################
# Authentication #
##################
app.config['JWT_SECRET_KEY'] = os.environ['JWT_SECRET_KEY']
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = False
JWTManager(app)


@app.route('/api/auth', methods=['POST'])
def auth():
    if not request.is_json:
        return jsonify({"message": "missing JSON in request"}), 400
    _id = request.json.get('id', None)
    password = request.json.get('password', None)
    if not _id:
        return jsonify({"message": {"id": "id is required"}}), 400
    if not password:
        return jsonify({"message": {"password": "password is required"}}), 400
    user_checked = User.check(_id, password)
    if not user_checked:
        return jsonify({"message": "invalid id or password"}), 401
    access_token = create_access_token(identity=_id)
    return jsonify(access_token=access_token), 200


########
# APIs #
########
app.config['BUNDLE_ERRORS'] = True
CORS(app, resources={r"/api/*": {"origins": "*"}})

api = Api(app)
api.add_resource(Users, '/api/users')

api.add_resource(Profile, '/api/profile/<string:profile_user_id>')

api.add_resource(NestedComments, '/api/posts/<string:post_id>/comment/<string:comment_id>/comment')
api.add_resource(Comments, '/api/posts/<string:post_id>/comment')
api.add_resource(Posts, '/api/posts')

api.add_resource(Circles, '/api/circles')
api.add_resource(CircleMember, '/api/circle/<string:circle_name>/membership/<string:member_user_id>')
api.add_resource(Circle, '/api/circle/<string:circle_name>')

api.add_resource(Followings, '/api/followings')
api.add_resource(Following, '/api/following/<string:following_user_id>')

api.add_resource(Me, '/api/me')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
