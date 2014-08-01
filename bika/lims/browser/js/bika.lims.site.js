/**
 * Controller class for all site views
 */
function SiteView() {

    var that = this;

    that.load = function() {

        loadClientEvents();

        loadReferenceDefinitionEvents();

        // TODO: Provisional method, needs its own controller?
        loadAnalysisRequestLayout();

    }

    // TODO Provisional method. needs its own controller?
    function loadAnalysisRequestLayout() {
        $('#layout').change(function(){
            var address = $(".context_action_link").attr('href');
            var href = addParam(address, 'layout', $(this).val())
            $(".context_action_link").attr('href', href);
        });
        $('#ar_count').each(function() {
            var elem = $(this);

            // Save current value of element
            elem.data('oldVal', elem.val());

            // Look for changes in the value
            elem.bind("propertychange keyup input paste", function(event){
                var new_val = elem.val();
                // If value has changed...
                if (new_val != '' && elem.data('oldVal') != new_val) {
                    // Updated stored value
                    elem.data('oldVal', new_val);
                    var address = $(".context_action_link").attr('href');
                    var href = addParam(address, 'ar_count', $(this).val())
                    $(".context_action_link").attr('href', href);
                }
            });
        });

        function addParam(address, param, val){
            var argparts;
            var parts = address.split("?");
            var url = parts[0];
            var args = [];
            if (parts.length > 1) {
                var found = false;
                args = parts[1].split("&");
                for (var arg=0; arg<args.length; arg++) {
                    argparts = args[arg].split('=');
                    if (argparts[0] == param) {
                        args[arg] = param + '=' + val;
                        found = true;
                    }
                };
                if (found == false) {
                    args.push(param + '=' + val);
                };
            } else {
                args.push(param + '=' + val);
            };
            return url + "?" + args.join('&');
        };
    }

    function loadClientEvents() {

        // Client creation overlay
        $('a.add_client').prepOverlay({
                subtype: 'ajax',
                filter: 'head>*,#content>*:not(div.configlet),dl.portalMessage.error,dl.portalMessage.info',
                formselector: '#client-base-edit',
                closeselector: '[name="form.button.cancel"]',
                width:'70%',
                noform:'close',
                config: {
                    closeOnEsc: false,
                    onLoad: function() {
                        // manually remove remarks
                        this.getOverlay().find("#archetypes-fieldname-Remarks").remove();
                    },
                    onClose: function(){
                        // here is where we'd populate the form controls, if we cared to.
                    }
                }
        });

        // Client combogrid searches by ID
        $("input[id*='ClientID']").combogrid({
            colModel: [{'columnName':'ClientUID','hidden':true},
                       {'columnName':'ClientID','width':'20','label':_('Client ID')},
                       {'columnName':'Title','width':'80','label':_('Title')}],
            showOn: true,
            width: '450px',
            url: window.portal_url + "/getClients?_authenticator=" + $('input[name="_authenticator"]').val(),
            select: function( event, ui ) {
                $(this).val(ui.item.ClientID);
                $(this).change();
                return false;
            }
        });

        // Display add Client button next to Client ID input for all
        // views except from Client View
        if($(".portaltype-client").length == 0){
            $("input[id='ClientID']")
                .after('<a style="border-bottom:none !important;margin-left:.5;"' +
                       ' class="add_client"' +
                       ' href="'+window.portal_url+'/clients/portal_factory/Client/new/edit"' +
                       ' rel="#overlay">' +
                       ' <img style="padding-bottom:1px;" src="'+window.portal_url+'/++resource++bika.lims.images/add.png"/>' +
                       '</a>');
        }

        // Confirm before resetting client specs to default lab specs
        $("a[href*='set_to_lab_defaults']").click(function(event){
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
    }

    function loadReferenceDefinitionEvents() {

        // a reference definition is selected from the dropdown
        // (../../skins/bika/bika_widgets/referenceresultswidget.js)
        $('#ReferenceDefinition\\:list').change(function(){
            authenticator = $('input[name="_authenticator"]').val();
            uid = $(this).val();
            option = $(this).children(":selected").html();

            if (uid == '') {
                // No reference definition selected;
                // render empty widget.
                $("#Blank").prop('checked',false);
                $("#Hazardous").prop('checked',false);
                $('.bika-listing-table')
                    .load('referenceresults', {'_authenticator': authenticator});
                return;
            }

            if(option.search(_("(Blank)")) > -1){
                $("#Blank").prop('checked',true);
            } else {
                $("#Blank").prop('checked',false);
            }

            if(option.search(_("(Hazardous)")) > -1){
                $("#Hazardous").prop('checked',true);
            } else {
                $("#Hazardous").prop('checked',false);
            }

            $('.bika-listing-table')
                .load('referenceresults',
                    {'_authenticator': authenticator,
                     'uid':uid});
        });

        // If validation failed, and user is returned to page - requires reload.
        if ($('#ReferenceDefinition\\:list').val() != ''){
            $('#ReferenceDefinition\\:list').change();
        }
    }
}