$(document).ready(function(){
  
    
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

})
