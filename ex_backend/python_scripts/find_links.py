import sys
import json
import requests
from PIL import Image
from transformers import BlipProcessor, BlipForConditionalGeneration
from youtubesearchpython import VideosSearch

def extract_product_keyword(caption) :
    """
    A simple function to extract the main keyword from a caption.
    It removes common stop words to find the subject.
    """

    stop_words = [
        'a', 'an', 'the', 'in', 'on', 'at', 'of', 'for', 'to',
        'is', 'are', 'was', 'were', 'up', 'down', 'out', 'close', 'and', 'someone',
        'holding', 'hands', 'their', 'his', 'her', 'they', 'them', 'all', 'none'
    ]

    words = caption.lower().split()
    keywords = [word for word in words if word not in stop_words]

    #joining the remaining keywords back to string
    return ' '.join(keywords)

def get_image_caption(image_url) :
    """
    Takes an image URL, downloads the image, and uses a Hugging Face
    model to generate a descriptive caption.
    """
    try :
        processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-large")
        model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-large")
        
        # download the image from the URL
        raw_image = Image.open(requests.get(image_url, stream=True).raw).convert('RGB')

        # Process the image and generate a caption
        inputs = processor(raw_image, return_tensors="pt")
        out = model.generate(**inputs, max_new_tokens=50)
        caption = processor.decode(out[0], skip_special_tokens=True)

        return caption
    except Exception as e :
        # If anything goes wrong (e.g., model download fails, bad URL), return None
        print(f"Error generating caption: {e}", file=sys.stderr)
        return None
    
def search_youtube_links(keyword, querry, limit=4) :
    """
    Takes a search query, searches YouTube, and returns a list of
    tutorial videos with their titles and URLs.
    """
    try :
        # Refine the query to be more tutorial-focused
        search_querry = f"{keyword} tutorial for beginners"

        #perform the search & limit the number of results
        videos_search = VideosSearch(search_querry, limit=limit)
        results = videos_search.result()['result']

        #format the results into desired structure
        tutorials = []
        for video in results :
            tutorials.append({
                "title" : video['title'],
                "url" : video['link'],
                "product_name" : keyword,
            })
        return tutorials
    except Exception as e :
        print(f"Error searching Youtube: {e}", file=sys.stderr)
        return []

def main() :
    # The first command-line argument is the script name itself.
    # The image URL will be the second argument.

    if len(sys.argv) < 2 :
        error_message = {"error": "No image URL provided."}
        print(json.dumps(error_message), file=sys.stderr)
        return
    
    image_url = sys.argv[1]

    #step 1: Generate the captiom from the image
    caption = get_image_caption(image_url)
    keyword = extract_product_keyword(caption)

    if not caption :
        error_message = {"error": "Could not generate a caption for the image."}
        print(json.dumps(error_message), file=sys.stderr)
        return
    
    # stage 2 & 3: search youtube & get links
    tutorials = search_youtube_links(keyword,caption)

    #final output : create a JSON object and print it to stdout
    final_output = {"tutorials" : tutorials}
    print(json.dumps(final_output))

if __name__ == "__main__" :
    main()