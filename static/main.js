$(document).ready(function () {


    $("#new-zoo-check").on("click", function () {
        if ($(this).is(":checked")) {
            $('.new-zoo-container').css("display", "block");
            $('.choose-zoo-container').css("display", "none");

        }
        else {
            $('.new-zoo-container').css("display", "none");
            $('.choose-zoo-container').css("display", "block");

        }
    })

    $('#flexCheckDate').on("click", function () {
        if ($(this).is(":checked")) {
            $('#field-set-date').removeAttr("disabled");
        }
        else {
            $('#field-set-date').attr('disabled', 'True');
        }
    })

    // скрипт вычисляющий текущую дату и вставляющий ее в страницу
    $(window).on('load', function () {
        // code here
        var d = new Date();

        var month = d.getMonth() + 1;
        var day = d.getDate();

        var output = d.getFullYear() + '-' +
            (month < 10 ? '0' : '') + month + '-' +
            (day < 10 ? '0' : '') + day;
        console.log(output);
        $('#inputDate').attr('value', output)
    });

    // скрипт вычисляющий текущее время и вставляющий его в страницу
    $(window).on('load', function () {
        var dt = new Date();
        var output = dt.getHours() + ":" + dt.getMinutes();
        console.log(output)
        $('#inputTime').attr('value', output)
    });


})
