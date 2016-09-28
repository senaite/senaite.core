/**
 * Controller class for Samples Print View
 */
function FormPrintView() {
    "use strict";
    var that = this;
    var referrer_cookie_name = '_spv';

    // Allowed Paper sizes and default margins, in mm
    var papersize_default = "A4";
    var default_margins = [15, 10, 15, 10];
    var papersize = {
        'A4': {
                dimensions: [210, 297],
                margins:    [15, 10, 15, 10] },

        'letter': {
                dimensions: [215.9, 279.4],
                margins:    [15, 10, 15, 10] },
    };

    /**
     * Entry-point method for AnalysisRequestPublishView
     */
    that.load = function() {

        // The report will be loaded dynamically by reloadReport()
        $('#report').html('').hide();

        // Load the report
        reloadReport();

        // Store referrer in cookie in case it is lost due to a page reload
        var cookiename = "samples.print.preview.referrer";
        var backurl = document.referrer;
        if (backurl) {
            createCookie(cookiename, backurl);
        } else {
            backurl = readCookie(cookiename);
            // Fallback to portal_url instead of staying inside publish.
            if (!backurl) {
                backurl = portal_url;
            }
        }

        // Smooth scroll to content
        $('#preview_container #preview_summary a[href^="#"]').click(function(e) {
            e.preventDefault();
            var anchor = $(this).attr('href');
            var offset = $(anchor).first().offset().top - 20;
            $('html,body').animate({scrollTop: offset},'fast');
        });

        $('#sel_format').change(function(e) {
            reloadReport();
        });

        $('#filter_button').click(function(e) {
            reloadReport();
        });

        $('#sel_layout').change(function(e) {
            $('body').removeClass($('body').attr('data-layout'));
            $('body').attr('data-layout', $(this).val());
            $('body').addClass($(this).val());
            reloadReport();
        });

        $('#print_button').click(function(e) {
            e.preventDefault();
            var url = window.location.href;
            $('#preview_container').animate({opacity:0.4}, 'slow');
            var count = $('#preview_container #report .preview_body').length;
            $('#preview_container #report .preview_body').each(function(){
                var rephtml = $(this).clone().wrap('<div>').parent().html();
                var repstyle = $('#report-style').clone().wrap('<div>').parent().html();
                repstyle += $('#layout-style').clone().wrap('<div>').parent().html();
                var form='<form action="'+url+'" name="form" method="post" style="display:none;">' +
                    '<textarea name="html">' + rephtml + '</textarea/>' +
                    '<input type="hidden" name="pdf" value="1" />' +
                    '<textarea name="style">' +repstyle+ '</textarea>' +
                    '</form>';
                $('body').html(form);
                document.forms.form.submit();
            });
        });

        $('#cancel_button').click(function(e) {
            location.href=backurl;
        });

        $('#disable_filter_by_date').change(function(e) {
            dateFilterController();
        });
        $.datepicker.setDefaults($.datepicker.regional['']);
        $('#filter_date_from, #filter_date_to').datepicker({
            onSelect: function(dateText, inst) {
                dateFilterFromToController();
            },
            dateFormat: 'yy-mm-dd'
        });
        $('#margin-top').change(function(e) {
            applyMarginAndReload($(this), 0);
        });
        $('#margin-right').change(function(e) {
            applyMarginAndReload($(this), 1);
        });
        $('#margin-bottom').change(function(e) {
            applyMarginAndReload($(this), 2);
        });
        $('#margin-left').change(function(e) {
            applyMarginAndReload($(this), 3);
        });
    };

    function applyMarginAndReload(element, idx) {
        var currentlayout = $('#sel_layout').val();
        // Maximum margin (1/4 of the total width)
        var maxmargin = papersize[currentlayout].dimensions[(idx+1) % 2]/4;
        // Is this a valid whole number?
        var margin = $(element).val();
        var n = ~~Number(margin);
        if (String(n) === margin && n >= 0 && n <= maxmargin) {
            papersize[currentlayout].margins[idx] = n;
            reloadReport();
        } else {
            // Not a number of out of bounds
            $(element).val(papersize[currentlayout].margins[idx]);
        }
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

    /**
     * Re-load the report view in accordance to the values set in the
     * options panel (report format, pagesize, QC visible, etc.)
     */
    function reloadReport() {
        var url = window.location.href;
        var template = $('#sel_format').val();
        if ($('#report:visible').length > 0) {
            $('#report').fadeTo('fast', 0.4);
        }
        $.ajax({
            url: url,
            type: 'POST',
            async: true,
            data: { "template": template,
                    "sampler": $("#sel_sampler option:selected").val(),
                    "client": $("#sel_client option:selected").val(),
                    "date_from": $("#filter_date_from").val(),
                    "date_to": $("#filter_date_to").val(),
                    "avoid_filter_by_date": $('#disable_filter_by_date').is(':checked')
                }
        })
        .always(function(data) {
            var htmldata = data;
            var cssdata = $(htmldata).find('#report-style').html();
            $('#report-style').html(cssdata);
            htmldata = $(htmldata).find('#report').html();
            $('#report').html(htmldata);
            $('#report').fadeTo('fast', 1);
            load_barcodes();
            load_layout();
        });
    }

    /**
     * Applies the selected layout (A4, US-letter) to the reports view,
     * splits each report in pages depending on the layout and margins
     * and applies the dynamic footer and/or header if required.
     * In fact, this method makes the html ready to be printed via
     * Weasyprint.
     */
    function load_layout() {
        // Set page layout (DIN-A4, US-letter, etc.)
        var currentlayout = $('#sel_layout').val();
        // Dimensions. All expressed in mm
        var dim = {
            size:         papersize[currentlayout].size,
            outerWidth:   papersize[currentlayout].dimensions[0],
            outerHeight:  papersize[currentlayout].dimensions[1],
            marginTop:    papersize[currentlayout].margins[0],
            marginRight:  papersize[currentlayout].margins[1],
            marginBottom: papersize[currentlayout].margins[2],
            marginLeft:   papersize[currentlayout].margins[3],
            width:        papersize[currentlayout].dimensions[0]-papersize[currentlayout].margins[1]-papersize[currentlayout].margins[3],
            height:       papersize[currentlayout].dimensions[1]-papersize[currentlayout].margins[0]-papersize[currentlayout].margins[2]
        };

        $('#margin-top').val(dim.marginTop);
        $('#margin-right').val(dim.marginRight);
        $('#margin-bottom').val(dim.marginBottom);
        $('#margin-left').val(dim.marginLeft);

        var layout_style =
            '@page { size:  ' + dim.size + ' !important;' +
            '        width:  ' + dim.width + 'mm !important;' +
            '        margin: 0mm '+dim.marginRight+'mm 0mm '+dim.marginLeft+'mm !important;';
        $('#layout-style').html(layout_style);
        $('#preview_container').css({'width':dim.width + 'mm', 'padding': '0mm '+dim.marginRight + 'mm 0mm '+dim.marginLeft +'mm '});
        $('#preview_header').css('margin', '0mm -'+dim.marginRight + 'mm 0mm -' +dim.marginLeft+'mm');
        $('div.preview_body').css({'width': dim.width + 'mm', 'max-width': dim.width + 'mm', 'min-width': dim.width + 'mm'});

        // Iterate for each AR report and apply the dimensions, header,
        // footer, etc.
        $('div.preview_body').each(function(i) {

            var arbody = $(this);

            // Header defined for this AR Report?
            // Note that if the header of the report is taller than the
            // margin, the header will be dismissed.
            var header_html = '<div class="page-header"></div>';
            var header_height = $(header_html).outerHeight(true);
            if ($(this).find('.page-header').length > 0) {
                var pgh = $(this).find('.page-header').first();
                header_height = parseFloat($(pgh).outerHeight(true));
                if (header_height > mmTopx(dim.marginTop)) {
                    // Footer too tall
                    header_html = "<div class='page-header header-invalid'>Header height is above page's top margin height</div>";
                    header_height = parseFloat($(header_html));
                } else {
                    header_html   = '<div class="page-header">'+$(pgh).html()+'</div>';
                }
                $(this).find('.page-header').remove();
            }

            // Footer defined for this AR Report?
            // Note that if the footer of the report is taller than the
            // margin, the footer will be dismissed
            var footer_html = '<div class="page-footer"></div>';
            var footer_height = $(footer_html).outerHeight(true);
            if ($(this).find('.page-footer').length > 0) {
                var pgf = $(this).find('.page-footer').first();
                footer_height = parseFloat($(pgf).outerHeight(true));
                if (footer_height > mmTopx(dim.marginBottom)) {
                    // Footer too tall
                    footer_html = "<div class='page-footer footer-invalid'>Footer height is above page's bottom margin height</div>";
                    footer_height = parseFloat($(footer_html));
                } else {
                    footer_html   = '<div class="page-footer">'+$(pgf).html()+'</div>';
                }
                $(this).find('.page-footer').remove();
            }

            // Remove undesired and orphan page breaks
            $(this).find('.page-break').remove();
            if ($(this).find('div').last().hasClass('manual-page-break')) {
                $(this).find('div').last().remove();
            }
            if ($(this).find('div').first().hasClass('manual-page-break')) {
                $(this).find('div').first().remove();
            }

            // Top offset by default. The position in which the report
            // starts relative to the top of the window. Used later to
            // calculate when a page-break is needed.
            var topOffset = $(this).position().top;
            var maxHeight = mmTopx(dim.height);
            var elCurrent = null;
            var elOutHeight = 0;
            var contentHeight = 0;
            var pagenum = 1;
            var pagecounts = Array();

            // Iterate through all div children to find the suitable
            // page-break points, split the report and add the header
            // and footer as well as pagination count as required.
            //
            // IMPORTANT
            // Please note that only first-level div elements from
            // within div.preview_body are checked and will be
            // treated as nob-breakable elements. So, if a div element
            // from within a div.preview_body is taller than the
            // maximum allowed height, that element will be omitted.
            // Further improvements may solve this and handle deeply
            // elements from the document, such as tables, etc. Other
            // elements could be then labeled with "no-break" class to
            // prevent the system to break them.
            //console.log("OFF\tABS\tREL\tOUT\tHEI\tMAX");
            $(this).children('div:visible').each(function(z) {

                // Is the first page?
                if (elCurrent === null) {
                    // Add page header if required
                    $(header_html).insertBefore($(this));
                    topOffset = $(this).position().top;
                }

                // Instead of using the height css of each element to
                // know if the total height at this iteration is above
                // the maximum health, we use the element's position.
                // This way, we will prevent underestimations due
                // non-div elements or plain text directly set inside
                // the div.preview_body container, not wrapped by
                // other div element.
                var elAbsTopPos = $(this).position().top;
                var elRelTopPos = elAbsTopPos - topOffset;
                var elNext      = $(this).next();
                elOutHeight = parseFloat($(this).outerHeight(true));
                if ($(elNext).length > 0) {
                    // Calculate the height of the element according to
                    // the position of the next element instead of
                    // using the outerHeight.
                    elOutHeight = $(elNext).position().top-elAbsTopPos;
                }

                // The current element is taller than the maximum?
                if (elOutHeight >  maxHeight) {
                    console.warn("Element with id "+$(this).attr('id')+
                                 " has a height above the maximum: "+
                                 elOutHeight);
                }

                // Accumulated height
                contentHeight = elRelTopPos + elOutHeight;
                /*console.log(Math.floor(topOffset)     + "\t" +
                            Math.floor(elAbsTopPos)   + "\t" +
                            Math.floor(elRelTopPos)   + "\t" +
                            Math.floor(elOutHeight)   + "\t" +
                            Math.floor(contentHeight) + "\t" +
                            Math.floor(maxHeight)     + "\t" +
                            '#'+$(this).attr('id')+"."+$(this).attr('class'));*/

                if (contentHeight > maxHeight ||
                    $(this).hasClass('manual-page-break')) {
                    // The content is taller than the allowed height
                    // or a manual page break reached. Add a page break.
                    var paddingTopFoot = maxHeight - elRelTopPos;
                    var manualbreak = $(this).hasClass('manual-page-break');
                    var restartcount = manualbreak && $(this).hasClass('restart-page-count');
                    var aboveBreakHtml = "<div style='clear:both;padding-top:"+pxTomm(paddingTopFoot)+"mm'></div>";
                    var pageBreak = "<div class='page-break"+(restartcount ? " restart-page-count" : "")+"' data-pagenum='"+pagenum+"'></div>";
                    $(aboveBreakHtml + footer_html + pageBreak + header_html).insertBefore($(this));
                    topOffset = $(this).position().top;
                    if (manualbreak) {
                        $(this).hide();
                        if (restartcount) {
                            // The page count needs to be restarted!
                            pagecounts.push(pagenum);
                            pagenum = 0;
                        }
                    }
                    contentHeight = $(this).outerHeight(true);
                    pagenum += 1;
                }
                $(this).css('width', '100%');
                elCurrent = $(this);
            });

            // Document end-footer
            if (elCurrent !== null) {
                var paddingTopFoot = maxHeight - contentHeight;
                var aboveBreakHtml = "<div style='clear:both;padding-top:"+pxTomm(paddingTopFoot)+"mm'></div>";
                var pageBreak = "<div class='page-break' data-pagenum='"+pagenum+"'></div>";
                pagecounts.push(pagenum);
                $(aboveBreakHtml + footer_html + pageBreak).insertAfter($(elCurrent));
            }

            // Wrap all elements in pages
            var split_at = 'div.page-header';
            $(this).find(split_at).each(function() {
                $(this).add($(this).nextUntil(split_at)).wrapAll("<div class='preview_page'/>");
            });

            // Move headers and footers out of the wrapping and assign
            // the top and bottom margins
            $(this).find('div.page-header').each(function() {
                var baseheight = $(this).height();
                $(this).css({'height': pxTomm(baseheight)+"mm",
                             'margin': 0,
                             'padding': (pxTomm(mmTopx(dim.marginTop) - baseheight)+"mm 0 0 0")});
                $(this).parent().before(this);
            });
            $(this).find('div.page-break').each(function() {
                $(this).parent().after(this);
            });
            $(this).find('div.page-footer').each(function() {
                $(this).css({'height': dim.marginBottom+"mm",
                             'margin': 0,
                             'padding': 0});
                $(this).parent().after(this);
            });

            // Page numbering
            pagenum = 1;
            var pagecntidx = 0;
            $(this).find('.page-current-num,.page-total-count,div.page-break').each(function() {
                if ($(this).hasClass('page-break')) {
                    if ($(this).hasClass('restart-page-count')) {
                        pagenum = 1;
                        pagecntidx += 1;
                    } else {
                        pagenum = parseInt($(this).attr('data-pagenum')) + 1;
                    }
                } else if ($(this).hasClass('page-current-num')) {
                    $(this).html(pagenum);
                } else {
                    $(this).html(pagecounts[pagecntidx]);
                }
            });
        });
        // Remove manual page breaks
        $('.manual-page-break').remove();
    }

    function dateFilterController(){
        /* This function enable/disable the date pickers whether the checkbox
        is set or not
        */
        if ($('#disable_filter_by_date').is(':checked')){
            $('#filter_date_from, #filter_date_to')
                .prop('disabled', true).val("");
        }
        else{
            $('#filter_date_from')
            .prop('disabled', false)
            .val($('#filter_date_from').attr('default'));
            $('#filter_date_to')
            .prop('disabled', false)
            .val($('#filter_date_to').attr('default'));
        }
    }
    function dateFilterFromToController(){
        if ($("#filter_date_from").datepicker("getDate") > $("#filter_date_to").datepicker("getDate")){
            $('#filter_date_from').datepicker("setDate", $('#filter_date_to').datepicker("getDate"));
        }
    }
}
var mmTopx = function(mm) {
    var px = parseFloat(mm*$('#my_mm').height());
    return px > 0 ? Math.ceil(px) : Math.floor(px);
};
var pxTomm = function(px){
    var mm = parseFloat(px/$('#my_mm').height());
    return mm > 0 ? Math.floor(mm) : Math.ceil(mm);
};
