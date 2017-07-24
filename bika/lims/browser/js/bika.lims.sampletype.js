/**
 * Controller class for Sample Type View
 */
 function SampleTypeView() {

    var that = this;

    /**
     * Entry-point method for SampleTypeEditView
     */
    that.load = function() {

        $('#Prefix').change(function() {
            if(this.value.includes(" ")){
                alert("Please do not use spaces in Prefix.");
                this.value="";
            }
        });

    }
}