/**
 * Analysis Request View Controllers
 */
window.AnalysisRequestView = class AnalysisRequestView {
  load() {
    this.bindTransitionWithPublicationSpec();
    this.bindScheduleSampling();
    this.bindWorkflowTransitionSample();
    this.bindInterpretationTemplateInsert();
  }

  bindTransitionWithPublicationSpec() {
    $("a[id^='workflow-transition']")
      .not("#workflow-transition-schedule_sampling")
      .not("#workflow-transition-sample")
      .on("click", function (event) {
        debugger
        event.preventDefault();
        let href = event.currentTarget.href;
        const element = $("#PublicationSpecification_uid");
        if (element.length > 0) {
          href += `&PublicationSpecification=${element.val()}`;
        }
        window.location.href = href;
      });
  }

  bindScheduleSampling() {
    const $btn = $("#workflow-transition-schedule_sampling");
    const url = $btn.attr("href");
    if (!url) return;

    $btn.on("click", (e) => {
      debugger
      e.preventDefault();
      const date = $("#SamplingDate").val();
      const sampler = $("#ScheduledSamplingSampler").val();
      let message = "";

      if (!date) {
        message += PMF("${name} is required for this action, please correct.", { name: _("Sampling Date") });
      }
      if (!sampler) {
        if (message) message += "<br/>";
        message += PMF("${name} is required, please correct.", { name: _("Define the Sampler for the scheduled") });
      }

      message ? window.senaite.core.globals.portalMessage(message) : (window.location.href = url);
    });
  }

  bindWorkflowTransitionSample() {
    $("#workflow-transition-sample").on("click", (event) => {
      debugger
      event.preventDefault();
      const date = $("#DateSampled").val();
      const sampler = $("#Sampler").val();
      let message = "";

      if (!date) {
        message += PMF("${name} is required, please correct.", { name: _("Date Sampled") });
      }
      if (!sampler) {
        if (message) message += "<br/>";
        message += PMF("${name} is required, please correct.", { name: _("Sampler") });
      }

      if (message) {
        window.senaite.core.globals.portalMessage(message);
        return;
      }

      const form = $("form[name='header_form']");
      form.append("<input type='hidden' name='transition' value='sample'/>");
      form.submit();
    });
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
