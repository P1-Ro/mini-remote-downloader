/*global
Materialize
*/
(function () {
    $(document).on("submit", "form", function (evt) {

        evt.stopPropagation();
        evt.preventDefault();

        const url = $("#url").val();
        const name = $("#name").val();
        const cat = $("#cat").val();
        const data = {
            url
        };
        if (name) {
            data["name"] = name;
        }
        if (cat) {
            data["category"] = cat;
        }

        $.ajax({
            url: "/download/",
            type: "POST",
            dataType: "json",
            contentType: "application/json;charset=utf-8",
            data: JSON.stringify(data)
        }).done(function () {
            Materialize.toast("File started downloading", 5000, "download green");
        }).fail(function (res) {
            Materialize.toast(res.responseJSON.reason, 5000, "download red");
        });
    });
}).call();