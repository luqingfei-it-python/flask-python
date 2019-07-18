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

$(document).ready(function () {
    // $.get("/api/v1.0/users/name", function(data){
    //     if ("4101" == data.errcode) {
    //         location.href = "/login.html";
    //     }
    //     else if ("0" == data.errcode) {
    //         $("#user-name").val(data.data.name);
    //         if (data.data.avatar) {
    //             $("#user-avatar").attr("src", data.data.avatar);
    //         }
    //     }
    // });
    $("#form-avatar").submit(function (e) {
        // 组织浏览器对于表单的默认行为
        e.preventDefault();
        $(this).ajaxSubmit({
            url: "/api/v1.0/users/avatar",
            method: "post",
            dataType: "json",
            headers: {
                "X-CSRFToken": getCookie("csrf_token")  //获取当前浏览器中cookie中的csrf_token
            },
            success: function (resp) {
                if (resp.errnum == "0"){
                    //上传成功
                    var avatarUrl = resp.data.avatar_url;
                    $("#user-avatar").attr("src", avatarUrl);
                }else {
                    alert(resp.errmsg);
                }

            }
        })
    });


    $("#form-name").submit(function(e){
        e.preventDefault();
        // console.log(name);
        var name = $("#user-name").val();
        var data = {
            user_name:name
        };
        var jsonData = JSON.stringify(data);
        $.ajax({
            url:"/api/v1.0/users/name",
            type:"PUT",
            data: jsonData,
            contentType: "application/json",
            dataType: "json",
            headers: {
                "X-CSRFToken": getCookie("csrf_token")  //获取当前浏览器中cookie中的csrf_token
            },
            success: function (data) {
                if ("0" == data.errnum) {
                    $(".error-msg").hide();
                    showSuccessMsg(); // 展示保存成功的页面效果
                } else if ("4001" == data.errnum) {
                    $(".error-msg").show();
                } else if ("4101" == data.errnum) { // 4101代表用户未登录，强制跳转到登录页面
                    location.href = "/login.html";
                }
            }
        });
    })
});

