from requests import post

"""Для тестирования нужно создать объект класса Users"""

first_name = 'auth_first'
second_name = 'auth_second'
email = 'auth_first@gmail.com'
password = 'test'

post('http://localhost:5000/api/v1/users/',
     json={'first_name': first_name,
           'second_name': second_name,
           'password': password,
           'email': email})

"""Тесты auth_resource"""

print(post('http://localhost:5000/api/v1/login/',
           json={'email': 'wrong_email',
                 'password': password,
                 'expires_in': 1000000}).json())

print(post('http://localhost:5000/api/v1/login/',
           json={'email': email,
                 'password': 'wrong_password',
                 'expires_in': 1000000}).json())

print(post('http://localhost:5000/api/v1/login/',
           json={'email': email,
                 'password': password,
                 'expires_in': 9999999999999999999999}).json())

true_request = post('http://localhost:5000/api/v1/login/',
                    json={'email': email,
                          'password': password,
                          'expires_in': 1000000}).json()

print(true_request)
refresh_token = true_request['refresh_token']

print(post('http://localhost:5000/api/v1/refresh/',
           json={'refresh_token': refresh_token}).json())
