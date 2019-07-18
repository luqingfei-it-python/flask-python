function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

function logout(){
    $.ajax({
        url:"/api/v1.0/session",
        type:"delete",
        dataType: "json",
        headers: {
            "X-CSRFToken": getCookie("csrf_token")  //获取当前浏览器中cookie中的csrf_token
        },
        success:function (resp) {
            if (resp.errnum == "0"){
                location.href = "/index.html";
            }
        }
    })
}

$(document).ready(function(){
    $.get("/api/v1.0/user", function(data) {
        if ("4101" == data.errnum) {
            location.href = "/login.html";
        }
        else if ("0" == data.errnum) {
            $("#user-name").html(data.data.name);
            $("#user-mobile").html(data.data.mobile);
            if (data.data.avatar_url) {
                $("#user-avatar").attr("src", data.data.avatar_url);
            }
        }
    }, "json");
});