// ./artemplatepartitionswidget.pt
// ../../../browser/widgets/artemplatepartitionswidget.py
// Some of the widget field are handled in ./analysisservice.js
(function( $ ) {

//////////////////////////////////////
function addPart(event){
	event.preventDefault();

	highest_part = '';
	from_tr = '';
	$.each($('#partitions td.part_id'), function(i,v){
		partid = $($(v).children()[1]).text();
		if (partid > highest_part){
			from_tr = $(v).parent();
			highest_part = partid;
		}
	});
	highest_part = highest_part.split("-")[1];
	next_part = parseInt(highest_part,10) + 1;

	// copy and re-format new partition table row
	part_trs = $("#partitions tbody tr")[0];
	uid	= $(from_tr).attr('uid');
	to_tr = $(from_tr).clone();
	$(to_tr).attr('id', 'folder-contents-item-part-'+next_part);
	$(to_tr).attr('uid', 'part-'+next_part);
	$(to_tr).find("#"+uid+"_row_data").attr('id', "part-"+next_part+"_row_data").attr('name', "row_data."+next_part+":records");
	$(to_tr).find("#"+uid).attr('id', 'part-'+next_part);
	$(to_tr).find("input[value='"+uid+"']").attr('value', 'part-'+next_part);
	$(to_tr).find("[uid='"+uid+"']").attr('uid', 'part-'+next_part);
	$(to_tr).find("span[uid='"+uid+"']").attr('uid', 'part-'+next_part);
	$(to_tr).find("input[name^='part_id']").attr('name', "part_id.part-"+next_part+":records").attr('value', 'part-'+next_part);
	$(to_tr).find("select[field='container_uid']").attr('name', "container_uid.part-"+next_part+":records");
	$(to_tr).find("select[field='preservation_uid']").attr('name', "preservation_uid.part-"+next_part+":records");
	$($($(to_tr).children('td')[0]).children()[1]).empty().append('part-'+next_part);
	$($("#partitions tbody")[0]).append($(to_tr));

	// add this part to Partition selectors in Analyses tab
	$.each($('select[name^="Partition\\."]'), function(i,v){
		$(v).append($("<option value='part-"+next_part+"'>part-"+next_part+"</option>"));
	});
}

////////////////////////////////////////
function removePart(event){
	event.preventDefault();

	//find and remove highest numbered part
	hp = '';
	tr = '';
	$.each($('#partitions td.part_id'), function(i,v){
		partid = $($(v).children()[1]).text();
		if (partid > hp){
			tr = $(v).parent();
			hp = partid;
		}
	});
	if (hp == 'part-1'){
		return;
	}
	$(tr).remove();

	// remove this part from Partition selectors
	$.each($('select[name^="Partition\\."]'), function(i,v){
		$(v).find("option[value='"+hp+"']").remove();
	});
}

$(document).ready(function(){

	$(".add_part").click(addPart);
	$(".remove_part").click(removePart);

});

}(jQuery));
