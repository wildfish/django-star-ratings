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

    for (i = 0; i < ratingActions.length; i += 1) {
        ratingActions[i].addEventListener("click", ratingClick);
    }
}


/*********************
 * Rating click event
 *********************/
function ratingClick(e) {
    e.preventDefault();
    var score = e.target.getAttribute('data-score');
    var ratingId = e.target.getAttribute('data-for');
    rate(ratingId, score, e.target);
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


/*********************
 * Update rating
 *********************/
function updateRating(rating, sender) {
    var parent = utils.findParent(sender, "wildfish-ratings");
    if (parent === undefined || parent === null) {
        return;
    }
    parent.querySelector(".wildfish-ratings-count").innerHTML = rating.rating_count.toString();
    parent.querySelector(".wildfish-ratings-total").innerHTML = rating.rating_total.toString();
    parent.querySelector(".wildfish-ratings-avg").innerHTML = rating.rating_average.toString();
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
        if (parentNode.hasOwnProperty('parentNode') === false) {
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
//# sourceMappingURL=data:application/json;base64,eyJ2ZXJzaW9uIjozLCJzb3VyY2VzIjpbIi4uLy4uLy4uLy4uLy4uLy4uLy4uLy4uLy4uL3Vzci9sb2NhbC9saWIvbm9kZV9tb2R1bGVzL3dhdGNoaWZ5L25vZGVfbW9kdWxlcy9icm93c2VyaWZ5L25vZGVfbW9kdWxlcy9icm93c2VyLXBhY2svX3ByZWx1ZGUuanMiLCJpbmRleC5qcyIsInNyYy9yYXRpbmdzLmpzIiwic3JjL3Jlc3QuanMiLCJzcmMvdXRpbHMuanMiXSwibmFtZXMiOltdLCJtYXBwaW5ncyI6IkFBQUE7QUNBQTs7QUNBQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTs7QUMvREE7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBOztBQ3RGQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQSIsImZpbGUiOiJnZW5lcmF0ZWQuanMiLCJzb3VyY2VSb290IjoiIiwic291cmNlc0NvbnRlbnQiOlsiKGZ1bmN0aW9uIGUodCxuLHIpe2Z1bmN0aW9uIHMobyx1KXtpZighbltvXSl7aWYoIXRbb10pe3ZhciBhPXR5cGVvZiByZXF1aXJlPT1cImZ1bmN0aW9uXCImJnJlcXVpcmU7aWYoIXUmJmEpcmV0dXJuIGEobywhMCk7aWYoaSlyZXR1cm4gaShvLCEwKTt2YXIgZj1uZXcgRXJyb3IoXCJDYW5ub3QgZmluZCBtb2R1bGUgJ1wiK28rXCInXCIpO3Rocm93IGYuY29kZT1cIk1PRFVMRV9OT1RfRk9VTkRcIixmfXZhciBsPW5bb109e2V4cG9ydHM6e319O3Rbb11bMF0uY2FsbChsLmV4cG9ydHMsZnVuY3Rpb24oZSl7dmFyIG49dFtvXVsxXVtlXTtyZXR1cm4gcyhuP246ZSl9LGwsbC5leHBvcnRzLGUsdCxuLHIpfXJldHVybiBuW29dLmV4cG9ydHN9dmFyIGk9dHlwZW9mIHJlcXVpcmU9PVwiZnVuY3Rpb25cIiYmcmVxdWlyZTtmb3IodmFyIG89MDtvPHIubGVuZ3RoO28rKylzKHJbb10pO3JldHVybiBzfSkiLCJyZXF1aXJlKCcuL3NyYy9yYXRpbmdzJykiLCJ2YXIgcmVzdCA9IHJlcXVpcmUoJy4vcmVzdC5qcycpO1xudmFyIHV0aWxzID0gcmVxdWlyZSgnLi91dGlscycpO1xuXG5cbi8qKioqKioqKioqKioqKioqKioqKipcbiAqIEluaXRpYWxpc2UgcmF0aW5nc1xuICoqKioqKioqKioqKioqKioqKioqKi9cbmZ1bmN0aW9uIGluaXQoKSB7XG4gICAgdmFyIHJhdGluZ0FjdGlvbnMgPSBkb2N1bWVudC5xdWVyeVNlbGVjdG9yQWxsKFwiLndpbGRmaXNoLXJhdGluZ3MtcmF0ZS1hY3Rpb25cIiksXG4gICAgICAgIGk7XG5cbiAgICBmb3IgKGkgPSAwOyBpIDwgcmF0aW5nQWN0aW9ucy5sZW5ndGg7IGkgKz0gMSkge1xuICAgICAgICByYXRpbmdBY3Rpb25zW2ldLmFkZEV2ZW50TGlzdGVuZXIoXCJjbGlja1wiLCByYXRpbmdDbGljayk7XG4gICAgfVxufVxuXG5cbi8qKioqKioqKioqKioqKioqKioqKipcbiAqIFJhdGluZyBjbGljayBldmVudFxuICoqKioqKioqKioqKioqKioqKioqKi9cbmZ1bmN0aW9uIHJhdGluZ0NsaWNrKGUpIHtcbiAgICBlLnByZXZlbnREZWZhdWx0KCk7XG4gICAgdmFyIHNjb3JlID0gZS50YXJnZXQuZ2V0QXR0cmlidXRlKCdkYXRhLXNjb3JlJyk7XG4gICAgdmFyIHJhdGluZ0lkID0gZS50YXJnZXQuZ2V0QXR0cmlidXRlKCdkYXRhLWZvcicpO1xuICAgIHJhdGUocmF0aW5nSWQsIHNjb3JlLCBlLnRhcmdldCk7XG59XG5cblxuLyoqKioqKioqKioqKioqKioqKioqKlxuICogUmF0ZSBpbnN0YW5jZVxuICoqKioqKioqKioqKioqKioqKioqKi9cbmZ1bmN0aW9uIHJhdGUoaWQsIHNjb3JlLCBzZW5kZXIpIHtcbiAgICB2YXIgdXJsID0gJy9yYXRpbmdzLycgKyBpZCArICcvJyArIHNjb3JlICsgJy8nO1xuXG4gICAgcmVzdC5nZXQodXJsLCB7fSwgZnVuY3Rpb24gKHJhdGluZykge1xuICAgICAgICB1cGRhdGVSYXRpbmcocmF0aW5nLCBzZW5kZXIpO1xuICAgIH0sIGZ1bmN0aW9uIChlcnJvcnMpIHtcbiAgICAgICAgY29uc29sZS5sb2coZXJyb3JzKTtcbiAgICB9KTtcbn1cblxuXG4vKioqKioqKioqKioqKioqKioqKioqXG4gKiBVcGRhdGUgcmF0aW5nXG4gKioqKioqKioqKioqKioqKioqKioqL1xuZnVuY3Rpb24gdXBkYXRlUmF0aW5nKHJhdGluZywgc2VuZGVyKSB7XG4gICAgdmFyIHBhcmVudCA9IHV0aWxzLmZpbmRQYXJlbnQoc2VuZGVyLCBcIndpbGRmaXNoLXJhdGluZ3NcIik7XG4gICAgaWYgKHBhcmVudCA9PT0gdW5kZWZpbmVkIHx8IHBhcmVudCA9PT0gbnVsbCkge1xuICAgICAgICByZXR1cm47XG4gICAgfVxuICAgIHBhcmVudC5xdWVyeVNlbGVjdG9yKFwiLndpbGRmaXNoLXJhdGluZ3MtY291bnRcIikuaW5uZXJIVE1MID0gcmF0aW5nLnJhdGluZ19jb3VudC50b1N0cmluZygpO1xuICAgIHBhcmVudC5xdWVyeVNlbGVjdG9yKFwiLndpbGRmaXNoLXJhdGluZ3MtdG90YWxcIikuaW5uZXJIVE1MID0gcmF0aW5nLnJhdGluZ190b3RhbC50b1N0cmluZygpO1xuICAgIHBhcmVudC5xdWVyeVNlbGVjdG9yKFwiLndpbGRmaXNoLXJhdGluZ3MtYXZnXCIpLmlubmVySFRNTCA9IHJhdGluZy5yYXRpbmdfYXZlcmFnZS50b1N0cmluZygpO1xufVxuXG5cbi8qKioqKioqKioqKioqKioqKioqKipcbiAqIE9ubHkgaW5pdGlhbGlzZSByYXRpbmdzXG4gKiBpZiB0aGVyZSBpcyBzb21ldGhpbmcgdG8gcmF0ZVxuICoqKioqKioqKioqKioqKioqKioqKi9cbmlmIChkb2N1bWVudC5xdWVyeVNlbGVjdG9yKFwiLndpbGRmaXNoLXJhdGluZ3NcIikpIHtcbiAgICBpbml0KCk7XG59XG4iLCIvKmpzbGludCBicm93c2VyOnRydWUgKi9cblwidXNlIHN0cmljdFwiO1xuXG5cbnZhciBkamFuZ29SZW1hcmtSZXN0ID0ge1xuICAgIGdldENvb2tpZTogZnVuY3Rpb24gKG5hbWUpIHtcbiAgICAgICAgLy8gRnJvbSBodHRwczovL2RvY3MuZGphbmdvcHJvamVjdC5jb20vZW4vMS43L3JlZi9jb250cmliL2NzcmYvXG4gICAgICAgIHZhciBjb29raWVWYWx1ZSA9IG51bGwsIGNvb2tpZXMsIGksIGNvb2tpZTtcbiAgICAgICAgaWYgKGRvY3VtZW50LmNvb2tpZSAmJiBkb2N1bWVudC5jb29raWUgIT09ICcnKSB7XG4gICAgICAgICAgICBjb29raWVzID0gZG9jdW1lbnQuY29va2llLnNwbGl0KCc7Jyk7XG4gICAgICAgICAgICBmb3IgKGkgPSAwOyBpIDwgY29va2llcy5sZW5ndGg7IGkgKz0gMSkge1xuICAgICAgICAgICAgICAgIGNvb2tpZSA9IGNvb2tpZXNbaV0udHJpbSgpOyAvLyBEb2Vzbid0IHdvcmsgaW4gYWxsIGJyb3dzZXJzXG4gICAgICAgICAgICAgICAgLy8gRG9lcyB0aGlzIGNvb2tpZSBzdHJpbmcgYmVnaW4gd2l0aCB0aGUgbmFtZSB3ZSB3YW50P1xuICAgICAgICAgICAgICAgIGlmIChjb29raWUuc3Vic3RyaW5nKDAsIG5hbWUubGVuZ3RoICsgMSkgPT09IChuYW1lICsgJz0nKSkge1xuICAgICAgICAgICAgICAgICAgICBjb29raWVWYWx1ZSA9IGRlY29kZVVSSUNvbXBvbmVudChjb29raWUuc3Vic3RyaW5nKG5hbWUubGVuZ3RoICsgMSkpO1xuICAgICAgICAgICAgICAgICAgICBicmVhaztcbiAgICAgICAgICAgICAgICB9XG4gICAgICAgICAgICB9XG4gICAgICAgIH1cbiAgICAgICAgcmV0dXJuIGNvb2tpZVZhbHVlO1xuICAgIH0sXG5cbiAgICBtYWtlUmVxdWVzdDogZnVuY3Rpb24gKHVybCwgbWV0aG9kLCBzdWNjZXNzLCBmYWlsKSB7XG4gICAgICAgIHVybCArPSBcIj9mb3JtYXQ9anNvblwiO1xuICAgICAgICB2YXIgcmVxID0gbmV3IFhNTEh0dHBSZXF1ZXN0KCk7XG4gICAgICAgIGlmIChyZXEub3ZlcnJpZGVNaW1lVHlwZSAhPT0gdW5kZWZpbmVkKSB7XG4gICAgICAgICAgICByZXEub3ZlcnJpZGVNaW1lVHlwZShcImFwcGxpY2F0aW9uL2pzb25cIik7XG4gICAgICAgIH1cbiAgICAgICAgcmVxLm9wZW4obWV0aG9kLCB1cmwsIHRydWUpO1xuICAgICAgICByZXEuc2V0UmVxdWVzdEhlYWRlcignQ29udGVudC1UeXBlJywgJ2FwcGxpY2F0aW9uL2pzb24nKTtcbiAgICAgICAgcmVxLnNldFJlcXVlc3RIZWFkZXIoJ1gtUmVxdWVzdGVkLVdpdGgnLCAnWE1MSHR0cFJlcXVlc3QnKTtcblxuICAgICAgICAvLyBXaGVuIGRvbmUgcHJvY2Vzc2luZyBkYXRhXG4gICAgICAgIHJlcS5vbnJlYWR5c3RhdGVjaGFuZ2UgPSBmdW5jdGlvbiAoKSB7XG4gICAgICAgICAgICBpZiAocmVxLnJlYWR5U3RhdGUgIT09IDQpIHtcbiAgICAgICAgICAgICAgICByZXR1cm47XG4gICAgICAgICAgICB9XG5cbiAgICAgICAgICAgIGlmIChyZXEuc3RhdHVzID49IDIwMCAmJiByZXEuc3RhdHVzIDw9IDI5OSkge1xuICAgICAgICAgICAgICAgIGlmIChzdWNjZXNzKSB7XG4gICAgICAgICAgICAgICAgICAgIGlmIChyZXEucmVzcG9uc2VUZXh0KSB7XG4gICAgICAgICAgICAgICAgICAgICAgICBzdWNjZXNzKEpTT04ucGFyc2UocmVxLnJlc3BvbnNlVGV4dCkpO1xuICAgICAgICAgICAgICAgICAgICB9IGVsc2UgeyBzdWNjZXNzKCk7IH1cbiAgICAgICAgICAgICAgICB9XG4gICAgICAgICAgICB9IGVsc2Uge1xuICAgICAgICAgICAgICAgIGlmIChmYWlsKSB7XG4gICAgICAgICAgICAgICAgICAgIGZhaWwoSlNPTi5wYXJzZShyZXEucmVzcG9uc2VUZXh0KSk7XG4gICAgICAgICAgICAgICAgfVxuICAgICAgICAgICAgfVxuICAgICAgICB9O1xuXG4gICAgICAgIHJldHVybiByZXE7XG4gICAgfSxcblxuICAgIGdldDogZnVuY3Rpb24gKHVybCwgZGF0YSwgc3VjY2VzcywgZmFpbCkge1xuICAgICAgICB2YXIgcmVxID0gdGhpcy5tYWtlUmVxdWVzdCh1cmwsICdHRVQnLCBzdWNjZXNzLCBmYWlsKTtcbiAgICAgICAgcmVxLnNlbmQoSlNPTi5zdHJpbmdpZnkoZGF0YSkpO1xuICAgIH0sXG5cbiAgICBwb3N0OiBmdW5jdGlvbiAodXJsLCBkYXRhLCBzdWNjZXNzLCBmYWlsKSB7XG4gICAgICAgIHZhciByZXEgPSB0aGlzLm1ha2VSZXF1ZXN0KHVybCwgJ1BPU1QnLCBzdWNjZXNzLCBmYWlsKTtcbiAgICAgICAgcmVxLnNldFJlcXVlc3RIZWFkZXIoXCJYLUNTUkZUb2tlblwiLCB0aGlzLmdldENvb2tpZSgnY3NyZnRva2VuJykpO1xuICAgICAgICByZXEuc2VuZChKU09OLnN0cmluZ2lmeShkYXRhKSk7XG4gICAgfSxcblxuICAgIHB1dDogZnVuY3Rpb24gKHVybCwgZGF0YSwgc3VjY2VzcywgZmFpbCkge1xuICAgICAgICB2YXIgcmVxID0gdGhpcy5tYWtlUmVxdWVzdCh1cmwsICdQVVQnLCBzdWNjZXNzLCBmYWlsKTtcbiAgICAgICAgcmVxLnNldFJlcXVlc3RIZWFkZXIoXCJYLUNTUkZUb2tlblwiLCB0aGlzLmdldENvb2tpZSgnY3NyZnRva2VuJykpO1xuICAgICAgICByZXEuc2VuZChKU09OLnN0cmluZ2lmeShkYXRhKSk7XG4gICAgfSxcblxuICAgIHBhdGNoOiBmdW5jdGlvbiAodXJsLCBkYXRhLCBzdWNjZXNzLCBmYWlsKSB7XG4gICAgICAgIHZhciByZXEgPSB0aGlzLm1ha2VSZXF1ZXN0KHVybCwgJ1BBVENIJywgc3VjY2VzcywgZmFpbCk7XG4gICAgICAgIHJlcS5zZXRSZXF1ZXN0SGVhZGVyKFwiWC1DU1JGVG9rZW5cIiwgdGhpcy5nZXRDb29raWUoJ2NzcmZ0b2tlbicpKTtcbiAgICAgICAgcmVxLnNlbmQoSlNPTi5zdHJpbmdpZnkoZGF0YSkpO1xuICAgIH0sXG5cbiAgICBcImRlbGV0ZVwiOiBmdW5jdGlvbiAodXJsLCBkYXRhLCBzdWNjZXNzLCBmYWlsKSB7XG4gICAgICAgIHZhciByZXEgPSB0aGlzLm1ha2VSZXF1ZXN0KHVybCwgJ0RFTEVURScsIHN1Y2Nlc3MsIGZhaWwpO1xuICAgICAgICByZXEuc2V0UmVxdWVzdEhlYWRlcihcIlgtQ1NSRlRva2VuXCIsIHRoaXMuZ2V0Q29va2llKCdjc3JmdG9rZW4nKSk7XG4gICAgICAgIHJlcS5zZW5kKEpTT04uc3RyaW5naWZ5KGRhdGEpKTtcbiAgICB9XG59O1xuXG5cbm1vZHVsZS5leHBvcnRzID0gZGphbmdvUmVtYXJrUmVzdDtcbiIsIi8qKioqKioqKioqKioqKioqKioqKioqKioqKlxuICogQ2hlY2sgaWYgYW4gZWxlbWVudCBoYXMgYSBjbGFzc1xuICoqKioqKioqKioqKioqKioqKioqKioqKioqL1xuZnVuY3Rpb24gaGFzQ2xhc3MgKGVsLCBuYW1lKSB7XG4gICAgcmV0dXJuICgnICcgKyBlbC5jbGFzc05hbWUgKyAnICcpLmluZGV4T2YoJyAnICsgbmFtZSArICcgJykgPiAtMTtcbn1cblxuXG4vKioqKioqKioqKioqKioqKioqKioqKioqKipcbiAqIEZpbmQgcGFyZW50IGVsZW1lbnRcbiAqKioqKioqKioqKioqKioqKioqKioqKioqKi9cbmZ1bmN0aW9uIGZpbmRQYXJlbnQoZWwsIGNsYXNzTmFtZSkge1xuICAgIHZhciBwYXJlbnROb2RlID0gZWwucGFyZW50Tm9kZTtcbiAgICB3aGlsZSAoaGFzQ2xhc3MocGFyZW50Tm9kZSwgY2xhc3NOYW1lKSA9PT0gZmFsc2UpIHtcbiAgICAgICAgaWYgKHBhcmVudE5vZGUuaGFzT3duUHJvcGVydHkoJ3BhcmVudE5vZGUnKSA9PT0gZmFsc2UpIHtcbiAgICAgICAgICAgIHJldHVybiBudWxsO1xuICAgICAgICB9XG4gICAgICAgIHBhcmVudE5vZGUgPSBwYXJlbnROb2RlLnBhcmVudE5vZGU7XG4gICAgfVxuICAgIHJldHVybiBwYXJlbnROb2RlXG59XG5cblxubW9kdWxlLmV4cG9ydHMgPSB7XG4gICAgaGFzQ2xhc3M6IGhhc0NsYXNzLFxuICAgIGZpbmRQYXJlbnQ6IGZpbmRQYXJlbnRcbn07XG4iXX0=
