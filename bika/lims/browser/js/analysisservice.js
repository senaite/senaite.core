jQuery( function($) {
$(document).ready(function(){

	_ = window.jsi18n;

//  change url to prevent caching
//		$.getJSON('as_setupdata?' + new Date().getTime(), function(data) {
		$.getJSON('as_setupdata',
			{'_authenticator': $('input[name="_authenticator"]').val()},
			function(data) {
				$('body').data('ar_formdata', data);

				// Contact dropdown is set in TAL to a default value.
				// we force change it to run the primary_contact .change()
				// code - but the ajax for ar_formdata must complete first.
				// So it goes here, in the ajax complete handler.
				contact_element = $("#primary_contact");
				if(contact_element.length > 0) {
					contact_element.change();
				}

			}
		);


	// setting the service default Preservation causes ContainerType
	// to be re-set
    $("[name^='Preservation:list']").change(function(){
        target = $("#Container:list");
		$.ajax({
			type: 'POST',
			url: window.location.href + "/getUpdatedContainers",
			data: {
				'pres_uid': $.toJSON($(this).val()),
				'allow_blank':false,
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




	// PartitionSetup RecordsWidget AJAX things
    // reset list of containers
	    $("[name^='PartitionSetup.preservation'], [name^='PartitionSetup.sampletype'], [name^='PartitionSetup.vol'],").change(function(){
        target = $(this).parents("tr").find("[name^='PartitionSetup.container']");
        st_uid = $(this).parents("tr").find("[name^='PartitionSetup.sampletype']").val();
        pres_uid = $(this).parents("tr").find("[name^='PartitionSetup.preservation']").val();
        minvol = $(this).parents("tr").find("[name^='PartitionSetup.vol']").val();
		$.ajax({
			type: 'POST',
			url: window.location.href + "/getUpdatedContainers",
			data: {
				'st_uid': st_uid,
				'pres_uid': $.toJSON(pres_uid),
				'minvol': minvol,
				'allow_blank': true,
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

