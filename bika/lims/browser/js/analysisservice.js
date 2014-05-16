(function( $ ) {
"use strict";

window.bika.lims.AnalysisService = window.bika.lims.AnalysisService || {
    Dependants: function(service_uid){
        var request_data = {
            catalog_name: "bika_setup_catalog",
            UID: service_uid
        };
        var deps = {};
        $.ajaxSetup({async:false});
        window.bika.lims.jsonapi_read(request_data, function(data){
            if (data.objects != null && data.objects.length > 0) {
                deps = data.objects[0].ServiceDependants;
            } else {
                deps = [];
            }
        });
        $.ajaxSetup({async:true});
        return deps;
    },
    Dependencies: function(service_uid){
        var request_data = {
            catalog_name: "bika_setup_catalog",
            UID: service_uid
        };
        var deps = {};
        $.ajaxSetup({async:false});
        window.bika.lims.jsonapi_read(request_data, function(data){
            if (data.objects != null && data.objects.length > 0) {
                deps = data.objects[0].ServiceDependencies;
            } else {
                deps = [];
            }
        });
        $.ajaxSetup({async:true});
        return deps;
    }
};



$(document).ready(function(){

    function updateContainers(target,requestdata){
        $.ajax({
            type: "POST",
            url: window.location.href + "/getUpdatedContainers",
            data: requestdata,
            success: function(data){
                // keep the current selection if possible
                var option = $(target).val();
                if (option === null || option === undefined){
                    option = [];
                }
                $(target).empty();
                $.each(data, function(i,v){
                    if($.inArray(v[0], option) > -1) {
                        $(target).append("<option value='"+v[0]+"' selected='selected'>"+v[1]+"</option>");
                    } else {
                        $(target).append("<option value='"+v[0]+"'>"+v[1]+"</option>");
                    }
                });
            },
            dataType: "json"
        });
    }

    // service defaults
    // update defalt Containers
    $(".portaltype-analysisservice #RequiredVolume, .portaltype-analysisservice #Separate").change(function(){
        var separate = $("#Separate").prop("checked");
        if(!separate){
            $("[name='Preservation\\:list']").prop("disabled", false);
        }
        var requestdata = {
            "allow_blank":true,
            "show_container_types":!separate,
            "show_containers":separate,
            "_authenticator": $("input[name='_authenticator']").val()
        };
        updateContainers("#Container\\:list", requestdata);
    });

    // partition table -> separate checkboxes
    // partition table -> minvol field
    // update row's containers
    $(".portaltype-analysisservice [name^='PartitionSetup.separate'],.portaltype-analysisservice [name^='PartitionSetup.vol']").change(function(){
        var separate = $(this).parents("tr").find("[name^='PartitionSetup.separate']").prop("checked");
        if (!separate){
            $(this).parents("tr").find("[name^='PartitionSetup.preservation']").prop("disabled", false);
        }
        var minvol = $(this).parents("tr").find("[name^='PartitionSetup.vol']").val();
        var target = $(this).parents("tr").find("[name^='PartitionSetup.container']");
        var requestdata = {
            "allow_blank":true,
            "minvol":minvol,
            "show_container_types":!separate,
            "show_containers":separate,
            "_authenticator": $("input[name='_authenticator']").val()
        };
        updateContainers(target, requestdata);
    });

    // copy sampletype MinimumVolume to minvol when selecting sampletype
    $(".portaltype-analysisservice [name^='PartitionSetup.sampletype']").change(function(){
        var st_element = this;
        var request_data = {
            catalog_name: "uid_catalog",
            UID: $(this).val()
        };
        window.bika.lims.jsonapi_read(request_data, function(data) {
            var minvol = data.objects[0].MinimumVolume;
            var target = $(st_element).parents("tr").find("[name^='PartitionSetup.vol']");
            $(target).val(minvol);
            // trigger change on containers, in case SampleType volume rendered
            // the selected container too small and removed it from the list
            $(st_element).parents("tr").find("[name^='PartitionSetup.container']").change();
        });
    });


    // handling of pre-preserved containers in the Default Container field
    // select the preservation and disable the input.
    $(".portaltype-analysisservice #Container").bind("selected", function(){
        var container_uid = $(this).attr("uid");
        var request_data = {
            catalog_name: "uid_catalog",
            UID: container_uid
        };
        window.bika.lims.jsonapi_read(request_data, function(data) {
            if (data.objects.length < 1 ||
                (!data.objects[0].PrePreserved) || (!data.objects[0].Preservation)) {
                $("#Preservation").val("");
                $("#Preservation").prop("disabled", false);
            } else {
                $("#Preservation").val(data.objects[0].Preservation);
                $("#Preservation").prop("disabled", true);
            }
        });
    });

    // handling of pre-preserved containers in the per Sample-Type rows
    // select the preservation and disable the input.
    $(".portaltype-analysisservice [name^='PartitionSetup.container']").change(function(){
        var target = $(this).parents("tr").find("[name^='PartitionSetup.preservation']");
        var container_uid = $(this).val();
        if(!container_uid || (container_uid.length == 1 && !container_uid[0])){
            $(target).prop("disabled", false);
            return;
        }
        container_uid = container_uid[0];
        var request_data = {
            catalog_name: "uid_catalog",
            UID: container_uid
        };
        window.bika.lims.jsonapi_read(request_data, function(data) {
            if (data.objects.length < 1 ||
                (!data.objects[0].PrePreserved) || (!data.objects[0].Preservation)) {
                $(target).prop("disabled", false);
            } else {
                $(this).val(container_uid);  // makes no sense to leave multiple items selected
                $(target).val(data.objects[0].Preservation);
                $(target).prop("disabled", true);
            }
        });
    });


    // update on first load
    // $(".portaltype-analysisservice [name^='PartitionSetup.separate']").change();
    // $(".portaltype-analysisservice [name^='Container']").change();
    // $(".portaltype-analysisservice [name^='PartitionSetup.container']").trigger("selected");

    // initial setup - hide Interim widget if no Calc is selected
    if($(".portaltype-analysisservice #Calculation").val() === ""){
        $("#InterimFields_more").click(); // blank last row
        var rows = $("tr.records_row_InterimFields"); // Clear the rest
        if($(rows).length > 1){
            for (var i = $(rows).length - 2; i >= 0; i--) {
                $($(rows)[i]).remove();
            }
        }
        $("#archetypes-fieldname-InterimFields").hide();
        return;
    }


});
}(jQuery));
