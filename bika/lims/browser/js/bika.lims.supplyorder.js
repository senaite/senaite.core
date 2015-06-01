/**
 * Controller class for SupplyOrderEditView
 */
function SupplyOrderEditView() {

	var that = this

	that.load = function () {
		"use strict"

		// Attach change event and calcualte current totals
		$('input.quantity').change(function () {
			calculateItemTotal(this)
			calculateTotals()
		})

	}

	function toInt(st) {
		"use strict"
		var i = parseInt(st, 10)
		if (!i || i == undefined || isNaN(i)) {
			i = 0
		}
		return i
	}

	function toFloat(st) {
		"use strict"
		var f = parseFloat(st)
		if (!f || f == undefined || isNaN(f)) {
			f = 0
		}
		return f
	}

	function calculateItemTotal(element) {
		"use strict"
		var row = $(element).parents('tr')
		var price = toFloat(row.find(".price").text())
		var quantity = toInt(row.find(".quantity").val())
		var total = price * quantity
		row.find(".item_total").text(total.toFixed(2))
	}

	function calculateTotals() {
		var subtotal = 0
		var VATAmount = 0
		$('td.item_total').each(function (i, element) {
			var price = toFloat($(element).text())
			var vat = toFloat($(element).siblings(".item_vat").text())
			subtotal += price
			VATAmount += (price / 100) * vat
		})
		$("tr.totals td.currency span.subtotal").text(subtotal.toFixed(2))
		$("tr.totals td.currency span.vat").text(VATAmount.toFixed(2))
		$("tr.totals td.currency span.total").text((subtotal + VATAmount).toFixed(2))
	}

}
