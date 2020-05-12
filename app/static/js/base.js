const apiServerUsersURL = new URL('/api/v1/users/', apiServerURL);
const apiServerUsersListURL = new URL('/api/v1/users', apiServerURL);
const apiServerUsersFriendsURL = new URL('/api/v1/users_friends/',
                                         apiServerURL);
const apiServerUsersFriendsListURL = new URL('/api/v1/users_friends',
    apiServerURL);
const apiServerMessagesURL = new URL('/api/v1/messages/', apiServerURL);
const apiServerMessagesListURL = new URL('/api/v1/messages', apiServerURL);
const apiServerChatsURL = new URL('/api/v1/chats/', apiServerURL);


// Устанавливаем CSRF токен перед отправкой AJAX запросов
$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) &&
                !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", csrfToken);
        }
    }
});

const refreshURL = new URL('/refresh', window.origin);

function refreshToken(){
    $.ajax({
        url: refreshURL,
        method: "GET"
    });
}

// Каждые несколько минут обновляем access_token
var refreshTimerID = setTimeout(refreshToken, refreshTime);