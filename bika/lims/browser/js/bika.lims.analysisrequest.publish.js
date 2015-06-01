/**
 * Controller class for Analysis Service Edit view
 */
function AnalysisRequestPublishView() {

    var that = this;

    var report_format    = $('#ar_publish_container #sel_format');
    var report_container = $('#ar_publish_container #report');

    var referrer_cookie_name = '_arpv';

    var layouts_size = {layout_a4: 'A4', layout_letter: 'letter'};

    var layouts_mm = {layout_a4:     [210, 297],
                      layout_letter: [216, 279]};

    var layouts_margin = {layout_a4:     [15, 15, 20, 15],
                          layout_letter: [15, 15, 20, 15]};
    var header_height = 0;
    var footer_height = 0;
    var header_html = '';
    var footer_html = '';
    var current_layout = 'layout_a4';


    /**
     * Entry-point method for AnalysisRequestPublishView
     */
    that.load = function() {

        load_barcodes();

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

        // Smooth scroll to content
        $('#ar_publish_container #ar_publish_summary a[href^="#"]').click(function(e) {
            e.preventDefault();
            var anchor = $(this).attr('href');
            var offset = $(anchor).first().offset().top - 20;
            $('html,body').animate({scrollTop: offset},'slow');
        });

        $('#sel_format').change(function(e) {
            reloadReport();
        });

        $('#qcvisible').click(function(e) {
            reloadReport();
        });

        $('#hvisible').click(function(e) {
            reloadReport();
        });

        $('#sel_layout').change(function(e) {
            $('body').removeClass($('body').attr('data-layout'));
            $('body').attr('data-layout', $(this).val());
            $('body').addClass($(this).val());
            reloadReport();
        });

        $('#publish_button').click(function(e) {
            var url = window.location.href;
            var qcvisible = $('#qcvisible').is(':checked') ? 1 : 0;
            var hvisible = $('#hvisible').is(':checked') ? 1 : 0;
            var template = $('#sel_format').val();
            $('#ar_publish_container').animate({opacity:0.4}, 'slow');
            var count = $('#ar_publish_container #report .ar_publish_body').length;
            $('#ar_publish_container #report .ar_publish_body').each(function(){
                var rephtml = $(this).clone().wrap('<div>').parent().html();
                var repstyle = $('#report-style').clone().wrap('<div>').parent().html();
                repstyle += $('#layout-style').clone().wrap('<div>').parent().html();
                repstyle += $('#layout-print').clone().wrap('<div>').parent().html();
                $.ajax({
                    url: url,
                    type: 'POST',
                    async: true,
                    data: { "publish":1,
                            "id":$(this).attr('id'),
                            "uid":$(this).attr('uid'),
                            "html": rephtml,
                            "template": template,
                            "qcvisible": qcvisible,
                            "hvisible": hvisible,
                            "style": repstyle}
                })
                .always(function(){
                    if (!--count) {
                        location.href=backurl;
                    }
                });
            });
        });

        $('#cancel_button').click(function(e) {
            location.href=backurl;
        });

        //load_pagination();

        var invalidbackurl = window.portal_url + '/++resource++bika.lims.images/report_invalid_back.png';
        $('.ar-invalid').css('background', "url('"+invalidbackurl+"') repeat scroll #ffffff");

        var provisbackurl = window.portal_url + '/++resource++bika.lims.images/report_provisional_back.png';
        $('.ar-provisional').css('background', "url('"+provisbackurl+"') repeat scroll #ffffff");

        $('#sel_format_info').click(function(e) {
            e.preventDefault();
            $('#sel_format_info_pane').toggle();
        });
        reloadReport();
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

    function load_pagination() {
        $(".paginated-report").each(function(i) {
            var layout = layouts[$('#sel_layout').val()];
            if ($('.page-footer').length > 0) {
                var hpf = $('.page-footer').css('margin-top',0).height();
            } else {
                $(this).css('height', layout[1]);
            }
        });

        $(".paginated-report").each(function(i) {
            var numpages = $(this).find('.page-footer').length;
            $(this).find('.page-total-count').html(numpages);
            $(this).find('.page-current-num').each(function(i) {
                $(this).html(i+1);
            });
        });
    }

    function reloadReport() {
        var url = window.location.href;
        var template = $('#sel_format').val();
        var qcvisible = $('#qcvisible').is(':checked') ? '1' : '0';
        var hvisible = $('#hvisible').is(':checked') ? '1' : '0';
        $('#report').fadeTo('fast', 0.4);
        //$('#report').animate({opacity:0.4}, 'slow');
        $.ajax({
            url: url,
            type: 'POST',
            async: true,
            data: { "template": template,
                    "qcvisible": qcvisible,
                    "hvisible": hvisible}
        })
        .always(function(data) {
            var htmldata = data;
            cssdata = $(htmldata).find('#report-style').html();
            $('#report-style').html(cssdata);
            htmldata = $(htmldata).find('#report').html();
            $('#report').html(htmldata);
            $('#report').fadeTo('fast', 1);
            load_barcodes();
            load_layout();
        });
    }

    function get_full_height(element) {
        var height = parseFloat($(element).outerHeight());
        height += parseFloat($(element).css('marginTop'));
        height += parseFloat($(element).css('marginBottom'));
        return height;
    }

    function load_layout() {
        // Store footer and header heights for further pagination and
        // page layout changes.
        header_height = 0;
        header_html = '';
        if ($('.page-header').length > 0) {
            var pgh = $('.page-header').first();
            header_height = get_full_height(pgh);
            header_html = $(pgh).html();
            $('.page-header').remove();
        }
        footer_height = 0;
        footer_html = '';
        if ($('.page-footer').length > 0) {
            var pgf = $('.page-footer').first();
            footer_height = get_full_height(pgf);
            footer_html = $(pgf).html();
            $('.page-footer').remove();
        }

        currentlayout = $('#sel_layout').val();
        var layout_style = '@page { size: '+layouts_size[currentlayout]+' !important;';
        layout_style += 'width: '+layouts_mm[currentlayout][0]+'mm !important;'
        layout_style += 'height: '+layouts_mm[currentlayout][1]+'mm !important;'
        layout_style += 'margin: '+layouts_margin[currentlayout][0]+'mm ';
        layout_style +=  layouts_margin[currentlayout][1]+'mm ';
        layout_style +=  layouts_margin[currentlayout][2]+'mm ';
        layout_style +=  layouts_margin[currentlayout][3]+'mm !important; }';
        $('#layout-style').html(layout_style);

        // Calculate pagination according to the selected Layout.
        // DIN-A4, Letter US Size, etc.
        // Iterate for each report body and apply the dimensions
        var currelement = null;
        var footadded = false;
        var prevarid = '';
        var prevheight = 0;
        var layheight = parseFloat(mmTopx(layouts_mm[currentlayout][1]));
        layheight -= parseFloat(mmTopx(layouts_margin[currentlayout][0]));
        layheight -= parseFloat(mmTopx(layouts_margin[currentlayout][2]));
        var maxheight = parseFloat(layheight - footer_height - header_height);
        console.log(layheight+" : "+maxheight);
        $('div.ar_publish_body > div').each(function(i) {
            footadded = false;
            var arbody = $(this).closest('div.ar_publish_body');
            var id_ar = $(arbody).attr('id');
            if (id_ar != prevarid) {
                // New AR report, new page
                if (prevarid != '') {
                    $("<div class='page-break'></div><div class='page-header'>"+header_html+"</div>").prependTo($(arbody));
                } else {
                    $("<div class='page-header'>"+header_html+"</div>").prependTo($(arbody));
                }
                prevheight = 0;
                prevarid = id_ar;
            }
            var elheight = get_full_height($(this));
            var currheight = parseFloat(prevheight + elheight);
            console.log($(this).attr('id')+": "+$(this).outerHeight()+" -> "+currheight);
            if (currheight > maxheight || $(this).hasClass('manual-page-break')) {
                // Add page-break, hader and footer
                var margin = maxheight - prevheight;
                $("<div style='clear:both;padding-top:"+pxTomm(margin)+"mm'></div><div class='page-footer'>"+footer_html+"</div>").insertBefore($(this));
                $("<div class='page-break'></div><div class='page-header'>"+header_html+"</div>").insertBefore($(this));
                console.log("---> "+ prevheight +" + " + margin + " + "+ footer_height + " = " +(prevheight + margin + footer_height));
                prevheight = $(this).hasClass('manual-page-break') ? 0 : elheight;
                footadded = true;
            } else {
                prevheight = currheight;
            }
            currelement = $(this);
        });
        if (footadded == false && currelement != null) {
            var margin =  maxheight - prevheight;
            $("<div style='clear:both;padding-top:"+pxTomm(margin)+"mm'></div><div class='page-footer'>"+footer_html+"</div>").insertAfter($(currelement));
        }
        $('.manual-page-break').hide();

        // Page numbering
        $('div.ar_publish_body').each(function(i) {
            var pagesnum = $(this).find('div.page-footer').length;
            $(this).find('.page-total-count').html(pagesnum);
            var currnum = 1;
            $(this).find('div.page-footer .page-current-num').each(function(j) {
                $(this).html(currnum);
                currnum += 1;
            });
            var currnum = 1;
            $(this).find('div.page-header .page-current-num').each(function(j) {
                $(this).html(currnum);
                currnum += 1;
            });
        });
    }
}
var mmTopx = function(mm) {
    return Math.floor(mm*$('#my_mm').height());
}
var pxTomm = function(px){
    return Math.floor(px/$('#my_mm').height());
};
