/*
 * Enable search form submission only if input field contains text
 */
function toggle_search(e) {
    var input = e.src()
    var value = input.value.replace(/\s+/, '');
    if (value) {
        search_disable(false);
    } else {
        search_disable(true);
    }
}

/*
 * Enable or disable search buttons
 */
function search_disable(flag) {
    $('searchform_title').disabled = flag;
    $('searchform_fulltext').disabled = flag;
}

/*
 * Add callbacks on page load
 */
RUZEE.Events.add(window, 'domload',
    function() {
        var searchform = $('searchform');
        if (searchform) {
            if (!searchform.q.value) {
                searchform.title.disabled = true;
                searchform.fulltext.disabled = true;
            }
            connect(searchform.q, 'onkeyup', toggle_search);
            connect(searchform.q, 'onchange', toggle_search);
            connect(searchform.q, 'onblur', toggle_search);
        }
    }
);
