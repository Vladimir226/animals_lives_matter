$(document).ready(function(){
    // вешаем маску на телефон
    $('.phone-field').inputmask("+7(999)999-9999");

    // добавляем правило для валидации телефона
    jQuery.validator.addMethod("checkMaskPhone", function (value, element) {
        return /\+\d{1}\(\d{3}\)\d{3}-\d{4}/g.test(value);
    });

    // получаем нашу форму по class
    var form = $('.form-request');

    // включаем валидацию в форме
     form.validate();

    $.validator.messages.required = 'Заполните это поле!';
    //  $("form").validate({
    //      rules: {
    //          password: {
    //              minlength: 8
    //          }
    //      },
    //      messages: {
    //          password: {
    //              minlength:  'Минимум {0} символов!',
    //              required: 'лошара'
    //          }
    //      }
    //  })
     $.validator.messages.minlength = 'Минимум {0} символов!'

    // вешаем валидацию на поле с телефоном по классу
    $.validator.addClassRules({
        'phone-field': {
            checkMaskPhone: true,
        }
    });

    

})