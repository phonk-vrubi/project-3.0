import werkzeug.datastructures
from flask_restful import reqparse


post_parser = reqparse.RequestParser()
post_parser.add_argument('first_name', required=True)
post_parser.add_argument('second_name', required=True)
post_parser.add_argument('password', required=True)
post_parser.add_argument('email', required=True)
post_parser.add_argument('phone_number')
post_parser.add_argument('age', type=int)
post_parser.add_argument('additional_inf')
post_parser.add_argument('city')
post_parser.add_argument('avatar',
                         type=werkzeug.datastructures.FileStorage,
                         location='files')


put_parser = reqparse.RequestParser()
put_parser.add_argument('first_name')
put_parser.add_argument('second_name')
put_parser.add_argument('phone_number')
put_parser.add_argument('age', type=int)
put_parser.add_argument('additional_inf')
put_parser.add_argument('city')
put_parser.add_argument('avatar', type=werkzeug.datastructures.FileStorage,
                        location='files')

put_parser.add_argument('old_password')
put_parser.add_argument('email')
put_parser.add_argument('password')


list_get_parser = reqparse.RequestParser()
list_get_parser.add_argument('first_name')
list_get_parser.add_argument('second_name')
list_get_parser.add_argument('search_request')
list_get_parser.add_argument('start', type=int, default=0)
list_get_parser.add_argument('limit', type=int)
