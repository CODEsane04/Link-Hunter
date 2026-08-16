from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import sys
import json
import os
import re
import base64
import requests
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
from typing import List, Optional
from langchain_core.messages import SystemMessage, HumanMessage
from datetime import datetime
import re
from sentence_transformers import SentenceTransformer, util



# Load environment variables
load_dotenv()


YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
embedder = SentenceTransformer('all-MiniLM-L6-v2')


# ----------------- HELPERS ---------------------------
def encode_image_to_base64(image_url: str):
    """
    Download an image and return a valid data URI.
    """

    try:
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/138.0 Safari/537.36"
            )
        }

        response = requests.get(
            image_url,
            headers=headers,
            timeout=20
        )

        print(f"Status Code : {response.status_code}")

        content_type = response.headers.get("content-type", "")
        print(f"Content-Type : {content_type}")

        if response.status_code != 200:
            raise Exception(
                f"Failed to download image. Status={response.status_code}"
            )

        if not content_type.startswith("image/"):
            raise Exception(
                f"URL is not an image. Received content-type={content_type}"
            )

        encoded = base64.b64encode(
            response.content
        ).decode("utf-8")

        return f"data:{content_type};base64,{encoded}"

    except Exception as e:
        print(f"Image Encoding Error: {e}")
        return None

def calculate_score(views, years):
    """
    UPDATED FORMULA: Score = (ViewsInMillions) / (1.2 ^ YearsOld)
    Example: 
    - 2.4M views, 0 years old -> Score = 2.4
    - 2.4M views, 2 years old -> Score = 2.4 / (1.2^2) = 1.66
    """
    
    if years < 0: years = 0
    
    # Convert raw views to Millions (float)
    views_in_millions = views / 1_000_000
    
    denominator = 1.2 ** years
    
    return round(views_in_millions / denominator, 3)

def format_view_count(views):
    if not isinstance(views, int): return "N/A"
    try:
        if views >= 1_000_000: return f"{views / 1_000_000:.1f}M"
        elif views >= 1_000: return f"{views // 1000}k"
        else: return str(views)
    except: return "N/A"

def format_published(published_at_str: str) -> int:
    """
    Extracts the publish year from a YouTube ISO 8601 string,
    calculates how many years ago it was compared to the current year,
    and returns the integer value.
    """
    if not published_at_str:
        return 0
        
    try:
        # 1. Extract the year (first 4 characters of the ISO string e.g., "2023")
        year_str = published_at_str[:4]
        
        # 2. Convert it to an integer
        published_year = int(year_str)
        
        # 3. Get the current year dynamically
        current_year = datetime.now().year
        
        # 4. Subtract to find out how many years ago it was published
        years_ago = current_year - published_year
        
        # Ensure we don't return a negative number (e.g., due to timezone overlaps)
        return max(0, years_ago)
        
    except (ValueError, TypeError):
        # Fallback in case the YouTube API returns a missing or malformed string
        return 0

def format_duration(duration_str: str) -> str:
    """
    Converts ISO 8601 duration string (e.g., 'PT19M27S', 'PT1H2M3S', 'PT45S')
    into a human-readable string (e.g., '19m, 27s', '1h, 2m, 3s', '45s').
    """
    if not duration_str or not isinstance(duration_str, str):
        return "N/A"

    # Match hours, minutes, and seconds from the ISO 8601 duration
    pattern = r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?'
    match = re.match(pattern, duration_str)

    if not match:
        return duration_str  # Return original if parsing fails

    hours, minutes, seconds = match.groups()

    parts = []
    if hours:
        parts.append(f"{hours}h")
    if minutes:
        parts.append(f"{minutes}m")
    if seconds:
        parts.append(f"{seconds}s")

    return ", ".join(parts) if parts else "0s"
# --- Helper Functions (Search & Format) ---


