/*global
Materialize
*/
(function () {

    const audioOnly = $("#audioOnly");
    const url = $("#url");
    let audioOnlyVisible = false;
    audioOnly.css({top: "-=20px"});

    function resetAudioCheckBox() {
        audioOnly.animate({
            opacity: 0,
            top: "-=30px"
        });
        audioOnlyVisible = false;
    }

    function enableButton(spinner, button) {
        spinner.addClass("hide");
        button.disabled = false;
    }

    function clearForm(url, name, cat, chckbx) {
        url.val("");
        name.val("");
        cat.val("");
        chckbx.prop("checked", false);
        resetAudioCheckBox();
    }

    url.on("input", function () {
        let val = url.val();
        if (val.indexOf("youtu") !== -1 && !audioOnlyVisible) {

            audioOnly.animate({
                opacity: 1,
                top: "+=30px"
            });
            audioOnlyVisible = true;
        } else {
            resetAudioCheckBox();
        }
    });

    $(document).on("submit", "form", function (evt) {
        const spinner = $(".ultra-small");
        const button = $("#submit")[0];
        button.disabled = true;

        evt.stopPropagation();
        evt.preventDefault();

        const urlField = $("#url");
        const nameField = $("#name");
        const catField = $("#cat");
        const audioField = $("#audio");


        const url = urlField.val();
        const name = nameField.val();
        const cat = catField.val();
        const audio = audioField.is(":checked");

        const data = {
            url
        };
        if (name) {
            data["name"] = name;
        }
        if (cat) {
            data["category"] = cat;
        }
        if (audio) {
            data["audioOnly"] = true;
        }


        spinner.removeClass("hide");

        $.ajax({
            url: "/download/",
            type: "POST",
            dataType: "json",
            contentType: "application/json;charset=utf-8",
            data: JSON.stringify(data)
        }).done(function () {
            Materialize.toast("File started downloading", 5000, "download green");
            clearForm(urlField, nameField, catField, audioField);
            enableButton(spinner, button);

        }).fail(function (res) {
            Materialize.toast(res.responseJSON.reason, 7000, "download red");
            enableButton(spinner, button);
        });
    });

}).call();