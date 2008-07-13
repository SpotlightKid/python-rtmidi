/*
 * Update article preview area with a new DOM node
 * (and put a link to hide it again at the top)
 */
function update_article_preview(el) {
    logDebug('update_article_preview called');
    var preview = $('articlepreview');
    var hidelink = A({
      'class': 'hidelink',
      'href': '#',
      'accesskey': 'w',
      'title': 'Hide article preview [w]',
    }, 'Hide');
    replaceChildNodes(preview, hidelink);
    if (! isArrayLike(el) || el.nodeType) {
        el = Array(el);
    }
    map(partial(appendChildNodes, preview), el);
    connect(hidelink, 'onclick',
        function() {
            hideElement('articlepreview');
            fcs($('articleform_text'));
        }
    );
    showElement(preview);
    fcs($('hidelink'));
}

/*
 * Show article preview received via AJAJ.
 */
function show_article_preview(res) {
    logDebug('show_article_preview called');
    res = evalJSONRequest(res);
    if (res['error']) {
        update_article_preview(P({'class': 'errmsg'}, res['error']));
    }
    else {
        var heading = H2({}, $('articleform_title').value);
        var container = DIV({});
        container.innerHTML = res['preview'];
        update_article_preview([heading, container]);
    }
}

/*
 * Show error message when no article preview is available.
 */
function no_preview(err) {
    update_article_preview(P({'class': 'errmsg'}, 'No preview available'));
}


/*
 * Load article preview via AJAJ.
 */
function load_article_preview(e) {
    logDebug('load_article_preview called');
    var text = $('articleform_text').value;
    /* do a POST XmlHttpRequest with url-encoded comment text */
    var d = doXHR('/preview', {
      'method': 'POST',
      'sendContent': 'text=' + escape(text) + '&format=rest',
      headers: {"Content-Type": "application/x-www-form-urlencoded"}
    });
    d.addCallbacks(show_article_preview, no_preview);
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
          'value': 'Preview',
          'accesskey': 'p',
          'title': 'Show article preview [p]'
        });
        submit.parentNode.appendChild(button);
        connect(button, 'onclick', load_article_preview);
    }
}

/*
 * Add event handlers to tag links
 */
function add_tag(e) {
    var entry = $('articleform_tags');
    if (!entry) {
        return;
    }
    var link = e.src();
    var tag = link.firstChild.nodeValue;
    if (entry.value.indexOf(tag) == -1) {
        entry.value = entry.value.replace(/\s*,\s*$/, '');
        if (entry.value) {
            entry.value += ', ';
        }
        entry.value += tag;
    }
    e.stop();
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
