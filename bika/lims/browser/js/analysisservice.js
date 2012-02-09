jQuery( function($) {
$(document).ready(function(){

// PartitionSetup RecordsWidget AJAX things

    // select a Preservation: reset list of containers

    $("[name^='PartitionSetup.preservation']").change(function(){
        e = $(this).parents("tr").find("[name^='PartitionSetup.container']");
		$.ajax({
			type: 'POST',
			url: window.location.href + "/getPreservationContainers",
			data: {'uid': $(this).val(),
				   '_authenticator': $('input[name="_authenticator"]').val()},
			success: function(data,textStatus,$XHR){
				// keep the current selection if possible
				option = $(e).val();
				$(e).empty();
				$.each(data, function(i,v){
					$(e).append("<option value='"+v[0]+"'>"+v[1]+"</option>");
				});
			},
			dataType: "json"
		});
    });
    $("[name^='PartitionSetup.preservation']").change();

});
});

