document.addEventListener('DOMContentLoaded', () => {
    const filters = document.querySelectorAll('.category-filter');
    const categorySections = document.querySelectorAll('.category-section');

    // Ensure all sections are visible on load
    categorySections.forEach(section => {
        section.style.display = 'block';
    });

    filters.forEach(filter => {
        filter.addEventListener('click', () => {
            // Update active filter
            filters.forEach(f => f.classList.remove('active'));
            filter.classList.add('active');

            const category = filter.getAttribute('data-category');

            // Filter category sections
            categorySections.forEach(section => {
                if (category === 'all' || section.getAttribute('data-category') === category) {
                    section.style.display = 'block';
                } else {
                    section.style.display = 'none';
                }
            });
        });
    });
});
