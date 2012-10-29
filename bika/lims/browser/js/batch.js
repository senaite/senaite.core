(function( $ ) {
$(document).ready(function(){

    _ = window.jsi18n_bika;
    PMF = window.jsi18n_plone;

    if(window.location.href.search(window.bika_utils.data.prefixes['Batch']) == -1 &&
       window.location.href.search('portal_factory/Batch') == -1){
        $("input[id=BatchID]").after('<a style="border-bottom:none !important;margin-left:.5;"' +
                    ' class="add_batch"' +
                    ' href="'+window.portal_url+'/batches/portal_factory/Batch/new/edit"' +
                    ' rel="#overlay">' +
                    ' <img style="padding-bottom:1px;" src="'+window.portal_url+'/++resource++bika.lims.images/add.png"/>' +
                ' </a>');
    }

    $('a.add_batch').prepOverlay(
        {
            subtype: 'ajax',
            filter: 'head>*,#content>*:not(div.configlet),dl.portalMessage.error,dl.portalMessage.info',
            formselector: '#batch-base-edit',
            closeselector: '[name="form.button.cancel"]',
            width:'40%',
            noform:'close',
            config: {
                onLoad: function() {
                    // manually remove remarks
                    this.getOverlay().find("#archetypes-fieldname-Remarks").remove();
//                  // display only first tab's fields
//                  $("ul.formTabs").remove();
//                  $("#fieldset-schemaname").remove();
                },
                onClose: function(){
                    // here is where we'd populate the form controls, if we cared to.
                }
            }
        }
    );

    $("input[id*=BatchID]").combogrid({
        colModel: [{'columnName':'BatchUID','hidden':true},
                   {'columnName':'BatchID','width':'25','label':window.jsi18n_bika('Batch ID')},
                   {'columnName':'Description','width':'35','label':window.jsi18n_bika('Description')}],
        url: window.location.href.replace("/ar_add","") + "/getBatches?_authenticator=" + $('input[name="_authenticator"]').val(),
        select: function( event, ui ) {
            $(this).val(ui.item.BatchID);
            $(this).change();
            return false;
        }
    });

});
}(jQuery));
