(function e(t,n,r){function s(o,u){if(!n[o]){if(!t[o]){var a=typeof require=="function"&&require;if(!u&&a)return a(o,!0);if(i)return i(o,!0);var f=new Error("Cannot find module '"+o+"'");throw f.code="MODULE_NOT_FOUND",f}var l=n[o]={exports:{}};t[o][0].call(l.exports,function(e){var n=t[o][1][e];return s(n?n:e)},l,l.exports,e,t,n,r)}return n[o].exports}var i=typeof require=="function"&&require;for(var o=0;o<r.length;o++)s(r[o]);return s})({"/Users/jonas/Projects/Django/wildfish-ratings/wildfish_ratings/static/wildfish-ratings/js/index.js":[function(require,module,exports){
require('./src/ratings')
},{"./src/ratings":"/Users/jonas/Projects/Django/wildfish-ratings/wildfish_ratings/static/wildfish-ratings/js/src/ratings.js"}],"/Users/jonas/Projects/Django/wildfish-ratings/wildfish_ratings/static/wildfish-ratings/js/src/ratings.js":[function(require,module,exports){
var rest = require('./rest.js');
var utils = require('./utils');


/*********************
 * Initialise ratings
 *********************/
function init() {
    var ratingActions = document.querySelectorAll(".wildfish-ratings-rate-action"),
        i;

    // Add click events to stars
    for (i = 0; i < ratingActions.length; i += 1) {
        ratingActions[i].addEventListener("click", ratingClick);

        ratingActions[i].onmouseenter = function () {
            var maxRating = getMaxRating(this);
            var score = this.getAttribute('data-score');
            var parent = utils.findParent(this, "wildfish-ratings");
            parent.querySelector(".wildfish-ratings-rating-foreground").style.width = 100 / maxRating * score + "%";
        };

        ratingActions[i].onmouseleave = function () {
            var avgRating = getAvgRating(this);
            var maxRating = getMaxRating(this);
            var score = this.getAttribute('data-score');
            var parent = utils.findParent(this, "wildfish-ratings");
            var percentage = 100 / maxRating * avgRating + "%";
            console.log(percentage);
            console.log(avgRating);
            parent.querySelector(".wildfish-ratings-rating-foreground").style.width = percentage;
        };
    }
}


/*********************
 * Rating click event
 *********************/
function ratingClick(ev) {
    ev.stopPropagation();
    ev.preventDefault();
    var score = this.getAttribute('data-score');
    var ratingId = this.getAttribute('data-for');
    rate(ratingId, score, this);
}


/*********************
 * Rate instance
 *********************/
function rate(id, score, sender) {
    var url = '/ratings/' + id + '/' + score + '/';

    rest.get(url, {}, function (rating) {
        updateRating(rating, sender);
    }, function (errors) {
        console.log(errors);
    });
}


function getMaxRating(el) {
    var parent = utils.findParent(el, "wildfish-ratings");
    if (parent) {
        return parseInt(parent.getAttribute('data-max-rating'));
    }

    return -1;
}


function getAvgRating(el) {
    var parent = utils.findParent(el, "wildfish-ratings");
    if (parent) {
        return parent.getAttribute('data-avg-rating');
    }

    return -1;
}


/*********************
 * Update rating
 *********************/
function updateRating(rating, sender) {
    var parent = utils.findParent(sender, "wildfish-ratings");
    if (parent === undefined || parent === null) {
        return;
    }

    parent.setAttribute("data-avg-rating", rating.rating_average);

    //parent.querySelector(".wildfish-ratings-count").innerHTML = rating.rating_count.toString();
    //parent.querySelector(".wildfish-ratings-total").innerHTML = rating.rating_total.toString();
    //parent.querySelector(".wildfish-ratings-avg").innerHTML = rating.rating_average.toString();
    parent.querySelector(".wildfish-ratings-rating-foreground").style.width = 100 / rating.max_value * rating.rating_average + "%";
}


/*********************
 * Only initialise ratings
 * if there is something to rate
 *********************/
if (document.querySelector(".wildfish-ratings")) {
    init();
}

},{"./rest.js":"/Users/jonas/Projects/Django/wildfish-ratings/wildfish_ratings/static/wildfish-ratings/js/src/rest.js","./utils":"/Users/jonas/Projects/Django/wildfish-ratings/wildfish_ratings/static/wildfish-ratings/js/src/utils.js"}],"/Users/jonas/Projects/Django/wildfish-ratings/wildfish_ratings/static/wildfish-ratings/js/src/rest.js":[function(require,module,exports){
/*jslint browser:true */
"use strict";


var djangoRemarkRest = {
    getCookie: function (name) {
        // From https://docs.djangoproject.com/en/1.7/ref/contrib/csrf/
        var cookieValue = null, cookies, i, cookie;
        if (document.cookie && document.cookie !== '') {
            cookies = document.cookie.split(';');
            for (i = 0; i < cookies.length; i += 1) {
                cookie = cookies[i].trim(); // Doesn't work in all browsers
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    },

    makeRequest: function (url, method, success, fail) {
        url += "?format=json";
        var req = new XMLHttpRequest();
        if (req.overrideMimeType !== undefined) {
            req.overrideMimeType("application/json");
        }
        req.open(method, url, true);
        req.setRequestHeader('Content-Type', 'application/json');
        req.setRequestHeader('X-Requested-With', 'XMLHttpRequest');

        // When done processing data
        req.onreadystatechange = function () {
            if (req.readyState !== 4) {
                return;
            }

            if (req.status >= 200 && req.status <= 299) {
                if (success) {
                    if (req.responseText) {
                        success(JSON.parse(req.responseText));
                    } else { success(); }
                }
            } else {
                if (fail) {
                    fail(JSON.parse(req.responseText));
                }
            }
        };

        return req;
    },

    get: function (url, data, success, fail) {
        var req = this.makeRequest(url, 'GET', success, fail);
        req.send(JSON.stringify(data));
    },

    post: function (url, data, success, fail) {
        var req = this.makeRequest(url, 'POST', success, fail);
        req.setRequestHeader("X-CSRFToken", this.getCookie('csrftoken'));
        req.send(JSON.stringify(data));
    },

    put: function (url, data, success, fail) {
        var req = this.makeRequest(url, 'PUT', success, fail);
        req.setRequestHeader("X-CSRFToken", this.getCookie('csrftoken'));
        req.send(JSON.stringify(data));
    },

    patch: function (url, data, success, fail) {
        var req = this.makeRequest(url, 'PATCH', success, fail);
        req.setRequestHeader("X-CSRFToken", this.getCookie('csrftoken'));
        req.send(JSON.stringify(data));
    },

    "delete": function (url, data, success, fail) {
        var req = this.makeRequest(url, 'DELETE', success, fail);
        req.setRequestHeader("X-CSRFToken", this.getCookie('csrftoken'));
        req.send(JSON.stringify(data));
    }
};


module.exports = djangoRemarkRest;

},{}],"/Users/jonas/Projects/Django/wildfish-ratings/wildfish_ratings/static/wildfish-ratings/js/src/utils.js":[function(require,module,exports){
/**************************
 * Check if an element has a class
 **************************/
function hasClass (el, name) {
    return (' ' + el.className + ' ').indexOf(' ' + name + ' ') > -1;
}


/**************************
 * Find parent element
 **************************/
function findParent(el, className) {
    var parentNode = el.parentNode;
    while (hasClass(parentNode, className) === false) {
        if (parentNode.parentNode === undefined) {
            return null;
        }
        parentNode = parentNode.parentNode;
    }
    return parentNode
}


module.exports = {
    hasClass: hasClass,
    findParent: findParent
};

},{}]},{},["/Users/jonas/Projects/Django/wildfish-ratings/wildfish_ratings/static/wildfish-ratings/js/index.js"])
//# sourceMappingURL=data:application/json;base64,eyJ2ZXJzaW9uIjozLCJzb3VyY2VzIjpbIi4uLy4uLy4uLy4uLy4uLy4uLy4uLy4uLy4uL3Vzci9sb2NhbC9saWIvbm9kZV9tb2R1bGVzL3dhdGNoaWZ5L25vZGVfbW9kdWxlcy9icm93c2VyaWZ5L25vZGVfbW9kdWxlcy9icm93c2VyLXBhY2svX3ByZWx1ZGUuanMiLCJpbmRleC5qcyIsInNyYy9yYXRpbmdzLmpzIiwic3JjL3Jlc3QuanMiLCJzcmMvdXRpbHMuanMiXSwibmFtZXMiOltdLCJtYXBwaW5ncyI6IkFBQUE7QUNBQTs7QUNBQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7O0FDM0dBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTs7QUN0RkE7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0EiLCJmaWxlIjoiZ2VuZXJhdGVkLmpzIiwic291cmNlUm9vdCI6IiIsInNvdXJjZXNDb250ZW50IjpbIihmdW5jdGlvbiBlKHQsbixyKXtmdW5jdGlvbiBzKG8sdSl7aWYoIW5bb10pe2lmKCF0W29dKXt2YXIgYT10eXBlb2YgcmVxdWlyZT09XCJmdW5jdGlvblwiJiZyZXF1aXJlO2lmKCF1JiZhKXJldHVybiBhKG8sITApO2lmKGkpcmV0dXJuIGkobywhMCk7dmFyIGY9bmV3IEVycm9yKFwiQ2Fubm90IGZpbmQgbW9kdWxlICdcIitvK1wiJ1wiKTt0aHJvdyBmLmNvZGU9XCJNT0RVTEVfTk9UX0ZPVU5EXCIsZn12YXIgbD1uW29dPXtleHBvcnRzOnt9fTt0W29dWzBdLmNhbGwobC5leHBvcnRzLGZ1bmN0aW9uKGUpe3ZhciBuPXRbb11bMV1bZV07cmV0dXJuIHMobj9uOmUpfSxsLGwuZXhwb3J0cyxlLHQsbixyKX1yZXR1cm4gbltvXS5leHBvcnRzfXZhciBpPXR5cGVvZiByZXF1aXJlPT1cImZ1bmN0aW9uXCImJnJlcXVpcmU7Zm9yKHZhciBvPTA7bzxyLmxlbmd0aDtvKyspcyhyW29dKTtyZXR1cm4gc30pIiwicmVxdWlyZSgnLi9zcmMvcmF0aW5ncycpIiwidmFyIHJlc3QgPSByZXF1aXJlKCcuL3Jlc3QuanMnKTtcbnZhciB1dGlscyA9IHJlcXVpcmUoJy4vdXRpbHMnKTtcblxuXG4vKioqKioqKioqKioqKioqKioqKioqXG4gKiBJbml0aWFsaXNlIHJhdGluZ3NcbiAqKioqKioqKioqKioqKioqKioqKiovXG5mdW5jdGlvbiBpbml0KCkge1xuICAgIHZhciByYXRpbmdBY3Rpb25zID0gZG9jdW1lbnQucXVlcnlTZWxlY3RvckFsbChcIi53aWxkZmlzaC1yYXRpbmdzLXJhdGUtYWN0aW9uXCIpLFxuICAgICAgICBpO1xuXG4gICAgLy8gQWRkIGNsaWNrIGV2ZW50cyB0byBzdGFyc1xuICAgIGZvciAoaSA9IDA7IGkgPCByYXRpbmdBY3Rpb25zLmxlbmd0aDsgaSArPSAxKSB7XG4gICAgICAgIHJhdGluZ0FjdGlvbnNbaV0uYWRkRXZlbnRMaXN0ZW5lcihcImNsaWNrXCIsIHJhdGluZ0NsaWNrKTtcblxuICAgICAgICByYXRpbmdBY3Rpb25zW2ldLm9ubW91c2VlbnRlciA9IGZ1bmN0aW9uICgpIHtcbiAgICAgICAgICAgIHZhciBtYXhSYXRpbmcgPSBnZXRNYXhSYXRpbmcodGhpcyk7XG4gICAgICAgICAgICB2YXIgc2NvcmUgPSB0aGlzLmdldEF0dHJpYnV0ZSgnZGF0YS1zY29yZScpO1xuICAgICAgICAgICAgdmFyIHBhcmVudCA9IHV0aWxzLmZpbmRQYXJlbnQodGhpcywgXCJ3aWxkZmlzaC1yYXRpbmdzXCIpO1xuICAgICAgICAgICAgcGFyZW50LnF1ZXJ5U2VsZWN0b3IoXCIud2lsZGZpc2gtcmF0aW5ncy1yYXRpbmctZm9yZWdyb3VuZFwiKS5zdHlsZS53aWR0aCA9IDEwMCAvIG1heFJhdGluZyAqIHNjb3JlICsgXCIlXCI7XG4gICAgICAgIH07XG5cbiAgICAgICAgcmF0aW5nQWN0aW9uc1tpXS5vbm1vdXNlbGVhdmUgPSBmdW5jdGlvbiAoKSB7XG4gICAgICAgICAgICB2YXIgYXZnUmF0aW5nID0gZ2V0QXZnUmF0aW5nKHRoaXMpO1xuICAgICAgICAgICAgdmFyIG1heFJhdGluZyA9IGdldE1heFJhdGluZyh0aGlzKTtcbiAgICAgICAgICAgIHZhciBzY29yZSA9IHRoaXMuZ2V0QXR0cmlidXRlKCdkYXRhLXNjb3JlJyk7XG4gICAgICAgICAgICB2YXIgcGFyZW50ID0gdXRpbHMuZmluZFBhcmVudCh0aGlzLCBcIndpbGRmaXNoLXJhdGluZ3NcIik7XG4gICAgICAgICAgICB2YXIgcGVyY2VudGFnZSA9IDEwMCAvIG1heFJhdGluZyAqIGF2Z1JhdGluZyArIFwiJVwiO1xuICAgICAgICAgICAgY29uc29sZS5sb2cocGVyY2VudGFnZSk7XG4gICAgICAgICAgICBjb25zb2xlLmxvZyhhdmdSYXRpbmcpO1xuICAgICAgICAgICAgcGFyZW50LnF1ZXJ5U2VsZWN0b3IoXCIud2lsZGZpc2gtcmF0aW5ncy1yYXRpbmctZm9yZWdyb3VuZFwiKS5zdHlsZS53aWR0aCA9IHBlcmNlbnRhZ2U7XG4gICAgICAgIH07XG4gICAgfVxufVxuXG5cbi8qKioqKioqKioqKioqKioqKioqKipcbiAqIFJhdGluZyBjbGljayBldmVudFxuICoqKioqKioqKioqKioqKioqKioqKi9cbmZ1bmN0aW9uIHJhdGluZ0NsaWNrKGV2KSB7XG4gICAgZXYuc3RvcFByb3BhZ2F0aW9uKCk7XG4gICAgZXYucHJldmVudERlZmF1bHQoKTtcbiAgICB2YXIgc2NvcmUgPSB0aGlzLmdldEF0dHJpYnV0ZSgnZGF0YS1zY29yZScpO1xuICAgIHZhciByYXRpbmdJZCA9IHRoaXMuZ2V0QXR0cmlidXRlKCdkYXRhLWZvcicpO1xuICAgIHJhdGUocmF0aW5nSWQsIHNjb3JlLCB0aGlzKTtcbn1cblxuXG4vKioqKioqKioqKioqKioqKioqKioqXG4gKiBSYXRlIGluc3RhbmNlXG4gKioqKioqKioqKioqKioqKioqKioqL1xuZnVuY3Rpb24gcmF0ZShpZCwgc2NvcmUsIHNlbmRlcikge1xuICAgIHZhciB1cmwgPSAnL3JhdGluZ3MvJyArIGlkICsgJy8nICsgc2NvcmUgKyAnLyc7XG5cbiAgICByZXN0LmdldCh1cmwsIHt9LCBmdW5jdGlvbiAocmF0aW5nKSB7XG4gICAgICAgIHVwZGF0ZVJhdGluZyhyYXRpbmcsIHNlbmRlcik7XG4gICAgfSwgZnVuY3Rpb24gKGVycm9ycykge1xuICAgICAgICBjb25zb2xlLmxvZyhlcnJvcnMpO1xuICAgIH0pO1xufVxuXG5cbmZ1bmN0aW9uIGdldE1heFJhdGluZyhlbCkge1xuICAgIHZhciBwYXJlbnQgPSB1dGlscy5maW5kUGFyZW50KGVsLCBcIndpbGRmaXNoLXJhdGluZ3NcIik7XG4gICAgaWYgKHBhcmVudCkge1xuICAgICAgICByZXR1cm4gcGFyc2VJbnQocGFyZW50LmdldEF0dHJpYnV0ZSgnZGF0YS1tYXgtcmF0aW5nJykpO1xuICAgIH1cblxuICAgIHJldHVybiAtMTtcbn1cblxuXG5mdW5jdGlvbiBnZXRBdmdSYXRpbmcoZWwpIHtcbiAgICB2YXIgcGFyZW50ID0gdXRpbHMuZmluZFBhcmVudChlbCwgXCJ3aWxkZmlzaC1yYXRpbmdzXCIpO1xuICAgIGlmIChwYXJlbnQpIHtcbiAgICAgICAgcmV0dXJuIHBhcmVudC5nZXRBdHRyaWJ1dGUoJ2RhdGEtYXZnLXJhdGluZycpO1xuICAgIH1cblxuICAgIHJldHVybiAtMTtcbn1cblxuXG4vKioqKioqKioqKioqKioqKioqKioqXG4gKiBVcGRhdGUgcmF0aW5nXG4gKioqKioqKioqKioqKioqKioqKioqL1xuZnVuY3Rpb24gdXBkYXRlUmF0aW5nKHJhdGluZywgc2VuZGVyKSB7XG4gICAgdmFyIHBhcmVudCA9IHV0aWxzLmZpbmRQYXJlbnQoc2VuZGVyLCBcIndpbGRmaXNoLXJhdGluZ3NcIik7XG4gICAgaWYgKHBhcmVudCA9PT0gdW5kZWZpbmVkIHx8IHBhcmVudCA9PT0gbnVsbCkge1xuICAgICAgICByZXR1cm47XG4gICAgfVxuXG4gICAgcGFyZW50LnNldEF0dHJpYnV0ZShcImRhdGEtYXZnLXJhdGluZ1wiLCByYXRpbmcucmF0aW5nX2F2ZXJhZ2UpO1xuXG4gICAgLy9wYXJlbnQucXVlcnlTZWxlY3RvcihcIi53aWxkZmlzaC1yYXRpbmdzLWNvdW50XCIpLmlubmVySFRNTCA9IHJhdGluZy5yYXRpbmdfY291bnQudG9TdHJpbmcoKTtcbiAgICAvL3BhcmVudC5xdWVyeVNlbGVjdG9yKFwiLndpbGRmaXNoLXJhdGluZ3MtdG90YWxcIikuaW5uZXJIVE1MID0gcmF0aW5nLnJhdGluZ190b3RhbC50b1N0cmluZygpO1xuICAgIC8vcGFyZW50LnF1ZXJ5U2VsZWN0b3IoXCIud2lsZGZpc2gtcmF0aW5ncy1hdmdcIikuaW5uZXJIVE1MID0gcmF0aW5nLnJhdGluZ19hdmVyYWdlLnRvU3RyaW5nKCk7XG4gICAgcGFyZW50LnF1ZXJ5U2VsZWN0b3IoXCIud2lsZGZpc2gtcmF0aW5ncy1yYXRpbmctZm9yZWdyb3VuZFwiKS5zdHlsZS53aWR0aCA9IDEwMCAvIHJhdGluZy5tYXhfdmFsdWUgKiByYXRpbmcucmF0aW5nX2F2ZXJhZ2UgKyBcIiVcIjtcbn1cblxuXG4vKioqKioqKioqKioqKioqKioqKioqXG4gKiBPbmx5IGluaXRpYWxpc2UgcmF0aW5nc1xuICogaWYgdGhlcmUgaXMgc29tZXRoaW5nIHRvIHJhdGVcbiAqKioqKioqKioqKioqKioqKioqKiovXG5pZiAoZG9jdW1lbnQucXVlcnlTZWxlY3RvcihcIi53aWxkZmlzaC1yYXRpbmdzXCIpKSB7XG4gICAgaW5pdCgpO1xufVxuIiwiLypqc2xpbnQgYnJvd3Nlcjp0cnVlICovXG5cInVzZSBzdHJpY3RcIjtcblxuXG52YXIgZGphbmdvUmVtYXJrUmVzdCA9IHtcbiAgICBnZXRDb29raWU6IGZ1bmN0aW9uIChuYW1lKSB7XG4gICAgICAgIC8vIEZyb20gaHR0cHM6Ly9kb2NzLmRqYW5nb3Byb2plY3QuY29tL2VuLzEuNy9yZWYvY29udHJpYi9jc3JmL1xuICAgICAgICB2YXIgY29va2llVmFsdWUgPSBudWxsLCBjb29raWVzLCBpLCBjb29raWU7XG4gICAgICAgIGlmIChkb2N1bWVudC5jb29raWUgJiYgZG9jdW1lbnQuY29va2llICE9PSAnJykge1xuICAgICAgICAgICAgY29va2llcyA9IGRvY3VtZW50LmNvb2tpZS5zcGxpdCgnOycpO1xuICAgICAgICAgICAgZm9yIChpID0gMDsgaSA8IGNvb2tpZXMubGVuZ3RoOyBpICs9IDEpIHtcbiAgICAgICAgICAgICAgICBjb29raWUgPSBjb29raWVzW2ldLnRyaW0oKTsgLy8gRG9lc24ndCB3b3JrIGluIGFsbCBicm93c2Vyc1xuICAgICAgICAgICAgICAgIC8vIERvZXMgdGhpcyBjb29raWUgc3RyaW5nIGJlZ2luIHdpdGggdGhlIG5hbWUgd2Ugd2FudD9cbiAgICAgICAgICAgICAgICBpZiAoY29va2llLnN1YnN0cmluZygwLCBuYW1lLmxlbmd0aCArIDEpID09PSAobmFtZSArICc9JykpIHtcbiAgICAgICAgICAgICAgICAgICAgY29va2llVmFsdWUgPSBkZWNvZGVVUklDb21wb25lbnQoY29va2llLnN1YnN0cmluZyhuYW1lLmxlbmd0aCArIDEpKTtcbiAgICAgICAgICAgICAgICAgICAgYnJlYWs7XG4gICAgICAgICAgICAgICAgfVxuICAgICAgICAgICAgfVxuICAgICAgICB9XG4gICAgICAgIHJldHVybiBjb29raWVWYWx1ZTtcbiAgICB9LFxuXG4gICAgbWFrZVJlcXVlc3Q6IGZ1bmN0aW9uICh1cmwsIG1ldGhvZCwgc3VjY2VzcywgZmFpbCkge1xuICAgICAgICB1cmwgKz0gXCI/Zm9ybWF0PWpzb25cIjtcbiAgICAgICAgdmFyIHJlcSA9IG5ldyBYTUxIdHRwUmVxdWVzdCgpO1xuICAgICAgICBpZiAocmVxLm92ZXJyaWRlTWltZVR5cGUgIT09IHVuZGVmaW5lZCkge1xuICAgICAgICAgICAgcmVxLm92ZXJyaWRlTWltZVR5cGUoXCJhcHBsaWNhdGlvbi9qc29uXCIpO1xuICAgICAgICB9XG4gICAgICAgIHJlcS5vcGVuKG1ldGhvZCwgdXJsLCB0cnVlKTtcbiAgICAgICAgcmVxLnNldFJlcXVlc3RIZWFkZXIoJ0NvbnRlbnQtVHlwZScsICdhcHBsaWNhdGlvbi9qc29uJyk7XG4gICAgICAgIHJlcS5zZXRSZXF1ZXN0SGVhZGVyKCdYLVJlcXVlc3RlZC1XaXRoJywgJ1hNTEh0dHBSZXF1ZXN0Jyk7XG5cbiAgICAgICAgLy8gV2hlbiBkb25lIHByb2Nlc3NpbmcgZGF0YVxuICAgICAgICByZXEub25yZWFkeXN0YXRlY2hhbmdlID0gZnVuY3Rpb24gKCkge1xuICAgICAgICAgICAgaWYgKHJlcS5yZWFkeVN0YXRlICE9PSA0KSB7XG4gICAgICAgICAgICAgICAgcmV0dXJuO1xuICAgICAgICAgICAgfVxuXG4gICAgICAgICAgICBpZiAocmVxLnN0YXR1cyA+PSAyMDAgJiYgcmVxLnN0YXR1cyA8PSAyOTkpIHtcbiAgICAgICAgICAgICAgICBpZiAoc3VjY2Vzcykge1xuICAgICAgICAgICAgICAgICAgICBpZiAocmVxLnJlc3BvbnNlVGV4dCkge1xuICAgICAgICAgICAgICAgICAgICAgICAgc3VjY2VzcyhKU09OLnBhcnNlKHJlcS5yZXNwb25zZVRleHQpKTtcbiAgICAgICAgICAgICAgICAgICAgfSBlbHNlIHsgc3VjY2VzcygpOyB9XG4gICAgICAgICAgICAgICAgfVxuICAgICAgICAgICAgfSBlbHNlIHtcbiAgICAgICAgICAgICAgICBpZiAoZmFpbCkge1xuICAgICAgICAgICAgICAgICAgICBmYWlsKEpTT04ucGFyc2UocmVxLnJlc3BvbnNlVGV4dCkpO1xuICAgICAgICAgICAgICAgIH1cbiAgICAgICAgICAgIH1cbiAgICAgICAgfTtcblxuICAgICAgICByZXR1cm4gcmVxO1xuICAgIH0sXG5cbiAgICBnZXQ6IGZ1bmN0aW9uICh1cmwsIGRhdGEsIHN1Y2Nlc3MsIGZhaWwpIHtcbiAgICAgICAgdmFyIHJlcSA9IHRoaXMubWFrZVJlcXVlc3QodXJsLCAnR0VUJywgc3VjY2VzcywgZmFpbCk7XG4gICAgICAgIHJlcS5zZW5kKEpTT04uc3RyaW5naWZ5KGRhdGEpKTtcbiAgICB9LFxuXG4gICAgcG9zdDogZnVuY3Rpb24gKHVybCwgZGF0YSwgc3VjY2VzcywgZmFpbCkge1xuICAgICAgICB2YXIgcmVxID0gdGhpcy5tYWtlUmVxdWVzdCh1cmwsICdQT1NUJywgc3VjY2VzcywgZmFpbCk7XG4gICAgICAgIHJlcS5zZXRSZXF1ZXN0SGVhZGVyKFwiWC1DU1JGVG9rZW5cIiwgdGhpcy5nZXRDb29raWUoJ2NzcmZ0b2tlbicpKTtcbiAgICAgICAgcmVxLnNlbmQoSlNPTi5zdHJpbmdpZnkoZGF0YSkpO1xuICAgIH0sXG5cbiAgICBwdXQ6IGZ1bmN0aW9uICh1cmwsIGRhdGEsIHN1Y2Nlc3MsIGZhaWwpIHtcbiAgICAgICAgdmFyIHJlcSA9IHRoaXMubWFrZVJlcXVlc3QodXJsLCAnUFVUJywgc3VjY2VzcywgZmFpbCk7XG4gICAgICAgIHJlcS5zZXRSZXF1ZXN0SGVhZGVyKFwiWC1DU1JGVG9rZW5cIiwgdGhpcy5nZXRDb29raWUoJ2NzcmZ0b2tlbicpKTtcbiAgICAgICAgcmVxLnNlbmQoSlNPTi5zdHJpbmdpZnkoZGF0YSkpO1xuICAgIH0sXG5cbiAgICBwYXRjaDogZnVuY3Rpb24gKHVybCwgZGF0YSwgc3VjY2VzcywgZmFpbCkge1xuICAgICAgICB2YXIgcmVxID0gdGhpcy5tYWtlUmVxdWVzdCh1cmwsICdQQVRDSCcsIHN1Y2Nlc3MsIGZhaWwpO1xuICAgICAgICByZXEuc2V0UmVxdWVzdEhlYWRlcihcIlgtQ1NSRlRva2VuXCIsIHRoaXMuZ2V0Q29va2llKCdjc3JmdG9rZW4nKSk7XG4gICAgICAgIHJlcS5zZW5kKEpTT04uc3RyaW5naWZ5KGRhdGEpKTtcbiAgICB9LFxuXG4gICAgXCJkZWxldGVcIjogZnVuY3Rpb24gKHVybCwgZGF0YSwgc3VjY2VzcywgZmFpbCkge1xuICAgICAgICB2YXIgcmVxID0gdGhpcy5tYWtlUmVxdWVzdCh1cmwsICdERUxFVEUnLCBzdWNjZXNzLCBmYWlsKTtcbiAgICAgICAgcmVxLnNldFJlcXVlc3RIZWFkZXIoXCJYLUNTUkZUb2tlblwiLCB0aGlzLmdldENvb2tpZSgnY3NyZnRva2VuJykpO1xuICAgICAgICByZXEuc2VuZChKU09OLnN0cmluZ2lmeShkYXRhKSk7XG4gICAgfVxufTtcblxuXG5tb2R1bGUuZXhwb3J0cyA9IGRqYW5nb1JlbWFya1Jlc3Q7XG4iLCIvKioqKioqKioqKioqKioqKioqKioqKioqKipcbiAqIENoZWNrIGlmIGFuIGVsZW1lbnQgaGFzIGEgY2xhc3NcbiAqKioqKioqKioqKioqKioqKioqKioqKioqKi9cbmZ1bmN0aW9uIGhhc0NsYXNzIChlbCwgbmFtZSkge1xuICAgIHJldHVybiAoJyAnICsgZWwuY2xhc3NOYW1lICsgJyAnKS5pbmRleE9mKCcgJyArIG5hbWUgKyAnICcpID4gLTE7XG59XG5cblxuLyoqKioqKioqKioqKioqKioqKioqKioqKioqXG4gKiBGaW5kIHBhcmVudCBlbGVtZW50XG4gKioqKioqKioqKioqKioqKioqKioqKioqKiovXG5mdW5jdGlvbiBmaW5kUGFyZW50KGVsLCBjbGFzc05hbWUpIHtcbiAgICB2YXIgcGFyZW50Tm9kZSA9IGVsLnBhcmVudE5vZGU7XG4gICAgd2hpbGUgKGhhc0NsYXNzKHBhcmVudE5vZGUsIGNsYXNzTmFtZSkgPT09IGZhbHNlKSB7XG4gICAgICAgIGlmIChwYXJlbnROb2RlLnBhcmVudE5vZGUgPT09IHVuZGVmaW5lZCkge1xuICAgICAgICAgICAgcmV0dXJuIG51bGw7XG4gICAgICAgIH1cbiAgICAgICAgcGFyZW50Tm9kZSA9IHBhcmVudE5vZGUucGFyZW50Tm9kZTtcbiAgICB9XG4gICAgcmV0dXJuIHBhcmVudE5vZGVcbn1cblxuXG5tb2R1bGUuZXhwb3J0cyA9IHtcbiAgICBoYXNDbGFzczogaGFzQ2xhc3MsXG4gICAgZmluZFBhcmVudDogZmluZFBhcmVudFxufTtcbiJdfQ==
