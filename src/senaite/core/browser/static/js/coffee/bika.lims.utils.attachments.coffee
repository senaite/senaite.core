### Please use this command to compile this file into the parent `js` directory:
    coffee --no-header -w -o ../ -c bika.lims.utils.attachments.coffee
###

###*
# Controller class for calculation events
###

window.AttachmentsUtils = ->
  that = this

  that.load = ->
    # Worksheets need to check these before enabling Add button
    $('#AttachFile,#Service,#Analysis').change (event) ->
      attachfile = $('#AttachFile').val()
      if attachfile == undefined
        attachfile = ''
      service = $('#Service').val()
      if service == undefined
        service = ''
      analysis = $('#Analysis').val()
      if analysis == undefined
        analysis = ''
      if @id == 'Service'
        $('#Analysis').val ''
      if @id == 'Analysis'
        $('#Service').val ''
      if attachfile != '' and (service != '' or analysis != '')
        $('#addButton').removeAttr 'disabled'
      else
        $('#addButton').prop 'disabled', true
      return

    # Dropdown grid of Analyses in attachment forms
    $('#Analysis').combogrid
      colModel: [
        {
          'columnName': 'analysis_uid'
          'hidden': true
        }
        {
          'columnName': 'slot'
          'width': '10'
          'label': _t('Slot')
        }
        {
          'columnName': 'service'
          'width': '35'
          'label': _t('Service')
        }
        {
          'columnName': 'parent'
          'width': '35'
          'label': _t('Parent')
        }
        {
          'columnName': 'type'
          'width': '20'
          'label': _t('Type')
        }
      ]
      url: window.location.href.replace('/manage_results', '') + '/attachAnalyses?_authenticator=' + $('input[name="_authenticator"]').val()
      showOn: true
      width: '650px'
      select: (event, ui) ->
        $('#Analysis').val ui.item.service + " (slot #{ui.item.slot})"
        $('#analysis_uid').val ui.item.analysis_uid
        $(this).change()
        false

    return

  return
