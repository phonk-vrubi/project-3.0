console.log('Connecting to WebSocket...');
var socket = io();
socket.on('connect', function() {
    console.log('Connected to WebSocket!');
});

socket.on('new_message', function(msg){
    let userID = msg.sender_id;
    if (userID != currentUserID && !hasChat(userID)){
        $.ajax({
            url: apiServerUsersURL,
            method: "GET",
            data: {user_id: msg.sender_id},
            success(data){
                let user = data.user;
                let chatData = {
                    user_id: userID,
                    avatar: new URL(user.avatar, uploadsURL),
                    last_msg: voidChar,
                    user_name: fullUserName(user)
                };
                chatsData.set(userID, chatData);
                appendChat(chatData);
                handleNewMessage(msg);
            }
        });
    }
    handleNewMessage(msg);
});

function hasChat(ID){
    return Boolean($(
            `.index-chats-chat-item[data-chat-id="${ID}"],
            .index-chats-chat-item[data-user-id="${ID}"]`
        ).length);
}

function handleNewMessage(msg){
    let msgText = msg.text;
    let chatInfo = currentChatInfo();
    let msgElem;
    if (chatInfo.chat_id == msg.chat_id){
        if (chatInfo.user_id == msg.sender_id){
            msgElem = getInterlocutorMsg(msgText);
        }
        else{
            msgElem = getUserMsg(msgText);
        }
        $('#indexCurrentChatMessagesList').append(msgElem);
        scrollMessages();
    }
    changeLastMsg(chatInfo.user_id || chatInfo.chat_id, msgText);
}

// Данный символ используется в тех местах, где должен был быть текст, но его
// там не оказалось (костыль в общем)
const voidChar = " ";  // Это не пробел

var chatsData = new Map();

var removedAdditionsFiles = [];

// Функция проматывает список сообщений до самого низа
function scrollMessages(){
    let elem = $('#indexCurrentChatMessagesList')
    elem.scrollTop(elem[0].scrollHeight);
}


// Функция переключает отображение текущего чата и списка чатов
function switchChat(){
    $('#indexCurrentChatBlock').style('display', 'block');
    let userID = $(this).attr('data-user-id');
    if (userID){
        let chatData = chatsData.get(userID);
        $('#indexChatHeaderUserName').text(chatData.user_name || '-');
        $('#indexCurrentChatUserAvatar').attr(
            'src', new URL(chatData.avatar, uploadsURL)
        );
        loadMessages(userID);
    }
    let curChatElem = $('#indexCurrentChatBlock');
    let chatsElem = $('#indexChatsBlock');
    if (curChatElem.hasClass('d-none')){
        curChatElem.removeClass('d-none');
        chatsElem.addClass('d-none');
        setTimeout(scrollMessages, 100);
    }
    else {
        let lgBreakpoint = parseInt($(':root').css('--grid-breakpoints-lg'));
        if ($(window).width() < lgBreakpoint){
            curChatElem.addClass('d-none');
            chatsElem.removeClass('d-none');
        }
    }
}

// При прикреплении приложения к сообщению функция прячет старый input и
// показывает новый, меняя ему id и name, обнуляя val
function addNewField(){
    let elem = $(this);
    let baseId = elem.attr('data-base-id');
    let fieldsCount = $(`input[data-base-id=${baseId}]`).length;
    let newId = baseId + fieldsCount;
    let newElem = elem.clone()
                    .attr('id', newId)
                    .attr('name', newId)
                    .attr('val', null)
    elem.after($(newElem));
    elem.hide();
    newElem.on('change', addNewField, appendAddition)
}

