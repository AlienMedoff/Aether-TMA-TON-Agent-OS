(function() {
    // Backend endpoint to communicate with the Agentic Runtime
    const RUNTIME_URL = "http://localhost:8000";
    
    // Whitelist approach: Only elements with this attribute are visible to the agent
    const AGENT_SELECTOR = '[data-agent-action]';

    console.log("🌌 Aether Bridge: Initialized with Semantic Extraction");

    /**
     * Scans the UI for interactive elements marked for agent control.
     * Prevents data leaks by NOT dumping the full DOM.
     */
    async function syncUIState() {
        const elements = Array.from(document.querySelectorAll(AGENT_SELECTOR)).map(el => {
            const rect = el.getBoundingClientRect();
            return {
                // Identity for the agent to reference this element
                id: el.getAttribute('data-agent-id') || 'unknown',
                // Action category to validate intent on the backend
                action: el.getAttribute('data-agent-action'), 
                // Minimal coordinate map instead of full DOM tree
                rect: { x: rect.left, y: rect.top, w: rect.width, h: rect.height },
                isVisible: rect.width > 0 && rect.height > 0
            };
        });

        try {
            // Push only the semantic UI map to the runtime
            await fetch(`${RUNTIME_URL}/control`, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ action: "SYNC_STATE", data: { elements } })
            });
        } catch (e) {
            // Silently fail to avoid console flooding during network hiccups
        }
    }

    /**
     * Executes commands from the backend with strict validation.
     * Prevents arbitrary script execution.
     */
    window.Aether = {
        execute: (cmd) => {
            // Validate that the target exists and the action matches the whitelist attribute
            const target = document.querySelector(`[data-agent-id="${cmd.id}"]`);
            if (target && target.getAttribute('data-agent-action') === cmd.action) {
                target.click();
            }
        },
        sync: syncUIState
    };

    // Periodic sync: heartbeat for the agent's view
    setInterval(syncUIState, 2000);
})();
