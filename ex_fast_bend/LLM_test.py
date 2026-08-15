import warnings

# Suppress noisy warnings
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", message=".*LibreSSL.*")
warnings.filterwarnings("ignore", message=".*google.generativeai.*")

import base64
import requests
from typing import List, Optional

from dotenv import load_dotenv
from pydantic import BaseModel, Field
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage

load_dotenv()


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


# ------------------------------------------------------------------
# LLM
# ------------------------------------------------------------------

model = ChatGoogleGenerativeAI(
    model="gemma-4-31b-it",
    temperature=0.0
)


# ------------------------------------------------------------------
# Output Schema
# ------------------------------------------------------------------

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


structured_model = model.with_structured_output(
    op_schema1
)


# ------------------------------------------------------------------
# Prompt
# ------------------------------------------------------------------

system_prompt = """
[SYSTEM DIRECTIVE: AUTOMATED DATA EXTRACTION MODE - ZERO CONVERSATION]

You are an automated visual data extraction pipeline. Your sole purpose is to parse image inputs and populate the requested output schema. You are NOT a conversational assistant.

TASK OBJECTIVES:
1. Determine if the image depicts a valid handmade craft / DIY project.
2. Extract the high-level object category.
3. Extract a 1-line detailed description.
4. List visible primary materials.
5. Identify the specific crafting technique or process used.

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


# ------------------------------------------------------------------
# IMPORTANT:
# This must be a DIRECT IMAGE URL.
# ------------------------------------------------------------------

image_url = "https://i.pinimg.com/736x/c6/4c/69/c64c691788cde515da9b6b4b383ccbcf.jpg"

encoded_image = encode_image_to_base64(
    image_url
)

if encoded_image is None:
    raise ValueError(
        "Image encoding failed. "
        "Check the URL and content type."
    )


messages = [
    SystemMessage(content=system_prompt),

    HumanMessage(
        content=[
            {
                "type": "image_url",
                "image_url": {
                    "url": encoded_image
                }
            },
            {
                "type": "text",
                "text": (
                    "Analyze this image and extract "
                    "the craft information."
                    "ONLY ans ONLY output the required information, donot at all output your thinking process"
                )
            }
        ]
    )
]


image_description = structured_model.invoke(messages)

print("\nParsed Response:")
print(image_description)


class op_schema2(BaseModel) :
    search_query : str = Field(description="use the image description based on different fields & generate the youtube search query")

structured__model2 = model.with_structured_output(op_schema2)

system_prompt2 = f"""[SYSTEM DIRECTIVE: AUTOMATED SEARCH QUERY GENERATOR - ZERO CONVERSATION]

You are a specialized search query optimization engine for YouTube DIY and craft tutorials. Your sole purpose is to convert extracted craft metadata into a high-intent, highly accurate YouTube search string. You are NOT a conversational assistant.

INPUT CRAFT METADATA:
- Category: {image_description.object_category}
- Detailed Description: {image_description.detailed_description}
- Materials: {image_description.materials}
- Crafting Technique: {image_description.crafting_process}

QUERY CONSTRUCTION RULES:
1. KEYWORD PRIORITY METHOD: Combine [Crafting Technique] + [Specific Object/Design] + [Primary Material (if relevant)] + ["tutorial" or "DIY"].
2. KEEP IT CONCISE: Output a concise 3 to 8 word search phrase. Do NOT write full sentences or conversational queries.
3. STRIP FILLER WORDS: Exclude vague adjectives and non-searchable descriptors (e.g., "beautiful", "cute", "nice", "simple looking", "a photo of").
4. TARGET HIGH-INTENT TUTORIALS: Always append "tutorial" or "how to make" to trigger instructional video results.

STRICT OPERATIONAL CONSTRAINTS (ZERO-TOLERANCE):
- DO NOT output any introductory text or preambles (e.g., "Here is the query:", "Search for:").
- DO NOT output any quotation marks, explanations, or reasoning.
- DO NOT output conversational closing remarks or postscripts.
- OUTPUT ONLY the raw search query string.
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

response = structured__model2.invoke(messages)
print(response.search_query)