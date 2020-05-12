from requests import get, post

"""Для тестирвоания нужно создать объект класса Users"""

first_name = 'token_first'
second_name = 'token_second'
email = 'token_first@gmail.com'
password = 'test'

post('http://localhost:5000/api/v1/users/',
     json={'first_name': first_name,
           'second_name': second_name,
           'password': password,
           'email': email})

"""Тесты tokens_resource"""


print(get('http://localhost:5000/api/v1/tokens',
          json={'email': 'wrong_email',
                'password': password}).json())

print(get('http://localhost:5000/api/v1/tokens',
          json={'email': email,
                'password': 'wrong_password'}).json())

true_request = get('http://localhost:5000/api/v1/tokens',
                   json={'email': email,
                         'password': password}).json()

print(true_request)
token = true_request['token']

print(post('http://localhost:5000/api/v1/tokens',
           json={'token': token}).json())
