### Please use this command to compile this file into the parent `js` directory:
    coffee --no-header -w -o ../ -c bika.lims.analysisrequest.publish.coffee
###

window.mmTopx = (mm) ->
  px = parseFloat(mm * $('#my_mm').height())
  if px > 0 then Math.ceil(px) else Math.floor(px)

window.pxTomm = (px) ->
  mm = parseFloat(px / $('#my_mm').height())
  if mm > 0 then Math.floor(mm) else Math.ceil(mm)

###*
# Controller class for Analysis Service Edit view
###

window.AnalysisRequestPublishView = ->
  that = this
  referrer_cookie_name = '_arpv'
  # Allowed Paper sizes and default margins, in mm
  papersize_default = 'A4'
  default_margins = [
    20
    20
    30
    20
  ]
  papersize =
    'A4':
      size: 'A4'
      dimensions: [
        210
        297
      ]
      margins: [
        20
        20
        30
        20
      ]
    'letter':
      size: 'letter'
      dimensions: [
        216
        279
      ]
      margins: [
        20
        20
        30
        20
      ]

  ###*
  # Entry-point method for AnalysisRequestPublishView
  ###

  applyMarginAndReload = (element, idx) ->
    currentlayout = $('#sel_layout').val()
    # Maximum margin (1/4 of the total width)
    maxmargin = papersize[currentlayout].dimensions[(idx + 1) % 2] / 4
    # Is this a valid whole number?
    margin = $(element).val()
    n = ~ ~Number(margin)
    if String(n) == margin and n >= 0 and n <= maxmargin
      papersize[currentlayout].margins[idx] = n
      reloadReport()
    else
      # Not a number of out of bounds
      $(element).val papersize[currentlayout].margins[idx]
    return

  get = (name) ->
    if name = new RegExp('[?&]' + encodeURIComponent(name) + '=([^&]*)').exec(location.search)
      return decodeURIComponent(name[1])
    return

  load_barcodes = ->
    # Barcode generator
    $('.barcode').each ->
      id = $(this).attr('data-id')
      code = $(this).attr('data-code')
      barHeight = $(this).attr('data-barHeight')
      addQuietZone = $(this).attr('data-addQuietZone')
      showHRI = $(this).attr('data-showHRI')
      $(this).barcode id, code,
        'barHeight': parseInt(barHeight)
        'addQuietZone': Boolean(addQuietZone)
        'showHRI': Boolean(showHRI)
      return
    return

  convert_svgs = ->
    $('svg').each (e) ->
      svg = $('<div />').append($(this).clone()).html()
      img = window.bika.lims.CommonUtils.svgToImage(svg)
      $(this).replaceWith img
      return
    return

  ###*
  # Re-load the report view in accordance to the values set in the
  # options panel (report format, pagesize, QC visible, etc.)
  ###

  reloadReport = ->
    url = window.location.href
    template = $('#sel_format').val()
    qcvisible = if $('#qcvisible').is(':checked') then '1' else '0'
    hvisible = if $('#hvisible').is(':checked') then '1' else '0'
    landscape = if $('#landscape').is(':checked') then '1' else '0'
    layout = $('#sel_layout').val()
    if $('#report:visible').length > 0
      $('#report').fadeTo 'fast', 0.4

    $.ajax(
      url: url
      type: 'POST'
      async: true
      data:
        'template': template
        'qcvisible': qcvisible
        'hvisible': hvisible
        'landscape': landscape
        'layout': layout).always (data) ->
      htmldata = data
      cssdata = $(htmldata).find('#report-style').html()
      $('#report-style').html cssdata
      htmldata = $(htmldata).find('#report').html()
      $('#report').html htmldata
      $('#report').fadeTo 'fast', 1
      load_barcodes()
      load_layout()
      window.bika.lims.RangeGraph.load()
      convert_svgs()
      return

    return

  ###*
  # Applies the selected layout (A4, US-letter) to the reports view,
  # splits each report in pages depending on the layout and margins
  # and applies the dynamic footer and/or header if required.
  # In fact, this method makes the html ready to be printed via
  # Weasyprint.
  ###

  load_layout = ->
    # Set page layout (DIN-A4, US-letter, etc.)
    currentlayout = $('#sel_layout').val()
    orientation = if $('#landscape').is(':checked') then 'landscape' else 'portrait'

    # Dimensions. All expressed in mm
    dim =
      size: papersize[currentlayout].size
      orientation: orientation
      outerWidth: papersize[currentlayout].dimensions[0]
      outerHeight: papersize[currentlayout].dimensions[1]
      marginTop: papersize[currentlayout].margins[0]
      marginRight: papersize[currentlayout].margins[1]
      marginBottom: papersize[currentlayout].margins[2]
      marginLeft: papersize[currentlayout].margins[3]
      width: papersize[currentlayout].dimensions[0] - (papersize[currentlayout].margins[1]) - (papersize[currentlayout].margins[3])
      height: papersize[currentlayout].dimensions[1] - (papersize[currentlayout].margins[0]) - (papersize[currentlayout].margins[2])

    console.debug "Dimensions (in mm): ", dim

    $('#margin-top').val dim.marginTop
    $('#margin-right').val dim.marginRight
    $('#margin-bottom').val dim.marginBottom
    $('#margin-left').val dim.marginLeft
    layout_style = '@page { size:  ' + dim.size + ' ' + orientation + ' !important;' + '        width:  ' + dim.width + 'mm !important;' + '        margin: 0mm ' + dim.marginRight + 'mm 0mm ' + dim.marginLeft + 'mm !important;' + '}'
    $('#layout-style').html layout_style
    $('#ar_publish_container').css
      'width': dim.width + 'mm'
      'padding': '0mm ' + dim.marginRight + 'mm 0mm ' + dim.marginLeft + 'mm '
    $('#ar_publish_header').css 'margin', '0mm -' + dim.marginRight + 'mm 0mm -' + dim.marginLeft + 'mm'
    $('div.ar_publish_body').css
      'width': dim.width + 'mm'
      'max-width': dim.width + 'mm'
      'min-width': dim.width + 'mm'

    # Iterate for each AR report and apply the dimensions, header,
    # footer, etc.
    $('div.ar_publish_body').each (i) ->
      arbody = $(this)
      # Header defined for this AR Report?
      # Note that if the header of the report is taller than the
      # margin, the header will be dismissed.
      header_html = '<div class="page-header"></div>'
      header_height = $(header_html).outerHeight(true)
      if $(this).find('.page-header').length > 0
        pgh = $(this).find('.page-header').first()
        header_height = parseFloat($(pgh).outerHeight(true))
        if header_height > mmTopx(dim.marginTop)
          # Footer too tall
          header_html = '<div class=\'page-header header-invalid\'>Header height is above page\'s top margin height</div>'
          header_height = parseFloat($(header_html))
        else
          header_html = '<div class="page-header">' + $(pgh).html() + '</div>'
        $(this).find('.page-header').remove()

      # Footer defined for this AR Report?
      # Note that if the footer of the report is taller than the
      # margin, the footer will be dismissed
      footer_html = '<div class="page-footer"></div>'
      footer_height = $(footer_html).outerHeight(true)
      if $(this).find('.page-footer').length > 0
        pgf = $(this).find('.page-footer').first()
        footer_height = parseFloat($(pgf).outerHeight(true))
        if footer_height > mmTopx(dim.marginBottom)
          # Footer too tall
          footer_html = '<div class=\'page-footer footer-invalid\'>Footer height is above page\'s bottom margin height</div>'
          footer_height = parseFloat($(footer_html))
        else
          footer_html = '<div class="page-footer">' + $(pgf).html() + '</div>'
        $(this).find('.page-footer').remove()

      # Remove undesired and orphan page breaks
      $(this).find('.page-break').remove()
      if $(this).find('div').last().hasClass('manual-page-break')
        $(this).find('div').last().remove()
      if $(this).find('div').first().hasClass('manual-page-break')
        $(this).find('div').first().remove()
      # Top offset by default. The position in which the report
      # starts relative to the top of the window. Used later to
      # calculate when a page-break is needed.
      topOffset = $(this).position().top
      maxHeight = mmTopx(dim.height)
      elCurrent = null
      elOutHeight = 0
      contentHeight = 0
      pagenum = 1
      pagecounts = Array()

      # Iterate through all div children to find the suitable
      # page-break points, split the report and add the header
      # and footer as well as pagination count as required.
      #
      # IMPORTANT
      # Please note that only first-level div elements from
      # within div.ar_publish_body are checked and will be
      # treated as nob-breakable elements. So, if a div element
      # from within a div.ar_publish_body is taller than the
      # maximum allowed height, that element will be omitted.
      # Further improvements may solve this and handle deeply
      # elements from the document, such as tables, etc. Other
      # elements could be then labeled with "no-break" class to
      # prevent the system to break them.
      #console.log("OFF\tABS\tREL\tOUT\tHEI\tMAX");
      $(this).children('div:visible').each (z) ->
        # Is the first page?
        if elCurrent == null
          # Add page header if required
          $(header_html).insertBefore $(this)
          topOffset = $(this).position().top

        # Instead of using the height css of each element to
        # know if the total height at this iteration is above
        # the maximum health, we use the element's position.
        # This way, we will prevent underestimations due
        # non-div elements or plain text directly set inside
        # the div.ar_publish_body container, not wrapped by
        # other div element.
        elAbsTopPos = $(this).position().top
        elRelTopPos = elAbsTopPos - topOffset
        elNext = $(this).next()
        elOutHeight = parseFloat($(this).outerHeight(true))

        if $(elNext).length > 0
          # Calculate the height of the element according to
          # the position of the next element instead of
          # using the outerHeight.
          elOutHeight = $(elNext).position().top - elAbsTopPos

        # The current element is taller than the maximum?
        if elOutHeight > maxHeight
          console.warn 'Element with id ' + $(this).attr('id') + ' has a height above the maximum: ' + elOutHeight
        # Accumulated height
        contentHeight = elRelTopPos + elOutHeight

        ###
        console.log(Math.floor(topOffset)     + "\t" +
                    Math.floor(elAbsTopPos)   + "\t" +
                    Math.floor(elRelTopPos)   + "\t" +
                    Math.floor(elOutHeight)   + "\t" +
                    Math.floor(contentHeight) + "\t" +
                    Math.floor(maxHeight)     + "\t" +
                    '#'+$(this).attr('id')+"."+$(this).attr('class'));
        ###

        if contentHeight > maxHeight or $(this).hasClass('manual-page-break')
          # The content is taller than the allowed height
          # or a manual page break reached. Add a page break.
          paddingTopFoot = maxHeight - elRelTopPos
          manualbreak = $(this).hasClass('manual-page-break')
          restartcount = manualbreak and $(this).hasClass('restart-page-count')
          aboveBreakHtml = '<div style=\'clear:both;padding-top:' + pxTomm(paddingTopFoot) + 'mm\'></div>'
          pageBreak = '<div class=\'page-break' + (if restartcount then ' restart-page-count' else '') + '\' data-pagenum=\'' + pagenum + '\'></div>'
          $(aboveBreakHtml + footer_html + pageBreak + header_html).insertBefore $(this)
          topOffset = $(this).position().top
          if manualbreak
            $(this).hide()
            if restartcount
              # The page count needs to be restarted!
              pagecounts.push pagenum
              pagenum = 0
          contentHeight = $(this).outerHeight(true)
          pagenum += 1
        $(this).css 'width', '100%'
        elCurrent = $(this)
        return

      # Document end-footer
      if elCurrent != null
        paddingTopFoot = maxHeight - contentHeight
        aboveBreakHtml = '<div style=\'clear:both;padding-top:' + pxTomm(paddingTopFoot) + 'mm\'></div>'
        pageBreak = '<div class=\'page-break\' data-pagenum=\'' + pagenum + '\'></div>'
        pagecounts.push pagenum
        $(aboveBreakHtml + footer_html + pageBreak).insertAfter $(elCurrent)

      # Wrap all elements in pages
      split_at = 'div.page-header'
      $(this).find(split_at).each ->
        $(this).add($(this).nextUntil(split_at)).wrapAll '<div class=\'ar_publish_page\'/>'
        return

      # Move headers and footers out of the wrapping and assign
      # the top and bottom margins
      $(this).find('div.page-header').each ->
        baseheight = $(this).height()
        $(this).css
          'height': pxTomm(baseheight) + 'mm'
          'margin': 0
          'padding': pxTomm(mmTopx(dim.marginTop) - baseheight) + 'mm 0 0 0'
        $(this).parent().before this
        return

      $(this).find('div.page-break').each ->
        $(this).parent().after this
        return

      $(this).find('div.page-footer').each ->
        $(this).css
          'height': dim.marginBottom + 'mm'
          'margin': 0
          'padding': 0
        $(this).parent().after this
        return

      # Page numbering
      pagenum = 1
      pagecntidx = 0
      $(this).find('.page-current-num,.page-total-count,div.page-break').each ->
        if $(this).hasClass('page-break')
          if $(this).hasClass('restart-page-count')
            pagenum = 1
            pagecntidx += 1
          else
            pagenum = parseInt($(this).attr('data-pagenum')) + 1
        else if $(this).hasClass('page-current-num')
          $(this).html pagenum
        else
          $(this).html pagecounts[pagecntidx]
        return
      return

    # Remove manual page breaks
    $('.manual-page-break').remove()
    return

  that.load = ->
    # The report will be loaded dynamically by reloadReport()
    $('#report').html('').hide()
    # Load the report
    reloadReport()
    # Store referrer in cookie in case it is lost due to a page reload
    cookiename = 'ar.publish.view.referrer'
    backurl = document.referrer
    if backurl
      createCookie cookiename, backurl
    else
      backurl = readCookie(cookiename)
      # Fallback to portal_url instead of staying inside publish.
      if !backurl
        backurl = portal_url

    # Smooth scroll to content
    $('#ar_publish_container #ar_publish_summary a[href^="#"]').click (e) ->
      e.preventDefault()
      anchor = $(this).attr('href')
      offset = $(anchor).first().offset().top - 20
      $('html,body').animate { scrollTop: offset }, 'fast'
      return

    $('#sel_format').change (e) ->
      reloadReport()
      return

    $('#landscape').click (e) ->
      # get the checkbox value
      landscape = if $('#landscape').is(':checked') then 1 else 0
      $('body').toggleClass 'landscape', landscape
      # reverse the dimensions of all layouts
      for key of papersize
        papersize[key]['dimensions'].reverse()
      reloadReport()
      return

    $('#qcvisible').click (e) ->
      reloadReport()
      return

    $('#hvisible').click (e) ->
      reloadReport()
      return

    $('#sel_layout').change (e) ->
      $('body').removeClass $('body').attr('data-layout')
      $('body').attr 'data-layout', $(this).val()
      $('body').addClass $(this).val()
      reloadReport()
      return

    $('#publish_button').click (e) ->
      url = window.location.href
      qcvisible = if $('#qcvisible').is(':checked') then 1 else 0
      hvisible = if $('#hvisible').is(':checked') then 1 else 0
      template = $('#sel_format').val()
      $('#ar_publish_container').animate { opacity: 0.4 }, 'slow'
      count = $('#ar_publish_container #report .ar_publish_body').length
      $('#ar_publish_container #report .ar_publish_body').each ->
        rephtml = $(this).clone().wrap('<div>').parent().html()
        repstyle = $('#report-style').clone().wrap('<div>').parent().html()
        repstyle += $('#layout-style').clone().wrap('<div>').parent().html()
        repstyle += $('#layout-print').clone().wrap('<div>').parent().html()
        # We want this sincronously because we don't want to
        # flood WeasyPrint
        $.ajax(
          url: url
          type: 'POST'
          async: false
          data:
            'publish': 1
            'id': $(this).attr('id')
            'uid': $(this).attr('uid')
            'html': rephtml
            'template': template
            'qcvisible': qcvisible
            'hvisible': hvisible
            'style': repstyle).always ->
          if !--count
            location.href = backurl
          return
        return
      return

    $('#cancel_button').click (e) ->
      location.href = backurl
      return

    invalidbackurl = window.portal_url + '/++resource++bika.lims.images/report_invalid_back.png'
    $('.ar-invalid').css 'background', 'url(\'' + invalidbackurl + '\') repeat scroll #ffffff'

    provisbackurl = window.portal_url + '/++resource++bika.lims.images/report_provisional_back.png'
    $('.ar-provisional').css 'background', 'url(\'' + provisbackurl + '\') repeat scroll #ffffff'

    $('#sel_format_info').click (e) ->
      e.preventDefault()
      $('#sel_format_info_pane').toggle()
      return

    $('#margin-top').change (e) ->
      applyMarginAndReload $(this), 0
      return

    $('#margin-right').change (e) ->
      applyMarginAndReload $(this), 1
      return

    $('#margin-bottom').change (e) ->
      applyMarginAndReload $(this), 2
      return

    $('#margin-left').change (e) ->
      applyMarginAndReload $(this), 3
      return

    return

  return