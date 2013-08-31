(function($) {

	$(function () {
		$('input[name*=product]').change(function (e) {
			var el = $(e.target);
			row = el.closest('tr');
			price = parseFloat(row.children().eq(4).text());
			quantity = parseFloat(el.val());
			total = price * quantity
			row.children().eq(6).text(total.toFixed(2));
		});
	});

})(jQuery);
