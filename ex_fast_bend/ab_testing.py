import os
import csv
import json
import re
import random
import base64
import requests
from datetime import datetime
from typing import List, Optional
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.prompts import PromptTemplate
from sentence_transformers import SentenceTransformer, util

# ==========================================
# 1. CONFIGURATION & MODELS
# ==========================================
load_dotenv()
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
CSV_FILENAME = "eval_dataset_LH.csv"

if not YOUTUBE_API_KEY:
    raise ValueError("Missing YOUTUBE_API_KEY in environment.")

print("Loading Sentence Transformer...")
embedder = SentenceTransformer('all-MiniLM-L6-v2')

# Shared LLM for Generation and Judging
shared_llm = ChatGoogleGenerativeAI(model="gemma-4-31b-it", temperature=0.1)
judge_llm = ChatGoogleGenerativeAI(model="gemma-4-31b-it", temperature=0.0)

# ==========================================
# 2. PROMPT VARIANTS FOR A/B TESTING
# ==========================================
# Notice the double curly braces {{ }} for JSON syntax so .format() doesn't crash

PROMPT_V1 = """[SYSTEM DIRECTIVE: AUTOMATED SEARCH QUERY GENERATOR - ZERO CONVERSATION]

You are a specialized search query optimization engine for YouTube DIY and craft tutorials. Your sole purpose is to convert extracted craft metadata into a high-intent, highly accurate YouTube search string. You are NOT a conversational assistant.

INPUT CRAFT METADATA:
- Category: {category}
- Detailed Description: {detailed_description}
- Materials: {materials}
- Crafting Technique: {crafting_process}

QUERY CONSTRUCTION RULES:
1. KEYWORD PRIORITY METHOD: Combine [Crafting Technique] + [Specific Object/Design] + [Primary Material (if relevant)] + ["tutorial" or "DIY"].
2. KEEP IT CONCISE: Output a concise 3 to 8 word search phrase. Do NOT write full sentences or conversational queries.
3. STRIP FILLER WORDS: Exclude vague adjectives and non-searchable descriptors (e.g., "beautiful", "cute", "nice", "simple looking", "a photo of").
4. TARGET HIGH-INTENT TUTORIALS: Always append "tutorial" or "how to make" to trigger instructional video results.

OUTPUT FORMAT DETAILS
Strictly output ONLY in JSON format, following this exact structure:
{{
    "search_query": "your generated query here"
}}

STRICT OPERATIONAL CONSTRAINTS (ZERO-TOLERANCE):
- DO NOT output any introductory text or preambles.
- DO NOT output any quotation marks, explanations, or reasoning.
- DO NOT output any chain-of-thought, reasoning steps, or internal commentary.
- OUTPUT ONLY the raw search query string as JSON.
"""

PROMPT_V2 = """[SYSTEM DIRECTIVE: AUTOMATED SEARCH QUERY GENERATOR - ZERO CONVERSATION]

You are a specialized search query optimization engine for YouTube DIY and craft tutorials. 
Your generated query must seamlessly answer this fundamental question: "What exact object is the user trying to make?"

INPUT CRAFT METADATA:
- Category: {category}
- Detailed Description: {detailed_description}
- Materials: {materials}
- Crafting Technique: {crafting_process}

QUERY CONSTRUCTION RULES:
1. SUBJECT-FIRST FOCUS: Identify the exact, specific object, shape, or character being made.
2. HUMAN-LIKE INTENT: Formulate the query exactly how a human crafter would type it to find a specific guide.
3. NO ARTIFICIAL TRUNCATION: Use as many words as necessary to capture the exact subject, defining shape, and primary material. 
4. STRIP FILLER: Exclude vague adjectives and conversational filler.
5. TUTORIAL ANCHOR: Always append "tutorial" or "DIY" at the end of the query.

OUTPUT FORMAT DETAILS
Strictly output ONLY in JSON format, following this exact structure:
{{
    "search_query": "your generated query here"
}}

STRICT OPERATIONAL CONSTRAINTS (ZERO-TOLERANCE):
- DO NOT output any introductory text, preambles, or conversational greetings.
- DO NOT output any chain-of-thought.
- OUTPUT ONLY the raw JSON.
"""

PROMPT_V3 = """[SYSTEM DIRECTIVE: AUTOMATED SEARCH QUERY GENERATOR]

You are a specialized search query optimization engine for YouTube DIY and craft tutorials. 

INPUT CRAFT METADATA:
- Category: {category}
- Detailed Description: {detailed_description}
- Materials: {materials}
- Crafting Technique: {crafting_process}

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

PROMPT_V4 = """[SYSTEM DIRECTIVE: AUTOMATED SEARCH QUERY GENERATOR]

You are an intelligent search query generator for YouTube DIY and craft tutorials. 

