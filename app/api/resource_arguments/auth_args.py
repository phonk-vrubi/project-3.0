from flask_restful import reqparse

login_post_parser = reqparse.RequestParser()
login_post_parser.add_argument('email', required=True)
login_post_parser.add_argument('password', required=True)
login_post_parser.add_argument('expires_in', type=float)
