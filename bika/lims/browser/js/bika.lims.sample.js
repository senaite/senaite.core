/**
 * Controller class for Sample View
 */
function SampleView() {

    var that = this;

    that.load = function() {
        // Plone "Sample" transition is only available when Sampler and DateSampled
        // are completed
        workflow_transition_sample();
        // fires AR workflow transitions when using the schedule samplign transition
        transition_schedule_sampling();
        // Trap the save button
        $("input[name='save']").click(save_header);

        // Disable Plone UI for preserve transition
        $("#workflow-transition-preserve").click(workflow_transition_preserve);

    }

    function workflow_transition_sample() {
        $("#workflow-transition-sample").click(function(event){
            event.preventDefault();
            var date = $("#DateSampled").val();
            var sampler = $("#Sampler").val();
            if (date && sampler) {
                var form = $("form[name='header_form']");
                // this 'transition' key is scanned for in header_table.py/__call__
                form.append("<input type='hidden' name='transition' value='sample'/>")
                form.submit();
            }
            else {
                var message = "";
                if (date == "" || date == undefined || date == null) {
                    message = message + PMF('${name} is required, please correct.',
                                            {'name': _("Date Sampled")})
                }
                if (sampler == "" || sampler == undefined || sampler == null) {
                    if (message != "") {
                        message = message + "<br/>";
                    }
                    message = message + PMF('${name} is required, please correct.',
                                            {'name': _("Sampler")})
                }
                if ( message != "") {
                    window.bika.lims.portalMessage(message);
                }
            }
        });
    }

    function save_header(event){
        event.preventDefault();
        requestdata = new Object();
        $.each($("form[name='header_form']").find("input,select"), function(i,v){
            name = $(v).attr('name');
            value =  $(v).attr('type') == 'checkbox' ? $(v).prop('checked') : $(v).val();
            requestdata[name] = value;
        });
        requeststring = $.param(requestdata);
        href = window.location.href.split("?")[0] + "?" + requeststring;
        window.location.href = href;
    }

    function workflow_transition_preserve(event){
        event.preventDefault()
        message = _("You must preserve individual Sample Partitions");
        window.bika.lims.portalMessage(message);
    }

    function transition_schedule_sampling(){
        /* Force the transition to use the "workflow_action" url instead of content_status_modify. workflow_action triggers a class from
        analysisrequest/workflow/AnalysisRequestWorkflowAction which manage
        workflow_actions from analysisrequest/sample/samplepartition objects.
        It is not possible to abort a transition using "workflow_script_*".
        The recommended way is to set a guard instead.

        The guard expression should be able to look up a view to facilitate more complex guard code, but when a guard returns False the transition isn't even listed as available. It is listed after saving the fields.

        TODO This should be using content_status_modify!  modifying the href
        is silly.*/
        var old_url = $('#workflow-transition-schedule_sampling').attr('href');
        /*The addAnalysisRequest doesn't has the transition url*/
        if(old_url){
            var new_url = old_url.replace("content_status_modify", "workflow_action");
            $('#workflow-transition-schedule_sampling').attr('href', new_url);
            // When user clicks on the transition
            $('#workflow-transition-schedule_sampling').click(function(){
                e.preventDefault();
                var date = $("#SamplingDate").val();
                var sampler = $("#ScheduledSamplingSampler").val();
                if (date !== "" && date !== undefined && date !== null &&
                        sampler !== "" && sampler !== undefined &&
                        sampler !== null) {
                    window.location.href = new_url;
                }
                else {
                    var message = "";
                    if (date === "" || date === undefined || date === null) {
                        message = message + PMF('${name} is required for this action, please correct.',
                                                {'name': _("Sampling Date")});
                    }
                    if (sampler === "" || sampler === undefined || sampler === null) {
                        if (message !== "") {
                            message = message + "<br/>";
                        }
                        message = message + PMF(
                            '${name} is required, please correct.',
                            {'name': _("'Define the Sampler for the shceduled'")});
                    }
                    if ( message !== "") {
                        window.bika.lims.portalMessage(message);
                    }
                }
            });
        }
    }
}
