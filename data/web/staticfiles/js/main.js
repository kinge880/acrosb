(function ($) {
    "use strict";

    // Spinner
    var spinner = function () {
        setTimeout(function () {
            if ($('#spinner').length > 0) {
                $('#spinner').removeClass('show');
            }
        }, 1);
    };
    spinner(0);

    
    // Sticky Navbar
    $(window).scroll(function () {
        if ($(this).scrollTop() > 45) {
            $('.navbarstickyhome').addClass('sticky-top shadow-sm');
        } else {
            $('.navbarstickyhome').removeClass('sticky-top shadow-sm');
        }
    });
    
   // Back to top button
    $(window).scroll(function () {
        if ($(this).scrollTop() > 300) {
            $('.back-to-top').fadeIn('slow');
        } else {
            $('.back-to-top').fadeOut('slow');
        }
    });
    
    $('.back-to-top').click(function () {
        $('html, body').animate({scrollTop: 0}, 1500, 'easeInOutExpo');
        return false;
    }); 

})(jQuery);


$(document).ready(function(){
    // Bootstrap validation
    (function () {
        'use strict'

        // Fetch all the forms we want to apply custom Bootstrap validation styles to
        var forms = document.querySelectorAll('.needs-validation')

        // Loop over them and prevent submission
        Array.prototype.slice.call(forms)
        .forEach(function (form) {
            form.addEventListener('submit', function (event) {
            if (!form.checkValidity()) {
                event.preventDefault()
                event.stopPropagation()
            }
            else{
                $('#spinner').addClass('show');
            }

            form.classList.add('was-validated')
            }, false)
        })
    })()

});

function redirectMenu() {
    var selectedRegion = $('#regionSelector').val();
    var newURL = "/" + selectedRegion + "/menu/";

    // Alterar a URL da página
    window.location.replace(newURL)
}


