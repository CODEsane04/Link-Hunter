
# Link Hunter 🎯

**Link Hunter** is an AI-powered Chrome Extension designed for makers, crafters, and DIY enthusiasts. It allows users to right-click any craft, hobby, or handmade item image on the web and instantly discover the best YouTube tutorials on how to make it. 

Instead of guessing keywords, Link Hunter uses a Vision-Language Model to analyze the image, figure out the exact materials and techniques required, and serves up the highest-quality, most relevant video guides directly in your browser.

## 🛠️ How to Install and Use

To use Link Hunter on your own machine, follow these simple steps:

1. **[Download the extension.zip file here](https://github.com/CODEsane04/Link-Hunter/raw/main/extension.zip)** and unzip it.
2. **Open Chrome** and navigate to `chrome://extensions` in your address bar.
3. **Enable "Developer mode"** (toggle in the top right corner).
4. Click **"Load unpacked"** in the top left menu.
5. **Select the unzipped folder** from step 1.

You're all set! Right-click any DIY image on the web and select "Search with VPS" to see the magic happen.

## 🧠 Technical Architecture & Features

Link Hunter is built on a polyglot microservice architecture, bridging a lightweight browser extension with a heavy-duty AI processing pipeline. 

* **Polyglot Backend Execution:** The backend utilizes a **Node.js/Express** server that natively spawns a **Python 3** child process. This allows the system to seamlessly handle fast web requests via JavaScript while leveraging Python's superior ecosystem for AI and data scraping tasks.
* **Vision-Language Model (VLM) Pipeline:** Image analysis is powered by Hugging Face's **Qwen2.5-VL-7B-Instruct** model. To bypass strict anti-bot and hotlinking protections on sites like Pinterest, the backend dynamically fetches and Base64-encodes the target image before transmitting it to the serverless GPU inference API.
* **Algorithmic Re-Ranking (Freshness Decay):** Standard YouTube search heavily favors older videos simply because they have accumulated more lifetime views. Link Hunter implements a custom **"Freshness Decay" mathematical algorithm** (`Score = Views / 1.2^Years`) that penalizes outdated content, ensuring the top results are a perfect balance of high popularity and modern relevance.
* **AI Guardrails & Query Expansion:** To optimize token usage and accuracy, the VLM is prompt-engineered to enforce a strict JSON schema. This acts as a guardrail to immediately reject non-DIY images (like memes or landscapes). For valid images, it executes a "Shotgun Strategy," generating both a highly specific query (precision) and a general category query (discovery) to guarantee robust results.

**Tech Stack:** JavaScript, Chrome Manifest V3, Node.js, Express, Python 3, Hugging Face Hub, `Youtube-python`.
