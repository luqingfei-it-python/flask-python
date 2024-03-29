function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

$(document).ready(function() {
    $("#mobile").focus(function(){
        $("#mobile-err").hide();
    });
    $("#password").focus(function(){
        $("#password-err").hide();
    });
    $(".form-login").submit(function(e){
        e.preventDefault();
        mobile = $("#mobile").val();
        passwd = $("#password").val();
        if (!mobile) {
            $("#mobile-err span").html("请填写正确的手机号！");
            $("#mobile-err").show();
            return;
        } 
        if (!passwd) {
            $("#password-err span").html("请填写密码!");
            $("#password-err").show();
            return;
        }
        var data = {
            mobile:mobile,
            password:passwd
        };

        var jsonData = JSON.stringify(data);
        $.ajax({
            url:"/api/v1.0/sessions",
            type:"POST",
            data: jsonData,
            contentType: "application/json",
            dataType: "json",
            headers: {
            "X-CSRFToken": getCookie("csrf_token")  //获取当前浏览器中cookie中的csrf_token
        },
            success: function (data) {
                if (data.errnum == "0") {
                    location.href = "/";
                }
                else {
                    $("#password-err span").html(data.errmsg);
                    $("#password-err").show();
                }
            }
        });
    });
});