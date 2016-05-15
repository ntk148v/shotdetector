$("#uploadFile").change(function() {
    var formData = new FormData(this);
    formData.append('file', this.files[0]);

    $.tmpl($("#fileUploadProgressTemplate")).appendTo("#files");
    $("#fileUploadError").addClass("hide");

    $.ajax({
        url: '/',
        type: 'POST',
        data: formData,
        cache: false,
        contentType: false,
        processData: false,
        xhr: function() {
            var xhr = $.ajaxSettings.xhr();
            if (xhr.upload) {
                xhr.upload.addEventListener('progress', function(evt) {
                    var percent = (evt.loaded / evt.total) * 100;
                    $("#files").find(".progress-bar").width(percent + "%");
                }, false);
            }
            return xhr;
        },
        success: function(data) {
            $("#files").children().last().remove();
            $.tmpl($("#fileUploadProgressTemplate"), data).appendTo("#files");
            $("#uploadFile").closest("form").trigger("reset");
        },
        error: function() {
            $("#fileUploadError").removeClass("hide").text("An error occured!");
            $("#files").children().last().remove();
            $("#uploadFile").closest("form").trigger("reset");
        },
    });
});