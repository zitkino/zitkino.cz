

$(document).on('ready', function() {
    // lazy loading of images
    $('img.lazy')
        .lazyload({
            threshold: 100,
            effect: 'fadeIn',
            skip_invisible: false,
            placeholder: 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABAQMAAAAl21bKAAAAA1BMVEXu7u6DSdFtAAAACklEQVQI12NgAAAAAgAB4iG8MwAAAABJRU5ErkJggg==',
        })
        .show();

    // tooltips
    $('[title]:not(.info [title])').tooltip();
    $('.info [title]').tooltip({'placement': 'right'});

    // showtimes toggle
    $('.showtimes-toggle').showtimesToggle();
});


(function($) {
    function init(event) {
        var $toggle = event.data.$toggle;
        var $context = $toggle.closest('.showtimes');

        if ($context.length && window.location.hash && window.location.hash.indexOf('#day-') == 0) {
            window.scrollTo(0, 0);  // prevent anchor jump

            if ($('.showtime').length > 1) {
                $('.showtime:not(' + window.location.hash + ')', $context).hide();
                $toggle.show();
            }
        }
    }

    $.fn.showtimesToggle = function() {
        if ($(this).length) {
            var $toggle = $(this);
            var $context = $(this).closest('.showtimes');

            $toggle.on('click', function (event) {
                // clear the hash
                if (Modernizr.history) {
                    window.history.pushState('', document.title, window.location.pathname);
                } else {
                    window.location.hash = '';
                }

                // show all showtimes, hide the button itself
                $('.showtime', $context).show();
                $toggle.hide();

                // prevent activation of the link
                event.preventDefault();
            });

            $(window)
                .on('hashchange', {'$toggle': $toggle}, init)
                .triggerHandler('hashchange');
        }
    };
})(jQuery);