def fetch_youtube_api_v3(query: str, max_results: int = 30) -> list:
    if not YOUTUBE_API_KEY:
        raise ValueError("YouTube API key is missing.")

    tutorials = []
    
    # ==========================================
    # STEP 1: Search for the Top 30 Video IDs
    # ==========================================
    search_url = "https://www.googleapis.com/youtube/v3/search"
    search_params = {
        "part": "snippet",
        "q": query,
        "type": "video",          # Strictly only return videos (no channels/playlists)
        "maxResults": max_results,
        "key": YOUTUBE_API_KEY
    }
    
    search_response = requests.get(search_url, params=search_params)
    search_data = search_response.json()
    
    if "items" not in search_data:
        print("YouTube API Error:", search_data)
        return []

    # Extract just the video IDs into a comma-separated string
    video_ids = [item["id"]["videoId"] for item in search_data["items"]]
    video_ids_string = ",".join(video_ids)

    # ==========================================
    # STEP 2: Fetch Statistics (Views) for those IDs
    # ==========================================
    videos_url = "https://www.googleapis.com/youtube/v3/videos"
    videos_params = {
        "part": "snippet,statistics,contentDetails",
        "id": video_ids_string,
        "key": YOUTUBE_API_KEY
    }
    
    videos_response = requests.get(videos_url, params=videos_params)
    videos_data = videos_response.json()

    # ==========================================
    # STEP 3: Format the Output for your Frontend
    # ==========================================
    for item in videos_data.get("items", []):
        video_id = item["id"]
        snippet = item["snippet"]
        statistics = item.get("statistics", {})
        content_details = item.get("contentDetails", {})

        # Some videos hide their view counts
        raw_views = int(statistics.get("viewCount", 0))
        published_time = snippet.get("publishedAt", "") # Format: 2023-10-15T14:30:00Z
        published_time_int = format_published(published_time)

        tutorials.append({
            "title": snippet.get("title"),
            "link": f"https://www.youtube.com/watch?v={video_id}",
            "duration": format_duration(content_details.get("duration")), # Format: PT5M33S (ISO 8601)
            "views": format_view_count(raw_views),
            "publishedTime": published_time_int,
            "product_name": query,
            "score" : calculate_score(raw_views, published_time_int)
        })

    return tutorials

def clean_title_for_embedding(title: str) -> str:
    """
    Sanitizes YouTube video titles before generating text embeddings.
    - Unpacks hashtags and splits camelCase words (e.g. #CrochetTutorial -> crochet tutorial)
    - Removes emojis, special characters, and noise symbols
    - Normalizes multiple spaces and lowercases output
    """
    if not title or not isinstance(title, str):
        return ""

    # 1. Split CamelCase / PascalCase words (e.g., "CrochetTutorial" -> "Crochet Tutorial", "DIYCraft" -> "DIY Craft")
    cleaned = re.sub(r'(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])', ' ', title)

    # 2. Replace '#' and '_' with spaces so hashtag words merge naturally into prose
    cleaned = cleaned.replace('#', ' ').replace('_', ' ')

    # 3. Strip emojis and special characters (keep only alphanumeric characters and spaces)
    cleaned = re.sub(r'[^a-zA-Z0-9\s]', ' ', cleaned)

    # 4. Collapse multiple spaces into a single space and strip leading/trailing whitespace
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()

    # 5. Lowercase for uniform tokenization
    return cleaned.lower()
# --------------- LLM ------------------------------

