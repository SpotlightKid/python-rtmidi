/*
 * Move cursor focus to element and select text if not empty
 */
function fcs(el) {
    if (el.value) {
        el.select();
    }
    el.focus();
}

/*
 * Open a small menu-less help window
 */
function open_helpwin(e) {
    var url = e.src().href;
    var helpwin = window.open(url, 'helpwin',
      "width=500,height=600,menubar=no,status=no,resizable=yes,scrollbars=yes");
    helpwin.focus();
    e.stop();
}

RUZEE.Events.add(window, 'domload',
    function() {
        /* attach 'onclick' handlers to online help links */
        links = getElementsByTagAndClassName('A', 'helplink');
        for (var i=0; i<links.length; i++) {
            connect(links[i], 'onclick', open_helpwin);
        }
    }
);
