(function( $ ) {
$(document).ready(function(){

    _ = window.jsi18n_bika;
    PMF = window.jsi18n_plone;

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
