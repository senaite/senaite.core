
/* Please use this command to compile this file into the parent `js` directory:
    coffee --no-header -w -o ../ -c bika.lims.analysisrequest.publish.coffee
 */

(function() {
  window.mmTopx = function(mm) {
    var px;
    px = parseFloat(mm * $('#my_mm').height());
    if (px > 0) {
      return Math.ceil(px);
    } else {
      return Math.floor(px);
    }
  };

  window.pxTomm = function(px) {
    var mm;
    mm = parseFloat(px / $('#my_mm').height());
    if (mm > 0) {
      return Math.floor(mm);
    } else {
      return Math.ceil(mm);
    }
  };


  /**
   * Controller class for Analysis Service Edit view
   */

  window.AnalysisRequestPublishView = function() {
    var applyMarginAndReload, convert_svgs, default_margins, get, load_barcodes, load_layout, papersize, papersize_default, referrer_cookie_name, reloadReport, that;
    that = this;
    referrer_cookie_name = '_arpv';
    papersize_default = 'A4';
    default_margins = [20, 20, 30, 20];
    papersize = {
      'A4': {
        size: 'A4',
        dimensions: [210, 297],
        margins: [20, 20, 30, 20]
      },
      'letter': {
        size: 'letter',
        dimensions: [216, 279],
        margins: [20, 20, 30, 20]
      }
    };

    /**
     * Entry-point method for AnalysisRequestPublishView
     */
    applyMarginAndReload = function(element, idx) {
      var currentlayout, margin, maxmargin, n;
      currentlayout = $('#sel_layout').val();
      maxmargin = papersize[currentlayout].dimensions[(idx + 1) % 2] / 4;
      margin = $(element).val();
      n = ~~Number(margin);
      if (String(n) === margin && n >= 0 && n <= maxmargin) {
        papersize[currentlayout].margins[idx] = n;
        reloadReport();
      } else {
        $(element).val(papersize[currentlayout].margins[idx]);
      }
    };
    get = function(name) {
      if (name = new RegExp('[?&]' + encodeURIComponent(name) + '=([^&]*)').exec(location.search)) {
        return decodeURIComponent(name[1]);
      }
    };
    load_barcodes = function() {
      $('.barcode').each(function() {
        var addQuietZone, barHeight, code, id, showHRI;
        id = $(this).attr('data-id');
        code = $(this).attr('data-code');
        barHeight = $(this).attr('data-barHeight');
        addQuietZone = $(this).attr('data-addQuietZone');
        showHRI = $(this).attr('data-showHRI');
        $(this).barcode(id, code, {
          'barHeight': parseInt(barHeight),
          'addQuietZone': Boolean(addQuietZone),
          'showHRI': Boolean(showHRI)
        });
      });
    };
    convert_svgs = function() {
      $('svg').each(function(e) {
        var img, svg;
        svg = $('<div />').append($(this).clone()).html();
        img = window.bika.lims.CommonUtils.svgToImage(svg);
        $(this).replaceWith(img);
      });
    };

    /**
     * Re-load the report view in accordance to the values set in the
     * options panel (report format, pagesize, QC visible, etc.)
     */
    reloadReport = function() {
      var hvisible, landscape, layout, qcvisible, template, url;
      url = window.location.href;
      template = $('#sel_format').val();
      qcvisible = $('#qcvisible').is(':checked') ? '1' : '0';
      hvisible = $('#hvisible').is(':checked') ? '1' : '0';
      landscape = $('#landscape').is(':checked') ? '1' : '0';
      layout = $('#sel_layout').val();
      if ($('#report:visible').length > 0) {
        $('#report').fadeTo('fast', 0.4);
      }
      $.ajax({
        url: url,
        type: 'POST',
        async: true,
        data: {
          'template': template,
          'qcvisible': qcvisible,
          'hvisible': hvisible,
          'landscape': landscape,
          'layout': layout
        }
      }).always(function(data) {
        var cssdata, htmldata;
        htmldata = data;
        cssdata = $(htmldata).find('#report-style').html();
        $('#report-style').html(cssdata);
        htmldata = $(htmldata).find('#report').html();
        $('#report').html(htmldata);
        $('#report').fadeTo('fast', 1);
        load_barcodes();
        load_layout();
        window.bika.lims.RangeGraph.load();
        convert_svgs();
      });
    };

    /**
     * Applies the selected layout (A4, US-letter) to the reports view,
     * splits each report in pages depending on the layout and margins
     * and applies the dynamic footer and/or header if required.
     * In fact, this method makes the html ready to be printed via
     * Weasyprint.
     */
    load_layout = function() {
      var currentlayout, dim, layout_style, orientation;
      currentlayout = $('#sel_layout').val();
      orientation = $('#landscape').is(':checked') ? 'landscape' : 'portrait';
      dim = {
        size: papersize[currentlayout].size,
        orientation: orientation,
        outerWidth: papersize[currentlayout].dimensions[0],
        outerHeight: papersize[currentlayout].dimensions[1],
        marginTop: papersize[currentlayout].margins[0],
        marginRight: papersize[currentlayout].margins[1],
        marginBottom: papersize[currentlayout].margins[2],
        marginLeft: papersize[currentlayout].margins[3],
        width: papersize[currentlayout].dimensions[0] - papersize[currentlayout].margins[1] - papersize[currentlayout].margins[3],
        height: papersize[currentlayout].dimensions[1] - papersize[currentlayout].margins[0] - papersize[currentlayout].margins[2]
      };
      console.debug("Dimensions (in mm): ", dim);
      $('#margin-top').val(dim.marginTop);
      $('#margin-right').val(dim.marginRight);
      $('#margin-bottom').val(dim.marginBottom);
      $('#margin-left').val(dim.marginLeft);
      layout_style = '@page { size:  ' + dim.size + ' ' + orientation + ' !important;' + '        width:  ' + dim.width + 'mm !important;' + '        margin: 0mm ' + dim.marginRight + 'mm 0mm ' + dim.marginLeft + 'mm !important;' + '}';
      $('#layout-style').html(layout_style);
      $('#ar_publish_container').css({
        'width': dim.width + 'mm',
        'padding': '0mm ' + dim.marginRight + 'mm 0mm ' + dim.marginLeft + 'mm '
      });
      $('#ar_publish_header').css('margin', '0mm -' + dim.marginRight + 'mm 0mm -' + dim.marginLeft + 'mm');
      $('div.ar_publish_body').css({
        'width': dim.width + 'mm',
        'max-width': dim.width + 'mm',
        'min-width': dim.width + 'mm'
      });
      $('div.ar_publish_body').each(function(i) {
        var aboveBreakHtml, arbody, contentHeight, elCurrent, elOutHeight, footer_height, footer_html, header_height, header_html, maxHeight, paddingTopFoot, pageBreak, pagecntidx, pagecounts, pagenum, pgf, pgh, split_at, topOffset;
        arbody = $(this);
        header_html = '<div class="page-header"></div>';
        header_height = $(header_html).outerHeight(true);
        if ($(this).find('.page-header').length > 0) {
          pgh = $(this).find('.page-header').first();
          header_height = parseFloat($(pgh).outerHeight(true));
          if (header_height > mmTopx(dim.marginTop)) {
            header_html = '<div class=\'page-header header-invalid\'>Header height is above page\'s top margin height</div>';
            header_height = parseFloat($(header_html));
          } else {
            header_html = '<div class="page-header">' + $(pgh).html() + '</div>';
          }
          $(this).find('.page-header').remove();
        }
        footer_html = '<div class="page-footer"></div>';
        footer_height = $(footer_html).outerHeight(true);
        if ($(this).find('.page-footer').length > 0) {
          pgf = $(this).find('.page-footer').first();
          footer_height = parseFloat($(pgf).outerHeight(true));
          if (footer_height > mmTopx(dim.marginBottom)) {
            footer_html = '<div class=\'page-footer footer-invalid\'>Footer height is above page\'s bottom margin height</div>';
            footer_height = parseFloat($(footer_html));
          } else {
            footer_html = '<div class="page-footer">' + $(pgf).html() + '</div>';
          }
          $(this).find('.page-footer').remove();
        }
        $(this).find('.page-break').remove();
        if ($(this).find('div').last().hasClass('manual-page-break')) {
          $(this).find('div').last().remove();
        }
        if ($(this).find('div').first().hasClass('manual-page-break')) {
          $(this).find('div').first().remove();
        }
        topOffset = $(this).position().top;
        maxHeight = mmTopx(dim.height);
        elCurrent = null;
        elOutHeight = 0;
        contentHeight = 0;
        pagenum = 1;
        pagecounts = Array();
        $(this).children('div:visible').each(function(z) {
          var aboveBreakHtml, elAbsTopPos, elNext, elRelTopPos, manualbreak, paddingTopFoot, pageBreak, restartcount;
          if (elCurrent === null) {
            $(header_html).insertBefore($(this));
            topOffset = $(this).position().top;
          }
          elAbsTopPos = $(this).position().top;
          elRelTopPos = elAbsTopPos - topOffset;
          elNext = $(this).next();
          elOutHeight = parseFloat($(this).outerHeight(true));
          if ($(elNext).length > 0) {
            elOutHeight = $(elNext).position().top - elAbsTopPos;
          }
          if (elOutHeight > maxHeight) {
            console.warn('Element with id ' + $(this).attr('id') + ' has a height above the maximum: ' + elOutHeight);
          }
          contentHeight = elRelTopPos + elOutHeight;

          /*
          console.log(Math.floor(topOffset)     + "\t" +
                      Math.floor(elAbsTopPos)   + "\t" +
                      Math.floor(elRelTopPos)   + "\t" +
                      Math.floor(elOutHeight)   + "\t" +
                      Math.floor(contentHeight) + "\t" +
                      Math.floor(maxHeight)     + "\t" +
                      '#'+$(this).attr('id')+"."+$(this).attr('class'));
           */
          if (contentHeight > maxHeight || $(this).hasClass('manual-page-break')) {
            paddingTopFoot = maxHeight - elRelTopPos;
            manualbreak = $(this).hasClass('manual-page-break');
            restartcount = manualbreak && $(this).hasClass('restart-page-count');
            aboveBreakHtml = '<div style=\'clear:both;padding-top:' + pxTomm(paddingTopFoot) + 'mm\'></div>';
            pageBreak = '<div class=\'page-break' + (restartcount ? ' restart-page-count' : '') + '\' data-pagenum=\'' + pagenum + '\'></div>';
            $(aboveBreakHtml + footer_html + pageBreak + header_html).insertBefore($(this));
            topOffset = $(this).position().top;
            if (manualbreak) {
              $(this).hide();
              if (restartcount) {
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
        if (elCurrent !== null) {
          paddingTopFoot = maxHeight - contentHeight;
          aboveBreakHtml = '<div style=\'clear:both;padding-top:' + pxTomm(paddingTopFoot) + 'mm\'></div>';
          pageBreak = '<div class=\'page-break\' data-pagenum=\'' + pagenum + '\'></div>';
          pagecounts.push(pagenum);
          $(aboveBreakHtml + footer_html + pageBreak).insertAfter($(elCurrent));
        }
        split_at = 'div.page-header';
        $(this).find(split_at).each(function() {
          $(this).add($(this).nextUntil(split_at)).wrapAll('<div class=\'ar_publish_page\'/>');
        });
        $(this).find('div.page-header').each(function() {
          var baseheight;
          baseheight = $(this).height();
          $(this).css({
            'height': pxTomm(baseheight) + 'mm',
            'margin': 0,
            'padding': pxTomm(mmTopx(dim.marginTop) - baseheight) + 'mm 0 0 0'
          });
          $(this).parent().before(this);
        });
        $(this).find('div.page-break').each(function() {
          $(this).parent().after(this);
        });
        $(this).find('div.page-footer').each(function() {
          $(this).css({
            'height': dim.marginBottom + 'mm',
            'margin': 0,
            'padding': 0
          });
          $(this).parent().after(this);
        });
        pagenum = 1;
        pagecntidx = 0;
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
      $('.manual-page-break').remove();
    };
    that.load = function() {
      var backurl, cookiename, invalidbackurl, provisbackurl;
      $('#report').html('').hide();
      reloadReport();
      cookiename = 'ar.publish.view.referrer';
      backurl = document.referrer;
      if (backurl) {
        createCookie(cookiename, backurl);
      } else {
        backurl = readCookie(cookiename);
        if (!backurl) {
          backurl = portal_url;
        }
      }
      $('#ar_publish_container #ar_publish_summary a[href^="#"]').click(function(e) {
        var anchor, offset;
        e.preventDefault();
        anchor = $(this).attr('href');
        offset = $(anchor).first().offset().top - 20;
        $('html,body').animate({
          scrollTop: offset
        }, 'fast');
      });
      $('#sel_format').change(function(e) {
        reloadReport();
      });
      $('#landscape').click(function(e) {
        var key, landscape;
        landscape = $('#landscape').is(':checked') ? 1 : 0;
        $('body').toggleClass('landscape', landscape);
        for (key in papersize) {
          papersize[key]['dimensions'].reverse();
        }
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
        var count, hvisible, qcvisible, template, url;
        url = window.location.href;
        qcvisible = $('#qcvisible').is(':checked') ? 1 : 0;
        hvisible = $('#hvisible').is(':checked') ? 1 : 0;
        template = $('#sel_format').val();
        $('#ar_publish_container').animate({
          opacity: 0.4
        }, 'slow');
        count = $('#ar_publish_container #report .ar_publish_body').length;
        $('#ar_publish_container #report .ar_publish_body').each(function() {
          var rephtml, repstyle;
          rephtml = $(this).clone().wrap('<div>').parent().html();
          repstyle = $('#report-style').clone().wrap('<div>').parent().html();
          repstyle += $('#layout-style').clone().wrap('<div>').parent().html();
          repstyle += $('#layout-print').clone().wrap('<div>').parent().html();
          $.ajax({
            url: url,
            type: 'POST',
            async: false,
            data: {
              'publish': 1,
              'id': $(this).attr('id'),
              'uid': $(this).attr('uid'),
              'html': rephtml,
              'template': template,
              'qcvisible': qcvisible,
              'hvisible': hvisible,
              'style': repstyle
            }
          }).always(function() {
            if (!--count) {
              location.href = backurl;
            }
          });
        });
      });
      $('#cancel_button').click(function(e) {
        location.href = backurl;
      });
      invalidbackurl = window.portal_url + '/++resource++bika.lims.images/report_invalid_back.png';
      $('.ar-invalid').css('background', 'url(\'' + invalidbackurl + '\') repeat scroll #ffffff');
      provisbackurl = window.portal_url + '/++resource++bika.lims.images/report_provisional_back.png';
      $('.ar-provisional').css('background', 'url(\'' + provisbackurl + '\') repeat scroll #ffffff');
      $('#sel_format_info').click(function(e) {
        e.preventDefault();
        $('#sel_format_info_pane').toggle();
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
  };

}).call(this);
