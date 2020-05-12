from flask_restful import reqparse

list_get_parser = reqparse.RequestParser()
list_get_parser.add_argument('type',
                             choices=('incoming', 'outgoing'))

post_parser = reqparse.RequestParser()
post_parser.add_argument('friend_id', required=True, type=str)
post_parser.add_argument('action', default='add',
                         choices=('add', 'accept', 'deny'))

delete_parser = reqparse.RequestParser()
delete_parser.add_argument('friend_id', required=True, type=str)
