/**
 * Controller class for Analysis Request Manage Results view
 */
function AnalysisRequestManageResultsView() {

    var that = this;

    /**
     * Entry-point method for AnalysisRequestManageResultsView
     */
    that.load = function() {

        // Set the analyst automatically when selected in the picklist
        $('.portaltype-analysisrequest .bika-listing-table td.Analyst select').change(function() {
            var analyst = $(this).val();
            var key = $(this).closest('tr').attr('keyword');
            var obj_path = window.location.href.replace(window.portal_url, '');
            var obj_path_split = obj_path.split('/');
            if (obj_path_split.length > 4) {
                obj_path_split[obj_path_split.length-1] = key;
            } else {
                obj_path_split.push(key);
            }
            obj_path = obj_path_split.join('/');
            $.ajax({
                type: "POST",
                url: window.portal_url+"/@@API/update",
                data: {"obj_path": obj_path,
                       "Analyst":  analyst}
            });
        });

    }
}
