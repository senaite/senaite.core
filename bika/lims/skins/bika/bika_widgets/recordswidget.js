jQuery(function($){
$(document).ready(function(){

	fieldname = $("#fieldname").val();

	new_row = '<tr class="'+fieldtype+'">\
		<td><input type="text" class="analysis_input" name="'+fieldname+'.id:records"/></td>\
		<td><input type="text" class="analysis_input" name="'+fieldname+'.title:records"/></td>\
		<td><input type="text" class="analysis_input" name="'+fieldname+'.value:records"/></td>\
		<td><input type="text" class="analysis_input" name="'+fieldname+'.unit:records"/></td>\
	</tr>';

	function remove_blank_rows(){
		$.each($("tr."+fieldtype), function(i,row){
			if($(this.children[0].children[0]).val().replace(" ","") == "" &&
			   $(this.children[1].children[0]).val().replace(" ","") == "" &&
			   $(this.children[2].children[0]).val().replace(" ","") == "" &&
			   $(this.children[3].children[0]).val().replace(" ","") == ""){
					$(this).remove();
			}
		});
	}

	$("."+fieldtype+"_input").live('change', function(){
		remove_blank_rows();
		$("#"+fieldtype+"_tbody").append(new_row);
	});
	$("#"+fieldtype+"_tbody").append(new_row);

	// just to be sure blank rows aren't interfering
	$("input[name='form\\.button\\.save']").click(function(){
		remove_blank_rows();
	});

});
});
