document.addEventListener("DOMContentLoaded", function () {
  var printButton = $('#print-button');
  var cancelButton = $('#cancel-button');
  var templateSelect = $('select#template');
  var copiesCountInput = $('#copies_count');
  var stickerRule = $('#sticker-rule');
  var stickersWrapper = $('#stickers-wrapper');

  printButton.click(function (e) {
    e.preventDefault();
    printPdf();
    window.location = cancelButton.attr('data-url');
  });

  cancelButton.click(function (e) {
    e.preventDefault();
    window.location = cancelButton.attr('data-url');
  });

  templateSelect.change(function () {
    reload(templateSelect.val(), copiesCountInput.val());
  });

  copiesCountInput.change(function () {
    reload(templateSelect.val(), copiesCountInput.val());
  });

  var stickerWidth = $('.sticker').first().width();
  stickerRule.css({ 'width': stickerWidth, 'max-width': stickerWidth }).fadeIn();

  function reload(template, copies_count) {
    stickersWrapper.fadeTo('fast', 0.4);
    $.ajax({
      url: $('body').attr('data-itemsurl'),
      type: 'POST',
      async: true,
      data: {
        "template": template,
        "copies_count": copies_count,
        "filter_by_type": $('body').attr('data-filter_by_type')
      }
    }).always(function (data) {
      let htmldata = $(data).find('#stickers-wrapper').html();
      let bu = new BarcodeUtils();
      stickersWrapper.html(htmldata).fadeTo('fast', 1);
      bu.load();
      stickerRule = $('#sticker-rule');
      stickerRule.css({
        'width': $('.sticker').first().width(),
        'max-width': $('.sticker').first().width()
      }).fadeIn();
    });
  }

  function printPdf() {
    var url = window.location.href;
    var style = $('#stickers-style').clone().wrap('<div></div>').parent().html();
    var stickersHtml = '';

    $('#stickers-wrapper .sticker').each(function () {
      stickersHtml += $(this).clone().wrap('<div></div>').parent().html();
    });

    var form = '<form action="' + url + '" name="topdf" method="post" style="display:none">' +
      '<textarea name="html"><div style="padding:0px;"></div>' + stickersHtml + '</textarea>' +
      '<input type="hidden" name="pdf" value="1" />' +
      '<textarea name="style">' + style + '</textarea>' +
      '</form>';

    var pdfWindow = window.open();
    $(pdfWindow.document.body).html(form);
    pdfWindow.document.forms.topdf.submit();
  }

  if (location.href.indexOf("autoprint=1") !== -1) {
    printPdf();
    window.location = cancelButton.attr('data-url');
  }
});
