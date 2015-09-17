/**
 * Controller class for Client's sampling round Add/Edit view
 */
function ClientSamplingRoundAddEditView() {

    var that = this;

    /**
     * Entry-point method for ClientSamplingRoundAddEditView
     */
    that.load = function() {
        /**
         *  Allow to fill out the fields manually or automatically by selecting a Sampling Round Template (ReferenceField).
         */
        $('select#form-widgets-sr_template')
            .bind('click', function () {
                if (hasSamplingRoundTemplateData()) {
                    setSamplingRoundTemplateData();
                }
                else {
                    unsetSamplingRoundTemplate();
                }
            });
        // Hiding not needed buttons
        $("button[name='upButton']").hide();
        $("button[name='downButton']").hide();
    };

    function hasSamplingRoundTemplateData() {
        /**
         * Checks if the sampling rounds template field has a sampling rounds template selected.
         * :return: True if the field has data and False if the field contains "--NOVALUE--"
         */
        var value = $('select#form-widgets-sr_template').val();
        return value != "--NOVALUE--";
    }

    function setSamplingRoundTemplateData() {
        /**
         * This function gets the Sampling Rounds Template information and fill out each field.
         * The function also binds an event to each filled field in order to unset the Sampling Round Template
         * if one of the fields change.
         */

        // Getting the Sampling Round Template's data
        var srt_uid = $('select#form-widgets-sr_template').val();
        var sampler, department, samp_freq, instructions, artemplates_uids;
        var request_data = {
            catalog_name: "portal_catalog",
            UID: srt_uid,
            content_type: 'SRTemplate'
        };
        window.bika.lims.jsonapi_read(request_data, function (data) {
            if (data.objects && data.objects.length > 0) {
                var ob = data.objects[0];
                sampler = ob['Sampler'];
                department = ob['Department_uid'];
                samp_freq = ob['SamplingDaysFrequency'];
                instructions = ob['Instructions'];
                artemplates_uids = ob['ARTemplates_uid'];
            }
            // Writing the Sampling Round Template's data
            $("select#form-widgets-sampler").val(sampler);
            $("select#form-widgets-department").val(department);
            $("input#form-widgets-sampling_freq").val(samp_freq);
            $("textarea#form-widgets-instructions").val(instructions);
            // Setting Analysis Request Template
            // Moving all options contained in "to" box to the "from" box
            var to_options = $("select#form-widgets-model-to option");
            if(to_options.length >=1) {
                to_options.each(function () {
                    $(this).click();
                });
                $("button[name='to2fromButton']").click(); // Trigger the widget JS
            }
            if (artemplates_uids) {
                for (var i = 0; i <= artemplates_uids.length; i++) {
                    $("option[value='" + artemplates_uids[i] + "']").attr('selected', 'selected');
                }
            }
            if(artemplates_uids.length > 0) {
                $("button[name='from2toButton']").click(); // Trigger the widget JS
            }
        });
        // Binding the unsetSamplingRoundsTemplate function
        $("select#form-widgets-sampler," +
            "select#form-widgets-department," +
            "input#form-widgets-sampling_freq," +
            "textarea#form-widgets-instructions")
            .bind('change copy selected', function () {
                unsetSamplingRoundTemplate();
            });
        $("button[name='to2fromButton'], button[name='from2toButton']")
            .bind('blur', function () {
                unsetSamplingRoundTemplate();
        });
    }

    function unsetSamplingRoundTemplate(){
        /**
        This function disables the selected sampling Round Template and cut all bindings done in
         setSamplingRoundTemplate().
         */
        $('select#form-widgets-sr_template').val("--NOVALUE--");
        $("select#form-widgets-sampler," +
            "select#form-widgets-department," +
            "input#form-widgets-sampling_freq," +
            "textarea#form-widgets-instructions," +
            "textarea#form-widgets-instructions," +
            "button[name='to2fromButton']," +
            "button[name='from2toButton']").unbind();
    }
}
