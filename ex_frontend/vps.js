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
            console.log("Links retrieved from the local storage : ", link_arr);

            productName.textContent = data.search_query;

            link_arr.forEach(link => {
                const container = document.createElement('div');
                container.style.marginBottom = "10px";

                const item = document.createElement('a');
                item.href = link.link; 
                item.title = link.title;
                item.textContent = link.title;
                item.target = "_blank";

                const view_count = document.createElement('span');
                view_count.classList.add('views');
                view_count.style.marginLeft = "10px";
                view_count.style.fontSize = "0.85em";
                view_count.style.color = "#555";
                view_count.textContent = `👁️ ${link.views || "0"}`;

                container.appendChild(item);
                container.appendChild(view_count);
                listOfLinks.appendChild(container);
            });
        }
        else {
            console.log("No links found in the local storage");
            show_invalid_state("No YouTube tutorials found for this object.");
        }
    }

    function show_invalid_state(reason) {
        productName.textContent = "No DIY Object Detected";
        productName.style.color = "#d9534f"; 
        
        listOfLinks.innerHTML = `
            <div style="text-align: center; padding: 20px; color: #555;">
                <div style="font-size: 24px; margin-bottom: 10px;">🤷‍♂️</div>
                <p style="margin-bottom: 10px; color: #d9534f;"><strong>${reason}</strong></p>
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
    }
    
    display_data();
});