Your goal is to generate a highly effective, natural, and human-like YouTube search query that will yield the absolute best tutorial videos for the specific object provided in the context below.

CONTEXT:
- Category: {category}
- Detailed Description: {detailed_description}
- Materials: {materials}
- Crafting Technique: {crafting_process}

THE GOLDEN RULE:
Your final search query MUST perfectly and naturally answer the question: "What exact object are we trying to make?" 

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

PROMPTS_TO_TEST = {
    "V1 (Strict/Concise)": PROMPT_V1,
    "V2 (Subject First)": PROMPT_V2,
    "V3 (Guided Natural)": PROMPT_V3,
    "V4 (Unrestricted/Intent)": PROMPT_V4
}

# ==========================================
# 3. BACKEND HELPER FUNCTIONS
# ==========================================
def encode_image_to_base64(image_url: str):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(image_url, headers=headers, timeout=20)
        content_type = response.headers.get("content-type", "")
        if response.status_code == 200 and content_type.startswith("image/"):
            encoded = base64.b64encode(response.content).decode("utf-8")
            return f"data:{content_type};base64,{encoded}"
    except: pass
    return None

def calculate_score(views, years):
    if years < 0: years = 0
    views_in_millions = views / 1_000_000
    return round(views_in_millions / (1.2 ** years), 3)

def format_view_count(views):
    try:
        if views >= 1_000_000: return f"{views / 1_000_000:.1f}M"
        elif views >= 1_000: return f"{views // 1000}k"
        else: return str(views)
    except: return "N/A"

def format_published(published_at_str: str) -> int:
    try:
        year = int(published_at_str[:4])
        return max(0, datetime.now().year - year)
    except: return 0

