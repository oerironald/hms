// dashboard.js

document.addEventListener('DOMContentLoaded', (event) => {
    // Sidebar toggle functionality
    const sidebarToggleBtn = document.getElementById('sidebar-toggle');
    const sidebar = document.getElementById('sidebar');
    const mainContent = document.querySelector('.main-content');

    if (sidebarToggleBtn && sidebar && mainContent) {
        sidebarToggleBtn.addEventListener('click', () => {
            sidebar.classList.toggle('hide');
            mainContent.classList.toggle('responsive');
        });
    } else {
        console.error('One or more elements not found for sidebar toggle');
    }

    function handleResize() {
        if (window.innerWidth > 768) {
            sidebar.classList.remove('hide');
            mainContent.classList.remove('responsive');
        } else {
            sidebar.classList.add('hide');
            mainContent.classList.add('responsive');
        }
    }

    window.addEventListener('resize', handleResize);
    handleResize();

    // Dropdown toggle
    const dropdownToggles = document.querySelectorAll('.sidebar-menu .dropdown > a');
    
    dropdownToggles.forEach(toggle => {
        toggle.addEventListener('click', (event) => {
            event.preventDefault();
            event.stopPropagation();

            const dropdownItem = toggle.closest('.dropdown');

            // Close all other open dropdowns
            dropdownToggles.forEach(otherToggle => {
                const otherDropdownItem = otherToggle.closest('.dropdown');
                if (otherDropdownItem !== dropdownItem) {
                    otherDropdownItem.classList.remove('open');
                }
            });

            // Toggle the clicked dropdown
            dropdownItem.classList.toggle('open');
        });
    });

    // Close dropdowns when clicking outside
    document.addEventListener('click', (event) => {
        if (!event.target.closest('.dropdown')) {
            dropdownToggles.forEach(toggle => {
                const dropdownItem = toggle.closest('.dropdown');
                dropdownItem.classList.remove('open');
            });
        }
    });

    // Add keyboard accessibility
    dropdownToggles.forEach(toggle => {
        toggle.addEventListener('keydown', (event) => {
            if (event.key === 'Enter' || event.key === ' ') {
                event.preventDefault();
                toggle.click();
            }
        });
    });

    // Responsive navbar functionality
    const mobileMenuToggle = document.getElementById('mobile-menu-toggle');
    const navbarMenu = document.getElementById('navbar-menu');

    if (mobileMenuToggle && navbarMenu) {
        mobileMenuToggle.addEventListener('click', function() {
            navbarMenu.classList.toggle('show');
        });

        // Close the menu when clicking outside
        document.addEventListener('click', function(event) {
            if (!navbarMenu.contains(event.target) && !mobileMenuToggle.contains(event.target)) {
                navbarMenu.classList.remove('show');
            }
        });
    } else {
        console.error('Mobile menu toggle or navbar menu not found');
    }

    // Update copyright year
    const currentYearElement = document.getElementById('current-year');
    if (currentYearElement) {
        currentYearElement.textContent = new Date().getFullYear();
    } else {
        console.error('Current year element not found');
    }

    const navbarItems = document.querySelectorAll('.navbar-item');

    navbarItems.forEach(item => {
        const tooltip = document.createElement('div');
        tooltip.classList.add('tooltip');
        tooltip.textContent = item.getAttribute('data-tooltip');
        item.appendChild(tooltip);

        item.addEventListener('mouseenter', () => {
            const rect = item.getBoundingClientRect();
            tooltip.style.top = `${rect.bottom + 5}px`;
            tooltip.style.left = `${rect.left + (rect.width / 2) - (tooltip.offsetWidth / 2)}px`;
            tooltip.style.opacity = '1';
        });

        item.addEventListener('mouseleave', () => {
            tooltip.style.opacity = '0';
        });
    });

});