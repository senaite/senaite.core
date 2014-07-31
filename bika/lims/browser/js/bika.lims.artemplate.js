/**
 * Controller class for AR Template Edit view
 */
function ARTemplateEditView() {

    window.jarn.i18n.loadCatalog("bika");
    var _ = window.jarn.i18n.MessageFactory("bika");

    var that = this;
    var samplepoint = $('#archetypes-fieldname-SamplePoint #SamplePoint');

    /**
     * Entry-point method for AnalysisServiceEditView
     */
    that.load = function() {

        $(".portaltype-artemplate input[name$='save']").addClass('allowMultiSubmit');
        $(".portaltype-artemplate input[name$='save']").click(clickSaveButton);

        // Display only the sample points contained by the same parent
        filterSamplePointsCombo();
    }

    /***
     * Filters the Sample Points Combo.
     * Display only the Sample Points from the same parent (Client or
     * BikaSetup) as the current Template.
     */
    function filterSamplePointsCombo() {
        var request_data = {};
        if (document.location.href.search('/clients/') > 0) {
            // The parent object for this template is a Client.
            // Need to retrieve the Client UID from the client ID
            var cid = document.location.href.split("clients")[1].split("/")[1];
            request_data = {
                portal_type: "Client",
                id: cid,
                include_fields: ["UID"]
            };
        } else {
            // The parent object is bika_setup
            request_data = {
                portal_type: "BikaSetup",
                include_fields: ["UID"]
            };
        }
        window.bika.lims.jsonapi_read(request_data, function(data){
            if(data.objects && data.objects.length < 1) {
                return;
            }
            var obj = data.objects[0];
            var puid = obj.UID;
            $(samplepoint).attr("search_query", $.toJSON({"getClientUID": obj.UID}));
            referencewidget_lookups([$(samplepoint)]);
        });
    }

    function clickSaveButton(event){
        var selected_analyses = $('[name^="uids\\:list"]').filter(':checked');
        if(selected_analyses.length < 1){
            window.bika.lims.portalMessage("No analyses have been selected");
            window.scroll(0, 0);
            return false;
        }
    }
}
