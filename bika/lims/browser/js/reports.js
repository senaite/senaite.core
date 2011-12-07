jQuery( function($) {

	$(document).ready(function(){
        e = $('[id$="date"]')
        $(e).datepicker({'dateFormat': 'dd M yy', showAnim: ''})
			.click(function(){$(this).attr('value', '');})

        $("#analysestotals_selector").click(function(event){
            $("#submitter").toggle(true);
            $(".criteria").toggle(false);
            event.preventDefault();
            $("#analysestotals").toggle(true);
        });
        $("#analysespersampletype_selector").click(function(event){
            $(".criteria").toggle(false);
            event.preventDefault();
            $("#analysespersampletype").toggle(true);
        });
        $("#analysesperclient_selector, #memberanalysesperclient_selector")
            .click(function(event){
            $(".criteria").toggle(false);
            event.preventDefault();
            $("#analysesperclient").toggle(true);
        });
        $("#tats_selector").click(function(event){
            $(".criteria").toggle(false);
            event.preventDefault();
            $("#tats").toggle(true);
        });
        $("#attachments_selector").click(function(event){
            $(".criteria").toggle(false);
            event.preventDefault();
            $("#attachments").toggle(true);
        });
	});

});


