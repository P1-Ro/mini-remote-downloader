(function () {

    $(document).on("submit", "form", function (evt) {

        evt.stopPropagation();
        evt.preventDefault();

        var url = $("#url").val();
        var name = $("#name").val();
        var cat = $("#cat").val();

        var data = {
            url: url
        };
        if(name){
            data["name"] = name;
        }
        if(cat){
            data["category"] = cat;
        }

        $.ajax({
            url: "/download/",
            type: "POST",
            dataType: "json",
            contentType: "application/json;charset=utf-8",
            data: JSON.stringify(data)
        }).done(function(res){
             Materialize.toast('File started downloading', 5000, 'download download-success')
        }).fail(function(res){
             Materialize.toast(res.responseJSON.reason, 5000, 'download download-error')
        })
    });

}).call();