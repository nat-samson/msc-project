$(function () {

  $("#add-word-button").click(function () {
    $.ajax({
      url: '/topic/add-word/',
      type: 'get',
      dataType: 'json',
      beforeSend: function () {
        // hide the button
        //$('#add-word-button').hide();
      },
      success: function (data) {
        // hide the button, inject the form into the page and display it
        $('#add-word-button').hide();
        $("#add-word-ui #add-word-ui-form").html(data.html_form);
        $('#add-word-ui').show();
      }
    });
  });

  $("#add-word-ui").on({
    "submit": function () {
    const form = $(this);
    $.ajax({
      url: `${form.attr("action")}${topicId}/`, // add the topicID from the page
      data: form.serialize(),
      type: form.attr("method"),
      dataType: 'json',
      success: function (data) {
        if (data.is_valid) {
          alert("Topic created!");  // placeholder
        }
        else {
          $("#add-word-ui #add-word-ui-form").html(data.html_form);
        }
      }
    });
    return false;
  },
  "reset": function () {
      $('#add-word-button').show();
      $('#add-word-ui').hide();
  }
  }, ".word-create-form");
});
