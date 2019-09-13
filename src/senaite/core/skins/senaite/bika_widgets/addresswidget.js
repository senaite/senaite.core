jQuery( function($) {

	$(document).ready(function(){

		function lookups(){
			// Selecting a Country (populate state field)
			$("[id*='\\.country']").change(function(){
				field = $(this).attr('name').split(".")[0];
				// // removes value from state, city, zip.
				// $("[id='"+field+"\\.state']").val("");
				// $("[id='"+field+"\\.district']").val("");
				// re-populate state dropdown
				populate_state_select(field);
			});
			// Selecting a State (populate district field)
			$("[id*='\\.state']").change(function(){
				field = $(this).attr('name').split(".")[0];
				populate_district_select(field);
			});
		}

		function copyAddress(){
			to_address = $(this).attr('id').split(".")[0];
			from_address = $(this).val();
			if (from_address == '') {
				return
			}

			state = $("#" + from_address + "\\.state").clone();
			$(state).attr('id', to_address + ".state");
			$(state).attr('name', to_address + ".state:record");
			$("#" + to_address + "\\.state").replaceWith(state);

			district = $("#" + from_address + "\\.district").clone();
			$(district).attr('id', to_address + ".district");
			$(district).attr('name', to_address + ".district:record");
			$("#" + to_address + "\\.district").replaceWith(district);

			$.each(['country', 'state', 'district'], function(i, item){
				val = $("#" + from_address + "\\." + item).val();
				$.each($("#" + to_address + "\\." + item + " > option"), function(i,e){
					if($(e).val() == val){
						$(e).attr('selected', 'selected');
					} else {
						$(e).removeAttr('selected');
					}
				});
			});

			$('#' + to_address + '\\.city').val($('#' + from_address + '\\.city').val()).change();
			$('#' + to_address + '\\.zip').val($('#' + from_address + '\\.zip').val()).change();
			$('#' + to_address + '\\.address').val($('#' + from_address + '\\.address').val()).change();

		    lookups();

		}

		function populate_state_select(field){
			$.ajax({
				type: 'POST',
				url: portal_url + "/getGeoStates",
				data: {'country': $("[id='"+field+"\\.country']").val(),
					   '_authenticator': $('input[name="_authenticator"]').val()},
				success: function(data,textStatus,$XHR){
					target = $("[id='"+field+"\\.state']");
					$(target).empty();
					$(target).append("<option value=''></option>");
					$.each(data, function(i,v){
						$(target).append('<option value="'+v[2]+'">'+v[2]+'</option>');
					});
					$("[id='"+field+"\\.district']").empty();
				},
				dataType: "json"
			});
		}
		function populate_district_select(field){
			$.ajax({
				type: 'POST',
				url: portal_url + "/getGeoDistricts",
				data: {'country': $("[id='"+field+"\\.country']").val(),
					  'state': $("[id='"+field+"\\.state']").val(),
					   '_authenticator': $('input[name="_authenticator"]').val()},
				success: function(data,textStatus,$XHR){
					target = $("[id='"+field+"\\.district']");
					$(target).empty();
					$(target).append("<option value=''></option>");
					$.each(data, function(i,v){
						$(target).append('<option value="'+v[2]+'">'+v[2]+'</option>');
					});
				},
				dataType: "json"
			});
		}

		$("[id*='\\.selection']").change(copyAddress);
		lookups();
	});
});
