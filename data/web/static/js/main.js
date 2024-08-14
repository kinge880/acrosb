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

    // International Tour carousel
    $(".InternationalTour-carousel").owlCarousel({
        autoplay: true,
        smartSpeed: 1000,
        center: false,
        dots: true,
        loop: true,
        margin: 25,
        nav : false,
        navText : [
            '<i class="bi bi-arrow-left"></i>',
            '<i class="bi bi-arrow-right"></i>'
        ],
        responsiveClass: true,
        responsive: {
            0:{
                items:1
            },
            768:{
                items:2
            },
            992:{
                items:2
            },
            1200:{
                items:3
            }
        }
    });


    // packages carousel
    $(".packages-carousel").owlCarousel({
        autoplay: true,
        smartSpeed: 1000,
        center: false,
        dots: false,
        loop: true,
        margin: 25,
        nav : true,
        navText : [
            '<i class="bi bi-arrow-left"></i>',
            '<i class="bi bi-arrow-right"></i>'
        ],
        responsiveClass: true,
        responsive: {
            0:{
                items:1
            },
            768:{
                items:2
            },
            992:{
                items:2
            },
            1200:{
                items:3
            }
        }
    });


    // testimonial carousel
    $(".testimonial-carousel").owlCarousel({
        autoplay: true,
        smartSpeed: 1000,
        center: true,
        dots: true,
        loop: true,
        margin: 25,
        nav : true,
        navText : [
            '<i class="bi bi-arrow-left"></i>',
            '<i class="bi bi-arrow-right"></i>'
        ],
        responsiveClass: true,
        responsive: {
            0:{
                items:1
            },
            768:{
                items:2
            },
            992:{
                items:2
            },
            1200:{
                items:3
            }
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

    $('.cep').mask('00000-000');
    $('.phone').mask('(00) 00000-0000');
    $('.cpf').mask('000.000.000-00');
    $('#email').mask("A", {
        translation: {
            "A": { pattern: /[\w@\-.+]/, recursive: true }
        }
    });

});

function redirectMenu() {
    var selectedRegion = $('#regionSelector').val();
    var newURL = "/" + selectedRegion + "/menu/";

    // Alterar a URL da página
    window.location.replace(newURL)
}

const passwordInput = document.getElementById('password-input');
const meterSections = document.querySelectorAll('.meter-section');

passwordInput.addEventListener('input', updateMeter);

function updateMeter() {
    const password = passwordInput.value;
    let strength = calculatePasswordStrength(password);

    // Remove all strength classes
    meterSections.forEach((section) => {
        section.classList.remove('weak', 'medium', 'strong', 'very-strong');
    });

    // If the strength is less than 4, mark it as invalid
    if (strength < 4) {
        passwordInput.setCustomValidity('A senha deve ter uma força mínima de 4.');
    }else{
        passwordInput.setCustomValidity('');
    }

    // Add the appropriate strength class based on the strength value
    if (strength >= 1) {
        meterSections[0].classList.add('weak');
    }
    if (strength >= 2) {
        meterSections[1].classList.add('medium');
    }
    if (strength >= 3) {
        meterSections[2].classList.add('strong');
    }
    if (strength >= 4) {
        meterSections[3].classList.add('very-strong');
    }
}

function calculatePasswordStrength(password) {
    const lengthWeight = 0.15;
    const uppercaseWeight = 0.5;
    const lowercaseWeight = 0.5;
    const numberWeight = 0.7;
    const symbolWeight = 1;

    let strength = 0;

    // Calculate the strength based on the password length
    strength += password.length * lengthWeight;

    // Calculate the strength based on uppercase letters
    if (/[A-Z]/.test(password)) {
        strength += uppercaseWeight;
    }

    // Calculate the strength based on lowercase letters
    if (/[a-z]/.test(password)) {
        strength += lowercaseWeight;
    }

    // Calculate the strength based on numbers
    if (/\d/.test(password)) {
        strength += numberWeight;
    }

    // Calculate the strength based on symbols
    if (/[^A-Za-z0-9]/.test(password)) {
        strength += symbolWeight;
    }

    return strength;
}

$(document).ready(function() {
    var senha = $('#actual_password');
    var new_senha = $('#password-input');
    var olho= $("#olho");
    var new_olho= $("#new_olho");

    olho.mousedown(function() {
        senha.attr("type", "text");
    });

    olho.mouseup(function() {
        senha.attr("type", "password");
    });
    // para evitar o problema de arrastar a imagem e a senha continuar exposta, 
    //citada pelo nosso amigo nos comentários
    $( "#new_olho" ).mouseout(function() { 
        $("#password-input").attr("type", "password");
    });

    new_olho.mousedown(function() {
        new_senha.attr("type", "text");
    });

    new_olho.mouseup(function() {
        new_senha.attr("type", "password");
    });
    // para evitar o problema de arrastar a imagem e a senha continuar exposta, 
    //citada pelo nosso amigo nos comentários
    $( "#olho" ).mouseout(function() { 
        $("#actual_password").attr("type", "password");
    });
});

