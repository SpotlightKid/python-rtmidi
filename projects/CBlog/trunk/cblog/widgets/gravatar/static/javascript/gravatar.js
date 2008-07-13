/*
 * Show image only when the image data has fully loaded
 */
function image_loaded(e) {
    var img = e.src();
    img.style.display = 'block';
}

/*
 * Attach 'onload' handlers to gravatar icons.
 * Uses RUZEE.Events JavaScript library for cross-browser support
 * of a pseudo DOMContentLoad event, so we can initialize things
 * on page load but before images are loaded.
 *
 * See: http://www.ruzee.com/blog/ruzeeevents/
 */
RUZEE.Events.add(window, 'domload',
    function() {
        imgs = getElementsByTagAndClassName('IMG', 'gravatar');
        for (var i=0; i<imgs.length; i++) {
            connect(imgs[i], 'onload', image_loaded);
        }
    }
);
