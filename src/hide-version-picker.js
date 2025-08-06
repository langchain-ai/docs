/**
 * Fallback script to add CSS classes for version picker hiding.
 * 
 * This minimal script adds CSS classes to the body element based on URL,
 * which works with the CSS file to hide the version picker on unversioned pages.
 */
(function() {
    'use strict';
    
    function addVersionPickerClasses() {
        const currentPath = window.location.pathname;
        const body = document.body;
        
        // Debug logging
        console.log('🔍 Version picker debug:', {
            currentPath,
            bodyClasses: body.className,
            isLangGraphPython: currentPath.includes('/langgraph/python/'),
            isLangGraphJavaScript: currentPath.includes('/langgraph/javascript/'),
            isPlatform: currentPath.includes('/langgraph-platform/'),
            isLabs: currentPath.includes('/labs/')
        });
        
        // Remove existing classes from body
        body.classList.remove('hide-version-picker-platform', 'hide-version-picker-labs', 'langgraph-python', 'langgraph-javascript');
        
        // Add appropriate class based on URL - check multiple patterns
        if (currentPath.includes('/langgraph/python/')) {
            body.classList.add('langgraph-python');
            console.log('✅ Added langgraph-python class');
        } else if (currentPath.includes('/langgraph/javascript/')) {
            body.classList.add('langgraph-javascript');
            console.log('✅ Added langgraph-javascript class');
        } else if (currentPath.includes('/langgraph-platform/') || currentPath.includes('/langgraph-platform')) {
            body.classList.add('hide-version-picker-platform');
            console.log('❌ Added hide-version-picker-platform class');
        } else if (currentPath.includes('/labs/') || currentPath.includes('/labs') || currentPath.match(/\/labs(?:\/|$)/)) {
            body.classList.add('hide-version-picker-labs');
            console.log('❌ Added hide-version-picker-labs class');
        } else {
            console.log('⚠️ No matching URL pattern found for:', currentPath);
        }
        
        // Also add content-based classes to version picker buttons
        const buttons = document.querySelectorAll('button[aria-haspopup="menu"]');
        console.log('🔘 Found buttons with aria-haspopup="menu":', buttons.length);
        
        buttons.forEach((button, index) => {
            // Remove existing version picker classes
            button.classList.remove('version-picker-python', 'version-picker-javascript');
            
            // Add class based on button text content
            const buttonText = button.textContent.trim().toLowerCase();
            console.log(`🔘 Button ${index}: "${buttonText}"`);
            
            if (buttonText === 'python') {
                button.classList.add('version-picker-python');
                console.log(`✅ Added version-picker-python to button ${index}`);
            } else if (buttonText === 'javascript') {
                button.classList.add('version-picker-javascript');
                console.log(`✅ Added version-picker-javascript to button ${index}`);
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