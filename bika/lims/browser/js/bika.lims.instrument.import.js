/**
 * Controller class for Instrument Import View
 */
function InstrumentImportView() {

    var that = this;

    /**
     * Entry-point method for Instrument Import View
     */
    that.load = function() {

        // Load import form for selected data interface
        $("#exim").change(function(){
            $('.portalMessage').remove();
            $("#intermediate").toggle(false);
            if($(this).val() == ""){
                $("#import_form").empty();
            } else {
                $("#import_form").load(
                    window.location.href.replace("/import", "/getImportTemplate"),
                    {'_authenticator': $('input[name="_authenticator"]').val(),
                     'exim': $(this).val()
                    });
            }
        });
        show_default_result_key();

        // Invoke import
        $("[name='firstsubmit']").live('click',  function(event){
            event.preventDefault();
            $('.portalMessage').remove();
            if ($("#intermediate").length == 0) {
                $("#import_form").after("<div id='intermediate'></div>");
            }
            $("#intermediate").toggle(false);
            form = $(this).parents('form');
            options = {
                target: $('#intermediate'),
                data: JSON.stringify(form.formToArray()),
                dataType: 'json',
                processData: false,
                success: function(responseText, statusText, xhr, $form){
                    $("#intermediate").empty();
                    if(responseText['log'].length > 0){
                        str = "<div class='logbox'>";
                        str += "<h3>"+ _("Log trace") + "</h3><ul>";
                        $.each(responseText['log'], function(i,v){
                            str += "<li>" + v + "</li>";
                        });
                        str += "</ul></div>";
                        $("#intermediate").append(str).toggle(true);
                    }
                    if(responseText['errors'].length > 0){
                        str = "<div class='errorbox'>";
                        str += "<h3>"+ _("Errors") + "</h3><ul>";
                        $.each(responseText['errors'], function(i,v){
                            str += "<li>" + v + "</li>";
                        });
                        str += "</ul></div>";
                        $("#intermediate").append(str).toggle(true);
                    }
                    if(responseText['warns'].length > 0){
                        str = "<div class='warnbox'>";
                        str += "<h3>"+ _("Warnings") + "</h3><ul>";
                        $.each(responseText['warns'], function(i,v){
                            str += "<li>" + v + "</li>";
                        });
                        str += "</ul></div>";
                        $("#intermediate").append(str).toggle(true);
                    }
                },
                error: function(jqXHR, textStatus, errorThrown) {
                    $("#intermediate").empty();
                    str = "<div class='errorbox'>";
                    str += "<h3>"+ _("Errors found") + "</h3><ul>";
                    str += "<li>" + textStatus;
                    str += "<pre>" + errorThrown + "</pre></li></ul></div>";
                    $("#intermediate").append(str).toggle(true);
                }

            };
            form.ajaxSubmit(options);
            return false;
        });

    }

    function portalMessage(messages){
        str = "<dl class='portalMessage error'>"+
            "<dt>"+_('error')+"</dt>"+
            "<dd>";
        $.each(messages, function(i,v){
            str = str + "<ul><li>" + v + "</li></ul>";
        });
        str = str + "</dd></dl>";
        $('.portalMessage').remove();
        $('#viewlet-above-content').append(str);
    }

    function show_default_result_key() {
        /**
         * Show/hide the input element div#default_result when an AS is (un)selected.
         */
        $("select#exim").change(function() {
            console.log("heyhey");
            setTimeout(function() {
                $('select#analysis_service').bind("select change", function() {
                    if ($('select#analysis_service').val() != '') {
                        $('div#default_result').fadeIn();
                    }
                    else { $('div#default_result').fadeOut(); }
                })
            }, 800);
        });
    }
}
