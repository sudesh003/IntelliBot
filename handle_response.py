# # LLM - llma2 
# from langchain.prompts import PromptTemplate
# from langchain_community.llms import CTransformers

# llm=CTransformers(model='models/llama-2-7b-chat.ggmlv3.q2_K.bin',
#                       model_type='llama',
#                       config={'max_new_tokens':250,
#                               'temperature':0.01})

# def getLLamaResponse(question):
#     formatted_prompt = f"{question} ?"
#     response = llm.invoke(formatted_prompt)
#     # print(response)
#     return response

# # Example usage
# # getLLamaResponse(str, 50)


import requests

API_URL = "https://api-inference.huggingface.co/models/meta-llama/Meta-Llama-3-8B-Instruct"
headers = {"Authorization": "Bearer "}



def query(payload):
	response = requests.post(API_URL, headers=headers, json=payload)
	return response.json()

def getLLMA3Response(question):

    output = query({
        "inputs":question,
        "parameters": {
            "temperature": 0.2,
        }
    })

    return output[0]['generated_text']



# print(getLLMA3Response("Hi"))