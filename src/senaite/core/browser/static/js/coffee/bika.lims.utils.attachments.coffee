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

    return

  return
