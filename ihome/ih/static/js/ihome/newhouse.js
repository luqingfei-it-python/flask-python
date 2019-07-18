function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

$(document).ready(function(){
    $.get("/api/v1.0/areas", function (resp) {
        // console.log(resp.errnum);
        if (resp.errnum == "0") {
            var areas = resp.data;
            // 使用js模板
            html = template("area-tmpl", {areas: areas});
            $("#area-id").html(html);
            // console.log(html);
            // for (i=0; i<areas.length; i++) {
            //     var area = areas[i];
            //     $("#area-id").append('<option value="'+area.aid+'">'+area.aname+'</option>');
            // }
        }else {
            alert(resp.errmsg);
        }
    }, "json");


    $("#form-house-info").submit(function(e){
        e.preventDefault();
        var data = {};
        $("#form-house-info").serializeArray().map(function(x){data[x.name] = x.value;});
        var facility = []; // 用来保存勾选了的设施编号
        // 通过jquery筛选出勾选了的页面元素
        // 通过each方法遍历元素
        $(":checked[name=facility]").each(function(index, x){facility[index] = $(x).val()});
        data.facility = facility;
        var jsonData = JSON.stringify(data);
        $.ajax({
            url:"/api/v1.0/houses/info",
            type:"POST",
            data: jsonData,
            contentType: "application/json",
            dataType: "json",
            headers: {
                    "X-CSRFToken": getCookie("csrf_token")  //获取当前浏览器中cookie中的csrf_token
                },
            success: function (data) {
                if ("4101" == data.errnum) {
                    location.href = "/login.html";
                } else if ("0" == data.errnum) {
                    $("#form-house-info").hide();
                    $("#form-house-image").show();
                    $("#house-id").val(data.data.house_id);
                }else {
                    alert(data.errmsg)
                }
            }
        });
    });
    $("#form-house-image").submit(function(e){
        e.preventDefault();
        $(this).ajaxSubmit({
            url: "api/v1.0/houses/image",
            type: "POST",
            dataType: "json",
            headers: {
                    "X-CSRFToken": getCookie("csrf_token")  //获取当前浏览器中cookie中的csrf_token
                },
            success: function (resp) {
                if (resp.errnum == "4101"){
                    location.href = "/login.html";
                }else if(resp.errnum == "0"){
                    $(".house-image-cons").append('<img src="' + resp.data.image_url +'">');
                }else {
                    alert(resp.errmsg);
                }
            }
        })
    });
});