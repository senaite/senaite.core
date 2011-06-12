jQuery( function($) {
	$(document).ready(function(){

		function inplace_submit(){
			options = {target: '#folderlisting-main-table', replaceTarget: true }
			form = $('.folderContentsForm');
			form.ajaxSubmit(options);
		}

		function folderlisting_filter_keyup(key){
		}
		
		// the filter text boxes trap the enter key and submit
		$(".folderlisting-filter").live('keyup', function(key){
			if(key.which == 13) {
				inplace_submit();
			}
		})

		// review_state radio boxes submit the form
		$(".review_state_filter").live('change', function(){
			inplace_submit();
		});

	});
});