function appendAddition(){
    let elem = $(this);
//    $('#indexAdditionLoadingModal').modal('show');
    elem.each(function(index, field){
        let fieldType = field.getAttribute('data-base-id');
        forEach(field.files, function(file, i, arr){
                if (fieldType == 'indexPhotoAddition'){
                    let reader = new FileReader();
                    reader.onload = function(e) {
                        let photo = $(photoAdditionHTML.format({
                            file_name: file.name,
                            last_modified: file.lastModified,
                            src: e.target.result
                        }));
                        $('#indexAdditionsPhotoList').append(photo);
                        photo.click(removeAddition);
                    }
                    reader.readAsDataURL(file);
                }
                else{
                    let addition = $(additionHTML.format({
                        file_name: file.name,
                        last_modified: file.lastModified
                    }));
                    $('#indexAdditionsList').append(addition);
                    addition.click(removeAddition);
                }
        });
    });
}

function removeAddition(){
    let addition = $(this)
    let fileName = addition.attr('data-file-name');
    let lastModified = addition.attr('data-last-modified');
    $('input.index-addition-field').each(function(i, item){
        if (item.files){
            forEach(item.files, function(file, j, files){
                if (file.name == fileName && file.lastModified == lastModified){
                    removedAdditionsFiles.push(file);
                    addition.remove();
                    return;
                }
            });
        }
    });
    return false;
}

function getChat(options){
    let chat = $(chatHTML.format(options));
    return chat.click(switchChat);
}

function appendChat(options){
    $('#indexMessagesChatsListGroup').append(getChat(options));
}

function getUserMsg(text){
    return $(userMsgHTML.format({text: text || voidChar}));
}

function getInterlocutorMsg(text){
    return $(interlocutorMsgHTML.format({text: text || voidChar}));
}

function changeLastMsg(ID, text){
    let chat = $(
        `.index-chats-chat-item[data-user-id="${ID}"],
        .index-chats-chat-item[data-chat-id="${ID}"]`
    );
    chat.find('.index-chat-last-msg').text(text || voidChar);
}

function loadMessages(userID){
    let messagesList = $('#indexCurrentChatMessagesList');
    messagesList.empty();
    $.ajax({
        url: apiServerMessagesListURL,
        data: {receiver_id: userID},
        success(data){
            data.messages.forEach(function(msg, i, messages){
                let msgElem;
                if (msg.sender_id == currentUserID){
                    msgElem = getUserMsg(msg.text);
                }
                else{
                    msgElem = getInterlocutorMsg(msg.text);
                }
                messagesList.append(msgElem);
            });
            scrollMessages();
        }
    });
}

function loadChatData(userID){
    $.ajax({
        url: apiServerChatsURL,
        data: {chat_with: userID},
        success(data){
            let chatData = $.extend({
                chat_with: userID,
            }, chatsData.get(userID, {}), data.chat);
            chatsData.set(userID, chatData);
            $('.index-chats-chat-item').attr('data-chat-id', data.chat.id);
        }
    });
}

function loadChats(){
    $.ajax({
        url: apiServerMessagesListURL,
        success(data){
            data.messages.forEach(function(msg, i, messages){
                chatsData.set(msg.chat_with || msg.chat_id,
                              {last_msg: msg.text, chat_id: msg.chat_id});
            });
            $.ajax({
                url: apiServerUsersFriendsListURL,
                success(data){
                    data.friends.forEach(function(friend, i, arr){
                        let curChatData = chatsData.get(friend.user_id, {});
                        let chatData = $.extend({
                            user_id: friend.user_id,
                            user_name: fullUserName(friend),
                            last_msg: voidChar,
                            avatar: new URL(friend.avatar, uploadsURL)
                        }, curChatData);
                        chatsData.set(friend.user_id, chatData);
                        appendChat(chatData);
                        if (!curChatData){
                            loadChatData(friend.user_id);
                        }
                    });
                }
            })
        }
    });
}

function currentChatInfo(){
    let chat = $('.index-chats-chat-item.active');
    if (chat){
        let userID = chat.attr('data-user-id');
        let chatID = chat.attr('data-chat-id');
        return {user_id: userID, chat_id: chatID};
    }
    return {};
}


function searchChat(){
    let searchText = $('#indexChatsAndFriendsSearchInput').val();
    let chatsList = $('#indexMessagesChatsListGroup');
    chatsList.children().each(function(i, chatElem){
        chatElem = $(chatElem);
        if (chatElem.text().includes(searchText)){
            chatElem.show();
        }
        else{
            chatElem.hide();
        }
    });
}


