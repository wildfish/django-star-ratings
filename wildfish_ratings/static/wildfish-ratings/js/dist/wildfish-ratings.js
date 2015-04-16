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
        showError(errors, sender);
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
    parent.querySelector(".wildfish-ratings-rating-foreground").style.width = 100 / rating.max_value * rating.rating_average + "%";
}


function showError (errors, sender) {
    var parent = utils.findParent(sender, "wildfish-ratings");
    if (parent === undefined || parent === null) {
        return;
    }
    parent.querySelector(".wildfish-ratings-errors").innerHTML = errors.error;
    setTimeout(function () {
        parent.querySelector(".wildfish-ratings-errors").innerHTML = "";
    }, 2500);
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
//# sourceMappingURL=data:application/json;base64,eyJ2ZXJzaW9uIjozLCJzb3VyY2VzIjpbIi4uLy4uLy4uLy4uLy4uLy4uLy4uLy4uLy4uL3Vzci9sb2NhbC9saWIvbm9kZV9tb2R1bGVzL3dhdGNoaWZ5L25vZGVfbW9kdWxlcy9icm93c2VyaWZ5L25vZGVfbW9kdWxlcy9icm93c2VyLXBhY2svX3ByZWx1ZGUuanMiLCJpbmRleC5qcyIsInNyYy9yYXRpbmdzLmpzIiwic3JjL3Jlc3QuanMiLCJzcmMvdXRpbHMuanMiXSwibmFtZXMiOltdLCJtYXBwaW5ncyI6IkFBQUE7QUNBQTs7QUNBQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBOztBQ2hIQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7O0FDdEZBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBIiwiZmlsZSI6ImdlbmVyYXRlZC5qcyIsInNvdXJjZVJvb3QiOiIiLCJzb3VyY2VzQ29udGVudCI6WyIoZnVuY3Rpb24gZSh0LG4scil7ZnVuY3Rpb24gcyhvLHUpe2lmKCFuW29dKXtpZighdFtvXSl7dmFyIGE9dHlwZW9mIHJlcXVpcmU9PVwiZnVuY3Rpb25cIiYmcmVxdWlyZTtpZighdSYmYSlyZXR1cm4gYShvLCEwKTtpZihpKXJldHVybiBpKG8sITApO3ZhciBmPW5ldyBFcnJvcihcIkNhbm5vdCBmaW5kIG1vZHVsZSAnXCIrbytcIidcIik7dGhyb3cgZi5jb2RlPVwiTU9EVUxFX05PVF9GT1VORFwiLGZ9dmFyIGw9bltvXT17ZXhwb3J0czp7fX07dFtvXVswXS5jYWxsKGwuZXhwb3J0cyxmdW5jdGlvbihlKXt2YXIgbj10W29dWzFdW2VdO3JldHVybiBzKG4/bjplKX0sbCxsLmV4cG9ydHMsZSx0LG4scil9cmV0dXJuIG5bb10uZXhwb3J0c312YXIgaT10eXBlb2YgcmVxdWlyZT09XCJmdW5jdGlvblwiJiZyZXF1aXJlO2Zvcih2YXIgbz0wO288ci5sZW5ndGg7bysrKXMocltvXSk7cmV0dXJuIHN9KSIsInJlcXVpcmUoJy4vc3JjL3JhdGluZ3MnKSIsInZhciByZXN0ID0gcmVxdWlyZSgnLi9yZXN0LmpzJyk7XG52YXIgdXRpbHMgPSByZXF1aXJlKCcuL3V0aWxzJyk7XG5cblxuLyoqKioqKioqKioqKioqKioqKioqKlxuICogSW5pdGlhbGlzZSByYXRpbmdzXG4gKioqKioqKioqKioqKioqKioqKioqL1xuZnVuY3Rpb24gaW5pdCgpIHtcbiAgICB2YXIgcmF0aW5nQWN0aW9ucyA9IGRvY3VtZW50LnF1ZXJ5U2VsZWN0b3JBbGwoXCIud2lsZGZpc2gtcmF0aW5ncy1yYXRlLWFjdGlvblwiKSxcbiAgICAgICAgaTtcblxuICAgIC8vIEFkZCBjbGljayBldmVudHMgdG8gc3RhcnNcbiAgICBmb3IgKGkgPSAwOyBpIDwgcmF0aW5nQWN0aW9ucy5sZW5ndGg7IGkgKz0gMSkge1xuICAgICAgICByYXRpbmdBY3Rpb25zW2ldLmFkZEV2ZW50TGlzdGVuZXIoXCJjbGlja1wiLCByYXRpbmdDbGljayk7XG5cbiAgICAgICAgcmF0aW5nQWN0aW9uc1tpXS5vbm1vdXNlZW50ZXIgPSBmdW5jdGlvbiAoKSB7XG4gICAgICAgICAgICB2YXIgbWF4UmF0aW5nID0gZ2V0TWF4UmF0aW5nKHRoaXMpO1xuICAgICAgICAgICAgdmFyIHNjb3JlID0gdGhpcy5nZXRBdHRyaWJ1dGUoJ2RhdGEtc2NvcmUnKTtcbiAgICAgICAgICAgIHZhciBwYXJlbnQgPSB1dGlscy5maW5kUGFyZW50KHRoaXMsIFwid2lsZGZpc2gtcmF0aW5nc1wiKTtcbiAgICAgICAgICAgIHBhcmVudC5xdWVyeVNlbGVjdG9yKFwiLndpbGRmaXNoLXJhdGluZ3MtcmF0aW5nLWZvcmVncm91bmRcIikuc3R5bGUud2lkdGggPSAxMDAgLyBtYXhSYXRpbmcgKiBzY29yZSArIFwiJVwiO1xuICAgICAgICB9O1xuXG4gICAgICAgIHJhdGluZ0FjdGlvbnNbaV0ub25tb3VzZWxlYXZlID0gZnVuY3Rpb24gKCkge1xuICAgICAgICAgICAgdmFyIGF2Z1JhdGluZyA9IGdldEF2Z1JhdGluZyh0aGlzKTtcbiAgICAgICAgICAgIHZhciBtYXhSYXRpbmcgPSBnZXRNYXhSYXRpbmcodGhpcyk7XG4gICAgICAgICAgICB2YXIgc2NvcmUgPSB0aGlzLmdldEF0dHJpYnV0ZSgnZGF0YS1zY29yZScpO1xuICAgICAgICAgICAgdmFyIHBhcmVudCA9IHV0aWxzLmZpbmRQYXJlbnQodGhpcywgXCJ3aWxkZmlzaC1yYXRpbmdzXCIpO1xuICAgICAgICAgICAgdmFyIHBlcmNlbnRhZ2UgPSAxMDAgLyBtYXhSYXRpbmcgKiBhdmdSYXRpbmcgKyBcIiVcIjtcbiAgICAgICAgICAgIHBhcmVudC5xdWVyeVNlbGVjdG9yKFwiLndpbGRmaXNoLXJhdGluZ3MtcmF0aW5nLWZvcmVncm91bmRcIikuc3R5bGUud2lkdGggPSBwZXJjZW50YWdlO1xuICAgICAgICB9O1xuICAgIH1cbn1cblxuXG4vKioqKioqKioqKioqKioqKioqKioqXG4gKiBSYXRpbmcgY2xpY2sgZXZlbnRcbiAqKioqKioqKioqKioqKioqKioqKiovXG5mdW5jdGlvbiByYXRpbmdDbGljayhldikge1xuICAgIGV2LnN0b3BQcm9wYWdhdGlvbigpO1xuICAgIGV2LnByZXZlbnREZWZhdWx0KCk7XG4gICAgdmFyIHNjb3JlID0gdGhpcy5nZXRBdHRyaWJ1dGUoJ2RhdGEtc2NvcmUnKTtcbiAgICB2YXIgcmF0aW5nSWQgPSB0aGlzLmdldEF0dHJpYnV0ZSgnZGF0YS1mb3InKTtcbiAgICByYXRlKHJhdGluZ0lkLCBzY29yZSwgdGhpcyk7XG59XG5cblxuLyoqKioqKioqKioqKioqKioqKioqKlxuICogUmF0ZSBpbnN0YW5jZVxuICoqKioqKioqKioqKioqKioqKioqKi9cbmZ1bmN0aW9uIHJhdGUoaWQsIHNjb3JlLCBzZW5kZXIpIHtcbiAgICB2YXIgdXJsID0gJy9yYXRpbmdzLycgKyBpZCArICcvJyArIHNjb3JlICsgJy8nO1xuXG4gICAgcmVzdC5nZXQodXJsLCB7fSwgZnVuY3Rpb24gKHJhdGluZykge1xuICAgICAgICB1cGRhdGVSYXRpbmcocmF0aW5nLCBzZW5kZXIpO1xuICAgIH0sIGZ1bmN0aW9uIChlcnJvcnMpIHtcbiAgICAgICAgc2hvd0Vycm9yKGVycm9ycywgc2VuZGVyKTtcbiAgICB9KTtcbn1cblxuXG5mdW5jdGlvbiBnZXRNYXhSYXRpbmcoZWwpIHtcbiAgICB2YXIgcGFyZW50ID0gdXRpbHMuZmluZFBhcmVudChlbCwgXCJ3aWxkZmlzaC1yYXRpbmdzXCIpO1xuICAgIGlmIChwYXJlbnQpIHtcbiAgICAgICAgcmV0dXJuIHBhcnNlSW50KHBhcmVudC5nZXRBdHRyaWJ1dGUoJ2RhdGEtbWF4LXJhdGluZycpKTtcbiAgICB9XG5cbiAgICByZXR1cm4gLTE7XG59XG5cblxuZnVuY3Rpb24gZ2V0QXZnUmF0aW5nKGVsKSB7XG4gICAgdmFyIHBhcmVudCA9IHV0aWxzLmZpbmRQYXJlbnQoZWwsIFwid2lsZGZpc2gtcmF0aW5nc1wiKTtcbiAgICBpZiAocGFyZW50KSB7XG4gICAgICAgIHJldHVybiBwYXJlbnQuZ2V0QXR0cmlidXRlKCdkYXRhLWF2Zy1yYXRpbmcnKTtcbiAgICB9XG5cbiAgICByZXR1cm4gLTE7XG59XG5cblxuLyoqKioqKioqKioqKioqKioqKioqKlxuICogVXBkYXRlIHJhdGluZ1xuICoqKioqKioqKioqKioqKioqKioqKi9cbmZ1bmN0aW9uIHVwZGF0ZVJhdGluZyhyYXRpbmcsIHNlbmRlcikge1xuICAgIHZhciBwYXJlbnQgPSB1dGlscy5maW5kUGFyZW50KHNlbmRlciwgXCJ3aWxkZmlzaC1yYXRpbmdzXCIpO1xuICAgIGlmIChwYXJlbnQgPT09IHVuZGVmaW5lZCB8fCBwYXJlbnQgPT09IG51bGwpIHtcbiAgICAgICAgcmV0dXJuO1xuICAgIH1cblxuICAgIHBhcmVudC5zZXRBdHRyaWJ1dGUoXCJkYXRhLWF2Zy1yYXRpbmdcIiwgcmF0aW5nLnJhdGluZ19hdmVyYWdlKTtcbiAgICBwYXJlbnQucXVlcnlTZWxlY3RvcihcIi53aWxkZmlzaC1yYXRpbmdzLXJhdGluZy1mb3JlZ3JvdW5kXCIpLnN0eWxlLndpZHRoID0gMTAwIC8gcmF0aW5nLm1heF92YWx1ZSAqIHJhdGluZy5yYXRpbmdfYXZlcmFnZSArIFwiJVwiO1xufVxuXG5cbmZ1bmN0aW9uIHNob3dFcnJvciAoZXJyb3JzLCBzZW5kZXIpIHtcbiAgICB2YXIgcGFyZW50ID0gdXRpbHMuZmluZFBhcmVudChzZW5kZXIsIFwid2lsZGZpc2gtcmF0aW5nc1wiKTtcbiAgICBpZiAocGFyZW50ID09PSB1bmRlZmluZWQgfHwgcGFyZW50ID09PSBudWxsKSB7XG4gICAgICAgIHJldHVybjtcbiAgICB9XG4gICAgcGFyZW50LnF1ZXJ5U2VsZWN0b3IoXCIud2lsZGZpc2gtcmF0aW5ncy1lcnJvcnNcIikuaW5uZXJIVE1MID0gZXJyb3JzLmVycm9yO1xuICAgIHNldFRpbWVvdXQoZnVuY3Rpb24gKCkge1xuICAgICAgICBwYXJlbnQucXVlcnlTZWxlY3RvcihcIi53aWxkZmlzaC1yYXRpbmdzLWVycm9yc1wiKS5pbm5lckhUTUwgPSBcIlwiO1xuICAgIH0sIDI1MDApO1xufVxuXG4vKioqKioqKioqKioqKioqKioqKioqXG4gKiBPbmx5IGluaXRpYWxpc2UgcmF0aW5nc1xuICogaWYgdGhlcmUgaXMgc29tZXRoaW5nIHRvIHJhdGVcbiAqKioqKioqKioqKioqKioqKioqKiovXG5pZiAoZG9jdW1lbnQucXVlcnlTZWxlY3RvcihcIi53aWxkZmlzaC1yYXRpbmdzXCIpKSB7XG4gICAgaW5pdCgpO1xufVxuIiwiLypqc2xpbnQgYnJvd3Nlcjp0cnVlICovXG5cInVzZSBzdHJpY3RcIjtcblxuXG52YXIgZGphbmdvUmVtYXJrUmVzdCA9IHtcbiAgICBnZXRDb29raWU6IGZ1bmN0aW9uIChuYW1lKSB7XG4gICAgICAgIC8vIEZyb20gaHR0cHM6Ly9kb2NzLmRqYW5nb3Byb2plY3QuY29tL2VuLzEuNy9yZWYvY29udHJpYi9jc3JmL1xuICAgICAgICB2YXIgY29va2llVmFsdWUgPSBudWxsLCBjb29raWVzLCBpLCBjb29raWU7XG4gICAgICAgIGlmIChkb2N1bWVudC5jb29raWUgJiYgZG9jdW1lbnQuY29va2llICE9PSAnJykge1xuICAgICAgICAgICAgY29va2llcyA9IGRvY3VtZW50LmNvb2tpZS5zcGxpdCgnOycpO1xuICAgICAgICAgICAgZm9yIChpID0gMDsgaSA8IGNvb2tpZXMubGVuZ3RoOyBpICs9IDEpIHtcbiAgICAgICAgICAgICAgICBjb29raWUgPSBjb29raWVzW2ldLnRyaW0oKTsgLy8gRG9lc24ndCB3b3JrIGluIGFsbCBicm93c2Vyc1xuICAgICAgICAgICAgICAgIC8vIERvZXMgdGhpcyBjb29raWUgc3RyaW5nIGJlZ2luIHdpdGggdGhlIG5hbWUgd2Ugd2FudD9cbiAgICAgICAgICAgICAgICBpZiAoY29va2llLnN1YnN0cmluZygwLCBuYW1lLmxlbmd0aCArIDEpID09PSAobmFtZSArICc9JykpIHtcbiAgICAgICAgICAgICAgICAgICAgY29va2llVmFsdWUgPSBkZWNvZGVVUklDb21wb25lbnQoY29va2llLnN1YnN0cmluZyhuYW1lLmxlbmd0aCArIDEpKTtcbiAgICAgICAgICAgICAgICAgICAgYnJlYWs7XG4gICAgICAgICAgICAgICAgfVxuICAgICAgICAgICAgfVxuICAgICAgICB9XG4gICAgICAgIHJldHVybiBjb29raWVWYWx1ZTtcbiAgICB9LFxuXG4gICAgbWFrZVJlcXVlc3Q6IGZ1bmN0aW9uICh1cmwsIG1ldGhvZCwgc3VjY2VzcywgZmFpbCkge1xuICAgICAgICB1cmwgKz0gXCI/Zm9ybWF0PWpzb25cIjtcbiAgICAgICAgdmFyIHJlcSA9IG5ldyBYTUxIdHRwUmVxdWVzdCgpO1xuICAgICAgICBpZiAocmVxLm92ZXJyaWRlTWltZVR5cGUgIT09IHVuZGVmaW5lZCkge1xuICAgICAgICAgICAgcmVxLm92ZXJyaWRlTWltZVR5cGUoXCJhcHBsaWNhdGlvbi9qc29uXCIpO1xuICAgICAgICB9XG4gICAgICAgIHJlcS5vcGVuKG1ldGhvZCwgdXJsLCB0cnVlKTtcbiAgICAgICAgcmVxLnNldFJlcXVlc3RIZWFkZXIoJ0NvbnRlbnQtVHlwZScsICdhcHBsaWNhdGlvbi9qc29uJyk7XG4gICAgICAgIHJlcS5zZXRSZXF1ZXN0SGVhZGVyKCdYLVJlcXVlc3RlZC1XaXRoJywgJ1hNTEh0dHBSZXF1ZXN0Jyk7XG5cbiAgICAgICAgLy8gV2hlbiBkb25lIHByb2Nlc3NpbmcgZGF0YVxuICAgICAgICByZXEub25yZWFkeXN0YXRlY2hhbmdlID0gZnVuY3Rpb24gKCkge1xuICAgICAgICAgICAgaWYgKHJlcS5yZWFkeVN0YXRlICE9PSA0KSB7XG4gICAgICAgICAgICAgICAgcmV0dXJuO1xuICAgICAgICAgICAgfVxuXG4gICAgICAgICAgICBpZiAocmVxLnN0YXR1cyA+PSAyMDAgJiYgcmVxLnN0YXR1cyA8PSAyOTkpIHtcbiAgICAgICAgICAgICAgICBpZiAoc3VjY2Vzcykge1xuICAgICAgICAgICAgICAgICAgICBpZiAocmVxLnJlc3BvbnNlVGV4dCkge1xuICAgICAgICAgICAgICAgICAgICAgICAgc3VjY2VzcyhKU09OLnBhcnNlKHJlcS5yZXNwb25zZVRleHQpKTtcbiAgICAgICAgICAgICAgICAgICAgfSBlbHNlIHsgc3VjY2VzcygpOyB9XG4gICAgICAgICAgICAgICAgfVxuICAgICAgICAgICAgfSBlbHNlIHtcbiAgICAgICAgICAgICAgICBpZiAoZmFpbCkge1xuICAgICAgICAgICAgICAgICAgICBmYWlsKEpTT04ucGFyc2UocmVxLnJlc3BvbnNlVGV4dCkpO1xuICAgICAgICAgICAgICAgIH1cbiAgICAgICAgICAgIH1cbiAgICAgICAgfTtcblxuICAgICAgICByZXR1cm4gcmVxO1xuICAgIH0sXG5cbiAgICBnZXQ6IGZ1bmN0aW9uICh1cmwsIGRhdGEsIHN1Y2Nlc3MsIGZhaWwpIHtcbiAgICAgICAgdmFyIHJlcSA9IHRoaXMubWFrZVJlcXVlc3QodXJsLCAnR0VUJywgc3VjY2VzcywgZmFpbCk7XG4gICAgICAgIHJlcS5zZW5kKEpTT04uc3RyaW5naWZ5KGRhdGEpKTtcbiAgICB9LFxuXG4gICAgcG9zdDogZnVuY3Rpb24gKHVybCwgZGF0YSwgc3VjY2VzcywgZmFpbCkge1xuICAgICAgICB2YXIgcmVxID0gdGhpcy5tYWtlUmVxdWVzdCh1cmwsICdQT1NUJywgc3VjY2VzcywgZmFpbCk7XG4gICAgICAgIHJlcS5zZXRSZXF1ZXN0SGVhZGVyKFwiWC1DU1JGVG9rZW5cIiwgdGhpcy5nZXRDb29raWUoJ2NzcmZ0b2tlbicpKTtcbiAgICAgICAgcmVxLnNlbmQoSlNPTi5zdHJpbmdpZnkoZGF0YSkpO1xuICAgIH0sXG5cbiAgICBwdXQ6IGZ1bmN0aW9uICh1cmwsIGRhdGEsIHN1Y2Nlc3MsIGZhaWwpIHtcbiAgICAgICAgdmFyIHJlcSA9IHRoaXMubWFrZVJlcXVlc3QodXJsLCAnUFVUJywgc3VjY2VzcywgZmFpbCk7XG4gICAgICAgIHJlcS5zZXRSZXF1ZXN0SGVhZGVyKFwiWC1DU1JGVG9rZW5cIiwgdGhpcy5nZXRDb29raWUoJ2NzcmZ0b2tlbicpKTtcbiAgICAgICAgcmVxLnNlbmQoSlNPTi5zdHJpbmdpZnkoZGF0YSkpO1xuICAgIH0sXG5cbiAgICBwYXRjaDogZnVuY3Rpb24gKHVybCwgZGF0YSwgc3VjY2VzcywgZmFpbCkge1xuICAgICAgICB2YXIgcmVxID0gdGhpcy5tYWtlUmVxdWVzdCh1cmwsICdQQVRDSCcsIHN1Y2Nlc3MsIGZhaWwpO1xuICAgICAgICByZXEuc2V0UmVxdWVzdEhlYWRlcihcIlgtQ1NSRlRva2VuXCIsIHRoaXMuZ2V0Q29va2llKCdjc3JmdG9rZW4nKSk7XG4gICAgICAgIHJlcS5zZW5kKEpTT04uc3RyaW5naWZ5KGRhdGEpKTtcbiAgICB9LFxuXG4gICAgXCJkZWxldGVcIjogZnVuY3Rpb24gKHVybCwgZGF0YSwgc3VjY2VzcywgZmFpbCkge1xuICAgICAgICB2YXIgcmVxID0gdGhpcy5tYWtlUmVxdWVzdCh1cmwsICdERUxFVEUnLCBzdWNjZXNzLCBmYWlsKTtcbiAgICAgICAgcmVxLnNldFJlcXVlc3RIZWFkZXIoXCJYLUNTUkZUb2tlblwiLCB0aGlzLmdldENvb2tpZSgnY3NyZnRva2VuJykpO1xuICAgICAgICByZXEuc2VuZChKU09OLnN0cmluZ2lmeShkYXRhKSk7XG4gICAgfVxufTtcblxuXG5tb2R1bGUuZXhwb3J0cyA9IGRqYW5nb1JlbWFya1Jlc3Q7XG4iLCIvKioqKioqKioqKioqKioqKioqKioqKioqKipcbiAqIENoZWNrIGlmIGFuIGVsZW1lbnQgaGFzIGEgY2xhc3NcbiAqKioqKioqKioqKioqKioqKioqKioqKioqKi9cbmZ1bmN0aW9uIGhhc0NsYXNzIChlbCwgbmFtZSkge1xuICAgIHJldHVybiAoJyAnICsgZWwuY2xhc3NOYW1lICsgJyAnKS5pbmRleE9mKCcgJyArIG5hbWUgKyAnICcpID4gLTE7XG59XG5cblxuLyoqKioqKioqKioqKioqKioqKioqKioqKioqXG4gKiBGaW5kIHBhcmVudCBlbGVtZW50XG4gKioqKioqKioqKioqKioqKioqKioqKioqKiovXG5mdW5jdGlvbiBmaW5kUGFyZW50KGVsLCBjbGFzc05hbWUpIHtcbiAgICB2YXIgcGFyZW50Tm9kZSA9IGVsLnBhcmVudE5vZGU7XG4gICAgd2hpbGUgKGhhc0NsYXNzKHBhcmVudE5vZGUsIGNsYXNzTmFtZSkgPT09IGZhbHNlKSB7XG4gICAgICAgIGlmIChwYXJlbnROb2RlLnBhcmVudE5vZGUgPT09IHVuZGVmaW5lZCkge1xuICAgICAgICAgICAgcmV0dXJuIG51bGw7XG4gICAgICAgIH1cbiAgICAgICAgcGFyZW50Tm9kZSA9IHBhcmVudE5vZGUucGFyZW50Tm9kZTtcbiAgICB9XG4gICAgcmV0dXJuIHBhcmVudE5vZGVcbn1cblxuXG5tb2R1bGUuZXhwb3J0cyA9IHtcbiAgICBoYXNDbGFzczogaGFzQ2xhc3MsXG4gICAgZmluZFBhcmVudDogZmluZFBhcmVudFxufTtcbiJdfQ==
