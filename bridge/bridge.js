(function() {
    const RUNTIME_URL = "http://localhost:8000";
    console.log("🌌 Aether Bridge: Initialized");

    async function syncUIState() {
        const state = {
            url: window.location.href,
            elements: Array.from(document.querySelectorAll('button, a, input')).map(el => ({
                id: el.id || 'unnamed',
                tag: el.tagName,
                text: el.innerText || el.value || '',
                visible: el.getBoundingClientRect().height > 0
            })),
            timestamp: Date.now()
        };

        await fetch(`${RUNTIME_URL}/control`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({action: "SYNC_STATE", data: state})
        }).catch(() => {});
    }

    window.Aether = {
        execute: (cmd) => {
            if (cmd.action === "CLICK") {
                document.querySelector(cmd.selector)?.click();
            }
        },
        sync: syncUIState
    };

    setInterval(syncUIState, 2000);
})();
