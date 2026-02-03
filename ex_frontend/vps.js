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
                view_count.textContent = link.formatted_views || "0";

                listOfLinks.appendChild(item);
                listOfLinks.appendChild(view_count);
            });

            productName.textContent = link_arr[0].product_name;
        }
        else {
            console.log("no links found in the local storage");

            // If no tutorials are found, display a message
            productName.textContent = "No DIY Object Detected";
            productName.style.color = "#d9534f"; // Red/Warning color
            
            listOfLinks.innerHTML = `
                <div style="text-align: center; padding: 20px; color: #555;">
                    <div style="font-size: 24px; margin-bottom: 10px;">🤷‍♂️</div>
                    <p style="margin-bottom: 10px;"><strong>Link Hunter works best on:</strong></p>
                    <ul style="text-align: left; margin-left: 20px; font-size: 0.9em;">
                        <li>🧶 Crochet & Knitting</li>
                        <li>🪵 Woodworking</li>
                        <li>🖼️ Arts & Crafts</li>
                        <li>🖨️ 3D Printing</li>
                    </ul>
                    <p style="margin-top: 15px; font-size: 0.8em; color: #888;">
                        Try clicking specifically on the <strong>object</strong> you want to make.
                    </p>
                </div>
            `;
        };
    };
    
    diplay_links();

});