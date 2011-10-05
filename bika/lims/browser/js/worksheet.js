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
				json = $.parseJSON(data);
				for(i=0; i< data.length; i++){
					html = html + "<option value='"+data[i][0]+"'>"+data[i][1]+"</option>";
				}
				html = html + "</select>";
				$('input[name="add_Worksheet"]').after(html);
			}
		});
	}

	$("#analyst").change(function(){
		if ($("#analyst").val() == '') {
			return false;
		}
		$.ajax({
		  type: 'POST',
		  url: window.location.href + "/setAnalyst",
		  data: {'value': $("#analyst").val(),
				  '_authenticator': $('input[name="_authenticator"]').val()}
		});
	});
});
});
