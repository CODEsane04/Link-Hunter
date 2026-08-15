import os
import json
import re
import csv
import requests
from pydantic import BaseModel, Field
from typing import List
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv

load_dotenv()

BACKEND_URL = "http://localhost:8000/get_links"
CSV_FILENAME = "eval_dataset_LH.csv"

class SingleEvaluation(BaseModel):
    is_relevant: bool = Field(description="True if the video title is a tutorial for making the exact expected object. False otherwise.")
    reasoning: str = Field(description="A 1-sentence explanation of why it is relevant or irrelevant.")

class BatchEvaluation(BaseModel):
    evaluations: List[SingleEvaluation] = Field(description="A list containing exactly the same number of evaluations as the provided titles, strictly maintaining the original order.")

judge_model = ChatGoogleGenerativeAI(
    model="gemma-4-31b-it", 
    temperature=0.0
)
structured_judge = judge_model.with_structured_output(BatchEvaluation, include_raw=True)

judge_prompt_template = """
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

def evaluate_titles_batch(expected_subject: str, titles: list) -> list:
    if not titles:
        return []

    titles_formatted = "\n".join([f"{i+1}. {t}" for i, t in enumerate(titles)])
    
    prompt = PromptTemplate.from_template(judge_prompt_template).format(
        expected_subject=expected_subject,
        video_titles_list=titles_formatted,
        num_titles=len(titles)
    )
    
    try:
        eval_result = structured_judge.invoke(prompt)
        
        if eval_result.get("parsed") is not None:
            batch_decision = eval_result["parsed"]
            decisions = [{"is_relevant": e.is_relevant, "reasoning": e.reasoning} for e in batch_decision.evaluations]
        else:
            raw_content = eval_result["raw"].content
            
            if isinstance(raw_content, list):
                text_parts = [part["text"] if isinstance(part, dict) else str(part) for part in raw_content]
                raw_text = "".join(text_parts)
            else:
                raw_text = str(raw_content)

            match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', raw_text, re.DOTALL)
            if not match:
                match = re.search(r'(\{.*\})', raw_text, re.DOTALL)
                
            if match:
                parsed_dict = json.loads(match.group(1))
                batch_decision = BatchEvaluation(**parsed_dict)
                decisions = [{"is_relevant": e.is_relevant, "reasoning": e.reasoning} for e in batch_decision.evaluations]
            else:
                raise ValueError("No JSON found in Judge output.")
                
        if len(decisions) != len(titles):
            print(f"⚠️ Judge Length Mismatch: Expected {len(titles)}, Got {len(decisions)}")
            while len(decisions) < len(titles):
                decisions.append({"is_relevant": False, "reasoning": "Judge failed to evaluate this item."})
                
        return decisions[:len(titles)]

    except Exception as e:
        print(f"⚠️ Gemma Judge Exception: {e}")
        return [{"is_relevant": False, "reasoning": "Failed to parse judge output."} for _ in titles]

def run_evaluation_pipeline():
    total_images = 0
    correct_routings = 0
    precision_scores = []
    
    if not os.path.exists(CSV_FILENAME):
        print(f"❌ Error: Could not find '{CSV_FILENAME}' in the current directory.")
        return

    print(f"🚀 Starting Evaluation Pipeline using {CSV_FILENAME}")
    print("🤖 Judge Model: gemma-4-31b-it")
    
    with open(CSV_FILENAME, mode='r', encoding='utf-8') as file:
        csv_reader = csv.DictReader(file)
        
        for row in csv_reader:
            image_url = row.get("image_url")
            expected_subject = row.get("expected description", "")
            
            expected_valid_str = row.get("is_valid", "TRUE").strip().upper()
            expected_is_valid = (expected_valid_str == "TRUE")
            
            print(f"\n{'-'*60}")
            print(f"🧪 TESTING: {expected_subject if expected_subject else 'Non-DIY Image'}")
            print(f"{'-'*60}")
            
            try:
                payload = {"image_url": image_url}
                response = requests.post(BACKEND_URL, json=payload)
                
                if response.status_code == 422:
                    print(f"❌ 422 Validation Error: {response.text}")
                    continue
                    
                response.raise_for_status()
                backend_data = response.json()
            except Exception as e:
                print(f"❌ Backend Request Failed: {e}")
                continue
                
            total_images += 1
            
            actual_is_valid = backend_data.get("is_valid", False)
            if actual_is_valid == expected_is_valid:
                correct_routings += 1
                print(f"✅ Metric 1: Routing Correct (is_valid = {actual_is_valid})")
            else:
                print(f"❌ Metric 1: Routing Failed (Expected {expected_is_valid}, Got {actual_is_valid})")
                
            if expected_is_valid and actual_is_valid:
                generated_query = backend_data.get("search_query", "None generated")
                print(f"\n🔎 Backend Search Query: '{generated_query}'")
                
                retrieved_links = backend_data.get("final_list", [])[:5]
                total_retrieved = len(retrieved_links)
                
                if total_retrieved > 0:
                    print("\n🔍 Judge Evaluating Top 5 Links (Batched):")
                    
                    titles_to_judge = [video.get("title", "") for video in retrieved_links]
                    decisions = evaluate_titles_batch(expected_subject, titles_to_judge)
                    
                    relevant_count = 0
                    
                    for idx, (title, decision) in enumerate(zip(titles_to_judge, decisions), 1):
                        is_relevant = decision.get("is_relevant", False)
                        reasoning = decision.get("reasoning", "No reasoning provided.")
                        
                        status_icon = "🟢" if is_relevant else "🔴"
                        print(f"  {idx}. {status_icon} | {title}")
                        print(f"       {reasoning}")
                        
                        if is_relevant:
                            relevant_count += 1
                            
                    p_at_5 = relevant_count / total_retrieved
                    precision_scores.append(p_at_5)
                    print(f"\n🎯 Metric 2: Precision@5 = {p_at_5:.2f} ({relevant_count}/{total_retrieved})")
                else:
                    print("\n⚠️ Metric 2: No links retrieved by backend.")

    if total_images == 0:
        print("\nNo valid rows processed.")
        return

    final_routing_accuracy = (correct_routings / total_images) * 100
    final_precision = sum(precision_scores) / len(precision_scores) if precision_scores else 0.0

    print(f"\n{'='*60}")
    print("📈 FINAL SYSTEM METRICS")
    print(f"{'='*60}")
    print(f"Total Test Cases Run: {total_images}")
    print(f"Routing Accuracy:     {final_routing_accuracy:.1f}%")
    print(f"Average Precision@5:  {final_precision:.2f}")

if __name__ == "__main__":
    run_evaluation_pipeline()