import time
from requests import post, get

"""Для тестирвоания данного ресурса необходимо
добавить хотябы 2 объекта класса Users"""

post('http://localhost:5000/api/v1/users/',
     json={'first_name': 'mes_first',
           'second_name': 'test',
           'password': 'test',
           'email': 'mes_first@gmail.com'}).json()

post('http://localhost:5000/api/v1/users/',
     json={'first_name': 'mes_second',
           'second_name': 'test',
           'password': 'test',
           'email': 'mes_second@gmail.com'}).json()

"""Также понадобятся токены и alternative_id каждого пользователя"""

access_token_1 = post('http://localhost:5000/api/v1/login/',
                      json={'email': 'mes_first@gmail.com',
                            'password': 'test',
                            'expires_in': 9999999}).json()['access_token']

access_token_2 = post('http://localhost:5000/api/v1/login/',
                      json={'email': 'mes_second@gmail.com',
                            'password': 'test',
                            'expires_in': 9999999}).json()['access_token']

alt_id_1 = get('http://localhost:5000/api/v1/users/',
               json={'access_token': access_token_1}).json()['user']['user_id']

alt_id_2 = get('http://localhost:5000/api/v1/users/',
               json={'access_token': access_token_2}).json()['user']['user_id']

"""Сообщения можно отправлять только друзьям"""

print(post('http://localhost:5000/api/v1/messages/',
           json={'receiver_id': alt_id_2,
                 'text': 'test',
                 'access_token': access_token_1}).json())

"""Так что пользователей необходимо добавить в друзья друг к другу"""

post('http://localhost:5000/api/v1/users_friends/',
     json={'friend_id': alt_id_2,
           'action': 'add',
           'access_token': access_token_1}).json()

post('http://localhost:5000/api/v1/users_friends/',
     json={'friend_id': alt_id_1,
           'action': 'accept',
           'access_token': access_token_2}).json()

"""Тесты messages_resource"""

print(post('http://localhost:5000/api/v1/messages/',
           json={'access_token': access_token_1}).json())

print(post('http://localhost:5000/api/v1/messages/',
           json={'receiver_id': alt_id_2,
                 'text': 'test',
                 'access_token': access_token_1}).json())

print(get('http://localhost:5000/api/v1/messages',
          json={'receiver_id': alt_id_2,
                'access_token': access_token_1}).json())

"""Из придыдущего запроса получим id чата"""
chat_id = get('http://localhost:5000/api/v1/messages',
              json={
                  'receiver_id': alt_id_2,
                  'access_token': access_token_1
              }).json()['messages'][-1]['chat_id']

print(get('http://localhost:5000/api/v1/messages',
          json={'chat_id': chat_id,
                'access_token': access_token_1}).json())

print(get('http://localhost:5000/api/v1/messages',
          json={'receiver_id': alt_id_2,
                'date': time.time(),
                'access_token': access_token_1}).json())
