/**
 * Controller class for Lab Contacts view of Department
 */
function DepartmentLabContactsView() {

    var that = this;

    /**
     * Entry-point method for DepartmentLabContactsViewView
     */
    that.load = function() {
        set_autosave();
    };

    function set_autosave() {
        /**
        Set an event for each checkbox in the view. After chenging the state of
        the checkbox, the event automatically saves the change.
        */
        $("table.bika-listing-table td input[type='checkbox']")
            .not('[type="hidden"]').each(function(i){
            // Save input fields
            $(this).change(function () {
                var pointer = this;
                save_change(pointer);
            });
        });
    }

    function save_change(pointer) {
        /**
         Build an array with the data to be saved.
         @pointer is the object which has been modified and we want to save
         its new state.
         */
        var check_value, contact_uid, department_uid, uid, department_path,
            requestdata={};
        // Getting the checkbox state
        check_value = $(pointer).prop('checked');
        // Getting the lab contact uid, url and name
        contact_uid = $(pointer).val();
        // Getting the department uid
        url = window.location.href.replace('/labcontacts', '');
        department_path = url.replace(window.portal_url, '');
        // Filling the requestdata
        requestdata.contact_uid = contact_uid;
        requestdata.checkbox_value = check_value;
        requestdata.department = department_path;
        save_element(requestdata);
    }

    function save_element(requestdata) {
        /**
        Given a dict with the uid and the checkbox value, update this state via
        ajax petition.
        @requestdata should has the format:
            {department=department_path,
            checkbox_value=check_value,
            contact_uid=contact_uid}
        */
        // Getting the name of the modified lab contact as an anchor
        var url =  $('tr[uid="' + requestdata.contact_uid + '"] td.Fullname a')
            .attr('href');
        var name =  $('tr[uid="' + requestdata.contact_uid + '"] td.Fullname a')
            .text();
        var anch =  "<a href='"+ url + "'>" + name + "</a>";
        $.ajax({
            type: "POST",
            dataType: "json",
            url: window.location.href.replace('/labcontacts', '')+"/labcontactupdate",
            data: {'data': JSON.stringify(requestdata)}
        })
        .done(function(data) {
            //success alert
            if (data !== null && data.success === true) {
                bika.lims.SiteView.notificationPanel(
                    anch + ' updated successfully', "succeed");
            } else {
                bika.lims.SiteView.notificationPanel(
                    'Failure while updating ' + anch, "error");
                var msg =
                    '[bika.lims.department.js in DepartmentLabContactsView] ' +
                    'Failure while updating ' + name + 'in ' +
                    window.location.href;
                console.warn(msg);
                window.bika.lims.error(msg);
            }
        })
        .fail(function(){
            //error
            bika.lims.SiteView.notificationPanel(
                'Error while updating ' + anch, "error");
            var msg =
                '[bika.lims.department.js in DepartmentLabContactsView] ' +
                'Error while updating ' + name + 'in ' +
                window.location.href;
            console.warn(msg);
            window.bika.lims.error(msg);
        });
    }

}
