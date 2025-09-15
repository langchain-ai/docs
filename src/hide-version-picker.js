/**
 * Minimal script to add CSS classes for version picker hiding.
 *
 * This script adds CSS classes to the body element based on URL,
 * and to version picker buttons based on their content.
 */
(function() {
    'use strict';

    function addVersionPickerClasses() {
        const currentPath = window.location.pathname;
        const body = document.body;

        // Remove existing classes
        body.classList.remove('hide-version-picker');

        // Add appropriate class based on URL
        if (currentPath.includes('/langgraph-platform/') || currentPath.includes('/langgraph-platform')) {
            body.classList.add('hide-version-picker');
        } else if (currentPath.match(/\/labs(?:\/|$)/)) {
            body.classList.add('hide-version-picker');
        } else if (currentPath.match(/\/langsmith(?:\/|$)/)) {
            body.classList.add('hide-version-picker');
        }

        // Add classes to version picker buttons
        document.querySelectorAll('button[aria-haspopup="menu"]').forEach(button => {
            const buttonText = button.textContent.trim().toLowerCase();
            if (buttonText === 'python' || buttonText === 'javascript') {
                button.classList.add('version-picker-button');
            }
        });

    }

    // Run immediately
    addVersionPickerClasses();

    // Run on page load
    document.addEventListener('DOMContentLoaded', addVersionPickerClasses);

    // Run on navigation
    window.addEventListener('popstate', addVersionPickerClasses);

    // Watch for URL changes (SPA navigation)
    let lastUrl = location.href;
    new MutationObserver(() => {
        const url = location.href;
        if (url !== lastUrl) {
            lastUrl = url;
            addVersionPickerClasses();
        }
    }).observe(document, { subtree: true, childList: true });
})();
