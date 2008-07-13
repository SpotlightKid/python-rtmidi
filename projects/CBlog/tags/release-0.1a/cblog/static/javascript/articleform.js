/*
 * Show article preview received via AJAJ.
 */
function show_preview(res) {
    var preview = $('articlepreview');
    var hidelink = A({'class': 'hidelink', 'href': '#'}, 'Hide');
    var res = evalJSONRequest(res);
    if (res['error']) {
        var errmsg = P({'class': 'errmsg'}, res['error']);
        replaceChildnodes(preview, hidelink);
        appendChildNodes(preview, errmsg);
    }
    else {
        var container = DIV({});
        var heading = H2({}, $('articleform_title').value);
        container.innerHTML = res['preview'];
        replaceChildNodes(preview, hidelink);
        appendChildNodes(preview, heading);
        appendChildNodes(preview, container);
        connect(hidelink, 'onclick',
            function() {
                hideElement('articlepreview');
            }
        );
    }
    showElement(preview);
}

/*
 * Show error message when no article preview is available.
 */
function no_preview(err) {
    //alert(err);
    var preview = P({'class': 'errmsg'}, 'No preview available');
    replaceChildNodes('articlepreview', preview);
    showElement('articlepreview');
}


/*
 * Load article preview via AJAJ.
 */
function load_article_preview(e) {
    var text = $('articleform_text').value;
    /* do a POST XmlHttpRequest with url-encoded comment text */
    var d = doXHR('/preview', {
      'method': 'POST',
      'sendContent': 'text=' + escape(text) + '&format=rest',
      headers: {"Content-Type": "application/x-www-form-urlencoded"}
    });
    d.addCallbacks(show_preview, no_preview);
}

/*
 * Add a 'Preview' link/button to the comment form
 */
function add_previewaction() {
    var submit = $('submit_article');
    if (submit) {
        var button = INPUT({
          'id': 'preview',
          'type': 'button',
          'class': 'submitbutton',
          'value': 'Preview'
        });
        submit.parentNode.appendChild(button);
        connect(button, 'onclick', load_article_preview);
    }
}

/*
 * Add event handlers to atg links
 */
function add_tag(e) {
    var entry = $('articleform_tags');
    if (!entry) {
        return;
    }
    var link = e.src()
    var tag = link.firstChild.nodeValue;
    if (entry.value.indexOf(tag) == -1) {
        entry.value = entry.value.replace(/\s*,\s*$/, '');
        if (entry.value) {
            entry.value += ', '
        }
        entry.value += tag;
    }
    e.stop()
}

/*
 * Add event handlers to tag links
 */
function add_tagactions(el) {
    if (el) {
        var links = getElementsByTagAndClassName('A', 'tag');
        for (var i=0; i < links.length; i++) {
            if (hasElementClass(links[i], 'tag')) {
                connect(links[i], 'onclick', add_tag);
            }
        }
    }
}
/*
 * Add callbacks on page load
 */
RUZEE.Events.add(window, 'domload',
    function() {
        var submit = $('submit_entry');
        add_previewaction(submit);
        add_tagactions($('taglist'));
    }
);
