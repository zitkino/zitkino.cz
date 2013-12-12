
$(document).ready(function() {

    $('img.lazy').show().lazyload({
        threshold: 100,
        effect: 'fadeIn',
        skip_invisible: false,
        placeholder: 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABAQMAAAAl21bKAAAAA1BMVEXu7u6DSdFtAAAACklEQVQI12NgAAAAAgAB4iG8MwAAAABJRU5ErkJggg==',
    });

    $('[title]:not(.info [title])').tooltip();
    $('.info [title]').tooltip({'placement': 'right'});
});
