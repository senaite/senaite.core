/* Prepare global namespace */
window.senaite = window.senaite || {};
window.senaite.core = window.senaite.core || {};
window.senaite.core.controllers = window.senaite.core.controllers || {};
window.senaite.core.globals = window.senaite.core.globals || {};

/**
 * Mapping of DOM selectors to controller class names.
 * Controllers are instantiated and stored in senaite.core.controllers.
 */
const CONTROLLER_MAP = {
  "html": ["CommonUtils", "SiteView"],
  ".barcode, .qrcode": ["BarcodeUtils"],
  ".attachments": ["AttachmentsUtils"],
  ".template-lims-setup": ["SetupViewController"],

  // Instruments
  ".portaltype-instrument.template-referenceanalyses": ["InstrumentReferenceAnalysesView"],
  ".portaltype-instrumentcertification.template-base_edit": ["InstrumentCertificationEditView"],
  ".portaltype-instrument.template-base_edit": ["InstrumentEditView"],

  // Calculations
  ".portaltype-calculation": ["CalculationEditView"],

  // Setup
  ".portaltype-bikasetup.template-base_edit": ["BikaSetupEditView"],

  // Clients
  ".portaltype-client.template-base_edit": ["ClientEditView"],

  // Reference Samples
  ".portaltype-referencesample.template-analyses": ["ReferenceSampleAnalysesView"],

  // Analysis Requests
  ".portaltype-analysisrequest": ["AnalysisRequestView"],
  ".portaltype-analysisrequest.template-base_view": ["WorksheetManageResultsView"],
  "#analysisrequest_add_form": ["AnalysisRequestAdd"],
  ".template-partition_magic": ["PartitionController"],

  // Worksheets
  ".portaltype-worksheetfolder": ["WorksheetFolderView"],
  ".portaltype-worksheet.template-manage_results": ["WorksheetManageResultsView"],
  "#worksheet-printview-wrapper": ["WorksheetPrintView"],

  // Remarks Widget
  ".ArchetypesRemarksWidget": ["RemarksWidgetView"]
};

/**
 * Load and initialize controllers, storing instances in senaite.core.controllers
 *
 * @param {boolean} all - Whether to force load all controllers
 * @param {Array<string>} controllerKeys - Force-load specific selectors
 * @returns {number} - Count of newly loaded controllers
 */
window.senaite.core.globals.loadControllers = function(all = false, controllerKeys = []) {
  const registry = window.senaite.core.controllers;
  const loaded = new Set(Object.keys(registry));
  let loadedCount = 0;

  for (const selector in CONTROLLER_MAP) {
    const shouldLoad = all || controllerKeys.includes(selector) || $(selector).length > 0;
    if (!shouldLoad) continue;

    CONTROLLER_MAP[selector].forEach(controllerName => {
      if (loaded.has(controllerName)) return;

      const ControllerClass = window[controllerName];
      if (typeof ControllerClass !== "function") {
        console.warn(`[senaite.core.loader] Controller not found: ${controllerName}`);
        return;
      }

      try {
        const instance = new ControllerClass();
        if (typeof instance.load === "function") {
          instance.load();
        }
        registry[controllerName] = instance;
        loaded.add(controllerName);
        loadedCount += 1;
        console.debug(`[senaite.core.loader] Loaded: ${controllerName}`);
      } catch (err) {
        console.error(`[senaite.core.loader] Failed to load ${controllerName}:`, err);
      }
    });
  }

  return loadedCount;
};

// Auto-load controllers when DOM is ready
document.addEventListener("DOMContentLoaded", () => {
  const count = window.senaite.core.globals.loadControllers(false, []);
  console.debug(`*** SENAITE LOADER INITIALIZED (${count} controllers loaded) ***`);
});
