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
 * The "add comment" link was clicked or the form already contains input
 * --> show the comment form
 */
function show_commentform(e) {
    if (!e) {
        var commentform = $('commentform');
        var focus = null;
        var fields = new Array('name', 'email', 'homepage', 'comment');
        for (var i=0; i<fields.length; i++) {
            var field = commentform[fields[i]];
            if (hasElementClass(field.parentNode, 'fielderror')) {
                focus = field;
                break;
            }
            else if (field.value) {
                focus = field;
            }
        }
        if (focus) {
            /* we found a field with input or an error -> show form */
            // $('commentform_wrapper').style.display = 'block';
            showElement('commentform_wrapper');
            hideElement('commentlink');
            /* IE does not allow setting focus on hidden elements
               thatswhy we do it here rather than in the for loop above */
            fcs(focus);
            return true;
        }
        else {
            showElement('commentlink');
            return false;
        }
    }
    else {
        hideElement('commentlink');
        showElement('commentform_wrapper');
        fcs($('commentform').name);
        e.stop();
    }
}

/*
 * Show comment preview received via AJAJ.
 */
function show_preview(res) {
    var preview = $('commentpreview');
    var hidelink = A({'class': 'hidelink', 'href': '#'}, 'Hide');
    var res = evalJSONRequest(res);
    if (res['error']) {
        var errmsg = P({'class': 'errmsg'}, res['error']);
        replaceChildnodes(preview, hidelink);
        appendChildNodes(preview, errmsg);
    }
    else {
        var container = DIV({});
        container.innerHTML = res['preview'];
        replaceChildNodes(preview, hidelink);
        appendChildNodes(preview, container);
        connect(hidelink, 'onclick',
            function() {
                hideElement('commentpreview');
            }
        );
    }
    showElement(preview);
}

/*
 * Show error message when no comment preview is available.
 */
function no_preview(err) {
    //alert(err);
    var preview = P({'class': 'errmsg'}, 'No preview available');
    replaceChildNodes('commentpreview', preview);
    showElement('commentpreview');
}

/*
 * Load comment preview via JSON RPC.
 */
function load_comment_preview(e) {
    var text = $('commentform_comment').value;
    /* do a POST XmlHttpRequest with url-encoded comment text */
    var d = doXHR('/preview', {
      'method': 'POST',
      'sendContent': 'text=' + escape(text) + '&format=textile',
      headers: {"Content-Type": "application/x-www-form-urlencoded"}
    });
    d.addCallbacks(show_preview, no_preview);
}

/*
 * Add a 'Preview' link/button to the comment form
 */
function add_previewaction() {
    var submit = $('submit_comment');
    if (submit) {
        var button = INPUT({
          'id': 'preview',
          'type': 'button',
          'class': 'submitbutton',
          'value': 'Preview'
        });
        submit.parentNode.appendChild(button);
        connect(button, 'onclick', load_comment_preview);
    }
}

/*
 * Add callbacks on page load
 */
RUZEE.Events.add(window, 'domload',
    function() {
        add_previewaction();
        if (!show_commentform()) {
            var links = getElementsByTagAndClassName(
              'A', 'show_commentlink');
            for (var i=0; i<links.length; i++) {
                connect(links[i], 'onclick', show_commentform);
            }
        }
    }
);
