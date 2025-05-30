// Fixed Browse page functionality with better error handling
    document.addEventListener('DOMContentLoaded', function() {
        console.log('🔍 Browse page JavaScript loaded');

        const searchInput = document.getElementById('searchInput');
        const languageFilter = document.getElementById('languageFilter');
        const sortSelect = document.getElementById('sortSelect');
        const inscriptionList = document.getElementById('inscriptionList');
        const allItems = document.querySelectorAll('.clean-inscription-item');

        console.log(`📊 Found ${allItems.length} inscription items in DOM`);

        // Convert NodeList to Array for easier manipulation
        let itemsArray = Array.from(allItems);

        function filterAndSortInscriptions() {
            console.log('🔍 Running filterAndSortInscriptions...');

            const searchTerm = (searchInput ? searchInput.value || '' : '').toLowerCase();
            const selectedLanguage = languageFilter ? languageFilter.value || '' : '';
            const sortBy = sortSelect ? sortSelect.value || 'id' : 'id';

            console.log(`🔍 Filter params: search="${searchTerm}", language="${selectedLanguage}", sort="${sortBy}"`);

            // Show loading state
            if (inscriptionList) {
                inscriptionList.dataset.loading = 'true';
            }

            // Small delay to show loading (smooth UX)
            setTimeout(() => {
                try {
                    // Filter items
                    const filteredItems = itemsArray.filter(item => {
                        const title = (item.dataset.title || '').toLowerCase();
                        const id = (item.dataset.id || '').toLowerCase();
                        const place = (item.dataset.place || '').toLowerCase();
                        const language = item.dataset.language || '';

                        const matchesSearch = !searchTerm ||
                                            title.includes(searchTerm) ||
                                            id.includes(searchTerm) ||
                                            place.includes(searchTerm);

                        const matchesLanguage = !selectedLanguage || language === selectedLanguage;

                        return matchesSearch && matchesLanguage;
                    });

                    console.log(`🔍 Filtered to ${filteredItems.length} items`);

                    // Sort items
                    filteredItems.sort((a, b) => {
                        let aValue, bValue;

                        switch(sortBy) {
                            case 'title':
                                aValue = (a.dataset.title || '').toLowerCase();
                                bValue = (b.dataset.title || '').toLowerCase();
                                return aValue.localeCompare(bValue);
                            case 'place':
                                aValue = (a.dataset.place || '').toLowerCase();
                                bValue = (b.dataset.place || '').toLowerCase();
                                return aValue.localeCompare(bValue);
                            case 'date':
                                aValue = (a.dataset.date || '').toLowerCase();
                                bValue = (b.dataset.date || '').toLowerCase();
                                return aValue.localeCompare(bValue);
                            case 'language':
                                aValue = (a.dataset.language || '').toLowerCase();
                                bValue = (b.dataset.language || '').toLowerCase();
                                return aValue.localeCompare(bValue);
                            case 'id':
                            default:
                                // Sort IDs numerically if they're numbers, alphabetically otherwise
                                aValue = a.dataset.id || '';
                                bValue = b.dataset.id || '';
                                const aNum = parseInt(aValue.replace(/[^0-9]/g, ''));
                                const bNum = parseInt(bValue.replace(/[^0-9]/g, ''));
                                if (!isNaN(aNum) && !isNaN(bNum)) {
                                    return aNum - bNum;
                                }
                                return aValue.localeCompare(bValue);
                        }
                    });

                    // Hide all items first
                    itemsArray.forEach(item => {
                        item.style.display = 'none';
                    });

                    // Clear the container and re-append filtered/sorted items
                    if (inscriptionList) {
                        inscriptionList.innerHTML = '';

                        // Add items with staggered animation
                        filteredItems.forEach((item, index) => {
                            item.style.display = 'block';
                            item.style.animationDelay = `${index * 10}ms`;
                            inscriptionList.appendChild(item);
                        });
                    }

                    // Update count display
                    updateResultCount(filteredItems.length, itemsArray.length);

                    // Remove loading state
                    if (inscriptionList) {
                        inscriptionList.dataset.loading = 'false';
                    }

                    console.log(`✅ Filtering complete, showing ${filteredItems.length} items`);

                } catch (error) {
                    console.error('❌ Error in filterAndSortInscriptions:', error);

                    // Fallback: show all items if filtering fails
                    itemsArray.forEach(item => {
                        item.style.display = 'block';
                        if (inscriptionList) {
                            inscriptionList.appendChild(item);
                        }
                    });

                    if (inscriptionList) {
                        inscriptionList.dataset.loading = 'false';
                    }
                    updateResultCount(itemsArray.length, itemsArray.length);
                }
            }, 50);
        }

        function updateResultCount(showing, total) {
            let countDisplay = document.getElementById('resultCount');
            if (!countDisplay && inscriptionList) {
                countDisplay = document.createElement('div');
                countDisplay.id = 'resultCount';
                countDisplay.className = 'result-count';
                inscriptionList.parentNode.insertBefore(countDisplay, inscriptionList);
            }

            if (countDisplay) {
                if (showing === total) {
                    countDisplay.innerHTML = `<strong>ნაჩვენებია ${total} წარწერა</strong>`;
                } else {
                    countDisplay.innerHTML = `
                        <strong>ნაჩვენებია ${showing} წარწერა ${total}-დან</strong>
                        ${(searchInput && searchInput.value) || (languageFilter && languageFilter.value) ?
                            `<br><small>Filtered by: ${getFilterDescription()}</small>` : ''}
                    `;
                }
            }
        }

        function getFilterDescription() {
            const filters = [];
            if (searchInput && searchInput.value) {
                filters.push(`search: "${searchInput.value}"`);
            }
            if (languageFilter && languageFilter.value) {
                const languageNames = {
                    'ka': 'Georgian',
                    'grc': 'Greek',
                    'hy': 'Armenian',
                    'arc': 'Aramaic',
                    'he': 'Hebrew',
                    'la': 'Latin',
                    'unknown': 'Unknown'
                };
                filters.push(`language: ${languageNames[languageFilter.value] || languageFilter.value}`);
            }
            return filters.join(', ');
        }

        // Debounce search input for better performance
        function debounce(func, wait) {
            let timeout;
            return function executedFunction(...args) {
                const later = () => {
                    clearTimeout(timeout);
                    func(...args);
                };
                clearTimeout(timeout);
                timeout = setTimeout(later, wait);
            };
        }

        const debouncedFilter = debounce(filterAndSortInscriptions, 200);

        // Add event listeners with error handling
        try {
            if (searchInput) {
                searchInput.addEventListener('input', debouncedFilter);

                searchInput.addEventListener('focus', function() {
                    if (this.parentElement) {
                        this.parentElement.classList.add('focused');
                    }
                });

                searchInput.addEventListener('blur', function() {
                    if (this.parentElement) {
                        this.parentElement.classList.remove('focused');
                    }
                });
            }

            if (languageFilter) {
                languageFilter.addEventListener('change', filterAndSortInscriptions);
            }

            if (sortSelect) {
                sortSelect.addEventListener('change', filterAndSortInscriptions);
            }

            // Initialize the display
            console.log('🔍 Initializing display...');
            filterAndSortInscriptions();

            // Add keyboard shortcuts
            document.addEventListener('keydown', function(e) {
                // Focus search with Ctrl/Cmd + F
                if ((e.ctrlKey || e.metaKey) && e.key === 'f') {
                    e.preventDefault();
                    if (searchInput) {
                        searchInput.focus();
                        searchInput.select();
                    }
                }

                // Clear search with Escape
                if (e.key === 'Escape' && document.activeElement === searchInput && searchInput) {
                    searchInput.value = '';
                    debouncedFilter();
                }
            });

            console.log('✅ Browse page JavaScript initialized successfully');

        } catch (error) {
            console.error('❌ Error initializing browse page:', error);

            // Fallback: ensure all items are visible
            itemsArray.forEach(item => {
                item.style.display = 'block';
            });
        }
    });
    