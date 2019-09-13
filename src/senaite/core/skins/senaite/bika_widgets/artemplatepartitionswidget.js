(function( $ ) {

$(document).ready(function(){

	function renumber(){
		// Read list of valid, existing parts from the ARTemplatePartitionsWidget
		var valid_parts = [];
		$.each($("input[id*='Partitions-part_id-']"), function(i,e){
			var p = i+1;
			$(this).val('part-'+p);
			valid_parts.push('part-'+p);
		});
		// Remove deleted parts from ARTemplateAnalysesWidget
		$.each($(".listing_select_entry[field='Partition'] option"), function(i,e){
			if($.inArray($(e).val(), valid_parts) == -1 ){
				$(e).remove();
			}
		});
		// Add new parts from ARTemplateAnalysesWidget
		$.each($(".listing_select_entry[field='Partition']"), function(x,e){
			for (var i = 0; i < valid_parts.length; i++) {
				var p = valid_parts[i];
				var opt = $(e).find("option[value='"+p+"']");
				if (opt.length == 0) {
					$(e).append("<option value='"+p+"'>"+p+"</option>");
				};
			};
		});
	}

	$("input[id$='_more']").click(function(i,e){
		renumber();
	});

	$(".rw_deletebtn").live('click', function(i,e){
		renumber();
	});

    // On first load, remove extra empty item placed here by recordswidget
    var rows = $(".records_row_Partitions");
    var last = rows.length;
    $($(".records_row_Partitions")[last-1]).remove();
});

}(jQuery));
