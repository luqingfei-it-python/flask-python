$(document).ready(function(){
    $.get("/api/v1.0/users/auth", function(data){
        if ("4101" == data.errnum) {
            location.href = "/login.html";
        } else if ("0" == data.errnum) {
            if (!(data.data.real_name && data.data.id_card)) {
                $(".auth-warn").show();
                return;
            }
            $.get("/api/v1.0/user/houses", function(resp){
                if (resp.errnum == "0") {
                    $("#houses-list").html(template("houses-list-tmpl", {"houses": resp.data}));
                }else {
                    $("#houses-list").html(template("houses-list-tmpl", {"houses": []}));
                }
            }, "json");
        }
    });
});