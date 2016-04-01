/**
 * Controller class for SamplingRound Print View
 */
function SamplingRoundtPrintView() {

    var that = this;
    var referrer_cookie_name = '_rspv';

    that.load = function() {

        // Store referrer in cookie in case it is lost due to a page reload
        var backurl = document.referrer;
        if (backurl) {
            createCookie("sr.print.urlback", backurl);
        } else {
            backurl = readCookie("sr.print.urlback");
            if (!backurl) {
                backurl = portal_url;
            }
        }

        load_barcodes();

        $('#print_button').click(function(e) {
            e.preventDefault();
            window.print();
        });

        $('#cancel_button').click(function(e) {
            e.preventDefault();
            location.href = backurl;
        });

        $('#template').change(function(e) {
            var url = window.location.href;
            var seltpl = $(this).val();
            var selcols = $("#numcols").val();
            $('#samplinground-printview').animate({opacity:0.2}, 'slow');
            $.ajax({
                url: url,
                type: 'POST',
                data: { "template":seltpl,
                        "numcols":selcols}
            })
            .always(function(data) {
                var htmldata = data;
                var cssdata = $(htmldata).find('#report-style').html();
                $('#report-style').html(cssdata);
                htmldata = $(htmldata).find('#samplinground-printview').html();
                $('#samplinground-printview').html(htmldata);
                $('#samplinground-printview').animate({opacity:1}, 'slow');
                load_barcodes();
            });
        });

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
};
}
