/**
 * Controller class for Analysis Service Edit view
 */
function AnalysisRequestPublishView() {

    window.jarn.i18n.loadCatalog("bika");
    var _ = window.jarn.i18n.MessageFactory("bika");

    var that = this;

    var report_format    = $('#ar_publish_container #sel_format');
    var report_container = $('#ar_publish_container #report');

    /**
     * Entry-point method for AnalysisRequestPublishView
     */
    that.load = function() {

        // Smooth scroll to content
        $('#ar_publish_container #ar_publish_summary a[href^="#"]').click(function(e) {
            e.preventDefault();
            var anchor = $(this).attr('href');
            var offset = $(anchor).first().offset().top - 20;
            $('html,body').animate({scrollTop: offset},'slow');
        });

        $('#qcvisible').click(function(e) {
            var url = window.location.href;
            if ($('#qcvisible').is(':checked')) {
                url += url.indexOf('?') >= 0 ? "&qcvisible=1" : "?qcvisible=1";
            }
            $('#report').animate({opacity:0.4}, 'slow');
            $.ajax({
                url: url,
                type: 'GET',
                success: function(data, textStatus, $XHR){
                    var htmldata = data;
                    htmldata = $(htmldata).find('#report').html();
                    $('#report').html(htmldata);
                    $('#report').animate({opacity:1}, 'slow');
                    load_barcodes();
                }
            });
        });

        $('#publish_button').click(function(e) {
            var url = window.location.href;
            var qcvisible = $('#qcvisible').is(':checked') ? 1 : 0;
            var template = $('#self_format').val();
            $('#ar_publish_container').animate({opacity:0.4}, 'slow');
            var count = $('#ar_publish_container #report .ar_publish_body').length;
            $('#ar_publish_container #report .ar_publish_body').each(function(){
                var rephtml = $(this).clone().wrap('<div>').parent().html();
                var repstyle = $('#report-style').clone().wrap('<div>').parent().html();
                $.ajax({
                    url: url,
                    type: 'POST',
                    async: false,
                    data: { "publish":1,
                            "id":$(this).attr('id'),
                            "uid":$(this).attr('uid'),
                            "html": rephtml,
                            "style": repstyle}
                })
                .always(function(){
                    if (!--count) {
                        location.href=document.referrer;
                    }
                });
            });
        });

        $('#cancel_button').click(function(e) {
            location.href=document.referrer;
        });

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
