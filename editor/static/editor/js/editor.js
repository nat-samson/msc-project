/**
 * @file Functions for asynchronous handling of the Add Word and Word Filter forms.
 * @author Nathaniel Samson
 */

// Set up some interactive elements
const addWordButton = document.getElementById("add-word-button");
const addWordForm = document.getElementById("add-word-ui");
const wordFilterForm = document.getElementById("word-filter-form");
const wordsTable = document.querySelector("#words-table > tbody");

/**
 * Ensure the DOM is fully loaded and set up the JS logic.
 * @param {Function} fn - a function to be invoked once the DOM is fully loaded.
 */
function ready(fn) {
    if (document.readyState !== 'loading') {
        fn();
    } else {
        document.addEventListener('DOMContentLoaded', fn, {once: true});
    }
}

/**
 * Attach the various Event Handlers to buttons.
 */
function setEventListeners() {
    // User is on a topic-specific page
    if (addWordForm) {
        addWordButton.addEventListener("click", insertForm);
        addWordForm.addEventListener("submit", addWord);
        addWordForm.addEventListener("reset", () => hideAndShow(addWordForm, addWordButton));
    }
    // User is on the all-topics page
    if (wordFilterForm) {
        wordFilterForm.addEventListener("submit", filterSubmit)
        wordFilterForm.addEventListener("reset", resetForm);
    }
}

/**
 * Get the HTML Add Word form and insert it into the page.
 */
function insertForm() {
    fetch(addWordButton.dataset.url, {
        headers: {
            'Accept': 'application/json',
            'X-Requested-With': 'XMLHttpRequest',
        },
    })
        .then(response => {
            return response.json();
        })
        .then(data => {
            addWordForm.innerHTML = data.html_form;
            hideAndShow(addWordButton, addWordForm);
        })
}

/**
 * Submit the Add Word form when the Save button is clicked, and update the word table.
 */
function addWord(event) {
    event.preventDefault();
    let url = addWordForm.querySelector("form").getAttribute("action");
    url = topicId ? `${url}${topicId}/` : url; // add the topicID from the page if present

    fetch(url, {
        method: 'POST',
        headers: {
            'Accept': 'application/json',
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': getCookie('csrftoken'),
        },
        mode: 'same-origin',
        body: new FormData(document.querySelector("form"))
    })
        .then(response => {
            return response.json();
        })
        .then(data => {
            if (data.is_valid) {
                // If the new word is valid, refresh the word table to show the newly added word
                wordsTable.innerHTML = data.html_word_rows;
                hideAndShow(addWordForm, addWordButton);
            } else {
                // If the new word is not valid, display the relevant errors
                addWordForm.innerHTML = data.html_form;
            }
        })
}

/**
 * Update the Words table based on the filter settings on the 'All Topics' page.
 * @param {Event} e - an event triggered by the 'All Topics' page form.
 */
function filterSubmit(e) {
    e.preventDefault();
    const url = wordFilterForm.getAttribute("action") + "?" + new URLSearchParams(new FormData(wordFilterForm));

    // fetch the filtered table data and insert it into the page
    fetch(url, {
        headers: {
            'Accept': 'application/json',
            'X-Requested-With': 'XMLHttpRequest',
        },
    })
        .then(response => {
            return response.json();
        })
        .then(data => {
            wordsTable.innerHTML = data.html_word_rows;
        })
}

/**
 * When the 'All Topics' form is reset, also resubmit it, refreshing the contents of the word table with one click.
 */
function resetForm(event) {
    setTimeout(function() {
        // Logic in here executes *after* the form gets reset
        filterSubmit(event);
    })
}

/**
 * Hide HTML element a, show HTML element b.
 * @param {HTMLElement} a - an HTML element to be hidden.
 * @param {HTMLElement} b - an HTML element to be displayed.
 */
function hideAndShow(a, b) {
    a.style.display = 'none';
    b.style.display = '';
}

/**
 * Return the specified cookie value, here expected to be used for obtaining the CSRF Token (default: 'csrftoken').
 * @param {string} name - name of the desired cookie.
 * @returns {string} -
 * @author - Django docs: https://docs.djangoproject.com/en/4.1/howto/csrf/
 */
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

window.ready(function() {
    setEventListeners();
});