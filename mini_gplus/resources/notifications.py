from flask_restful import Resource, fields, marshal_with
from flask_jwt_extended import jwt_required, get_jwt_identity
from mini_gplus.daos.user import find_user
from mini_gplus.daos.notification import get_notifications, mark_notification_as_read, mark_all_notifications_as_read
from .users import user_fields
from .pagination import pagination_parser


class NotifyingAction(fields.Raw):
    def format(self, notifying_action):
        return notifying_action.value


notification_fields = {
    'id': fields.String(attribute='eid'),
    'created_at_seconds': fields.Integer(attribute='created_at'),
    'notifier': fields.Nested(user_fields),
    'notifying_href': fields.String,
    'notifying_summary': fields.String,
    'notifying_action': NotifyingAction,
    'notifying_deleted': fields.Boolean,
    'notified_href': fields.String,
    'notified_summary': fields.String,
    'notified_deleted': fields.Boolean,
    'unread': fields.Boolean
}


class Notifications(Resource):
    @jwt_required()
    @marshal_with(notification_fields)
    def get(self):
        """
        Get all of a user's notifications
        """
        user_id = get_jwt_identity()
        user = find_user(user_id)

        args = pagination_parser.parse_args()
        return get_notifications(user, args['from_id'])


class NotificationRead(Resource):
    @jwt_required()
    def put(self, notification_id):
        """
        Mark a notification as read
        """
        user_id = get_jwt_identity()
        user = find_user(user_id)
        if not mark_notification_as_read(user, notification_id):
            return {'msg': "Not allowed to mark notification as read"}, 401


class NotificationsAllRead(Resource):
    @jwt_required()
    def put(self):
        """
        Mark a user's all notifications as read
        """
        user_id = get_jwt_identity()
        user = find_user(user_id)
        mark_all_notifications_as_read(user)
