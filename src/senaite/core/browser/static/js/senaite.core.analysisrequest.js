/** Sample View Controller
 *
 * This controller is loaded for sample view, e.g.:
 * `/senaite/samples/clients/client-1/H2O-0001`
 *
 */
window.AnalysisRequestView = class AnalysisRequestView {
  load() {
    this.bindInterpretationTemplateInsert();
  }

  bindInterpretationTemplateInsert() {
    $("#interpretationtemplate-insert").on("click", (event) => {
      event.preventDefault();
      const template_uid = $("#interpretationtemplate").val();
      if (!template_uid) return;

      const container = $("div[id^='ResultsInterpretationDepts-'].active textarea[id^='ResultsInterpretationDepts-richtext-']");
      if (container.length !== 1) return;
      const container_id = container.attr("id");

      const request_data = {
        catalog_name: "uid_catalog",
        UID: template_uid,
        include_fields: ["text"]
      };

      window.senaite.core.globals.jsonapi_read(request_data, (data) => {
        if (data.objects.length === 1) {
          const text = data.objects[0].text;
          tinymce.get(container_id).insertContent(text);
        }
      });
    });
  }
}
