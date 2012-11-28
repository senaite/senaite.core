(function( $ ) {

	$(document).ready(function(){

		_ = jarn.i18n.MessageFactory('bika');
		PMF = jarn.i18n.MessageFactory('plone');

		function updateContainers(target,requestdata){
			$.ajax({
				type: 'POST',
				url: window.location.href + "/getUpdatedContainers",
				data: requestdata,
				success: function(data,textStatus,$XHR){
					// keep the current selection if possible
					option = $(target).val();
					if (option == null || option == undefined){ option = []; }
					$(target).empty();
					$.each(data, function(i,v){
						if($.inArray(v[0], option) > -1) {
							$(target).append("<option value='"+v[0]+"' selected='selected'>"+v[1]+"</option>");
						} else {
							$(target).append("<option value='"+v[0]+"'>"+v[1]+"</option>");
						}
					});
				},
				dataType: "json"
			});
		}

		// service defaults
		// update defalt Containers
		$("#RequiredVolume, #Separate").change(function(){
			separate = $("#Separate").attr('checked');
			if(!separate){
				$("[name='Preservation\\:list']").removeAttr('disabled');
			}
			requestdata = {
				'allow_blank':true,
				'show_container_types':!separate,
				'show_containers':separate,
				'_authenticator': $('input[name="_authenticator"]').val()}
			updateContainers("#Container\\:list", requestdata);
		});

		// partition table -> separate checkboxes
		// partition table -> minvol field
		// update row's containers
		$("[name^='PartitionSetup.separate'],[name^='PartitionSetup.vol']").change(function(){
			separate = $(this).parents("tr").find("[name^='PartitionSetup.separate']").attr("checked");
			if (!separate){
				$(this).parents("tr").find("[name^='PartitionSetup.preservation']").removeAttr('disabled');
			}
			minvol = $(this).parents("tr").find("[name^='PartitionSetup.vol']").val();
			target = $(this).parents("tr").find("[name^='PartitionSetup.container']");
			requestdata = {
				'allow_blank':true,
				'minvol':minvol,
				'show_container_types':!separate,
				'show_containers':separate,
				'_authenticator': $('input[name="_authenticator"]').val()}
			updateContainers(target, requestdata);
		});

		// copy sampletype MinimumVolume to minvol when selecting sampletype
		$("[name^='PartitionSetup.sampletype']").change(function(){
			// get sampletype volume from bika_utils
			option = $(this).children().filter(":selected");
			if(!option || $(option).val() == '' || option.length == 0){
				return;
			}
			option = option[0];
			title = $(option).text();
			minvol = window.bika_utils.data['st_uids'][title]['minvol'];
			// put value in minvol field
			target = $(this).parents("tr").find("[name^='PartitionSetup.vol']");
			$(target).val(minvol);
			// trigger change on containers, in case SampleType volume rendered
			// the selected container too small and removed it from the list
			$(this).parents("tr").find("[name^='PartitionSetup.container']").change();

		});

		// Selecting a pre-preserved container will filter and disable the
		// Preservations list.
		$("[name^='Container'],[name^='PartitionSetup.container']").change(function(){
			if ($(this).attr('name').search("Container") == 0){
				target = "[name='Preservation\\:list']";
				separate = $('#Separate').attr("checked");
				if (!separate){
					$(target).removeAttr('disabled');
					return;
				}
			} else {
				separate = $(this).parents("tr").find("[name^='PartitionSetup.separate']").attr("checked");
				target = $(this).parents("tr").find("[name^='PartitionSetup.preservation']");
				if(!separate){
					$(target).removeAttr('disabled');
					return;
				}
			}
			preservations = window.bika_utils.data.preservations;
			containers = window.bika_utils.data.containers;
			selection = $(this).val();
			if(selection == null || selection == undefined || selection.length == 0) {
				$(target).removeAttr('disabled');
				return;
			}
			// Only allow first container to be selected.
			selection = selection[0];
			$(this).val(selection);

			container = containers[selection];
			if(container!=null
			   && container!=undefined
			   && container.prepreserved
			   && container.preservation){
					$(target).val(container.preservation);
					$(target).attr('disabled', true);
			} else {
				$(target).removeAttr('disabled');
			}
		});


		// update on first load
		$("[name^='PartitionSetup.separate']").change();
		$("[name^='Container']").change();
		$("[name^='PartitionSetup.container']").change();


	});
}(jQuery));
