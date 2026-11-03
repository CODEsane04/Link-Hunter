function setupContextMenu() {
    chrome.contextMenus.create({
        id: "searchWithLH",
        title: "Search with LH",
        contexts: ["image"]
    });
}

chrome.runtime.onInstalled.addListener(() => {
    setupContextMenu();
});

// 1. Listen for external messages from the React web app (http://localhost:3000)
chrome.runtime.onMessageExternal.addListener((request, sender, sendResponse) => {
    if (request.action === "SAVE_AUTH_TOKEN" && request.token) {
        chrome.storage.local.set({ 
            authToken: request.token,
            userEmail: request.email || null 
        }, () => {
            console.log(" Auth token synced successfully from React web app!");
            sendResponse({ success: true, message: "Token stored in extension" });
        });
        return true; // Keep message channel open for async response
    }
});

// 2. Handle context menu right-click on craft images
chrome.contextMenus.onClicked.addListener(async (info, tab) => {
    if (info.menuItemId === "searchWithLH") {
        console.log("Image right-clicked. URL: ", info.srcUrl);
        const img_url = info.srcUrl;

        // Check if an auth token exists in extension storage
        const { authToken } = await chrome.storage.local.get("authToken");

        if (!authToken) {
            console.log("⚠️ No auth token found! Redirecting to React login page...");
            chrome.tabs.create({ url: "http://localhost:3000" });
            return;
        }

        // Authenticated -> proceed with backend request
        await getlinks(img_url, authToken);
    }
});

// 3. Dispatch POST /get_links with Bearer token
async function getlinks(img_url, authToken) {
    const backendUrl = 'http://localhost:8000/get_links';
    console.log("Sending image URL with Bearer token to backend: ", img_url);
    
    try {
        const response = await fetch(backendUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${authToken}`
            },
            body: JSON.stringify({ image_url: img_url }),
        });

        // If the token is expired or unauthorized (401), clear and prompt login
        if (response.status === 401) {
            console.error("401 Unauthorized! Token expired or invalid. Clearing and opening login...");
            await chrome.storage.local.remove(["authToken", "userEmail"]);
            chrome.tabs.create({ url: "http://localhost:3000" });
            return;
        }

        if (!response.ok) {
            console.error(`HTTP error status: ${response.status}`);
        } else {
            const data = await response.json();
            console.log("Received links from backend:", data);

            // Store results in chrome local storage for popup display
            chrome.storage.local.set({ fetchedData: data }, () => {
                console.log("Stored fetched data successfully in local storage");
            });
        }
    } catch (e) {
        console.log("Failed to fetch links: ", e);
    }
}
