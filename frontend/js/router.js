// Client-side router
document.addEventListener('DOMContentLoaded', function() {
    // Initial loading of content based on URL
    loadInitialContent();
    
    // Handle browser back/forward navigation
    window.addEventListener('popstate', handlePopState);
    
    // Intercept link clicks for SPA navigation
    document.addEventListener('click', handleLinkClick);
});

function loadInitialContent() {
    const path = window.location.pathname;
    navigateTo(path);
}

function handlePopState() {
    const path = window.location.pathname;
    navigateTo(path, false); // Don't push state on popstate events
}

function handleLinkClick(e) {
    // Only handle clicks on links
    const link = e.target.closest('a');
    if (!link) return;
    
    // Skip external links, download links, etc.
    const href = link.getAttribute('href');
    
    if (
        !href || 
        href.startsWith('http') || 
        href.startsWith('//') || 
        href.startsWith('#') || 
        link.hasAttribute('download') ||
        link.getAttribute('target') === '_blank' ||
        e.ctrlKey || 
        e.metaKey || 
        e.shiftKey
    ) {
        return;
    }
    
    // Handle SPA navigation
    e.preventDefault();
    navigateTo(href);
}

function navigateTo(path, pushState = true) {
    // Update browser history
    if (pushState) {
        history.pushState(null, '', path);
    }
    
    // Scroll to top
    window.scrollTo(0, 0);
    
    // Update content based on route
    if (typeof loadContent === 'function') {
        loadContent(path);
    } else {
        console.error('loadContent function not found. Make sure app.js is loaded before router.js');
    }
}