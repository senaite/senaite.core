/**
 * Barcode Controller
 *
 * This controller is loaded if a barcode or qrcode element was found
 */
window.BarcodeUtils = class BarcodeUtils {
  constructor() {
    this.load = this.load.bind(this);
  }

  load() {
    // Generate QR codes
    $(".qrcode").each(function () {
      const $el = $(this);
      const render = $el.data("render") || "div";
      const size = $el.data("size");
      const code = $el.data("code");
      const quiet = $el.data("quiet") || 0;
      const text = $el.data("text") || "no text";

      $el.qrcode({
        render: render,
        size: size, // 37.79 px ~ 10mm
        code: code,
        quiet: quiet,
        text: text.toString()
      });
    });

    // Generate barcodes
    $(".barcode").each(function () {
      const $el = $(this);
      const id = $el.data("id") || "deadbeef";
      const code = $el.data("code") || "code128";
      const barHeight = $el.data("barheight") || 10;
      const addQuietZone = $el.data("addquietzone") || false;
      const showHRI = $el.data("showhri") || false;
      const output = $el.data("output") || "svg";
      const color = $el.data("color") || "#000000";

      $el.barcode(id.toString(), code, {
        barHeight: barHeight,
        addQuietZone: addQuietZone,
        showHRI: showHRI,
        output: output,
        color: color
      });
    });
  }
}