def get_image_description(encoded_image_url) :

    model = ChatGoogleGenerativeAI (
        model="gemma-4-31b-it",
        temperature=0.0,
        max_retries=0
    )

    if not encoded_image_url :
        raise HTTPException(
            status_code=404,
            detail="the encoded image url is not valid"
        )

    class op_schema1(BaseModel):
        is_valid: bool = Field(
            description="True if the image is a handmade craft or DIY project. False if it is a commercially manufactured object, real car, nature, etc."
        )
        rejection_reason: Optional[str] = Field(
            default=None, 
            description="If is_valid is false, explain why in one sentence. If true, leave null."
        )
        object_category: Optional[str] = Field(
            default=None, 
            description="High-level classification (e.g., keychain, greeting card, vase, plushie, purse-charm, bag-charm etc. Identify descriptively)."
        )
        detailed_description: Optional[str] = Field(
            default=None, 
            description="Specific details of the object in one line, mention excatly if it resembles to any real-life object, character, animal, human etc. (e.g., a green tortoise keychain with a pink shell)."
        )
        materials: Optional[List[str]] = Field(
            default=None, 
            description="List of primary materials visible in 1 line (e.g., ['wool', 'metal keyring'], ['paper']. ['safety-pins'])."
        )
        crafting_process: Optional[str] = Field(
            default=None, 
            description="The specific technique used in 1 line (e.g., amigurumi crochet, origami, cross-stitch, resin pouring)."
        )

    structured_model1 = model.with_structured_output(op_schema1, include_raw=True)
    system_prompt1 = """
        [SYSTEM DIRECTIVE: AUTOMATED DATA EXTRACTION MODE - ZERO CONVERSATION]

        You are an automated visual data extraction pipeline. Your sole purpose is to parse image inputs and populate the requested output schema. You are NOT a conversational assistant.

        TASK OBJECTIVES:
        1. Determine if the image depicts a valid handmade craft / DIY project.
        2. Extract the high-level object category.
        3. Extract a 1-line detailed description.
        4. List visible primary materials.
        5. Identify the specific crafting technique or process used.

        STRICT OUTPUT GUIDELINES:
        output must only be given in the following json format. no conversations, no thinking nothing, only follow the following. JSON strucure
        {
            "is_valid" : ,
            "rejection_reason" : ,
            "object_category" : ,
            "detailed_description" :  ,
            "materials" : ,
            "crafting_process" : 
        }

        VALIDATION & REJECTION PROTOCOL:
        - Set `is_valid = true` ONLY if the subject is a verified handmade craft or DIY project.
        - Set `is_valid = false` if the subject is a mass-produced commercial product, real vehicle, natural landscape, screenshot, or non-DIY object.
        - If `is_valid = false`, populate `rejection_reason` with a single concise sentence explaining why, and set all other craft attribute fields to null.

        STRICT OPERATIONAL CONSTRAINTS (ZERO-TOLERANCE):
        - DO NOT output any introductory text, preambles, or conversational greetings (e.g., "Sure", "Here is your JSON", "Based on the image").
        - DO NOT output any chain-of-thought, reasoning steps, or internal commentary.
        - DO NOT output any closing remarks, postscripts, or offers for further help.
        - OUTPUT ONLY raw JSON matching the required schema. Your output MUST begin with '{' and end with '}'.
    """

    message = [
        SystemMessage(content=system_prompt1),

        HumanMessage(
            content = [
                {
                    "type" : "image_url",
                    "image_url" : {
                        "url" : encoded_image_url
                    }
                },
                {
                    "type" : "text",
                    "text" : "Analyze this image and extract the craft information into the requested schema."
                }
            ]
        )
    ]

    try:
        # Keep include_raw=True so we can access the raw text if Pydantic fails
        response = structured_model1.invoke(message)

        # 1. First, check if LangChain successfully parsed it natively
        if response.get("parsed") is not None:
            return response["parsed"]

        # 2. FALLBACK: LangChain failed (likely due to CoT chatter and lists)
        print("\n===== USING FALLBACK REGEX PARSER =====")
        raw_content = response["raw"].content
        
        # Convert the raw content into a single string (flattening lists if necessary)
        if isinstance(raw_content, list):
            text_parts = []
            for part in raw_content:
                if isinstance(part, dict) and "text" in part:
                    text_parts.append(part["text"])
                else:
                    text_parts.append(str(part))
            raw_text = "".join(text_parts)
        else:
            raw_text = str(raw_content)

        # 3. Surgically extract the JSON block using Regex
        # This looks for ```json { ... } ``` and extracts just the dictionary
        match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', raw_text, re.DOTALL)
        
        if match:
            json_string = match.group(1)
        else:
            # If the model forgot the markdown backticks, try to find the outermost brackets
            match_bare = re.search(r'(\{.*\})', raw_text, re.DOTALL)
            if match_bare:
                json_string = match_bare.group(1)
            else:
                raise ValueError("Could not locate any JSON structure in the LLM output.")

        # 4. Parse the extracted string and validate it against your schema manually
        parsed_dict = json.loads(json_string)
        
        # Convert the raw dictionary into your Pydantic object
        final_object = op_schema1(**parsed_dict)
        
        print("\n===== IMAGE DESCRIPTION (RECOVERED) =====")
        print(final_object)
        
        return final_object

    except Exception as e:
        print("\n===== IMAGE DESCRIPTION ERROR =====")
        print(type(e))
        print(e)
        return None

