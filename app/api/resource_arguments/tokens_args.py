from flask_restful import reqparse


get_parser = reqparse.RequestParser()
get_parser.add_argument('email', required=True)
get_parser.add_argument('password', required=True)

post_parser = reqparse.RequestParser()
post_parser.add_argument('token', required=True)
