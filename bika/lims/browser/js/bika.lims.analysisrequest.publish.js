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
                }
            });
        });

        $('#publish_button').click(function(e) {
            var url = window.location.href;
            url += url.indexOf('?') >= 0 ? "&pub=1" : "?pub=1";
            url += "&template="+$('#sel_format').val();
            if ($('#qcvisible').is(':checked')) {
                url += "&qcvisible=1";
            }
            $('#ar_publish_container').animate({opacity:0.4}, 'slow');
            $.ajax({
                url: url,
                type: 'GET',
                success: function(data, textStatus, $XHR){
                    $('#ar_publish_container').fadeOut();
                }
            });
        });

        $('#cancel_button').click(function(e) {
            $('#ar_publish_container').fadeOut();
        });
    }

    function get(name){
       if(name=(new RegExp('[?&]'+encodeURIComponent(name)+'=([^&]*)')).exec(location.search))
          return decodeURIComponent(name[1]);
    }
}
