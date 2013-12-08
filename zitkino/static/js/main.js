
$(document).ready(function() {

    $('.thumbnail img.lazy').show().lazyload({
        threshold : 100,
        effect : 'fadeIn',
        skip_invisible : false
    });

});
