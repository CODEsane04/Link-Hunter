from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv

load_dotenv()

model = ChatGoogleGenerativeAI (
    model="gemma-4-31b-it",
    temperature=0.0
)
parser = StrOutputParser()

chian = model | parser

respone = chian.invoke("of given an output schema in oydantic, can you give stuctured output too, ONLY ansd ONLY reply with the answer to the question, DONOT at all output your thinnking process or the thinking chat that you do with yourself, strictly adhere to guidelines & only output a very clean reaponse to the asked question?")
print(respone)

