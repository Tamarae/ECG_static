// Bibliography page functionality
    document.addEventListener('DOMContentLoaded', function() {
        const searchInput = document.getElementById('bibliographySearch');
        const bibliographyList = document.getElementById('bibliographyList');
        const allEntries = document.querySelectorAll('.bibliography-entry');

        function filterBibliography() {
            const searchTerm = searchInput.value.toLowerCase();

            allEntries.forEach(entry => {
                const content = entry.querySelector('.bib-content').textContent.toLowerCase();
                const id = entry.querySelector('.bib-id').textContent.toLowerCase();

                if (content.includes(searchTerm) || id.includes(searchTerm)) {
                    entry.style.display = 'block';
                } else {
                    entry.style.display = 'none';
                }
            });
        }

        if (searchInput) {
            searchInput.addEventListener('input', filterBibliography);
        }

        if (window.location.hash) {
            const targetEntry = document.querySelector(window.location.hash);
            if (targetEntry) {
                setTimeout(() => {
                    targetEntry.scrollIntoView({ behavior: 'smooth' });
                }, 100);
            }
        }
    });
    