jQuery( function($) {
	$(document).ready(function(){

		
		// the filter text boxes trap the enter key and submit
		function inplace_submit(){
			options = {
					target: '',
					replaceTarget: false
			}
			form = $('folderContentsForm_filter');
			form.ajaxSubmit();
		}

		$(".folderlisting-filter").keyup(function (event) {
			if(event.which == 13){
				inplace_submit();
			}
		});

		$(".review_state_filter").change(function(){
			inplace_submit();
		});


	});
});
