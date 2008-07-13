/**
 * RUZEE.Events 0.2
 * (c) 2006 Steffen Rusitschka <steffen@rusitschka.de>
 *
 * RUZEE.Events is freely distributable under the terms of
 * an MIT-style license. For details, see http://www.ruzee.com/
 */

var RUZEE=window.RUZEE||{};

RUZEE.Events={
  domloadEvents: [],
  domloadDone: false,

  add: function(obj, event, fn, useCapture) {
    if (event == 'domload') {
      RUZEE.Events.domloadEvents.push(fn);
      return true;
    }
    if(obj.addEventListener){
      obj.addEventListener(event,fn,useCapture);
      return true;
    }
    if(obj.attachEvent){
      return obj.attachEvent('on'+event,fn);
    }
    var f=obj['on'+event];
    obj['on'+event]=(f&&typeof f=='function')?function(){ f(); fn(); }:fn;
  },

  remove: function(obj, event, fn, useCapture) {
    if (obj.removeEventListener) {
      obj.removeEventListener(event, fn, useCapture);
      return true;
    }
    if (obj.detachEvent) {
      return obj.detachEvent('on'+event, fn);
    }
    alert('Handler could not be removed!');
  },

  getSrc: function(e) {
    var s;
    e = e || window.event;
    if (e.target)
      s = e.target;
    else if (e.srcElement)
      s = e.srcElement;
    if (s.nodeType == 3) // defeat Safari bug
      s = s.parentNode;
    return s;
  },

  ondomload: function() {
    if (RUZEE.Events.domloadDone)
      return;
    RUZEE.Events.domloadDone=true;

    for (var i=0; i<RUZEE.Events.domloadEvents.length; i++)
      RUZEE.Events.domloadEvents[i]();
  },

  domloadCheck: function() {
    if(RUZEE.Events.domloadDone)
      return true;

    var loaded = (/KHTML/i.test(navigator.userAgent)) &&
      (/loaded|complete/.test(document.readyState));
    var eofAvail = document.getElementById  &&
      document.getElementById('domloadeof');
    // wait till the element with ID domloadeof is in the DOM or
    // readyState=loaded on KHTML
    if (loaded || eofAvail) {
      RUZEE.Events.ondomload();
    } else {
      // Not ready yet, wait a little more.
      setTimeout('RUZEE.Events.domloadCheck()',100);
    }
    return true;
  }
};

// if possible, use the "standard" way
if (document.addEventListener)
  document.addEventListener('DOMContentLoaded', RUZEE.Events.ondomload, false);

// for Internet Explorer
/*@cc_on @*/
/*@if (@_win32)
document.write("<script id=__ie_ondomload defer src=javascript:void(0)><\/script>");
document.getElementById("__ie_ondomload").onreadystatechange=function() {
  if (this.readyState=="complete") {
    RUZEE.Events.ondomload();
  }
};
/*@end @*/

setTimeout('RUZEE.Events.domloadCheck()',100);
// Just in case window.onload happens first, add it there, too
RUZEE.Events.add(window, 'load', RUZEE.Events.ondomload);
