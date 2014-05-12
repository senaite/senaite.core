(function($) {

	$(function () {

		var parent, table, totalsTd, subtotalTd,
			VATAmountTd, totalTd, calculateTotals;

		parent = $('#supplyorder_edit');
		table = $('table.items', parent);

		totalTds = $('tr.totals td:nth-child(2) span:nth-child(2)', parent);
		subtotalTd = totalTds.eq(0);
		VATAmountTd = totalTds.eq(1);
		totalTd = totalTds.eq(2);

		// Add up the totals for all the items
		calculateTotals = function () {
			var table, subtotal, VATAmount;
			subtotal = 0;
			VATAmount = 0;
			$('tr td:nth-child(8) span:nth-child(2)', table).each(function () {
				var el, vatEl, price, vat;
				el = $(this);
				vatEl = el.parent().siblings('td:nth-child(6)');
				price = parseFloat(el.text()),
				vat = parseFloat(vatEl.text());
				subtotal += price;
				VATAmount += (price / 100) * vat;
			});
			subtotalTd.text(subtotal.toFixed(2));
			VATAmountTd.text(VATAmount.toFixed(2));
			totalTd.text((subtotal + VATAmount).toFixed(2));
		};

		// Calculate the total for a item
		calculateItemTotal = function (el) {
			row = el.closest('tr');
			window.test = row;
			price = parseFloat($('td:eq(4) span:eq(1)', row).text());
			quantity = parseFloat(el.val());
			total = price * quantity;
			$('td:eq(7) span:eq(1)', row).text(total.toFixed(2));
		}

		// Attach change event and calcualte current totals
		$('input[name*=product]', parent).change(function (e) {
			calculateItemTotal($(e.target));
			calculateTotals();
		});

	});

})(jQuery);
