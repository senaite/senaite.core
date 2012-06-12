(function( $ ) {

function updateContainers(target,requestdata){
	$.ajax({
		type: 'POST',
		url: window.location.href + "/getUpdatedContainers",
		data: requestdata,
		success: function(data,textStatus,$XHR){
			// keep the current selection if possible
			option = $(target).val();
			if (option != null && option != undefined){
				$(target).empty();
				$.each(data, function(i,v){
					if($.inArray(v[0], option) > -1) {
						$(target).append("<option value='"+v[0]+"' selected='selected'>"+v[1]+"</option>");
					} else {
						$(target).append("<option value='"+v[0]+"'>"+v[1]+"</option>");
					}
				});
			}
		},
		dataType: "json"
	});
}

$(document).ready(function(){

	_ = window.jsi18n;

	// Setting default preservation or default required volume
	// causes default containers to be filtered
	$("[name='Preservation\\:list'], #RequiredVolume").change(function(){
		requestdata = {
			'pres_uid': $.toJSON($("[name='Preservation\\:list']").val()),
			'allow_blank':true,
			'_authenticator': $('input[name="_authenticator"]').val()
		}
		updateContainers("#Container\\:list", requestdata);
	});

	// When changing preservation, sampletype, or required volume fields,
	// in any PartitionSetup field row, causes thes row's
	// containers to be filtered
    $("[name^='PartitionSetup.preservation'],[name^='PartitionSetup.sampletype'], [name^='PartitionSetup.vol']").change(function(){
		target = $(this).parents("tr").find("[name^='PartitionSetup.container']");
		minvol = $(this).parents("tr").find("[name^='PartitionSetup.vol']").val();
		requestdata = {
			'minvol': minvol,
			'allow_blank':true,
			'_authenticator': $('input[name="_authenticator"]').val()
		}
		pres_uid = $(this).parents("tr").find("[name^='PartitionSetup.preservation']").val();
		if (pres_uid != null && pres_uid != undefined){
			requestdata['pres_uid'] = $.toJSON(pres_uid);
			requestdata['pres_uid'] = $.toJSON(pres_uid);
		}
		st_uid = $(this).parents("tr").find("[name^='PartitionSetup.sampletype']").val();
		if (st_uid != null && st_uid != undefined){
			requestdata['st_uid'] = st_uid;
		}
		updateContainers(target, requestdata);
    });

	// Selecting a pre-preserved container will filter and disable the
	// Preservations list.
	$("[name^='Container'],[name^='PartitionSetup.container']").change(function(){
		if ($(this).attr('name').search("Container") == 0){
			target = "[name='Preservation\\:list']";
		} else {
			target = $(this).parents("tr").find("[name^='PartitionSetup.preservation']");
		}
		preservations = window.bsc.data['preservations'];
		containers = window.bsc.data['containers'];
		selection = $(this).val();
		if(selection == null || selection == undefined){
			return;
		}
		prepreserved = [];
		// foreach selected container
		for(c=0;c<selection.length;c++){
			container = containers[selection[c]];
			if(container!=null
			   && container!=undefined
			   && container.prepreserved){
				prepreserved.push(container.preservation);
			}
		}
		if(prepreserved.length > 0){
			$(target).attr('disabled', true);
		} else {
			$(target).removeAttr('disabled');
		}
	});

	// Refresh on first load
	$("[name^='PartitionSetup.sampletype']").change();
	$("[name^='PartitionSetup.container']").change();
	console.log($("[name^='Container']").val());
	$("[name^='Container']").change();


});
}(jQuery));
