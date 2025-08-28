document.addEventListener('DOMContentLoaded', () => {
    const listOfLinks = document.getElementById('link-list');
    const productName = document.getElementById('prod-name');

    let link_arr = [];
    
    async function get_links() {
        let result = await chrome.storage.local.get('fetchedLinks');
        return result.fetchedLinks;
    }

    async function diplay_links() {

        link_arr = await get_links();
        
        if (link_arr && link_arr.length > 0) {
            console.log("links retrieved from the local storage : ", link_arr);

            link_arr.forEach(link => {
                const item = document.createElement('a');
                item.href = link.url;
                item.title = link.title;
                item.textContent = link.title;
                item.target = "_blank";

                const view_count = document.createElement('span');
                view_count.classList.add('views');
                view_count.textContent = "2.5M";

                listOfLinks.appendChild(item);
                listOfLinks.appendChild(view_count);
            });

            productName.textContent = link_arr[0].product_name;
        }
        else {
            console.log("no links found in the local storage");

            // If no tutorials are found, display a message
            const messageElement = document.createElement('p');
            messageElement.textContent = "No tutorials found for the last image.";
            messageElement.style.gridColumn = "1 / -1"; // Make message span both columns
            messageElement.style.textAlign = "center";
            listOfLinks.appendChild(messageElement);
        };
    };
    
    diplay_links();

});