jQuery(function ($) {
	$(document).ready(function () {

		function lookups() {
			// Selecting a Country (populate state field)
			$("[id*='\\.country']").on("change", function () {
				const field = $(this).attr("name").split(".")[0];
				populate_state_select(field);
			});

			// Selecting a State (populate district field)
			$("[id*='\\.state']").on("change", function () {
				const field = $(this).attr("name").split(".")[0];
				populate_district_select(field);
			});
		}

		function copyAddress() {
			const to_address = $(this).attr("id").split(".")[0];
			const from_address = $(this).val();
			if (!from_address) return;

			// Replace state field
			const state = $("#" + from_address + "\\.state").clone();
			state.attr({
				id: to_address + ".state",
				name: to_address + ".state:record"
			});
			$("#" + to_address + "\\.state").replaceWith(state);

			// Replace district field
			const district = $("#" + from_address + "\\.district").clone();
			district.attr({
				id: to_address + ".district",
				name: to_address + ".district:record"
			});
			$("#" + to_address + "\\.district").replaceWith(district);

			// Sync selected options
			["country", "state", "district"].forEach(function (item) {
				const val = $("#" + from_address + "\\." + item).val();
				$("#" + to_address + "\\." + item + " option").each(function () {
					$(this).prop("selected", $(this).val() === val);
				});
			});

			// Copy text fields
			$("#" + to_address + "\\.city").val($("#" + from_address + "\\.city").val()).trigger("change");
			$("#" + to_address + "\\.zip").val($("#" + from_address + "\\.zip").val()).trigger("change");
			$("#" + to_address + "\\.address").val($("#" + from_address + "\\.address").val()).trigger("change");

			// Reapply dependent handlers
			lookups();
		}

		function populate_state_select(field) {
			$.ajax({
				type: "POST",
				url: portal_url + "/geo_subdivisions",
				data: {
					parent: $("#" + field + "\\.country").val(),
					_authenticator: $("input[name='_authenticator']").val()
				},
				success: function (data) {
					const target = $("#" + field + "\\.state");
					target.empty().append("<option value=''></option>");
					data.forEach(function (v) {
						target.append('<option value="' + v.name + '">' + v.name + "</option>");
					});
					$("#" + field + "\\.district").empty();
				},
				dataType: "json"
			});
		}

		function populate_district_select(field) {
			$.ajax({
				type: "POST",
				url: portal_url + "/geo_subdivisions",
				data: {
					parent: $("#" + field + "\\.state").val(),
					_authenticator: $("input[name='_authenticator']").val()
				},
				success: function (data) {
					const target = $("#" + field + "\\.district");
					target.empty().append("<option value=''></option>");
					data.forEach(function (v) {
						target.append('<option value="' + v.name + '">' + v.name + "</option>");
					});
				},
				dataType: "json"
			});
		}

		// Event bindings
		$("[id*='\\.selection']").on("change", copyAddress);
		lookups();
	});
});
