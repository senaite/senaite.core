/**
 * Controller class for Bika LIMS Reports
 */
function ReportFolderView() {

    var that = this;

    /**
     * Entry-point method for AnalysisServiceEditView
     */
    that.load = function() {

        $("a[id$='_selector']").click(function(event){
            $(".criteria").toggle(false);
            event.preventDefault();
            var div_id = $(this).attr("id").split("_selector")[0];
            $("[id='"+div_id+"']").toggle(true);
        });

        // AJAX: Set ReferenceSamples dropdown when Supplier is selected
        $("#SupplierUID").change(function(){
            var val = $(this).val();
            $.getJSON("referenceanalysisqc_samples",
                    {"SupplierUID":val,
                    "_authenticator": $("input[name='_authenticator']").val()},
                    function(data){
                        $("#ReferenceSampleUID").empty().append("<option value=''></option>");
                        if(data){
                            for(var i=0;i<data.length;i++){
                                var sample = data[i];
                                $("#ReferenceSampleUID").append("<option value='"+sample[0]+"'>"+sample[1]+"</option>");
                            }
                        }
                    }
            );
        });

        // AJAX: Set ReferenceServices dropdown when ReferenceSample is selected
        $("#ReferenceSampleUID").change(function(){
            var val = $(this).val();
            $.getJSON("referenceanalysisqc_services",
                    {"ReferenceSampleUID":val,
                    "_authenticator": $("input[name='_authenticator']").val()},
                    function(data){
                        $("#ReferenceServiceUID").empty().append("<option value=''></option>");
                        if(data){
                            for(var i=0;i<data.length;i++){
                                var service = data[i];
                                $("#ReferenceServiceUID").append("<option value='"+service[0]+"'>"+service[1]+"</option>");
                            }
                        }
                    }
            );
        });

        // Reference QC: reset the dropdowns on page reload
        $("#SupplierUID").val("");

    }
}