// Следующий код выполнится после загрузки DOM
$(document).ready(function (){
    freezeScroll('#indexCurrentChatMessagesList', '#indexChatsList');

    let messageInput = $('#indexMessageInput')
    // Убираем всё форматирование из текста, который вставляется в поле ввода
    // сообщения
    messageInput.on('paste', function (e) {
        e.preventDefault();
        let text = (e.originalEvent || e).clipboardData.getData('text/plain');
        window.document.execCommand('insertText', false, text);
    });

    // При нажатии Ctrl + Enter вставляем перенос строки, а при нажатии Enter
    // отправляем сообщение
    messageInput.keydown(function (e) {
        if(e.keyCode == 13){
            if (e.ctrlKey){
                window.document.execCommand('insertText', false, '\n');
            }
            else {
                let msgText = messageInput.text();
                if (!msgText){
                    return false;
                }
                let chatInfo = currentChatInfo();
                if (chatInfo){
                    let chatSendInfo = {};
                    if (chatInfo.user_id){
                        chatSendInfo.receiver_id = chatInfo.user_id;
                    }
                    else if (chatInfo.chat_id){
                        chatSendInfo.chat_id = chatInfo.chat_id;
                    }
                    messageInput.text('');
                    $.ajax({
                        url: apiServerMessagesURL,
                        method: "POST",
                        dataType: 'json',
                        data: $.extend(chatSendInfo,
                                       {text: msgText}),
                        success(data){
                        }
                    });
                    return false;
                }
            }
        }
    });

    let messagesHeaderHeight = $('.index-messages-header').css('height');

    // При изменении размера блока с полем ввода сообщения меняем размер блока
    // с сообщениями
    let curInputHeight = $('#indexMessageBlock').css('height');
    let prevInputHeight = null;
    new ResizeSensor($('#indexMessageBlock'), function() {
        prevInputHeight = curInputHeight;
        curInputHeight = $('#indexMessageBlock').css('height');
        $('#indexCurrentChatMessagesList').css(
            'height',
            `calc(100% - ${messagesHeaderHeight} - ${curInputHeight})`
        );
        // Скроллим сообщения вверх при показе списка стикеров, чтобы сообщения
        // сохраняли свои позиции
        let messagesListElem = $('#indexCurrentChatMessagesList');
        if (messagesListElem[0].scrollHeight - messagesListElem.scrollTop() ==
                messagesListElem[0].clientHeight){
            // Из-за бага, либо моего недопонимания JS и JQuery, во время
            // закрытия окна со стикерами, при проскроленных до самого низа
            // сообщениях, сообщения не прокручиваются вниз. Для исправления
            // этого недоразумения я полностью проскроливаю сообщения вручную
            messagesListElem.scrollTop(messagesListElem[0].scrollHeight);
            return;
        }
        let scrollDistance = (parseInt(curInputHeight) -
                                      (parseInt(prevInputHeight)));
        messagesListElem.scrollTop(
            messagesListElem.scrollTop() + scrollDistance
        );
    });

    $('#indexChatBackBtn').on('click', switchChat);

    let stickerBlock = $('#indexStickersBlock')
    $('#indexAttachStickerBtn').on('click', () => switchDisplay(stickerBlock));

    $('.index-addition-field').on('change', addNewField, appendAddition);

    loadChats();

    $('#indexCurrentChatBlock').style('display', 'none', 'important');

    $('#indexSearchForm').on('submit', searchChat);
})

// Следующий код выполнится после полной загрузки документа
$(window).on("load", function() {
    // Через 100 мс запускаем функцию промотки сообщений до самого низа. Если
    // вызывать функцию без задержки, то страница не будет промотана (по всей
    // видимости это происходит из-за того, что некоторые функции выше не
    // успевают отработать).
    setTimeout(scrollMessages, 100);
});