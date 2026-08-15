function setupContextMenu() {
    chrome.contextMenus.create({
        id: "searchWithLH",
        title: "Search with LH",
        contexts: ["image"]
    });
};

chrome.runtime.onInstalled.addListener(() => {
    setupContextMenu();
});

chrome.contextMenus.onClicked.addListener(async (info, tab) => {
    if (info.menuItemId === "searchWithLH") {

        console.log("Image right-clicked. URL : ", info.srcUrl);

        //storing the img url in the chrome storage as a key value pair
        const img_url = info.srcUrl;
        /*chrome.storage.local.set({capturedImageUrl: img_url}, () => {
            console.log("image url stored succesfully in chrome storage");
        });*/
        await getlinks(img_url);
    }
});

async function getlinks(img_url) {

    // backend url - https://link-hunter-backend.onrender.com/api/get-url

    const backendUrl = 'http://localhost:8000/get_links';
    console.log("sending image url to the backend : ", img_url);
    
    try {
        
        //response is a Response Object, you need to unpack this object
        //which is done by response.json() it unpacks & parses

        //we send a POST request to the backend with the image url in the body
        const response = await fetch(backendUrl, {
            method : 'POST',
            headers : {
                'Content-Type' : 'application/json'
            },
            body : JSON.stringify( {image_url: img_url} ),
        });

        if (!response.ok) {
            console.error(`HTTP error status : ${response.status}`); 
        } else {
            const data = await response.json();
            console.log("recieved the links from the backend, in response to the POST request", data.tutorials);

            //we have to store these links in the chrome local storage
            chrome.storage.local.set({fetchedData : data}, () => {
                console.log("stored the fetched data successfully in the local storage");
            });
        }
        
    } catch (e) {
        console.log("failed to fetch links : ", e);
    }
    
}



