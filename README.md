# Local Server Using LLM API (compatible with OpenAI's functions)

A Python script that utilizes LM Studio as a local server that implements a tool-driven workflow with an LLM:  
- The local function `generate_receipt(order_id)` produces a random list of items, each with a randomly assigned price.  
- **The LLM is tasked with summing the item prices itself** to compute the final total.  
- **Tool registration**: Exposes `generate_receipt` to the LLM via the OpenAI-compatible API.  
- **Model responsibility**: The model receives only item names and prices; it must calculate and report the total.  

