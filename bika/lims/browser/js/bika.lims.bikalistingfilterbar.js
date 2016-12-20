/**
 * Controller class for Bika Listing Filter Bar
 */
function BikaListingFilterBarController() {
    var that = this;
    that.load = function() {
        filter_bar_submit_controller();
    };
    /**
    This function submits the form once the filter button is clicked.
    The function sets the input[name="bika_listing_filter_bar_button"]
    value as '1'
    */
    function filter_bar_submit_controller(){
        $('input#bika_listing_filter_bar_button').bind('click', function () {
            var form = $(this).parents("form");
            $('input#bika_listing_filter_bar_submit').val('1');
            $(form).submit();
        });
    }
}
