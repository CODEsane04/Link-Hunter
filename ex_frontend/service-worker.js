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

        //storing the img url in the chrome storage as a key value pair
        const img_url = info.srcUrl;
        chrome.storage.local.set({capturedImageUrl: img_url}, () => {
            console.log("image url stored succesfully in chrome storage");
        });
    }
});