def get_search_query(image_description) :

    model = ChatGoogleGenerativeAI(
        model="gemma-4-31b-it",
        temperature=0.1,
        max_retries=0
    )

    class op_schema2(BaseModel) :
        search_query : str = Field(description="use the image description based on different fields & generate the youtube search query")

    structured__model2 = model.with_structured_output(op_schema2, include_raw=True)

    system_prompt2 = f"""[SYSTEM DIRECTIVE: AUTOMATED SEARCH QUERY GENERATOR]

        You are a specialized search query optimization engine for YouTube DIY and craft tutorials. 

        INPUT CRAFT METADATA:
        - Category: {image_description.object_category}
        - Detailed Description: {image_description.detailed_description}
        - Materials: {image_description.materials}
        - Crafting Technique: {image_description.crafting_process}

        QUERY CONSTRUCTION RULES:
        1. SUBJECT-FIRST FOCUS: Identify the exact, specific object, shape, or character being made.
        2. HUMAN-LIKE INTENT: Formulate the query exactly how a human crafter would type it. You are encouraged to use natural phrasing like "how to make a" or "DIY tutorial for".
        3. NO ARTIFICIAL TRUNCATION: Use as many words as necessary.
        4. SELF-VERIFICATION: Before finalizing your output, you must verify that your generated query perfectly and naturally answers the question: "What exact object is the user trying to make?"

        OUTPUT FORMAT DETAILS
        Strictly output ONLY in JSON format, following this exact structure:
        {{
            "search_query": "your generated query here"
        }}

        STRICT OPERATIONAL CONSTRAINTS (ZERO-TOLERANCE):
        - DO NOT output any introductory text.
        - DO NOT output any chain-of-thought.
        - OUTPUT ONLY the raw JSON.
    """

    messages = [
        SystemMessage(content=system_prompt2),

        HumanMessage(
            content= [
                {
                    "type" : "text",
                    "text" : "Follow the instructions & generate the search query"
                }
            ]
        )
    ]

    try:
        response = structured__model2.invoke(messages)

        # 2. NATIVE PARSER: If LangChain successfully parsed it, return it immediately
        if response.get("parsed") is not None:
            return response["parsed"]

        # 3. FALLBACK PARSER: LangChain failed (likely due to a list), so we extract manually
        print("\n===== USING FALLBACK REGEX PARSER FOR SEARCH QUERY =====")
        raw_content = response["raw"].content
        print("\nprintig in search querry fucntion\n")
        print(raw_content)
        
        # Flatten the list into a single string
        if isinstance(raw_content, list):
            text_parts = []
            for part in raw_content:
                if isinstance(part, dict) and "text" in part:
                    text_parts.append(part["text"])
                else:
                    text_parts.append(str(part))
            raw_text = "".join(text_parts)
        else:
            raw_text = str(raw_content)

        # Surgically extract the JSON block
        match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', raw_text, re.DOTALL)
        if match:
            json_string = match.group(1)
        else:
            match_bare = re.search(r'(\{.*\})', raw_text, re.DOTALL)
            if match_bare:
                json_string = match_bare.group(1)
            else:
                raise ValueError("Could not locate any JSON structure in the LLM output.")

        # Manually parse the dictionary and feed it to Pydantic
        parsed_dict = json.loads(json_string)
        final_object = op_schema2(**parsed_dict)
        
        print("\n===== SEARCH QUERY (RECOVERED) =====")
        print(final_object)
        
        return final_object

    except Exception as e:
        print("\n===== SEARCH QUERY ERROR =====")
        print(type(e))
        print(e)
        raise HTTPException(
            status_code=500,
            detail="LLM failed to generate the search query after applying fallback parser."
        )

# ------------------ Processing the results -----------------

def semantic_filtering(tutorial_list, search_query) :

    if len(tutorial_list) == 0 :
        raise HTTPException(
            status_code=500,
            detail="the tutorial list was empty when it came for semantic filtering"
        )
    #search query will be matched with all the retrieved tutorial video titles & similarity score will be calculated

    #out of the 50 retrieved items, we will pick top 25, 

    #out of those 25 we will pick top 10 or top 15 based on the freshness score & also rank them accordingly in the frontend

    try :

        query_embedding = embedder.encode(search_query, convert_to_tensor=True)
        for video_items in tutorial_list :
            cleaned_title = clean_title_for_embedding(video_items["title"])
            title_embedding = embedder.encode(cleaned_title, convert_to_tensor=True)
            cosine_score = util.cos_sim(query_embedding, title_embedding).item()
            video_items["cosine_score"] = cosine_score

        filtered_tutorials = [
            video_item
            for video_item in tutorial_list
            if video_item["cosine_score"] >= 0.1
        ]

        return filtered_tutorials
    
    except Exception as e :
        raise HTTPException(
            status_code=500,
            detail=f"couldn't compute the cosine similarity {str(e)}"
        )

