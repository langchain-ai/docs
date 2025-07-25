// Simple dark mode link hover enhancement
(function() {
  function enhanceDarkModeLinks() {
    if (document.documentElement.getAttribute('data-theme') === 'dark') {
      const links = document.querySelectorAll('a:not([data-hover-enhanced])');
      links.forEach(link => {
        link.addEventListener('mouseenter', () => {
          link.style.setProperty('color', '#beb4fd', 'important');
        });
        link.addEventListener('mouseleave', () => {
          link.style.setProperty('color', '#ffffff', 'important');
        });
        link.setAttribute('data-hover-enhanced', 'true');
      });
    }
  }
  
  // Run on theme changes and new content
  const observer = new MutationObserver(enhanceDarkModeLinks);
  observer.observe(document.documentElement, {
    attributes: true,
    attributeFilter: ['data-theme'],
    childList: true,
    subtree: true
  });
  
  // Initial run
  document.addEventListener('DOMContentLoaded', enhanceDarkModeLinks);
})();