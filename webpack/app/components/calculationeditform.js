import $ from "jquery";
import { flushSync } from "react-dom";

class CalculationEditForm {

    constructor() {
        this.DataGrid = null;
        this.rawTestValue = null;
        this.initialized = false;
        this.initializeFrame = null;
        this.initialize = this.initialize.bind(this);
        this.rawTestInput = document.getElementById("form-widgets-raw_test_keywords");
        if (this.rawTestInput) {
            this.load();
        }
    }

    load() {
        this.rawTestValue = this.rawTestInput.value;
        this.makeReadonlyTestKeywords();
        this.hideAAField();
        this.wrapRawTestInput(this);
        document.addEventListener("senaite.core.widgets:loaded", this.initialize);
        this.initialize();

        // Update parameters while typing, without waiting for the field to blur.
        const formula = document.getElementById("form-widgets-formula");
        if (formula) {
            let timer;
            formula.addEventListener("input", () => {
                clearTimeout(timer);
                timer = setTimeout(() => {
                    formula.dispatchEvent(new Event("change", {bubbles: true}));
                }, 250);
            });
            formula.addEventListener("change", () => clearTimeout(timer));
        }
    }

    // The first datagrid to mount can be the interim grid. Wait until the
    // test grid is ready, and replay keywords received before our setter existed.
    initialize() {
        if (this.initialized || this.initializeFrame !== null) return;
        this.initializeFrame = requestAnimationFrame(() => {
            this.initializeFrame = null;
            if (this.updateTestParameters(this.rawTestValue)) {
                this.initialized = true;
                document.removeEventListener("senaite.core.widgets:loaded", this.initialize);
            }
        });
    }

    updateTestParameters(newValue) {
        const keywords = newValue.split(",").filter(k => k);
        const table = this.getTestParamTable();
        if (!table) return false;
        const visibleRows = this.getDataGridWidget().get_visible_rows(table);
        if (!visibleRows.length) return false;
        // The callback serializes the DOM, so commit React rows first.
        flushSync(() => {
            if (keywords.length === 0) {
                for (let i = 0; i < visibleRows.length - 1; i++) {
                    this.getDataGridWidget().remove_row(visibleRows[i]);
                }
            } else if (keywords.length > (visibleRows.length - 1)) {
                let newRows = keywords.length - visibleRows.length + 1;
                for (let i = 0; i < newRows; i++) {
                    this.getDataGridWidget().auto_append_row(table);
                }
            } else if (keywords.length < visibleRows.length - 1) {
                for (let i = 0; i < visibleRows.length - 1; i++) {
                    let row = $(visibleRows[i]).find("input[id$='-widgets-keyword']");
                    if (row) {
                        if (!keywords.includes(row?.val())) {
                            this.getDataGridWidget().remove_row(visibleRows[i]);
                        }
                    }
                }
            }
        });

        this.hideAAField();
        this.getDataGridWidget().trigger_custom_event("update_test_parameters", keywords);
        this.makeReadonlyTestKeywords();
        return true;
    }

    getDataGridWidget() {
        if (!this.DataGrid) {
            this.DataGrid = window.widgets.datagrid;
        }
        return this.DataGrid;
    }

    getTestParamTable() {
        return $("tbody[data-name_prefix='form.widgets.test_parameters']")[0];
    }

    makeReadonlyTestKeywords() {
        $("input[id^='form-widgets-test_parameters-']")
            .filter("[id$='-widgets-keyword']")
            .each((i, e) => $(e).attr("readonly", true));
        $("#form-widgets-test_result").attr("readonly", true);
    }

    hideAAField() {
        $("tbody[data-name_prefix='form.widgets.test_parameters'] > tr")
            .each((i, e) => {
                if (!["AA", "TT"].includes($(e).attr("data-index"))) {
                    $(e).show();
                } else {
                    $(e).hide();
                }
            });
    }

    /**
     * Overrides the native setter for the raw test input field to control the test parameter DataGrid.
     *
     * XXX: This feels a bit hacky and is dependent on how the editform.js sets the input value!
     * E.g. if we use therer the `native_set_value` method, this will not work.
     *
     * Maybe it would be better to react on the `input` event or do this in a mutation observer
     */
    wrapRawTestInput(parent) {
        const nativeSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, "value").set;
        Object.defineProperty(this.rawTestInput, "value", {
            set: function(newValue) {
                // prevent maximum call stack size exceeded error by using the native setter
                nativeSetter.call(this, newValue);
                parent.rawTestValue = newValue;
                parent.updateTestParameters(newValue);
            },
            get: function() {
                return parent.rawTestValue;
            }
        });
    }
}

export default CalculationEditForm;
