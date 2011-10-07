jQuery( function($) {
$(document).ready(function(){

	function portalMessage(message){
		str = "<dl class='portalMessage error'>"+
			"<dt i18n:translate='error'>Error</dt>"+
			"<dd><ul>" + message +
			"</ul></dd></dl>";
		$('.portalMessage').remove();
		$(str).appendTo('#viewlet-above-content');
	}

	// add Worksheet Templates dropdown menu
	if($("input[name='add_Worksheet']").length == 1){
		$.ajax({
			url: window.location.href + "/getWorksheetTemplates",
			type: 'POST',
			data: {'_authenticator': $('input[name="_authenticator"]').val()},
			dataType: "json",
			success: function(data,textStatus,$XHR){
				html = "&nbsp;&nbsp;From template:&nbsp;<select name='wstemplate'><option value=''>None</option>";
				for(i=0; i< data.length; i++){
					html = html + "<option value='"+data[i][0]+"'>"+data[i][1]+"</option>";
				}
				html = html + "</select>";
				$('input[name="add_Worksheet"]').after(html);
			}
		});
	}

	// search form - selecting a category fills up the service selector
	$("#CategorySelector").live("change", function(){
		val = $("#CategorySelector").val();
		if(val == 'any'){
			$("#ServiceSelector").empty();
			$("#ServiceSelector").append("<option value='any'>Any</option>");
			return;
		}
		$.ajax({
			url: window.location.href.replace("/add_analyses","") + "/getServices",
			type: 'POST',
			data: {'_authenticator': $('input[name="_authenticator"]').val(),
			       'getCategoryUID': val},
			dataType: "json",
			success: function(data,textStatus,$XHR){
				$("#ServiceSelector").empty();
				$("#ServiceSelector").append("<option value='any'>Any</option>");
				for(i=0; i< data.length; i++){
					$("#ServiceSelector").append("<option value='"+data[i][0]+"'>"+data[i][1]+"</option>");
				}
			}
		});
	});
	$("#CategorySelector").trigger("change");


});
});
