// Tab functionality for inscription pages
    function showTab(tabName) {
        // Hide all tab contents
        const contents = document.querySelectorAll('.tab-content');
        contents.forEach(content => {
            content.classList.remove('active');
        });

        // Remove active class from all tab buttons
        const buttons = document.querySelectorAll('.tabs button');
        buttons.forEach(button => {
            button.classList.remove('active');
        });

        // Show the selected tab content
        const selectedContent = document.getElementById('content-' + tabName);
        if (selectedContent) {
            selectedContent.classList.add('active');
        }

        // Activate the selected tab button
        const selectedButton = document.getElementById('tab-' + tabName);
        if (selectedButton) {
            selectedButton.classList.add('active');
        }
    }
    // Initialize the first tab as active when page loads
    document.addEventListener('DOMContentLoaded', function() {
        showTab('overview');
    });
    