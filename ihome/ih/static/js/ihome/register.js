function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

var imageCodeId = "";

function generateUUID() {
    var d = new Date().getTime();
    if(window.performance && typeof window.performance.now === "function"){
        d += performance.now(); //use high-precision timer if available
    }
    var uuid = 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
        var r = (d + Math.random()*16)%16 | 0;
        d = Math.floor(d/16);
        return (c=='x' ? r : (r&0x3|0x8)).toString(16);
    });
    return uuid;
}

function generateImageCode() {
    imageCodeId = generateUUID();
    var  url = "/api/v1.0/image_code/" + imageCodeId;
    $(".image-code img").attr("src", url);
}

function sendSMSCode() {
    $(".phonecode-a").removeAttr("onclick");
    var mobile = $("#mobile").val();
    if (!mobile) {
        $("#mobile-err span").html("请填写正确的手机号！");
        $("#mobile-err").show();
        $(".phonecode-a").attr("onclick", "sendSMSCode();");
        return;
    }
    var imageCode = $("#imagecode").val();
    if (!imageCode) {
        $("#image-code-err span").html("请填写验证码！");
        $("#image-code-err").show();
        $(".phonecode-a").attr("onclick", "sendSMSCode();");
        return;
    }
    // $.get("/api/smscode", {mobile:mobile, code:imageCode, codeId:imageCodeId},
    //     function(data){
    //         if (0 != data.errno) {
    //             $("#image-code-err span").html(data.errmsg);
    //             $("#image-code-err").show();
    //             if (2 == data.errno || 3 == data.errno) {
    //                 generateImageCode();
    //             }
    //             $(".phonecode-a").attr("onclick", "sendSMSCode();");
    //         }
    //         else {
    //             var $time = $(".phonecode-a");
    //             var duration = 60;
    //             var intervalid = setInterval(function(){
    //                 $time.html(duration + "秒");
    //                 if(duration === 1){
    //                     clearInterval(intervalid);
    //                     $time.html('获取验证码');
    //                     $(".phonecode-a").attr("onclick", "sendSMSCode();");
    //                 }
    //                 duration = duration - 1;
    //             }, 1000, 60);
    //         }
    // }, 'json');

    //构造向后端请求的参数
    var req_data = {
        image_code: imageCode,
        image_code_id: imageCodeId
    };

    $.get("/api/v1.0/sms_code/" + mobile, req_data, function (data) {
        if (data.errnum == "0") {
            var num = 60;
            var timer = setInterval(function () {
                if (num > 1) {
                    $(".phonecode-a").html(num + "秒");
                    num -= 1;
                } else {
                    $(".phonecode-a").html("获取验证码");
                    $(".phonecode-a").attr("onclick", "sendSMSCode();");
                    clearInterval(timer);
                }
            }, 1000, 60)
        } else {
            alert(data.errmsg);
            $(".phonecode-a").attr("onclick", "sendSMSCode();")
        }
    });
}
//     var data = {mobile:mobile, piccode:imageCode, piccode_id:imageCodeId};
//     $.ajax({
//         url: "/api/smscode",
//         method: "POST",
//         headers: {
//             "X-XSRFTOKEN": getCookie("_xsrf"),
//         },
//         data: JSON.stringify(data),
//         contentType: "application/json",
//         dataType: "json",
//         success: function (data) {
//             // data = {
//             //     errcode
//             //     errmsg
//             // }
//             if ("0" == data.errcode) {
//                 var duration = 60;
//                 var timeObj = setInterval(function () {
//                     duration = duration - 1;
//                     $(".phonecode-a").html(duration+"秒");
//                     if (1 == duration) {
//                         clearInterval(timeObj)
//                         $(".phonecode-a").html("获取验证码");
//                         $(".phonecode-a").attr("onclick", "sendSMSCode();")
//                     }
//                 }, 1000, 60)
//             } else {
//                 $("#image-code-err span").html(data.errmsg);
//                 $("#image-code-err").show();
//                 $(".phonecode-a").attr("onclick", "sendSMSCode();")
//                 if (data.errcode == "4002" || data.errcode == "4004") {
//                     generateImageCode();
//                 }
//             }
//         }
//     })
//
// }

$(document).ready(function() {
    generateImageCode();
    $("#mobile").focus(function(){
        $("#mobile-err").hide();
    });
    $("#imagecode").focus(function(){
        $("#image-code-err").hide();
    });
    $("#phonecode").focus(function(){
        $("#phone-code-err").hide();
    });
    $("#password").focus(function(){
        $("#password-err").hide();
        $("#password2-err").hide();
    });
    $("#password2").focus(function(){
        $("#password2-err").hide();
    });

    // 当用户点击表单提交按钮时执行自己定义的函数
    $(".form-register").submit(function(e){
        // 组织浏览器对于表单的默认行为
        e.preventDefault();

        // 校验用户填写的参数
        mobile = $("#mobile").val();
        phoneCode = $("#phonecode").val();
        passwd = $("#password").val();
        passwd2 = $("#password2").val();
        if (!mobile) {
            $("#mobile-err span").html("请填写正确的手机号！");
            $("#mobile-err").show();
            return;
        }
        if (!phoneCode) {
            $("#phone-code-err span").html("请填写短信验证码！");
            $("#phone-code-err").show();
            return;
        }
        if (!passwd) {
            $("#password-err span").html("请填写密码!");
            $("#password-err").show();
            return;
        }
        if (passwd != passwd2) {
            $("#password2-err span").html("两次密码不一致!");
            $("#password2-err").show();
            return;
        }

        // 声明一个要保存结果的变量
        var resp_data = {
            mobile: mobile,
            sms_code: phoneCode,
            password: passwd,
            password2:passwd2
        };

        // 把data变量转为json格式字符串
        var json_data = JSON.stringify(resp_data);
        //向后端发送请求
        $.ajax({
            url: "/api/v1.0/users",
            method: "POST",
            data: json_data,
            contentType: "application/json", // 告诉后端服务器，发送的请求数据是json格式的
            dataType: "json",   // 告诉前端，收到的响应数据是json格式的
            headers: {
            "X-CSRFToken": getCookie("csrf_token")  //获取当前浏览器中cookie中的csrf_token
            },
            success: function (data) {
                if (data.errnum == "0") {
                    location.href = "/";
                } else {
                    alert(data.errmsg);
                }

            }
        })
    });
});



// $(".form-register").serializeArray()
//     li = [Object, Object, Object, Object, Object]
//     [0:Object
//         name: "mobile"
//         value: "18111111111"
//
//     1:Object
//         name: "phonecode"
//         value: "1234"
//             ...
//     ]
//
//     {
//         mobile: 181111111,
//             phonecode: 1234
//     }
//
//     $(".form-register").serializeArray().map(action)
//
// for ele in li:
//     fun(ele)
//
//
//     dict = {}
//
//     function action(x){
//         x.name
//         x.value
//         dict[x.name] = x.value
//     }




























