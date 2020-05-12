from flask_restful import reqparse


post_parser = reqparse.RequestParser()
post_parser.add_argument('chat_id', type=int)
post_parser.add_argument('receiver_id', type=str)
post_parser.add_argument('text')

list_get_parser = reqparse.RequestParser()
list_get_parser.add_argument('date', type=float, default=0)
list_get_parser.add_argument('receiver_id', type=str)
list_get_parser.add_argument('chat_id', type=int)
