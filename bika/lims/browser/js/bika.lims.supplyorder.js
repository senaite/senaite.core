/**
 * Controller class for SupplyOrderEditView
 */
function SupplyOrderEditView() {

    var that = this;

    var manual_fd  = $('#archetypes-fieldname-ManualEntryOfResults');
    var manual_chk = $('#archetypes-fieldname-ManualEntryOfResults #ManualEntryOfResults');
    var instre_fd  = $('#archetypes-fieldname-InstrumentEntryOfResults');
    var instr_chk  = $('#archetypes-fieldname-InstrumentEntryOfResults #InstrumentEntryOfResults');
    var methods_fd = $('#archetypes-fieldname-Methods');
    var methods_ms = $('#archetypes-fieldname-Methods #Methods');
    var method_fd  = $('#archetypes-fieldname-_Method');
    var method_sel = $('#archetypes-fieldname-_Method #_Method');
    var instrs_fd  = $('#archetypes-fieldname-Instruments');
    var instrs_ms  = $('#archetypes-fieldname-Instruments #Instruments');
    var instr_fd   = $('#archetypes-fieldname-Instrument');
    var instr_sel  = $('#archetypes-fieldname-Instrument #Instrument');
    var defcalc_chk= $('#archetypes-fieldname-UseDefaultCalculation #UseDefaultCalculation');
    var calc_fd    = $('#archetypes-fieldname-_Calculation');
    var calc_sel   = $('#archetypes-fieldname-_Calculation #_Calculation');
    var acalc_fd   = $('#archetypes-fieldname-DeferredCalculation');
    var acalc_sel  = $('#archetypes-fieldname-DeferredCalculation #DeferredCalculation');
    var interim_fd = $("#archetypes-fieldname-InterimFields");
    var interim_rw = $("#archetypes-fieldname-InterimFields tr.records_row_InterimFields");

    var parent, table, totalsTd, subtotalTd, VATAmountTd, totalTd,
        calculateTotals;


    /**
     * Entry-point method for InstrumentCertificationEditView
     */
    that.load = function() {

        parent = $('#supplyorder_edit');
        table = $('table.items', parent);

        totalTds = $('tr.totals td:nth-child(2) span:nth-child(2)', parent);
        subtotalTd = totalTds.eq(0);
        VATAmountTd = totalTds.eq(1);
        totalTd = totalTds.eq(2);

        // Attach change event and calcualte current totals
        $('input[name*=product]', parent).change(function (e) {
            calculateItemTotal($(e.target));
            calculateTotals();
        });

    }

    /**
     * Add up the totals for all the items
     */
    function calculateTotals() {
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
    }

    /**
     * Calculate the total for a item
     */
    function calculateItemTotal(el) {
        row = el.closest('tr');
        window.test = row;
        price = parseFloat($('td:eq(4) span:eq(1)', row).text());
        quantity = parseFloat(el.val());
        total = price * quantity;
        $('td:eq(7) span:eq(1)', row).text(total.toFixed(2));
    }
}
