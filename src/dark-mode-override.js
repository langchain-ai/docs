// Force dark mode background override via JavaScript
(function() {
  function forceDarkModeStyles() {
    const isDarkMode = document.documentElement.getAttribute('data-theme') === 'dark';
    
    if (isDarkMode) {
      // Force background on key elements
      const elements = [
        document.documentElement,
        document.body,
        document.querySelector('#__next'),
        document.querySelector('.app'),
        document.querySelector('.layout'),
        ...document.querySelectorAll('div'),
        ...document.querySelectorAll('section'),
        ...document.querySelectorAll('main'),
        ...document.querySelectorAll('[class*="bg-"]')
      ].filter(Boolean);
      
      elements.forEach(el => {
        if (el) {
          el.style.setProperty('background-color', '#1c3c3c', 'important');
          el.style.setProperty('background', '#1c3c3c', 'important');
          el.style.setProperty('background-image', 'none', 'important');
        }
      });
      
      // Force text color on text elements
      const textElements = [
        ...document.querySelectorAll('p'),
        ...document.querySelectorAll('span'),
        ...document.querySelectorAll('div'),
        ...document.querySelectorAll('h1, h2, h3, h4, h5, h6'),
        ...document.querySelectorAll('li'),
        ...document.querySelectorAll('td'),
        ...document.querySelectorAll('th'),
        ...document.querySelectorAll('label')
      ];
      
      textElements.forEach(el => {
        if (el && !el.closest('code') && !el.closest('pre')) {
          el.style.setProperty('color', '#f0e6ff', 'important');
        }
      });
    }
  }
  
  // Run immediately
  forceDarkModeStyles();
  
  // Run when DOM changes
  const observer = new MutationObserver(forceDarkModeStyles);
  observer.observe(document.documentElement, {
    attributes: true,
    attributeFilter: ['data-theme'],
    childList: true,
    subtree: true
  });
  
  // Run on load
  document.addEventListener('DOMContentLoaded', forceDarkModeStyles);
  window.addEventListener('load', forceDarkModeStyles);
  
  // Run periodically to catch any missed changes
  setInterval(forceDarkModeStyles, 1000);
})();