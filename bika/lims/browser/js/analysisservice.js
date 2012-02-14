jQuery( function($) {
$(document).ready(function(){

// PartitionSetup RecordsWidget AJAX things

    // reset list of containers
    $("[name^='PartitionSetup.preservation'], [name^='PartitionSetup.sampletype'], [name^='PartitionSetup.vol'],").change(function(){
        target = $(this).parents("tr").find("[name^='PartitionSetup.container']");
        st_uid = $(this).parents("tr").find("[name^='PartitionSetup.sampletype']").val();
        pres_uid = $(this).parents("tr").find("[name^='PartitionSetup.preservation']").val();
        minvol = $(this).parents("tr").find("[name^='PartitionSetup.vol']").val();
		$.ajax({
			type: 'POST',
			url: window.location.href + "/getContainers",
			data: {
				'st_uid': st_uid,
				'pres_uid': pres_uid,
				'minvol': minvol,
				'_authenticator': $('input[name="_authenticator"]').val()},
			success: function(data,textStatus,$XHR){
				// keep the current selection if possible
				option = $(target).val();
				$(target).empty();
				$.each(data, function(i,v){
					if(option == v[0]) {
						selected = 'selected="selected"';
					} else {
						selected = "";
					}
					$(target).append("<option value='"+v[0]+"' "+selected+">"+v[1]+"</option>");
				});
			},
			dataType: "json"
		});
    });
    //$("[name^='PartitionSetup.preservation']").change();

});
});

