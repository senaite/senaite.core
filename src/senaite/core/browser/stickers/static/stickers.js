document.addEventListener("DOMContentLoaded", function () {
  var backURL = $('body').data('back_url');
  var cancelButton = $('#cancel-button');
  var copiesCountInput = $('#copies_count');
  var filterByType = $('body').data('filter_by_type');
  var itemsURL = $('body').data('items_url');
  var printButton = $('#print-button');
  var stickerRule = $('#sticker-rule');
  var stickersWrapper = $('#stickers-wrapper');
  var templateSelect = $('select#template');

  printButton.click(function (e) {
    e.preventDefault();
    printPdf();
    window.location = backURL;
  });

  cancelButton.click(function (e) {
    e.preventDefault();
    window.location = backURL;
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
      url: itemsURL,
      type: 'POST',
      async: true,
      data: {
        "template": template,
        "copies_count": copies_count,
        "filter_by_type": filterByType
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

    var form = $('<form>', {
        action: url,
        method: 'post',
        target: '_blank',
      style: 'display:none'
    });
    form.append($('<textarea>', { name: 'html', text: '<div style="padding:0px;"></div>' + stickersHtml }));
    form.append($('<input>', { type: 'hidden', name: 'pdf', value: '1' }));
    form.append($('<textarea>', { name: 'style', text: style }));

    $('body').append(form);
    form.submit();
    form.remove();
  }
});
