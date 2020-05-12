from requests import post, get, put

print(post('http://localhost:5000/api/v1/users/',
           json={'first_name': 'test_first',
                 'second_name': 'test_second',
                 'password': 'test',
                 'email': 'test@gmail.com'}).json())

"""Для тестирования последующих методов понадобится токен"""

access_token = post('http://localhost:5000/api/v1/login/',
                    json={'email': 'test@gmail.com',
                          'password': 'test',
                          'expires_in': 9999999}).json()['access_token']

wrong_token = 'wrong'

print(post('http://localhost:5000/api/v1/users/').json())

print(get('http://localhost:5000/api/v1/users/',
          json={'access_token': access_token}).json())

print(get('http://localhost:5000/api/v1/users/',
          json={'access_token': wrong_token}).json())

print(put('http://localhost:5000/api/v1/users/',
          json={'first_name': 'test_first_edited',
                'old_password': 'test',
                'email': 'test@gmail.com',
                'access_token': access_token}).json())

print(put('http://localhost:5000/api/v1/users/',
          json={'first_name': 'test_first_edited',
                'access_token': wrong_token}).json())

print(put('http://localhost:5000/api/v1/users/',
          json={'first_name': 'test_first_edited',
                'old_password': 'wrong_password',
                'email': 'test@gmail.com',
                'access_token': access_token}).json())

print(put('http://localhost:5000/api/v1/users/',
          json={'first_name': 'test_first_edited',
                'password': 'new_password',
                'email': 'test@gmail.com',
                'access_token': access_token}).json())

print(get('http://localhost:5000/api/v1/users').json())

print(get('http://localhost:5000/api/v1/users',
          json={'limit': 21}).json())

print(get('http://localhost:5000/api/v1/users',
          json={'search_request': 'test_first'}).json())
