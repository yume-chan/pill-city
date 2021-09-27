import os
import werkzeug
from bson import ObjectId
from flask_restful import reqparse, Resource, fields, marshal_with
from flask_jwt_extended import jwt_required, get_jwt_identity
from mini_gplus.daos.user import find_user, update_profile_pic, update_avatar, get_users
from mini_gplus.daos.user_cache import get_in_user_cache_by_oid
from mini_gplus.utils.now_ms import now_seconds
from .s3 import upload_to_s3


class UserId(fields.Raw):
    def format(self, value):
        return get_in_user_cache_by_oid(value).user_id


class UserCreatedAtSeconds(fields.Raw):
    def format(self, value):
        return get_in_user_cache_by_oid(value).created_at


class UserAvatar(fields.Raw):
    def format(self, value):
        avatar_media = get_in_user_cache_by_oid(value).avatar
        if not avatar_media:
            return None
        return f"{os.environ['CDN_URL']}/{avatar_media.id}"


class UserProfilePic(fields.Raw):
    def format(self, value):
        return get_in_user_cache_by_oid(value).profile_pic


user_fields = {
    'id': UserId(attribute='id'),
    'created_at_seconds': UserCreatedAtSeconds(attribute='id'),
    # todo: following not included is this a problem?
    'avatar_url': UserAvatar(attribute='id'),
    'profile_pic': UserProfilePic(attribute='id')
}


class Me(Resource):
    @jwt_required()
    @marshal_with(user_fields)
    def get(self):
        user_id = get_jwt_identity()
        user = find_user(user_id)
        return user


user_avatar_parser = reqparse.RequestParser()
user_avatar_parser.add_argument('file', type=werkzeug.datastructures.FileStorage, location='files', required=True)


class MyAvatar(Resource):
    @jwt_required()
    def post(self):
        # check user
        user_id = get_jwt_identity()
        user = find_user(user_id)
        if not user:
            return {'msg': f'User {user_id} is not found'}, 404
        args = user_avatar_parser.parse_args()
        file = args['file']

        # the resulting object name looks like avatars/kt-1627815711477.jpeg
        # avatars prefix is made explicitly public readable
        # because it's faster to read a user's metadata, and we are fine with all avatars being public
        # BUG: the suffix was previously now_ms() // 1_000_000, meaning the timestamps where at ~1/3 hour scale
        object_name_stem = f"avatars/{user_id}-{str(now_seconds())}"
        avatar_media = upload_to_s3(file, object_name_stem)
        if not avatar_media:
            return {'msg': f"Disallowed image type"}, 400

        update_avatar(user, avatar_media)


class MyProfilePic(Resource):
    @jwt_required()
    def patch(self, user_profile_pic):
        """
        Update User profile pic
        """
        # check user
        user_id = get_jwt_identity()
        user = find_user(user_id)
        if not user:
            return {'msg': f'User {user_id} is not found'}, 404

        update_profile_pic(user, user_profile_pic)


class IsFollowing(fields.Raw):
    def format(self, value):
        user_id = get_jwt_identity()
        user = find_user(user_id)
        if not user:
            return False
        return ObjectId(value) in map(lambda u: u.id, user.followings)


user_with_following_fields = dict({
    'is_following': IsFollowing(attribute='id')
}, **user_fields)


class Users(Resource):
    @jwt_required()
    @marshal_with(user_with_following_fields)
    def get(self):
        """
        Get all users other than the logged in user
        """
        user_id = get_jwt_identity()
        # TODO: pretty inefficient because all Users needs to call get user by oid once more lol
        return get_users(user_id), 200


class User(Resource):
    @jwt_required()
    @marshal_with(user_with_following_fields)
    def get(self, user_id):
        """
        Get a specific user by ID
        """
        user = find_user(user_id)
        if not user:
            return {'msg': f'User {user_id} is not found'}, 404
        return user
