$(document).ready(function(){
    // Убираем readonly с полей info_form при нажатии на "изменить", и
    // показываем кнопку сохранить изменения
    $('#profileChangeInfoBtn').click(function(){
        $(this).hide()
        $('.profile-info-field').attr('readonly', false);
        $('#info-submit').show();
        $('#profileAvatarFileField').show();
    });

    // Тоже самое для security_form
    $('#profileChangeSecurityBtn').click(function(){
        $(this).hide()
        $('.profile-security-field').attr('readonly', false);
        $('#security-submit').show();
    });

    // Показываем новую загруженную аватарку
    $('#profileAvatarFileField').on('change', function(){
        let file = $('#info-avatar')[0].files[0];
        let reader = new FileReader();
        reader.onload = function(e) {
            $('#profileAvatarImg').attr('src', e.target.result);
        }
        reader.readAsDataURL(file);
    });
})