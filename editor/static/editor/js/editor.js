/**
 * @file Functions for asynchronous handling of the Add Word and Word Filter forms.
 * @author Nathaniel Samson
 */

$(document).ready(function () {
  /**
   * Inject the Add Word form into the page each time the 'Add Word' button is clicked.
   */
  $("#add-word-button").click(function () {
    const url = $(this).data('url');
    $.getJSON(url, function (data) {
      // hide the button, inject the form into the page and display it
      $("#add-word-ui #add-word-ui-form").html(data.html_form);
      hideAndShow($('#add-word-button'), $('#add-word-ui'));
    });
  });

  /**
   * Process the Add Word form when Save button is clicked, and update the word table.
   */
  $("#add-word-ui").on({
    "submit": function () {
      const form = $(this);
      const url = topicId ? `${form.attr("action")}${topicId}/` : form.attr("action"); // add the topicID from the page
      $.ajax({
        url: url,
        data: form.serialize(),
        type: form.attr("method"),
        dataType: "json",
        success: function (data) {
          if (data.is_valid) {
            // If the new word is valid, refresh the word table to show the newly added word
            $("#words-table tbody").html(data.html_word_rows);
            hideAndShow($('#add-word-ui'), $('#add-word-button'))
          }
          else {
            // If the new word is not valid, display the relevant errors
            $("#add-word-ui #add-word-ui-form").html(data.html_form);
          }
        }
      });
      return false;
    },
    // If Cancel button is clicked, hide the form again
    "reset": function () {
      hideAndShow($('#add-word-ui'), $('#add-word-button'))
    }
  }, ".word-create-form");

  // Hide element a, show element b
  let hideAndShow = (a, b) => {
    a.hide();
    b.show();
  };

  /**
   * Update the Words table based on the filter settings on the 'All Topics' page.
   */
  $("#filter-submit").on("click", function (e) {
    e.preventDefault();
    let targetForm = $('#word-filter-form');
    let url = targetForm.attr('action') + "?" + targetForm.serialize();
    $.getJSON(url, function (data) {
      $("#words-table tbody").html(data.html_word_rows);
    });
  });

  /**
   * When the 'All Topics' form is reset, also resubmit it, refreshing the contents of the word table in one go.
   */
  $("#word-filter-form").on("reset", function() {
    setTimeout(function() {
      $("#filter-submit").click();
    });
  });

});