import sys

path = r'c:\Users\Admin\Desktop\CareerVerse\static\css\style.css'
try:
    with open(path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    if len(lines) < 3220:
        print(f"Error: File too short ({len(lines)} lines)")
        sys.exit(1)

    # Keep first 3220 lines
    clean_lines = lines[:3220]

    results_mq = """
@media (max-width: 768px) {
    .results-page {
        height: 100dvh !important;
        display: flex !important;
        flex-direction: column !important;
        overflow: hidden !important;
    }

    .results-page .main-content {
        flex: 1 !important;
        display: flex !important;
        flex-direction: column !important;
        overflow: hidden !important;
        padding-top: 0 !important;
    }

    .results-page .footer {
        flex-shrink: 0 !important;
    }

    .nav-header-actions {
        order: 2;
    }

    .mobile-menu-toggle {
        order: 3 !important;
        margin-left: 5px;
    }

    .perf-toggle-btn {
        display: flex !important;
    }

    .results-layout-new {
        flex-direction: column !important;
        padding: 0 !important;
        height: 100% !important;
        width: 100% !important;
        gap: 0 !important;
        overflow: hidden !important;
    }

    .results-sidebar {
        position: fixed !important;
        top: 0 !important;
        left: 0 !important;
        width: 85% !important;
        height: 100vh !important;
        max-height: 100vh !important;
        z-index: 2500 !important;
        margin: 0 !important;
        border-radius: 0 !important;
        transform: translateX(-100%) !important;
        transition: transform 0.4s cubic-bezier(0.165, 0.84, 0.44, 1) !important;
        background: rgba(10, 15, 30, 0.95) !important;
        box-shadow: 20px 0 50px rgba(0, 0, 0, 0.5) !important;
        padding: 60px 24px 24px !important;
    }

    .results-sidebar.active {
        transform: translateX(0) !important;
    }

    .sidebar-close-btn {
        display: block !important;
    }

    .results-main {
        width: 100% !important;
        height: 100% !important;
        display: flex !important;
        flex-direction: column !important;
        overflow: hidden !important;
        padding: 0 !important;
    }

    .chat-hero-header {
        flex-shrink: 0 !important;
        padding: 88px 10px 10px 10px !important;
        text-align: center !important;
    }

    .avatar-container {
        margin: 0 auto !important;
        height: 220px !important;
    }

    #avatar-3d-container {
        width: 220px !important;
        height: 220px !important;
        margin: 0 auto !important;
    }

    .chat-history-viewport {
        flex: 1 !important;
        overflow-y: auto !important;
        padding: 15px !important;
        -webkit-overflow-scrolling: touch;
    }

    .chat-input-area {
        flex-shrink: 0 !important;
        padding: 5px 15px 0px 15px !important;
        margin-bottom: 0 !important;
        background: rgba(10, 15, 30, 0.5) !important;
        backdrop-filter: blur(10px) !important;
        border-top: 1px solid rgba(255, 255, 255, 0.05) !important;
    }

    .chat-input-wrapper {
        max-width: 100% !important;
        margin: 0 !important;
    }
}
"""

    flash_msgs = """
/*  Flash Messages  */
.flash-messages {
    position: fixed;
    top: 20px;
    left: 50%;
    transform: translateX(-50%);
    z-index: 9999;
    display: flex;
    flex-direction: column;
    gap: 10px;
    pointer-events: none;
}

.flash-message {
    padding: 12px 24px;
    border-radius: 8px;
    background: rgba(15, 23, 42, 0.9);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.1);
    color: #fff;
    font-weight: 500;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
    pointer-events: auto;
    animation: flash-in 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275) forwards,
        flash-out 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275) forwards 4s;
}

.flash-message.success {
    border-left: 4px solid #10b981;
}

.flash-message.error {
    border-left: 4px solid #ef4444;
}

@keyframes flash-in {
    from {
        opacity: 0;
        transform: translateY(-20px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

@keyframes flash-out {
    from {
        opacity: 1;
        transform: translateY(0);
    }
    to {
        opacity: 0;
        transform: translateY(-20px);
    }
}
"""

    nav_mq = """
/* ── Final Consolidated Mobile Navigation ── */

.mobile-menu-toggle {
    display: none;
    flex-direction: column;
    justify-content: space-between;
    width: 28px;
    height: 18px;
    background: none;
    border: none;
    cursor: pointer;
    padding: 0;
    z-index: 2001;
}

.mobile-menu-toggle span {
    width: 100%;
    height: 2.5px;
    background: var(--text-primary);
    border-radius: 10px;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.mobile-menu-toggle.active span:nth-child(1) {
    transform: translateY(8px) rotate(45deg);
}

.mobile-menu-toggle.active span:nth-child(2) {
    opacity: 0;
    transform: translateX(-10px);
}

.mobile-menu-toggle.active span:nth-child(3) {
    transform: translateY(-8px) rotate(-45deg);
}

@media (max-width: 768px) {
    .navbar {
        padding: 0 20px !important;
        height: 70px !important;
    }

    .mobile-menu-toggle {
        display: flex !important;
        order: 2;
    }

    .nav-brand {
        order: 1;
    }

    .nav-links {
        position: fixed !important;
        top: 70px !important;
        left: 0 !important;
        right: 0 !important;
        width: 100% !important;
        height: auto !important;
        max-height: calc(100vh - 70px) !important;
        background: rgba(5, 1, 30, 0.98) !important;
        backdrop-filter: blur(30px) !important;
        -webkit-backdrop-filter: blur(30px) !important;
        flex-direction: column !important;
        display: flex !important;
        padding: 40px 24px !important;
        gap: 20px !important;
        border-bottom: 1px solid rgba(56, 189, 248, 0.2) !important;
        transform: translateY(-100%) !important;
        opacity: 0 !important;
        visibility: hidden !important;
        z-index: 1500 !important;
        pointer-events: none !important;
        transition: all 0.4s cubic-bezier(0.165, 0.84, 0.44, 1) !important;
        overflow-y: auto !important;
    }

    .nav-links.mobile-active {
        transform: translateY(0) !important;
        opacity: 1 !important;
        visibility: visible !important;
        pointer-events: all !important;
    }

    .nav-link {
        width: 100% !important;
        text-align: center !important;
        padding: 16px !important;
        font-size: 18px !important;
        background: rgba(255, 255, 255, 0.05) !important;
        border-radius: 12px !important;
        display: block !important;
    }

    .history-toggle-btn {
        width: 100% !important;
        text-align: center !important;
        padding: 16px !important;
        font-size: 18px !important;
        background: rgba(255, 255, 255, 0.05) !important;
        border-radius: 12px !important;
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
        border: 1px solid transparent !important;
        color: var(--text-secondary) !important;
        margin-top: 0 !important;
        transition: var(--transition) !important;
    }

    .history-toggle-btn:hover,
    .nav-link:hover {
        background: rgba(56, 189, 248, 0.1) !important;
        color: var(--accent) !important;
        border-color: rgba(56, 189, 248, 0.3) !important;
    }

    /* Account Section Reversion */
    .user-profile-wrapper {
        display: flex !important;
        justify-content: center !important;
        width: 100% !important;
        margin-top: 10px !important;
        padding-top: 20px !important;
        border-top: 1px solid rgba(255, 255, 255, 0.1) !important;
    }

    .user-dropdown-content {
        position: absolute !important;
        top: auto !important;
        bottom: 100% !important;
        left: 50% !important;
        transform: translateX(-50%) translateY(-10px) !important;
        z-index: 2000 !important;
    }
}
"""

    with open(path, 'w', encoding='utf-8') as f:
        f.writelines(clean_lines)
        f.write(results_mq)
        f.write("\\n")
        f.write(flash_msgs)
        f.write("\\n")
        f.write(nav_mq)

    print("SUCCESS: style.css restored.")
except Exception as e:
    print(f"FAILED: {e}")
    sys.exit(1)
