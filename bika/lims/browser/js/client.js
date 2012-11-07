(function( $ ) {
$(document).ready(function(){

	_ = window.jsi18n_bika;
	PMF = window.jsi18n_plone;

	// Confirm before resetting client specs to default lab specs
    $("a[href*=set_to_lab_defaults]").click(function(event){
		// always prevent default/
		// url is activated manually from 'Yes' below.
		url = $(this).attr("href");
		event.preventDefault();
		yes = _('Yes');
		no = _('No');
		var $confirmation = $("<div></div>")
			.html(_("This will remove all existing client analysis specifications "+
					"and create copies of all lab specifications. "+
					"Are you sure you want to do this?"))
			.dialog({
				resizable:false,
				title: _('Set to lab defaults'),
				buttons: {
					yes: function(event){
						$(this).dialog("close");
						window.location.href = url;
					},
					no: function(event){
						$(this).dialog("close");
					}
				}
			});
    });

    if(window.location.href.search(window.bika_utils.data.prefixes['Client']) == -1 &&
       window.location.href.search('portal_factory/Client') == -1){
        $("input[id=ClientID]").after('<a style="border-bottom:none !important;margin-left:.5;"' +
                    ' class="add_client"' +
                    ' href="'+window.portal_url+'/clients/portal_factory/Client/new/edit"' +
                    ' rel="#overlay">' +
                    ' <img style="padding-bottom:1px;" src="'+window.portal_url+'/++resource++bika.lims.images/add.png"/>' +
                ' </a>');
    }

    $('a.add_client').prepOverlay(
        {
            subtype: 'ajax',
            filter: 'head>*,#content>*:not(div.configlet),dl.portalMessage.error,dl.portalMessage.info',
            formselector: '#client-base-edit',
            closeselector: '[name="form.button.cancel"]',
            width:'40%',
            noform:'close',
            config: {
                onLoad: function() {
                    // manually remove remarks
                    this.getOverlay().find("#archetypes-fieldname-Remarks").remove();
                },
                onClose: function(){
                    // here is where we'd populate the form controls, if we cared to.
                }
            }
        }
    );

    $("input[id*=ClientID]").combogrid({
        colModel: [{'columnName':'ClientUID','hidden':true},
                   {'columnName':'ClientID','width':'25','label':window.jsi18n_bika('Client ID')},
                   {'columnName':'Title','width':'75','label':window.jsi18n_bika('Title')}],
        url: window.portal_url + "/getClients?_authenticator=" + $('input[name="_authenticator"]').val(),
        select: function( event, ui ) {
            $(this).val(ui.item.ClientID);
            $(this).change();
            return false;
        }
    });

});
}(jQuery));
