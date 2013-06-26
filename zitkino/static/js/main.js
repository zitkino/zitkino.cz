
$(document).ready(function() {

    function scrollSchedule() {
        $('.showtimes-schedule').each(function() {
            $(this).scrollLeft(1000000); // dummy 'rightmost' number
        });
    };
    $(window).resize(scrollSchedule);
    scrollSchedule();

});
