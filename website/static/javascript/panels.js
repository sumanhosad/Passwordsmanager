function goBack() {
            window.history.back();
        }

    // Get all buttons with class "copy-btn"
    var copyButtons = document.querySelectorAll('.copy-btn');

    // Loop through each button and add a click event listener
    copyButtons.forEach(function(button) {
        button.addEventListener('click', function() {
            // Get the input field next to the clicked button
            var inputField = this.previousElementSibling;

            // Select the text in the input field
            inputField.select();

            // Copy the selected text to the clipboard
            document.execCommand('copy');
        });
    });


// Get all buttons with class "accordion"
var accordions = document.querySelectorAll('.accordion');

// Loop through each button and add a click event listener
accordions.forEach(function(accordion) {
    accordion.addEventListener('click', function() {
        // Close all other open panels
        accordions.forEach(function(otherAccordion) {
            if (otherAccordion !== accordion) {
                otherAccordion.classList.remove('active');
                var otherPanel = otherAccordion.nextElementSibling;
                otherPanel.style.maxHeight = null;
                otherPanel.classList.remove("show");
            }
        });

        // Toggle the class "active" to highlight the button
        this.classList.toggle('active');

        // Toggle the next sibling element (which is the panel)
        var panel = this.nextElementSibling;
        if (panel.style.maxHeight) {
            panel.style.maxHeight = null;
            panel.classList.remove("show");
        } else {
            panel.style.maxHeight = panel.scrollHeight + "px";
            panel.classList.add("show");
        }
    });
});

$(document).ready(function() {
        $('#search-query').on('input', function() {
            let query = $(this).val().toLowerCase();
            let found = false;
            $('.accordion').each(function() {
                let text = $(this).text().toLowerCase();
                let panel = $(this).next('.panel');
                let matches = false;

                // Check if the accordion button or any of its panel items match the query
                if (text.includes(query)) {
                    matches = true;
                } else {
                    panel.find('.password-item input').each(function() {
                        if ($(this).val().toLowerCase().includes(query)) {
                            matches = true;
                        }
                    });
                }

                if (matches) {
                    $(this).show();
                    panel.show();
                    found = true;
                } else {
                    $(this).hide();
                    panel.hide();
                }
            });

            // Show or hide the "no results" message
            if (!found) {
                $('#password-list').hide();
                $('#no-results').show();
            } else {
                $('#password-list').show();
                $('#no-results').hide();
            }
        });
    });

