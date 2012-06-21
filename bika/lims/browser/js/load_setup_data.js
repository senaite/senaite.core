(function( $ ) {

function progress_bar() {
    setTimeout("progressbar()", 1000);
    var qresult = _pop('_progress', false);
    if (result) {
        progress = result * 1;

        // Progress bar
        $('#progressbar').style.width = progress*1.0/100*300 + 'px';
        top.document.getElementById('progress-bar-message').innerHTML = '&nbsp; (' + (Math.floor(progress*100.0/total)) + '%)';
    }
}

$(document).ready(function(){

});
}(jQuery));
