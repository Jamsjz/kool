const SVG = "svg+png";
const PNG = "png";

function handleDownloadLink(file) {
	$("#download-link").attr("href", URL.createObjectURL(file));
	$("#download-link").attr("download", file.name);
	$("#download-link").show();
}

function handleImage(file) {
	$("#file-content").attr("src", URL.createObjectURL(file))
}

function handleSubmit(event) {
	form = event.target;
	formdata = new FormData(form);
	fetch("http://127.0.0.1:8000", {
		method: "POST",
		body: formdata
	}).then((res) => {
		return res.formData();
	}).then((formdata) => {

		$("#answer").html(formdata.get("message"));
		const file = formdata.get("file")
		console.log(file.type)

		handleImage(file)
		handleDownloadLink(file)
	});
	event.preventDefault();
}

$(document).ready(() => {
	$("#download-link").hide();
	$("#from").on("change", e => {
		if (e.target.value == "png") {
			$("#tosvg").hide()
			$("#to").val(PNG)
			$("#image").attr("accept", ".png");
		} else {
			$("#tosvg").show()
			$("#image").attr("accept", ".svg");
		}
	});

	$("#to").on("change", e => {
		if (e.target.value == SVG) {
			$("#frompng").hide()
			$("#from").val(SVG)
		} else {
			$("#frompng").show()
			$("#fromsvg").show()
		}
	});
});
