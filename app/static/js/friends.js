let currentFriendsSearchIndex = 0;
let friendsSearchLimit = 20;
let loadNewOn = 10;
let lastSearchRequest = "";
let userFriendsIDs = [];
let usersData = new Map();

function actionWithFriend(friend_id, action, options={}){
    $.ajax($.extend({
        url: apiServerUsersFriendsURL,
        method: "POST",
        data: {action: action, friend_id: friend_id}
    }, options));
}

function getFriendCard(userID){
    let user = usersData.get(userID);
    let friendCard = $(friendHTML.format({
        friend_id: userID, friend_name: fullUserName(user),
        avatar: new URL(user.avatar, uploadsURL)
    }));
    friendCard.find('.friends-delete-friend-btn').click(deleteFriend);
    return friendCard;
}

function getDeniedCard(userID){
    let user = usersData.get(userID);
    let deniedCard = $(friendDeniedHTML.format({
        friend_id: userID, friend_name: fullUserName(user),
        avatar: new URL(user.avatar, uploadsURL)
    }));
    deniedCard.find('.friends-add-friend-btn').click(addDeniedFriend);
    return deniedCard;
}

function getNewFriendCard(userID, userName){
    let user = usersData.get(userID);
    let newFriendCard = $(friendNewHTML.format({
        friend_id: userID,
        friend_name: fullUserName(user),
        avatar: new URL(user.avatar, uploadsURL)
    }));
    newFriendCard.find('.friends-add-friend-btn').click(addNewFriend);
    return newFriendCard;
}

function getRequestCard(userID, userName){
    let user = usersData.get(userID);
    let requestCard = $(friendRequestHTML.format({
        friend_id: userID,
        friend_name: fullUserName(user),
        avatar: new URL(user.avatar, uploadsURL)
    }));
    requestCard.find('.friends-add-friend-btn').click(acceptFriendRequest);
    requestCard.find('.friends-deny-friend-btn').click(denyFriend);
    return requestCard;
}

function getOutgoingCard(userID, userName){
    let user = usersData.get(userID);
    let outgoingCard = $(friendOutgoingHTML.format({
        friend_id: userID,
        friend_name: fullUserName(user),
        avatar: new URL(user.avatar, uploadsURL)
    }));
    outgoingCard.find('.friends-cancel-request-btn').click(cancelFriendRequest);
    return outgoingCard;
}

function cancelFriendRequest(){
    let userID = this.getAttribute('data-user-id');
    let outgoingCard = $(`#friendsOutgoingList
        .friends-friend-card[data-user-id="${userID}"]`);
    $.ajax({
        url: apiServerUsersFriendsURL,
        method: "DELETE",
        data: {friend_id: userID},
        success(data){
            outgoingCard.remove();
            userFriendsIDs.remove(userID);
        }
    });
}

function deleteFriend(){
    let userID = this.getAttribute('data-user-id');
    let friendCard = $(`#friendsFriendsList
        .friends-friend-card[data-user-id="${userID}"]`);
    actionWithFriend(userID, 'deny', {
        success(data){
            let deniedCard = getDeniedCard(userID);
            friendCard.remove();
            $('#friendsDeniedList').append(deniedCard);
        }
    });
}

function acceptFriendRequest(){
    let userID = this.getAttribute('data-user-id');
    let requestCard = $(`#friendsRequestsList
        .friends-friend-card[data-user-id="${userID}"]`);
    actionWithFriend(userID, 'accept', {
        success(data){
            let friendCard = getFriendCard(userID);
            requestCard.remove();
            $('#friendsFriendsList').append(friendCard);
        }
    });
}

function addDeniedFriend(){
    let userID = this.getAttribute('data-user-id');
    let deniedCard = $(`#friendsDeniedList
        .friends-friend-card[data-user-id="${userID}"]`);
    actionWithFriend(userID, 'accept', {
        success(data){
            let friendCard = getFriendCard(userID);
            deniedCard.remove();
            $('#friendsFriendsList').append(friendCard);
        }
    });
}

