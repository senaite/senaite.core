/**
 * Controller class for barcode utils
 */
function BarcodeUtils() {

    var that = this;

    that.load = function() {

        // https://larsjung.de/jquery-qrcode
        $(".qrcode").each(function() {
           let render = $(this).data("render") || "div";
           let size = $(this).data("size");
           let code = $(this).data("code");
           let quiet = $(this).data("quiet") || 0;
           let text = $(this).data("text") || "no text";

           $(this).qrcode({
                render: render,
                size: size, // 37.79 pixel == 10mm
                code: code,
                quiet: quiet, // quiet zone in modules
                text: text.toString()
            });
        });


        // https://barcode-coder.com/en/barcode-jquery-plugin-201.html
        $(".barcode").each(function() {
            let id = $(this).data("id") || "deadbeef";
            let code = $(this).data("code") || "code128";
            let barHeight = $(this).data("barheight") || 10;
            let addQuietZone = $(this).data("addquietzone") || false;
            let showHRI = $(this).data("showhri") || false;
            let output = $(this).data("output") || "svg";
            let color = $(this).data("color") || "#000000";

            $(this).barcode(id.toString(), code, {
                barHeight: barHeight,
                addQuietZone: addQuietZone,
                showHRI: showHRI,
                output: output,
                color: color
            });
        });
    }
}
