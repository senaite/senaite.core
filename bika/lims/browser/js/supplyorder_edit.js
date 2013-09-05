(function($) {

	$(function () {

		var parent, table, totalsTd, subtotalTd,
			vatTotalTd, totalTd, calculateTotals;

		parent = $('#supplyorder_edit');
		table = $('table.items', parent);

		totalTds = $('tr.totals td:nth-child(2)', parent);
		subtotalTd = totalTds.eq(0);
		vatTotalTd = totalTds.eq(1);
		totalTd = totalTds.eq(2);

		// Add up the totals for all the items
		calculateTotals = function () {
			var table, subtotal, vatTotal;
			subtotal = 0;
			vatTotal = 0;
			$('tr td:nth-child(8)', table).each(function () {
				var el, price, vat;
				el = $(this);
				price = parseFloat(el.text()),
				vat = parseFloat(el.siblings('td:nth-child(6)').text());
				subtotal += price;
				vatTotal += (price / 100) * vat;
			});
			subtotalTd.text(subtotal.toFixed(2));
			vatTotalTd.text(vatTotal.toFixed(2));
			totalTd.text((subtotal + vatTotal).toFixed(2));
		};

		// Calculate the total for a item
		calculateItemTotal = function (el) {
			row = el.closest('tr');
			price = parseFloat(row.children().eq(4).text());
			quantity = parseFloat(el.val());
			total = price * quantity;
			row.children().eq(7).text(total.toFixed(2));
		}

		// Attach change event and calcualte current totals
		$('input[name*=product]', parent).change(function (e) {
			calculateItemTotal($(e.target));
			calculateTotals();
		});

	});

})(jQuery);