function denyFriend(){
    let userID = this.getAttribute('data-user-id');
    let requestCard = $(`#friendsRequestsList
        .friends-friend-card[data-user-id="${userID}"]`);
    actionWithFriend(userID, 'deny', {
        success(data){
            let deniedCard = getDeniedCard(userID);
            requestCard.remove();
            $('#friendsDeniedList').append(deniedCard);
        }
    });
}

function addNewFriend(){
    let userID = this.getAttribute('data-user-id');
    let newFriendCard = $(`#friendsSearchList
        .friends-friend-card[data-user-id="${userID}"]`);
    actionWithFriend(userID, 'add', {
        success(data){
            newFriendCard.remove();
            let outgoingCard = getOutgoingCard(userID);
            $('#friendsOutgoingList').append(outgoingCard);
            userFriendsIDs.push(userID);
        }
    });
}

function searchFriends(){
    $('#friendsSearchList').empty();
    let searchReq = $('#friendsSearchInput').val();
    loadFriendsFromSearch(searchReq);
}

function loadFriendsFromSearch(searchReq=lastSearchRequest){
    if (lastSearchRequest != searchReq){
        currentFriendsSearchIndex = 0;
    }
    let friendsSearchList = $('#friendsSearchList');
    $.ajax({
        url: apiServerUsersListURL,
        data: {search_request: searchReq,
               start: currentFriendsSearchIndex,
               limit: friendsSearchLimit},
        success(data){
            currentFriendsSearchIndex += friendsSearchLimit;
            data.users.forEach(function(user, i, arr){
                if (currentUserID == user.user_id ||
                    userFriendsIDs.includes(user.user_id)){
                    return;
                }
                usersData.set(user.user_id, user);
                let newFriendCard = getNewFriendCard(user.user_id);
                if (i + 1 == loadNewOn){
                    newFriendCard.appear(loadFriendsFromSearch, {once: true});
                }
                friendsSearchList.append(newFriendCard);
            });
        }
    });
}

// Функция загружает всю необходимую информацию о друзьях
function loadFriends(){
    let friendsFriendsList = $('#friendsFriendsList');
    let friendsDeniedList = $('#friendsDeniedList');
    let friendsRequestsList = $('#friendsRequestsList');
    let friendsOutgoingList = $('#friendsOutgoingList');
    $.ajax({
        url: apiServerUsersFriendsListURL,
        success(data){
            data.friends.forEach(function(friend, i, arr){
                usersData.set(friend.user_id, friend);
                let friendCard = getFriendCard(friend.user_id);
                friendsFriendsList.append(friendCard);
                userFriendsIDs.push(friend.user_id);
            });
        }
    });
    $.ajax({
        url: apiServerUsersFriendsListURL,
        data: {type: "outgoing"},
        success(data){
            data.friends.forEach(function(friend, i, arr){
                usersData.set(friend.user_id, friend);
                let outgoingCard = getOutgoingCard(friend.user_id);
                friendsOutgoingList.append(outgoingCard);
                userFriendsIDs.push(friend.user_id);
            });
        }
    });
    $.ajax({
        url: apiServerUsersFriendsListURL,
        data: {type: "incoming"},
        success(data){
            data.friends.forEach(function(friend, i, arr){
                usersData.set(friend.user_id, friend);
                if (friend.is_accepted === false){
                    let deniedCard = getDeniedCard(friend.user_id);
                    friendsDeniedList.append(deniedCard);
                }
                else if (friend.is_accepted === null){
                    let requestCard = getRequestCard(friend.user_id);
                    friendsRequestsList.append(requestCard);
                }
                userFriendsIDs.push(friend.user_id);
            });
        }
    });
}

$(function(){
    $('.friends-delete-friend-btn').click(deleteFriend);

    $('#friendsRequestsList .friends-add-friend-btn').click(
        acceptFriendRequest
    );

    $('#friendsDeniedList .friends-add-friend-btn').click(addDeniedFriend);

    $('#friendsRequestsList .friends-deny-friend-btn').click(denyFriend);

    $('#friendsSearchForm').submit(searchFriends);

    loadFriends();

    $('#friendsSearchTab').one('show.bs.tab', () => loadFriendsFromSearch());
});