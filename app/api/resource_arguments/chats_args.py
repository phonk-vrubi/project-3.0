from flask_restful import reqparse

get_parser = reqparse.RequestParser()
get_parser.add_argument('chat_id')
get_parser.add_argument('chat_with')

post_parser = reqparse.RequestParser()
# post_parser.add_argument('title')
post_parser.add_argument('first_author_id', required=True, type=str)
post_parser.add_argument('second_author_id', required=True, type=str)
# список объектов класса Users(реализация через ChatParticipants)
# post_parser.add_argument('chat_participants', required=True, type=list)

delete_parser = reqparse.RequestParser()
delete_parser.add_argument('id', type=int)
delete_parser.add_argument('user_id', type=str)