def format_duration(duration_str: str) -> str:
    if not duration_str: return "N/A"
    match = re.match(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', duration_str)
    if not match: return duration_str
    h, m, s = match.groups()
    parts = [f"{x}{l}" for x, l in zip((h, m, s), ('h', 'm', 's')) if x]
    return ", ".join(parts) if parts else "0s"

def clean_title_for_embedding(title: str) -> str:
    cleaned = re.sub(r'(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])', ' ', title)
    cleaned = cleaned.replace('#', ' ').replace('_', ' ')
    cleaned = re.sub(r'[^a-zA-Z0-9\s]', ' ', cleaned)
    return re.sub(r'\s+', ' ', cleaned).strip().lower()

def fetch_youtube_api_v3(query: str, max_results: int = 30) -> list:
    search_url = "https://www.googleapis.com/youtube/v3/search"
    search_response = requests.get(search_url, params={"part": "snippet", "q": query, "type": "video", "maxResults": max_results, "key": YOUTUBE_API_KEY})
    search_data = search_response.json()
    if "items" not in search_data: return []

    video_ids = ",".join([item["id"]["videoId"] for item in search_data["items"]])
    videos_response = requests.get("https://www.googleapis.com/youtube/v3/videos", params={"part": "snippet,statistics,contentDetails", "id": video_ids, "key": YOUTUBE_API_KEY})
    
    tutorials = []
    for item in videos_response.json().get("items", []):
        raw_views = int(item.get("statistics", {}).get("viewCount", 0))
        pub_int = format_published(item["snippet"].get("publishedAt", ""))
        tutorials.append({
            "title": item["snippet"].get("title"),
            "link": f"https://www.youtube.com/watch?v={item['id']}",
            "duration": format_duration(item.get("contentDetails", {}).get("duration")),
            "views": format_view_count(raw_views),
            "score": calculate_score(raw_views, pub_int)
        })
    return tutorials

def semantic_filtering(tutorial_list, search_query) :
    if not tutorial_list: return []
    query_embedding = embedder.encode(search_query, convert_to_tensor=True)
    for video in tutorial_list:
        title_embedding = embedder.encode(clean_title_for_embedding(video["title"]), convert_to_tensor=True)
        video["cosine_score"] = util.cos_sim(query_embedding, title_embedding).item()
    
    filtered = [v for v in tutorial_list if v["cosine_score"] >= 0.1]
    return sorted(filtered, key=lambda x: x["cosine_score"], reverse=True)[:15]

# ==========================================
# 4. LLM INVOCATIONS
# ==========================================
class ImageDescriptionSchema(BaseModel):
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

structured_describer = shared_llm.with_structured_output(ImageDescriptionSchema, include_raw=True)

def get_image_description(encoded_image_url):
    prompt = """
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
    msg = [
        SystemMessage(content=prompt), 
        HumanMessage(content=[
            {"type":"image_url","image_url":{"url":encoded_image_url}}, 
            {"type":"text","text":"Analyze this image and extract the craft information into the requested schema."}
        ])
    ]
    
    try:
        response = structured_describer.invoke(msg)
        
        # 1. First, check if LangChain successfully parsed it natively
        if response.get("parsed") is not None:
            return response["parsed"]
            
        # 2. FALLBACK: LangChain failed (likely due to CoT chatter and lists)
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
        return ImageDescriptionSchema(**parsed_dict)
        
    except Exception as e:
        print(f"⚠️ Image Description Error: {e}")
        return None

class SearchQuerySchema(BaseModel):
    search_query : str = Field(description="use the image description based on different fields & generate the youtube search query")

structured_query_gen = shared_llm.with_structured_output(SearchQuerySchema, include_raw=True)

def generate_search_query(image_description, prompt_template_str):
    formatted_prompt = prompt_template_str.format(
        category=image_description.object_category,
        detailed_description=image_description.detailed_description,
        materials=image_description.materials,
        crafting_process=image_description.crafting_process
    )
    
    msg = [SystemMessage(content=formatted_prompt), HumanMessage(content="Follow the instructions & generate the search query")]
    
    try:
        response = structured_query_gen.invoke(msg)
        
        # 1. Native Parser
        if response.get("parsed") is not None:
            return response["parsed"].search_query
            
        # 2. Fallback Parser (Backend Logic)
        raw_content = response["raw"].content
        
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

        match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', raw_text, re.DOTALL)
        
        if match:
            json_string = match.group(1)
        else:
            match_bare = re.search(r'(\{.*\})', raw_text, re.DOTALL)
            if match_bare:
                json_string = match_bare.group(1)
            else:
                raise ValueError("Could not locate any JSON structure in the LLM output.")

        parsed_dict = json.loads(json_string)
        return parsed_dict.get("search_query", "")
        
    except Exception as e:
        print(f"⚠️ Search Query Generation Error: {e}")
        return ""

# ==========================================
# 5. JUDGE EVALUATION (UPDATED PROMPT)
# ==========================================
class SingleEvaluation(BaseModel):
    is_relevant: bool = Field(description="True if the video title is a tutorial for making the exact expected object. False otherwise.")
    reasoning: str = Field(description="A 1-sentence explanation of why it is relevant or irrelevant.")

class BatchEvaluation(BaseModel):
    evaluations: List[SingleEvaluation] = Field(description="A list containing exactly the same number of evaluations as the provided titles, strictly maintaining the original order.")

structured_judge = judge_llm.with_structured_output(BatchEvaluation, include_raw=True)

JUDGE_PROMPT = """
[SYSTEM DIRECTIVE: AUTOMATED BATCH RELEVANCE EVALUATION]

You are an objective relevance judge for a DIY craft search engine.
Your task is to evaluate {num_titles} retrieved YouTube video titles against a user's expected project and determine if they are genuinely helpful tutorials for the user.

EXPECTED PROJECT: {expected_subject}

RETRIEVED VIDEO TITLES:
{video_titles_list}

EVALUATION PRINCIPLES:
1. CORE SUBJECT & TECHNIQUE (MANDATORY):
   - The video MUST teach how to make the primary object/subject using the correct technique (e.g., crochet Spider-Man, origami rose, curtain tieback).
   - If the core craft matches, the video is RELEVANT (`is_relevant = true`).

2. PLACEMENTS, ACCESSORIES & MODIFIERS (FLEXIBLE / OPTIONAL):
   - Secondary add-ons, physical placements, and minor variations (e.g., "for car hanging", "keychain", "with stem and leaves", "on a ring tray") are NOT mandatory in the title.
   - Example 1: If expected is "crochet Spider-Man car hanging", a video titled "How to crochet Spider-Man amigurumi" is RELEVANT (true) because learning the Spider-Man craft is 80%+ of the project.
   - Example 2: If expected is "origami paper rose flower with stem and leaves", an "Origami Rose Tutorial" is RELEVANT (true).
   - Example 3: If expected is "crochet daisy curtain tieback", any crochet flower curtain tieback or generic curtain tieback tutorial is RELEVANT (true).

3. WHEN TO REJECT (`is_relevant = false`):
   - Completely different subject or technique (e.g., expected "crochet whale", but video is "crochet octopus" or "clay whale").
   - Non-tutorials (e.g., unboxing, product reviews, speed drawings, gameplay, buying guides).
   - Unrelated crafts or commercial product showcases.

STRICT OUTPUT GUIDELINES:
- Output ONLY a raw JSON object containing an "evaluations" key with exactly {num_titles} items, matching the input order.
- In your reasoning, explicitly identify the Core Subject and explain why it satisfies the user's intent.
"""

def evaluate_titles(expected_subject, titles):
    if not titles: return []
    formatted_titles = "\n".join([f"{i+1}. {t}" for i, t in enumerate(titles)])
    prompt = PromptTemplate.from_template(JUDGE_PROMPT).format(expected_subject=expected_subject, video_titles_list=formatted_titles, num_titles=len(titles))
    
    try:
        response = structured_judge.invoke(prompt)
        
        # 1. Native Parser
        if response.get("parsed") is not None:
            return [{"is_relevant": e.is_relevant, "reasoning": e.reasoning} for e in response["parsed"].evaluations]
            
        # 2. Fallback Parser (Backend Logic)
        raw_content = response["raw"].content
        
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

        match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', raw_text, re.DOTALL)
        
        if match:
            json_string = match.group(1)
        else:
            match_bare = re.search(r'(\{.*\})', raw_text, re.DOTALL)
            if match_bare:
                json_string = match_bare.group(1)
            else:
                raise ValueError("Could not locate any JSON structure in the LLM output.")

        parsed_dict = json.loads(json_string)
        parsed_batch = BatchEvaluation(**parsed_dict)
        return [{"is_relevant": e.is_relevant, "reasoning": e.reasoning} for e in parsed_batch.evaluations]
        
    except Exception as e:
        print(f"⚠️ Judge Error: {e}")
        return [{"is_relevant": False, "reasoning": "Error parsing judge response."} for _ in titles]
# ==========================================
# 6. MAIN A/B TESTING LOOP
# ==========================================
def run_ab_test():
    print("Loading CSV...")
    valid_diy_cases = []
    with open(CSV_FILENAME, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row.get("is_valid", "TRUE").strip().upper() == "TRUE":
                valid_diy_cases.append(row)
                
    # Get top 35, then pick 15 randomly
    top_35 = valid_diy_cases[:35]
    test_set = random.sample(top_35, min(15, len(top_35)))
    
    print(f"Selected {len(test_set)} random test cases for A/B Testing.\n")
    
    # Store results: { "Prompt Name": [list of P@5 scores] }
    ab_results = {name: [] for name in PROMPTS_TO_TEST.keys()}
    
    for i, test_case in enumerate(test_set, 1):
        expected_subject = test_case.get("expected description", "Unknown")
        image_url = test_case.get("image_url")
        
        print(f"{'='*80}")
        print(f"🖼️ TEST CASE {i}/{len(test_set)}: {expected_subject}")
        print(f"{'='*80}")
        
        # 1. Encode & Describe (Do this ONCE per image)
        print(">> Generating Image Description...")
        encoded = encode_image_to_base64(image_url)
        if not encoded:
            print("Failed to encode image. Skipping.")
            continue
            
        description_obj = get_image_description(encoded)
        if not description_obj:
            print("Failed to get description. Skipping.")
            continue
            
        print(f"   Identified as: {description_obj.detailed_description}")
        
        # 2. Iterate through prompt variants
        for prompt_name, prompt_template in PROMPTS_TO_TEST.items():
            print(f"\n--- Testing Variant: {prompt_name} ---")
            
            # Generate Query
            search_query = generate_search_query(description_obj, prompt_template)
            print(f"🔎 Generated Query: '{search_query}'")
            if not search_query:
                ab_results[prompt_name].append(0.0)
                continue
                
            # Fetch & Filter
            raw_tutorials = fetch_youtube_api_v3(search_query)
            final_tutorials = semantic_filtering(raw_tutorials, search_query)[:5]
            
            if not final_tutorials:
                print("⚠️ No relevant tutorials found.")
                ab_results[prompt_name].append(0.0)
                continue
                
            # Judge
            titles = [t["title"] for t in final_tutorials]
            judgments = evaluate_titles(expected_subject, titles)
            
            relevant_count = 0
            for idx, (title, j) in enumerate(zip(titles, judgments), 1):
                status = "🟢" if j["is_relevant"] else "🔴"
                print(f"  {idx}. {status} | {title}")
                print(f"       {j['reasoning']}")
                if j["is_relevant"]: relevant_count += 1
                
            p_at_5 = relevant_count / len(final_tutorials)
            print(f"🎯 Score for {prompt_name}: Precision@5 = {p_at_5:.2f}")
            ab_results[prompt_name].append(p_at_5)

    # ==========================================
    # 7. FINAL REPORT
    # ==========================================
    print(f"\n\n{'='*80}")
    print("🏆 A/B TESTING RESULTS REPORT 🏆")
    print(f"{'='*80}")
    
    for prompt_name, scores in ab_results.items():
        if scores:
            avg = sum(scores) / len(scores)
            print(f"{prompt_name: <25} | Avg Precision@5: {avg:.2f}  | (Tested {len(scores)} cases)")
        else:
            print(f"{prompt_name: <25} | Avg Precision@5: 0.00  | (Failed to execute)")

if __name__ == "__main__":
    run_ab_test()