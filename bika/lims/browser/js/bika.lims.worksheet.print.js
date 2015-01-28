/**
 * Controller class for Worksheed Print View
 */
function WorksheetPrintView() {

    var that = this;
    var referrer_cookie_name = '_wspv';

    /**
     * Entry-point method for AnalysisRequestPublishView
     */
    that.load = function() {

        // Store referrer in cookie in case it is lost due to a page reload
        var backurl = document.referrer;
        if (backurl) {
            var d = new Date();
            d.setTime(d.getTime() + (1*24*60*60*1000));
            document.cookie = referrer_cookie_name + '=' + document.referrer + '; expires=' + d.toGMTString() + '; path=/';
        } else {
            var cookies = document.cookie.split(';');
            for(var i=0; i<cookies.length; i++) {
                var cookie = cookies[i];
                while (cookie.charAt(0)==' ') {
                    cookie = cookie.substring(1);
                }
                if (cookie.indexOf(referrer_cookie_name) != -1) {
                    backurl = cookie.substring(referrer_cookie_name.length+1, cookie.length);
                    break;
                }
            }
            // Fallback to portal_url instead of staying inside publish.
            if (!backurl) {
                backurl = portal_url;
            }
        }

        load_barcodes();

    }

    function get(name){
       if(name=(new RegExp('[?&]'+encodeURIComponent(name)+'=([^&]*)')).exec(location.search))
          return decodeURIComponent(name[1]);
    }

    function load_barcodes() {
        // Barcode generator
        $('.barcode').each(function() {
            var id = $(this).attr('data-id');
            var code = $(this).attr('data-code');
            var barHeight = $(this).attr('data-barHeight');
            var addQuietZone = $(this).attr('data-addQuietZone');
            var showHRI = $(this).attr('data-showHRI');
            $(this).barcode(id, code,
                            {'barHeight': parseInt(barHeight),
                             'addQuietZone': Boolean(addQuietZone),
                             'showHRI': Boolean(showHRI) });
        });
    }
}
