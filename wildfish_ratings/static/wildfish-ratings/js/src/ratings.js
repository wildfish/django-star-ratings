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
