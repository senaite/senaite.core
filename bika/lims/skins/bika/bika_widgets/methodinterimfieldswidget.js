jQuery(function($){
$(document).ready(function(){

	$("input[name^='interim_field_']").live('change', function(){
		blank_names = [] // this will be a list of $('tr') objects which have an empty 'Field Name' value
		$.each($("tr.interimfield"), function(i,row){
			if($(this.children[0].firstChild).val() == ""){
				blank_names.push(row);
			}
			if($(this.children[0].firstChild).val() == "" &&
			   $(this.children[1].firstChild).val() == "" &&
			   $(this.children[2].firstChild).val() == ""){
				$(this).remove();
			}
		});

		if(blank_names.length == 0){
			$("#interim_fields_tbody").append('<tr class="interimfield">\
            <td><input type="text" name="interim_field_name:list"/></td>\
            <td><input type="text" name="interim_field_type:list"/></td>\
            <td><input type="text" name="interim_field_default:list"/></td>\
          </tr>');
		}
	});

});
});
