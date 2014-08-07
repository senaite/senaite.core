/**
 * Controller class for barcode utils
 */
function BarcodeUtils() {

    var that = this;

    that.load = function() {

        // if collection gets something worth submitting,
        // it's sent to utils.barcode_entry here.
        function redirect(code){
            $.ajax({
                type: 'POST',
                url: 'barcode_entry',
                data: {'entry':code.replace("*",""),
                        '_authenticator': $('input[name="_authenticator"]').val()},
                success: function(responseText, statusText, xhr, $form) {
                    if (responseText) {
                        window.location.href = responseText;
                    }
                }
            });
        }

        var collecting = false;
        var code = ""

        $(window).keypress(function(event) {
            if (collecting) {
                // short-circuit tineout when ending * is reached
                if (event.which == "42"){
                    collecting = false;
                    redirect(code);
                }
                code = code + String.fromCharCode(event.which);
            } else {
                // valid barcodes will start and end with "*"
                if (event.which == "42") {
                    collecting = true;
                    code = String.fromCharCode(event.which);
                    setTimeout(function(){
                        if(collecting == true && code != ""){
                            collecting = false;
                            redirect(code);
                        }
                    }, 500)
                }
            }
        });
    }
}
