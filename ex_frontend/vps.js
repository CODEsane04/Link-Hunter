document.addEventListener('DOMContentLoaded', () => {
    const listOfLinks = document.getElementById('link-list');
    const productName = document.getElementById('prod-name');

    async function get_data() {
        let result = await chrome.storage.local.get('fetchedData');
        await chrome.storage.local.remove('fetchedData');
        return result.fetchedData;
    }

    async function display_data() {
        const data = await get_data();
        
        if (!data) {
            console.log("No data found in local storage");
            show_invalid_state("No data received from the backend.");
            return;
        }

        if (!data.is_valid) {
            console.log("Invalid image:", data.rejection_reason);
            show_invalid_state(data.rejection_reason || "Not a valid DIY craft.");
            return;
        }

        const link_arr = data.final_list;
        
        if (link_arr && link_arr.length > 0) {
            console.log("Links retrieved from local storage: ", link_arr);

            productName.textContent = data.search_query;
            listOfLinks.innerHTML = ""; // Clear loader if any

            link_arr.forEach(link => {
                // Creating a fully clickable row container (a tag)
                const item = document.createElement('a');
                item.href = link.link; 
                item.title = link.title;
                item.target = "_blank";
                item.className = "link-item";

                // Title Element
                const titleSpan = document.createElement('span');
                titleSpan.className = "link-title";
                titleSpan.textContent = link.title;

                // Views/Score Element (Aligns to the right)
                const view_count = document.createElement('span');
                view_count.className = 'views';
                view_count.textContent = link.views || "0";

                item.appendChild(titleSpan);
                item.appendChild(view_count);
                listOfLinks.appendChild(item);
            });
        }
        else {
            console.log("No links found in the local storage");
            show_invalid_state("No YouTube tutorials found for this object.");
        }
    }

    function show_invalid_state(reason) {
        productName.textContent = "No DIY Object Detected";
        productName.style.color = "var(--danger-color)"; 
        
        listOfLinks.innerHTML = `
            <div class="invalid-state">
                <div class="invalid-icon">🤷‍♂️</div>
                <div class="invalid-reason">${reason}</div>
                <div class="invalid-tips">
                    <p><strong>Link Hunter works best on:</strong></p>
                    <ul>
                        <li>🧶 Crochet & Knitting</li>
                        <li>🪵 Woodworking</li>
                        <li>🖼️ Arts & Crafts</li>
                        <li>🖨️ 3D Printing</li>
                    </ul>
                    <p style="margin-top: 15px;">
                        Try clicking specifically on the <strong>object</strong> you want to make.
                    </p>
                </div>
            </div>
        `;
    }
    
    display_data();
});