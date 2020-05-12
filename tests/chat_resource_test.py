from requests import get, post, delete

"""Для тестирования понадобятся для экземпляра класса Users"""

first_name_1 = 'chat_first_1'
second_name_1 = 'chat_second_1'
email_1 = 'chat_first_1@gmail.com'
password_1 = 'test'

first_name_2 = 'chat_first_2'
second_name_2 = 'chat_second_2'
email_2 = 'chat_first_2@gmail.com'
password_2 = 'test'

post('http://localhost:5000/api/v1/users/',
     json={'first_name': first_name_1,
           'second_name': second_name_1,
           'password': password_1,
           'email': email_1})

post('http://localhost:5000/api/v1/users/',
     json={'first_name': first_name_2,
           'second_name': second_name_2,
           'password': password_2,
           'email': email_2})

"""Получим их alternative_id"""

access_token_1 = post('http://localhost:5000/api/v1/login/',
                      json={'email': email_1,
                            'password': password_1,
                            'expires_in': 9999999}).json()['access_token']

access_token_2 = post('http://localhost:5000/api/v1/login/',
                      json={'email': email_2,
                            'password': password_2,
                            'expires_in': 9999999}).json()['access_token']

alt_id_1 = get('http://localhost:5000/api/v1/users/',
               json={'access_token': access_token_1}).json()['user']['user_id']

alt_id_2 = get('http://localhost:5000/api/v1/users/',
               json={'access_token': access_token_2}).json()['user']['user_id']

print(post('http://localhost:5000/api/v1/chats/',
           json={'first_author_id': alt_id_1,
                 'second_author_id': alt_id_2,
                 'access_token': access_token_1}).json())

true_request = get('http://localhost:5000/api/v1/chats/',
                   json={'access_token': access_token_1}).json()
print(true_request)
chat_id = true_request['chats'][-1]['id']

print(delete('http://localhost:5000/api/v1/chats/',
             json={'id': chat_id,
                   'access_token': access_token_1}).json())

print(post('http://localhost:5000/api/v1/chats/',
           json={'first_author_id': alt_id_1,
                 'second_author_id': alt_id_2,
                 'access_token': access_token_1}).json())

print(delete('http://localhost:5000/api/v1/chats/',
             json={'alternative_id': alt_id_2,
                   'access_token': access_token_1}).json())

print(delete('http://localhost:5000/api/v1/chats/',
             json={'alternative_id': 'wrong_id',
                   'access_token': access_token_1}).json())

print(get('http://localhost:5000/api/v1/chats/',
          json={'access_token': access_token_1}).json())
