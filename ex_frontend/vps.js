document.addEventListener('DOMContentLoaded', () => {
    const url_space = document.getElementById('img-url');

    async function diplayUrl(getUrl) {
        let url = await getUrl();
        if (url){
        url_space.textContent = url;
        }
        else {
            url_space.textContent = "No image URL found.";
        }
    }

    async function getUrl() {
        let result = await chrome.storage.local.get('capturedImageUrl');
        return result.capturedImageUrl;
    }
    
    diplayUrl(getUrl);

})