#schema of the in coming body
class Input_req(BaseModel) :
    image_url : str

app = FastAPI()

# Add this CORS configuration right after initializing your app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins (perfect for Chrome extensions)
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods, including POST and OPTIONS
    allow_headers=["*"],  # Allows all headers
)

@app.post("/get_links")
def get_links(request : Input_req) :
    url = request.image_url

    if not url :
        raise HTTPException(
            status_code=400,
            detail="No image url recieved"
        )
    else :
        print("url recieved succesfully", url)

    print("sending url for further processing")

    print("\n==============================")
    print("STEP 1 : Encoding Image")
    print("==============================")

    encoded_image_url = encode_image_to_base64(url)

    if not encoded_image_url :
        raise HTTPException(
            status_code=500,
            detail="failed to generate the encoded url"
        )
    else :
        print("url encoded successfully, sending it to the LLM to get the description")

    print("\n==============================")
    print("STEP 2 : Getting Image Description")
    print("==============================")

    image_description = None
    tries = 0
    max_tries = 10

    while not image_description and tries < max_tries:
        tries += 1
        print(f"Attempt {tries} of {max_tries}...")
        image_description = get_image_description(encoded_image_url)
        
        if image_description:
            print("LLM successfully generated the image description")
            break
        else:
            print("Failed to generate or parse description. Retrying...")

    if not image_description:
        # Handle the total failure (e.g., raise an HTTPException to inform the frontend)
        print("Failed to get a valid image description after maximum retries.")
        raise HTTPException(
            status_code=500,
            detail="Failed to analyze the image structure after multiple attempts."
        )
    
    print(f"Description generated in {tries} tries")

    print("\nIMAGE DESCRIPTION:")
    print(image_description)

    if image_description.is_valid == False :
        return {
            "is_valid" : False,
            "rejection_reason" : image_description.rejection_reason,
            "search_query" : None,
            "total_results" : None,
            "final_list" : None
        }


    print("\n==============================")
    print("STEP 3 : Generating Search Query")
    print("==============================")

    print("\n")

    generated_sq_object = None
    tries = 0
    
    while not generated_sq_object and tries < max_tries :

        tries += 1
        print(f"Attempt {tries} of {max_tries}...")
        generated_sq_object = get_search_query(image_description)

        if generated_sq_object : 
            print("llm succesfullly generated the search query")
            break
        else :
            print("failed to generate the search query or parse the output....retrying")

    if not generated_sq_object :
        raise HTTPException(
            status_code=500,
            detail="failed to generate the search query after multiple attempts"
        )

    print("\n")
    print(f"search querry generated in {tries} tries")
    print("\n")

    print("using the search query to get links from the YT DB")

    print("\n==============================")
    print("STEP 4 : Fetching data from YT API")
    print("==============================")

    tutorial_list = fetch_youtube_api_v3(generated_sq_object.search_query)

    if not tutorial_list :
        raise HTTPException(
            status_code=500,
            detail="couldn't fetch the links from the youtube databse"
        )
    else :
        print("succesfully fetched the links and metadata from Youtube DB")


    print("\n===================================")
    print("STEP 5 : Performing semantic filtering")
    print("=======================================")

    semantically_filtered_tutorial = semantic_filtering(tutorial_list, generated_sq_object.search_query)

    if not semantically_filtered_tutorial :
        raise HTTPException(
            status_code=500,
            detail="couldn't semantically filter the tutorial list"
        )
    else :
        print("succesfully filtered the tutorial list")

    if len(semantically_filtered_tutorial) > 15:
        semantically_filtered_tutorial = sorted(
            semantically_filtered_tutorial,
            key=lambda x: x["cosine_score"],
            reverse=True
        )[:15]

    #return filtered_tutorials

    return {

        "is_valid" : True,
        "rejection_reason" : None,
        "search_query" : generated_sq_object.search_query,
        "total_results" : len(semantically_filtered_tutorial),
        "final_list" : semantically_filtered_tutorial
    }

@app.get("/")
def Home() :
    return {
        "message" : "No queries yet"
    }
    
@app.get("/health")
def health_check() :
    return {
        "message" : "All fine dude"
    }