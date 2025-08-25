document.addEventListener('DOMContentLoaded', async () => {
    const url_space = document.getElementById('img-url');
    
    const data = await chrome.storage.local.get('capturedImageUrl');

    if (data.capturedImageUrl){
        url_space.textContent = data.capturedImageUrl;
    }
    else {
        url_space.textContent = "No image URL found.";
    }

})