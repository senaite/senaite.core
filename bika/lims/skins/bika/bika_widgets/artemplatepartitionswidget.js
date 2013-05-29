(function( $ ) {

$(document).ready(function(){

	function renumber(){
		$.each($("input[id*='Partitions-part_id-']"), function(i,e){
			p = i+1;
			$(this).val('part-'+p)
		});
	}

	$("input[id$='_more']").click(function(i,e){
		renumber();
	});

	$(".rw_deletebtn").live('click', function(i,e){
		renumber();
	});

    // On first load, remove extra empty item placed here by recordswidget
    rows = $(".records_row_Partitions");
    last = rows.length;
    $($(".records_row_Partitions")[last-1]).remove();
});

}(jQuery));
