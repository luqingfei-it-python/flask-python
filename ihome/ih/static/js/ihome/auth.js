function showSuccessMsg() {
    $('.popup_con').fadeIn('fast', function() {
        setTimeout(function(){
            $('.popup_con').fadeOut('fast',function(){}); 
        },1000) 
    });
}

function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

$(document).ready(function(){
    $.get("/api/v1.0/users/auth", function(data){
        if ("4101" == data.errnum) {
            location.href = "/login.html";
        }
        else if ("0" == data.errnum) {
            if (data.data.real_name && data.data.id_card) {
                $("#real-name").val(data.data.real_name);
                $("#id-card").val(data.data.id_card);
                $("#real-name").prop("disabled", true);
                $("#id-card").prop("disabled", true);
                $("#form-auth>input[type=submit]").hide();
            }
        }
    }, "json");
    $("#form-auth").submit(function(e){
        e.preventDefault();
        var real_name = $("#real-name").val();
        var id_card = $("#id-card").val();
        if (real_name == "" || id_card == "") {
            $(".error-msg").show();
        }
        var data = {
            "real_name": real_name,
            "id_card": id_card
        };
        // $(this).serializeArray().map(function(x){data[x.name] = x.value;});
        var jsonData = JSON.stringify(data);
        $.ajax({
            url:"/api/v1.0/users/auth",
            type:"POST",
            data: jsonData,
            contentType: "application/json",
            dataType: "json",
            headers: {
            "X-CSRFToken": getCookie("csrf_token")  //获取当前浏览器中cookie中的csrf_token
        },
            success: function (data) {
                if ("0" == data.errnum) {
                    $(".error-msg").hide();
                    showSuccessMsg();
                    $("#real-name").prop("disabled", true);
                    $("#id-card").prop("disabled", true);
                    $("#form-auth>input[type=submit]").hide();
                }
            }
        });
    })

});

