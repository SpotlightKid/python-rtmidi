/*
 * fancyflash.js - Dynamically display a status message in a DIV overlay
 *
 * Based on the article by Lee McFadden at
 * <http://www.splee.co.uk/2005/11/23/fancy-status-messages-using-tg_flash/>.
 *
 * Relies on MochiKit <http://www.mochikit.com/>.
 */

/*
 * Clear/destroy flash message.
 */
function clearStatusMessage(msgbox) {
    swapDOM(msgbox, DIV({'id': 'statusmessage'}, null));
}

/*
 * The flash message box was clicked. Hide it.
 */
function statusMessageClicked(e) {
    var msgbox = e.src();
    if (msgbox._hide_cb instanceof Deferred) {
        msgbox._hide_cb.cancel();
    }
    disconnect(msgbox);
    clearStatusMessage(msgbox);
}

/*
 * Display the flash message by inserting a DIV into the DOM.
 *
 * The page needs to contain and element with ID 'statusmessage', which
 * will be replaced with the message box.
 */
function displayStatusMessage(msg, status, timeout) {
    if (!status) {
        status = 'info';
    }
    var innerbox = DIV({'class': status}, msg);
    var msgbox = swapDOM('statusmessage',
      DIV({'id': 'statusmessage'}, innerbox));
    // doesn't work for me on Firefox 1.0.8
    //roundElement(innerbox, {'corners': 'all'});
    if (timeout) {
        msgbox._hide_cb = callLater(timeout, clearStatusMessage, msgbox);
    }
    connect(msgbox, 'onclick', statusMessageClicked);
}

/*
 * Schedules hiding of message box with 'id' after 'timeout' seconds.
 */
function setHideTimeout(id, timeout) {
    connect(window, 'onload',
        function() {
            var msgbox = $(id);
            msgbox._hide_cb = callLater(timeout, clearStatusMessage, msgbox);
        }
    );
}

RUZEE.Events.add(window, 'domload',
    function() {
        msgbox = $('statusmessage');
        if (msgbox && msgbox.hasChildNodes()) {
            connect(msgbox, 'onclick', statusMessageClicked);
        }
    }
);

