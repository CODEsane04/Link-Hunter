function setupContextMenu() {
    chrome.contextMenus.create({
        id: "searchWithVPS",
        title: "Search with VPS",
        contexts: ["image"]
    });
};

chrome.runtime.onInstalled.addListener(() => {
    setupContextMenu();
});

chrome.contextMenus.onClicked.addListener((info, tab) => {
    if (info.menuItemId === "searchWithVPS") {
        console.log("Image right-clicked. URL : ", info.srcUrl);
    }
});

