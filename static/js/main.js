/* ═══════════════════════════════════════════════════
   CareerVerse – Main JavaScript
   ═══════════════════════════════════════════════════ */

// ── Navbar scroll effect ──
document.addEventListener('DOMContentLoaded', () => {
    const nav = document.getElementById('main-nav');
    if (nav) {
        window.addEventListener('scroll', () => {
            if (window.scrollY > 10) {
                nav.style.background = 'rgba(2, 6, 23, 0.95)';
            } else {
                nav.style.background = 'rgba(2, 6, 23, 0.85)';
            }
        });
    }

    // ── Animate elements on scroll ──
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, { threshold: 0.1 });

    document.querySelectorAll('.glass-card, .feature-card, .tech-tag').forEach(el => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(20px)';
        el.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
        observer.observe(el);
    });

    // ── Initialize Custom Dropdowns ──
    initCustomDropdowns();
});

// ── Custom Dropdown System ──
function initCustomDropdowns() {
    const selects = document.querySelectorAll('.form-select');
    
    selects.forEach(select => {
        // Create custom dropdown structure
        const container = document.createElement('div');
        container.className = 'custom-dropdown';
        if (select.id) container.id = 'custom-' + select.id;
        
        const selected = document.createElement('div');
        selected.className = 'dropdown-selected';
        
        const selectedText = document.createElement('span');
        selectedText.className = 'selected-text';
        selectedText.textContent = select.options[select.selectedIndex]?.text || 'Select...';
        
        const arrow = document.createElement('span');
        arrow.className = 'dropdown-arrow';
        arrow.textContent = '▼';
        
        selected.appendChild(selectedText);
        selected.appendChild(arrow);
        
        const menu = document.createElement('div');
        menu.className = 'dropdown-menu';
        
        // Populate menu items
        Array.from(select.options).forEach((option, index) => {
            const item = document.createElement('div');
            item.className = 'dropdown-item';
            if (index === select.selectedIndex) item.classList.add('active');
            item.textContent = option.text;
            item.setAttribute('data-value', option.value);
            
            item.addEventListener('click', (e) => {
                e.stopPropagation();
                
                // Update select
                select.selectedIndex = index;
                select.dispatchEvent(new Event('change'));
                
                // Update UI
                selectedText.textContent = option.text;
                container.querySelectorAll('.dropdown-item').forEach(i => i.classList.remove('active'));
                item.classList.add('active');
                
                // Close menu
                container.classList.remove('open');
            });
            
            menu.appendChild(item);
        });
        
        container.appendChild(selected);
        container.appendChild(menu);
        
        // Toggle menu
        selected.addEventListener('click', (e) => {
            e.stopPropagation();
            
            const isOpen = container.classList.contains('open');
            
            // Close other open dropdowns
            document.querySelectorAll('.custom-dropdown.open').forEach(d => {
                d.classList.remove('open');
                d.closest('.glass-card, .settings-card')?.classList.remove('card-active');
            });
            
            if (!isOpen) {
                container.classList.add('open');
                container.closest('.glass-card, .settings-card')?.classList.add('card-active');
            }
        });
        
        // Hide original select and insert custom one
        select.style.display = 'none';
        select.parentNode.insertBefore(container, select.nextSibling);
    });
}

// Close custom dropdowns when clicking outside
window.addEventListener('click', () => {
    document.querySelectorAll('.custom-dropdown.open').forEach(dropdown => {
        dropdown.classList.remove('open');
        dropdown.closest('.glass-card, .settings-card')?.classList.remove('card-active');
    });
});

// ── Profile Dropdown Toggle ──
function toggleDropdown(event) {
    if (event) event.stopPropagation();
    const dropdown = document.getElementById('profile-dropdown');
    dropdown.classList.toggle('show');
}

// Close dropdown when clicking outside
window.addEventListener('click', (e) => {
    const dropdown = document.getElementById('profile-dropdown');
    const trigger = document.getElementById('profile-trigger');
    
    if (dropdown && dropdown.classList.contains('show')) {
        if (!dropdown.contains(e.target) && !trigger.contains(e.target)) {
            dropdown.classList.remove('show');
        }
    }
});

// ── AI Response Formatting (Markdown-lite) ──
function formatAIResponse(text) {
    if (!text) return "";
    
    // Trim text and ensure it ends with a newline for easier regex matching
    let formatted = text.trim() + "\n";
    
    formatted = formatted
        // Headers
        .replace(/^### (.*$)/gm, '<h4>$1</h4>')
        .replace(/^## (.*$)/gm, '<h3>$1</h3>')
        .replace(/^# (.*$)/gm, '<h2>$1</h2>')
        
        // Bold and Italic
        .replace(/\*\*\*(.*?)\*\*\*/g, '<strong><em>$1</em></strong>')
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.*?)\*/g, '<em>$1</em>')
        
        // Horizontal Rule
        .replace(/^\s*---+\s*$/gm, '<hr>')
        
        // Unordered Lists
        .replace(/^\s*[-*•]\s+(.*$)/gm, '<li>$1</li>')
        // Wrap adjacent <li> in <ul>
        .replace(/(<li>.*<\/li>(?:\n<li>.*<\/li>)*)/gs, match => `<ul>${match}</ul>`)
        
        // Ordered Lists
        .replace(/^\s*\d+\.\s+(.*$)/gm, '<li class="ordered">$1</li>')
        // Wrap adjacent <li class="ordered"> in <ol>
        .replace(/((?:<li class="ordered">.*<\/li>\n?)+)/gs, match => `<ol>${match}</ol>`)
        
        // Remove helper class
        .replace(/ class="ordered"/g, '')
        
        // Convert remaining newlines to <br> (but not inside block tags)
        .replace(/\n/g, '<br>')
        
        // Final cleanup of extra <br> around block tags
        .replace(/<br><\/?(ul|ol|li|h[234]|hr)/g, '<$1')
        .replace(/<\/(ul|ol|li|h[234]|hr)><br>/g, '</$1>');
        
    return formatted.trim();
}
