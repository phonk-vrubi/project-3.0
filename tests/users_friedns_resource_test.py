from requests import get, post, delete

"""Для тестирвоания данного ресурса необходимо
добавить хотябы 2 объекта класса Users"""

post('http://localhost:5000/api/v1/users/',
     json={'first_name': 'friend_first',
           'second_name': 'test',
           'password': 'test',
           'email': 'friend_first@gmail.com'})

post('http://localhost:5000/api/v1/users/',
     json={'first_name': 'friend_second',
           'second_name': 'test',
           'password': 'test',
           'email': 'friend_second@gmail.com'})

"""Также понадобятся токены и alternative_id каждого пользователя"""

access_token_1 = post('http://localhost:5000/api/v1/login/',
                      json={'email': 'friend_first@gmail.com',
                            'password': 'test',
                            'expires_in': 9999999}).json()['access_token']

access_token_2 = post('http://localhost:5000/api/v1/login/',
                      json={'email': 'friend_second@gmail.com',
                            'password': 'test',
                            'expires_in': 9999999}).json()['access_token']

alt_id_1 = get('http://localhost:5000/api/v1/users/',
               json={'access_token': access_token_1}).json()['user']['user_id']

alt_id_2 = get('http://localhost:5000/api/v1/users/',
               json={'access_token': access_token_2}).json()['user']['user_id']

"""Тесты users_friends_resource"""

print(post('http://localhost:5000/api/v1/users_friends/',
           json={'friend_id': alt_id_2,
                 'action': 'add',
                 'access_token': access_token_1}).json())

print(post('http://localhost:5000/api/v1/users_friends/',
           json={'friend_id': alt_id_1,
                 'action': 'accept',
                 'access_token': access_token_2}).json())

print(delete('http://localhost:5000/api/v1/users_friends/',
             json={'friend_id': alt_id_2,
                   'access_token': access_token_1}).json())

print(post('http://localhost:5000/api/v1/users_friends/',
           json={'friend_id': alt_id_1,
                 'action': 'add',
                 'access_token': access_token_2}).json())

print(post('http://localhost:5000/api/v1/users_friends/',
           json={'friend_id': alt_id_2,
                 'action': 'deny',
                 'access_token': access_token_1}).json())

print(delete('http://localhost:5000/api/v1/users_friends/',
             json={'friend_id': alt_id_1,
                   'access_token': access_token_2}).json())

print(post('http://localhost:5000/api/v1/users_friends/',
           json={'friend_id': alt_id_2,
                 'action': 'add',
                 'access_token': access_token_1}).json())

print(post('http://localhost:5000/api/v1/users_friends/',
           json={'friend_id': alt_id_1,
                 'action': 'accept',
                 'access_token': access_token_2}).json())

print(get('http://localhost:5000/api/v1/users_friends',
          json={'access_token': access_token_1}).json())

print(post('http://localhost:5000/api/v1/users_friends/',
           json={'friend_id': alt_id_1,
                 'action': 'add',
                 'access_token': access_token_2}).json())

print(get('http://localhost:5000/api/v1/users_friends',
          json={'access_token': access_token_1,
                'type': 'incoming'}).json())

print(post('http://localhost:5000/api/v1/users_friends/',
           json={'friend_id': alt_id_2,
                 'action': 'add',
                 'access_token': access_token_1}).json())

print(get('http://localhost:5000/api/v1/users_friends',
          json={'access_token': access_token_1,
                'type': 'outgoing'}).json())
