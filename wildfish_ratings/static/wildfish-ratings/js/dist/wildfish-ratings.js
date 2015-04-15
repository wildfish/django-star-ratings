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
        currentRatings = document.querySelectorAll(".wildfish-ratings-current-rating"),
        i;

    // Add click events to stars
    for (i = 0; i < ratingActions.length; i += 1) {
        ratingActions[i].addEventListener("click", ratingClick);
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
//# sourceMappingURL=data:application/json;base64,eyJ2ZXJzaW9uIjozLCJzb3VyY2VzIjpbIi4uLy4uLy4uLy4uLy4uLy4uLy4uLy4uLy4uL3Vzci9sb2NhbC9saWIvbm9kZV9tb2R1bGVzL3dhdGNoaWZ5L25vZGVfbW9kdWxlcy9icm93c2VyaWZ5L25vZGVfbW9kdWxlcy9icm93c2VyLXBhY2svX3ByZWx1ZGUuanMiLCJpbmRleC5qcyIsInNyYy9yYXRpbmdzLmpzIiwic3JjL3Jlc3QuanMiLCJzcmMvdXRpbHMuanMiXSwibmFtZXMiOltdLCJtYXBwaW5ncyI6IkFBQUE7QUNBQTs7QUNBQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBOztBQ25FQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7O0FDdEZBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBIiwiZmlsZSI6ImdlbmVyYXRlZC5qcyIsInNvdXJjZVJvb3QiOiIiLCJzb3VyY2VzQ29udGVudCI6WyIoZnVuY3Rpb24gZSh0LG4scil7ZnVuY3Rpb24gcyhvLHUpe2lmKCFuW29dKXtpZighdFtvXSl7dmFyIGE9dHlwZW9mIHJlcXVpcmU9PVwiZnVuY3Rpb25cIiYmcmVxdWlyZTtpZighdSYmYSlyZXR1cm4gYShvLCEwKTtpZihpKXJldHVybiBpKG8sITApO3ZhciBmPW5ldyBFcnJvcihcIkNhbm5vdCBmaW5kIG1vZHVsZSAnXCIrbytcIidcIik7dGhyb3cgZi5jb2RlPVwiTU9EVUxFX05PVF9GT1VORFwiLGZ9dmFyIGw9bltvXT17ZXhwb3J0czp7fX07dFtvXVswXS5jYWxsKGwuZXhwb3J0cyxmdW5jdGlvbihlKXt2YXIgbj10W29dWzFdW2VdO3JldHVybiBzKG4/bjplKX0sbCxsLmV4cG9ydHMsZSx0LG4scil9cmV0dXJuIG5bb10uZXhwb3J0c312YXIgaT10eXBlb2YgcmVxdWlyZT09XCJmdW5jdGlvblwiJiZyZXF1aXJlO2Zvcih2YXIgbz0wO288ci5sZW5ndGg7bysrKXMocltvXSk7cmV0dXJuIHN9KSIsInJlcXVpcmUoJy4vc3JjL3JhdGluZ3MnKSIsInZhciByZXN0ID0gcmVxdWlyZSgnLi9yZXN0LmpzJyk7XG52YXIgdXRpbHMgPSByZXF1aXJlKCcuL3V0aWxzJyk7XG5cblxuLyoqKioqKioqKioqKioqKioqKioqKlxuICogSW5pdGlhbGlzZSByYXRpbmdzXG4gKioqKioqKioqKioqKioqKioqKioqL1xuZnVuY3Rpb24gaW5pdCgpIHtcbiAgICB2YXIgcmF0aW5nQWN0aW9ucyA9IGRvY3VtZW50LnF1ZXJ5U2VsZWN0b3JBbGwoXCIud2lsZGZpc2gtcmF0aW5ncy1yYXRlLWFjdGlvblwiKSxcbiAgICAgICAgY3VycmVudFJhdGluZ3MgPSBkb2N1bWVudC5xdWVyeVNlbGVjdG9yQWxsKFwiLndpbGRmaXNoLXJhdGluZ3MtY3VycmVudC1yYXRpbmdcIiksXG4gICAgICAgIGk7XG5cbiAgICAvLyBBZGQgY2xpY2sgZXZlbnRzIHRvIHN0YXJzXG4gICAgZm9yIChpID0gMDsgaSA8IHJhdGluZ0FjdGlvbnMubGVuZ3RoOyBpICs9IDEpIHtcbiAgICAgICAgcmF0aW5nQWN0aW9uc1tpXS5hZGRFdmVudExpc3RlbmVyKFwiY2xpY2tcIiwgcmF0aW5nQ2xpY2spO1xuICAgIH1cbn1cblxuXG4vKioqKioqKioqKioqKioqKioqKioqXG4gKiBSYXRpbmcgY2xpY2sgZXZlbnRcbiAqKioqKioqKioqKioqKioqKioqKiovXG5mdW5jdGlvbiByYXRpbmdDbGljayhldikge1xuICAgIGV2LnN0b3BQcm9wYWdhdGlvbigpO1xuICAgIGV2LnByZXZlbnREZWZhdWx0KCk7XG4gICAgdmFyIHNjb3JlID0gdGhpcy5nZXRBdHRyaWJ1dGUoJ2RhdGEtc2NvcmUnKTtcbiAgICB2YXIgcmF0aW5nSWQgPSB0aGlzLmdldEF0dHJpYnV0ZSgnZGF0YS1mb3InKTtcbiAgICByYXRlKHJhdGluZ0lkLCBzY29yZSwgdGhpcyk7XG59XG5cblxuLyoqKioqKioqKioqKioqKioqKioqKlxuICogUmF0ZSBpbnN0YW5jZVxuICoqKioqKioqKioqKioqKioqKioqKi9cbmZ1bmN0aW9uIHJhdGUoaWQsIHNjb3JlLCBzZW5kZXIpIHtcbiAgICB2YXIgdXJsID0gJy9yYXRpbmdzLycgKyBpZCArICcvJyArIHNjb3JlICsgJy8nO1xuXG4gICAgcmVzdC5nZXQodXJsLCB7fSwgZnVuY3Rpb24gKHJhdGluZykge1xuICAgICAgICB1cGRhdGVSYXRpbmcocmF0aW5nLCBzZW5kZXIpO1xuICAgIH0sIGZ1bmN0aW9uIChlcnJvcnMpIHtcbiAgICAgICAgY29uc29sZS5sb2coZXJyb3JzKTtcbiAgICB9KTtcbn1cblxuXG4vKioqKioqKioqKioqKioqKioqKioqXG4gKiBVcGRhdGUgcmF0aW5nXG4gKioqKioqKioqKioqKioqKioqKioqL1xuZnVuY3Rpb24gdXBkYXRlUmF0aW5nKHJhdGluZywgc2VuZGVyKSB7XG4gICAgdmFyIHBhcmVudCA9IHV0aWxzLmZpbmRQYXJlbnQoc2VuZGVyLCBcIndpbGRmaXNoLXJhdGluZ3NcIik7XG4gICAgaWYgKHBhcmVudCA9PT0gdW5kZWZpbmVkIHx8IHBhcmVudCA9PT0gbnVsbCkge1xuICAgICAgICByZXR1cm47XG4gICAgfVxuICAgIHBhcmVudC5xdWVyeVNlbGVjdG9yKFwiLndpbGRmaXNoLXJhdGluZ3MtY291bnRcIikuaW5uZXJIVE1MID0gcmF0aW5nLnJhdGluZ19jb3VudC50b1N0cmluZygpO1xuICAgIHBhcmVudC5xdWVyeVNlbGVjdG9yKFwiLndpbGRmaXNoLXJhdGluZ3MtdG90YWxcIikuaW5uZXJIVE1MID0gcmF0aW5nLnJhdGluZ190b3RhbC50b1N0cmluZygpO1xuICAgIHBhcmVudC5xdWVyeVNlbGVjdG9yKFwiLndpbGRmaXNoLXJhdGluZ3MtYXZnXCIpLmlubmVySFRNTCA9IHJhdGluZy5yYXRpbmdfYXZlcmFnZS50b1N0cmluZygpO1xuICAgIHBhcmVudC5xdWVyeVNlbGVjdG9yKFwiLndpbGRmaXNoLXJhdGluZ3MtcmF0aW5nLWZvcmVncm91bmRcIikuc3R5bGUud2lkdGggPSAxMDAgLyByYXRpbmcubWF4X3ZhbHVlICogcmF0aW5nLnJhdGluZ19hdmVyYWdlICsgXCIlXCI7XG59XG5cblxuLyoqKioqKioqKioqKioqKioqKioqKlxuICogT25seSBpbml0aWFsaXNlIHJhdGluZ3NcbiAqIGlmIHRoZXJlIGlzIHNvbWV0aGluZyB0byByYXRlXG4gKioqKioqKioqKioqKioqKioqKioqL1xuaWYgKGRvY3VtZW50LnF1ZXJ5U2VsZWN0b3IoXCIud2lsZGZpc2gtcmF0aW5nc1wiKSkge1xuICAgIGluaXQoKTtcbn1cbiIsIi8qanNsaW50IGJyb3dzZXI6dHJ1ZSAqL1xuXCJ1c2Ugc3RyaWN0XCI7XG5cblxudmFyIGRqYW5nb1JlbWFya1Jlc3QgPSB7XG4gICAgZ2V0Q29va2llOiBmdW5jdGlvbiAobmFtZSkge1xuICAgICAgICAvLyBGcm9tIGh0dHBzOi8vZG9jcy5kamFuZ29wcm9qZWN0LmNvbS9lbi8xLjcvcmVmL2NvbnRyaWIvY3NyZi9cbiAgICAgICAgdmFyIGNvb2tpZVZhbHVlID0gbnVsbCwgY29va2llcywgaSwgY29va2llO1xuICAgICAgICBpZiAoZG9jdW1lbnQuY29va2llICYmIGRvY3VtZW50LmNvb2tpZSAhPT0gJycpIHtcbiAgICAgICAgICAgIGNvb2tpZXMgPSBkb2N1bWVudC5jb29raWUuc3BsaXQoJzsnKTtcbiAgICAgICAgICAgIGZvciAoaSA9IDA7IGkgPCBjb29raWVzLmxlbmd0aDsgaSArPSAxKSB7XG4gICAgICAgICAgICAgICAgY29va2llID0gY29va2llc1tpXS50cmltKCk7IC8vIERvZXNuJ3Qgd29yayBpbiBhbGwgYnJvd3NlcnNcbiAgICAgICAgICAgICAgICAvLyBEb2VzIHRoaXMgY29va2llIHN0cmluZyBiZWdpbiB3aXRoIHRoZSBuYW1lIHdlIHdhbnQ/XG4gICAgICAgICAgICAgICAgaWYgKGNvb2tpZS5zdWJzdHJpbmcoMCwgbmFtZS5sZW5ndGggKyAxKSA9PT0gKG5hbWUgKyAnPScpKSB7XG4gICAgICAgICAgICAgICAgICAgIGNvb2tpZVZhbHVlID0gZGVjb2RlVVJJQ29tcG9uZW50KGNvb2tpZS5zdWJzdHJpbmcobmFtZS5sZW5ndGggKyAxKSk7XG4gICAgICAgICAgICAgICAgICAgIGJyZWFrO1xuICAgICAgICAgICAgICAgIH1cbiAgICAgICAgICAgIH1cbiAgICAgICAgfVxuICAgICAgICByZXR1cm4gY29va2llVmFsdWU7XG4gICAgfSxcblxuICAgIG1ha2VSZXF1ZXN0OiBmdW5jdGlvbiAodXJsLCBtZXRob2QsIHN1Y2Nlc3MsIGZhaWwpIHtcbiAgICAgICAgdXJsICs9IFwiP2Zvcm1hdD1qc29uXCI7XG4gICAgICAgIHZhciByZXEgPSBuZXcgWE1MSHR0cFJlcXVlc3QoKTtcbiAgICAgICAgaWYgKHJlcS5vdmVycmlkZU1pbWVUeXBlICE9PSB1bmRlZmluZWQpIHtcbiAgICAgICAgICAgIHJlcS5vdmVycmlkZU1pbWVUeXBlKFwiYXBwbGljYXRpb24vanNvblwiKTtcbiAgICAgICAgfVxuICAgICAgICByZXEub3BlbihtZXRob2QsIHVybCwgdHJ1ZSk7XG4gICAgICAgIHJlcS5zZXRSZXF1ZXN0SGVhZGVyKCdDb250ZW50LVR5cGUnLCAnYXBwbGljYXRpb24vanNvbicpO1xuICAgICAgICByZXEuc2V0UmVxdWVzdEhlYWRlcignWC1SZXF1ZXN0ZWQtV2l0aCcsICdYTUxIdHRwUmVxdWVzdCcpO1xuXG4gICAgICAgIC8vIFdoZW4gZG9uZSBwcm9jZXNzaW5nIGRhdGFcbiAgICAgICAgcmVxLm9ucmVhZHlzdGF0ZWNoYW5nZSA9IGZ1bmN0aW9uICgpIHtcbiAgICAgICAgICAgIGlmIChyZXEucmVhZHlTdGF0ZSAhPT0gNCkge1xuICAgICAgICAgICAgICAgIHJldHVybjtcbiAgICAgICAgICAgIH1cblxuICAgICAgICAgICAgaWYgKHJlcS5zdGF0dXMgPj0gMjAwICYmIHJlcS5zdGF0dXMgPD0gMjk5KSB7XG4gICAgICAgICAgICAgICAgaWYgKHN1Y2Nlc3MpIHtcbiAgICAgICAgICAgICAgICAgICAgaWYgKHJlcS5yZXNwb25zZVRleHQpIHtcbiAgICAgICAgICAgICAgICAgICAgICAgIHN1Y2Nlc3MoSlNPTi5wYXJzZShyZXEucmVzcG9uc2VUZXh0KSk7XG4gICAgICAgICAgICAgICAgICAgIH0gZWxzZSB7IHN1Y2Nlc3MoKTsgfVxuICAgICAgICAgICAgICAgIH1cbiAgICAgICAgICAgIH0gZWxzZSB7XG4gICAgICAgICAgICAgICAgaWYgKGZhaWwpIHtcbiAgICAgICAgICAgICAgICAgICAgZmFpbChKU09OLnBhcnNlKHJlcS5yZXNwb25zZVRleHQpKTtcbiAgICAgICAgICAgICAgICB9XG4gICAgICAgICAgICB9XG4gICAgICAgIH07XG5cbiAgICAgICAgcmV0dXJuIHJlcTtcbiAgICB9LFxuXG4gICAgZ2V0OiBmdW5jdGlvbiAodXJsLCBkYXRhLCBzdWNjZXNzLCBmYWlsKSB7XG4gICAgICAgIHZhciByZXEgPSB0aGlzLm1ha2VSZXF1ZXN0KHVybCwgJ0dFVCcsIHN1Y2Nlc3MsIGZhaWwpO1xuICAgICAgICByZXEuc2VuZChKU09OLnN0cmluZ2lmeShkYXRhKSk7XG4gICAgfSxcblxuICAgIHBvc3Q6IGZ1bmN0aW9uICh1cmwsIGRhdGEsIHN1Y2Nlc3MsIGZhaWwpIHtcbiAgICAgICAgdmFyIHJlcSA9IHRoaXMubWFrZVJlcXVlc3QodXJsLCAnUE9TVCcsIHN1Y2Nlc3MsIGZhaWwpO1xuICAgICAgICByZXEuc2V0UmVxdWVzdEhlYWRlcihcIlgtQ1NSRlRva2VuXCIsIHRoaXMuZ2V0Q29va2llKCdjc3JmdG9rZW4nKSk7XG4gICAgICAgIHJlcS5zZW5kKEpTT04uc3RyaW5naWZ5KGRhdGEpKTtcbiAgICB9LFxuXG4gICAgcHV0OiBmdW5jdGlvbiAodXJsLCBkYXRhLCBzdWNjZXNzLCBmYWlsKSB7XG4gICAgICAgIHZhciByZXEgPSB0aGlzLm1ha2VSZXF1ZXN0KHVybCwgJ1BVVCcsIHN1Y2Nlc3MsIGZhaWwpO1xuICAgICAgICByZXEuc2V0UmVxdWVzdEhlYWRlcihcIlgtQ1NSRlRva2VuXCIsIHRoaXMuZ2V0Q29va2llKCdjc3JmdG9rZW4nKSk7XG4gICAgICAgIHJlcS5zZW5kKEpTT04uc3RyaW5naWZ5KGRhdGEpKTtcbiAgICB9LFxuXG4gICAgcGF0Y2g6IGZ1bmN0aW9uICh1cmwsIGRhdGEsIHN1Y2Nlc3MsIGZhaWwpIHtcbiAgICAgICAgdmFyIHJlcSA9IHRoaXMubWFrZVJlcXVlc3QodXJsLCAnUEFUQ0gnLCBzdWNjZXNzLCBmYWlsKTtcbiAgICAgICAgcmVxLnNldFJlcXVlc3RIZWFkZXIoXCJYLUNTUkZUb2tlblwiLCB0aGlzLmdldENvb2tpZSgnY3NyZnRva2VuJykpO1xuICAgICAgICByZXEuc2VuZChKU09OLnN0cmluZ2lmeShkYXRhKSk7XG4gICAgfSxcblxuICAgIFwiZGVsZXRlXCI6IGZ1bmN0aW9uICh1cmwsIGRhdGEsIHN1Y2Nlc3MsIGZhaWwpIHtcbiAgICAgICAgdmFyIHJlcSA9IHRoaXMubWFrZVJlcXVlc3QodXJsLCAnREVMRVRFJywgc3VjY2VzcywgZmFpbCk7XG4gICAgICAgIHJlcS5zZXRSZXF1ZXN0SGVhZGVyKFwiWC1DU1JGVG9rZW5cIiwgdGhpcy5nZXRDb29raWUoJ2NzcmZ0b2tlbicpKTtcbiAgICAgICAgcmVxLnNlbmQoSlNPTi5zdHJpbmdpZnkoZGF0YSkpO1xuICAgIH1cbn07XG5cblxubW9kdWxlLmV4cG9ydHMgPSBkamFuZ29SZW1hcmtSZXN0O1xuIiwiLyoqKioqKioqKioqKioqKioqKioqKioqKioqXG4gKiBDaGVjayBpZiBhbiBlbGVtZW50IGhhcyBhIGNsYXNzXG4gKioqKioqKioqKioqKioqKioqKioqKioqKiovXG5mdW5jdGlvbiBoYXNDbGFzcyAoZWwsIG5hbWUpIHtcbiAgICByZXR1cm4gKCcgJyArIGVsLmNsYXNzTmFtZSArICcgJykuaW5kZXhPZignICcgKyBuYW1lICsgJyAnKSA+IC0xO1xufVxuXG5cbi8qKioqKioqKioqKioqKioqKioqKioqKioqKlxuICogRmluZCBwYXJlbnQgZWxlbWVudFxuICoqKioqKioqKioqKioqKioqKioqKioqKioqL1xuZnVuY3Rpb24gZmluZFBhcmVudChlbCwgY2xhc3NOYW1lKSB7XG4gICAgdmFyIHBhcmVudE5vZGUgPSBlbC5wYXJlbnROb2RlO1xuICAgIHdoaWxlIChoYXNDbGFzcyhwYXJlbnROb2RlLCBjbGFzc05hbWUpID09PSBmYWxzZSkge1xuICAgICAgICBpZiAocGFyZW50Tm9kZS5oYXNPd25Qcm9wZXJ0eSgncGFyZW50Tm9kZScpID09PSBmYWxzZSkge1xuICAgICAgICAgICAgcmV0dXJuIG51bGw7XG4gICAgICAgIH1cbiAgICAgICAgcGFyZW50Tm9kZSA9IHBhcmVudE5vZGUucGFyZW50Tm9kZTtcbiAgICB9XG4gICAgcmV0dXJuIHBhcmVudE5vZGVcbn1cblxuXG5tb2R1bGUuZXhwb3J0cyA9IHtcbiAgICBoYXNDbGFzczogaGFzQ2xhc3MsXG4gICAgZmluZFBhcmVudDogZmluZFBhcmVudFxufTtcbiJdfQ==
