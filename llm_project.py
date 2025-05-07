import json
import random
from openai import OpenAI

# Connect with local host (LM Studio)
client = OpenAI(
    base_url="http://localhost:1234/v1",
    api_key="lm-studio"
)
# LLM model of choice
model = "llama-3.2-3b-instruct"


def generate_receipt(order_id: str):
    """
    Generate a random receipt:
      • Picks 1–10 items
      • Assigns each a random price between $1.00 and $100.00
    Returns a dict with order_id, num_items, and the items list.
    (No total_price!)
    """
    num_items = random.randint(1, 10)
    items = []
    for i in range(num_items):
        price = round(random.uniform(1.0, 100.0), 2)
        items.append({
            "name": f"item_{i+1}",
            "price": price
        })

    receipt = {
        "order_id": order_id,
        "num_items": num_items,
        "items": items
    }

    # debug print
    print(f"\ngenerate_receipt returns:\n\n{json.dumps(receipt, indent=2)}", flush=True)
    return receipt


# Expose it as a tool to the model
tools = [
    {
        "type": "function",
        "function": {
            "name": "generate_receipt",
            "description": (
                "Generate a random receipt for the given order_id. "
                "Returns the number of items and a list of {name, price}—"
                "the model must sum the prices to compute the final total."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "order_id": {
                        "type": "string",
                        "description": "The order ID to generate a receipt for."
                    }
                },
                "required": ["order_id"],
                "additionalProperties": False
            }
        }
    }
]

# Instruct the LLM to calculate the total on its own (these are the prompts that are fed to the LLM)
messages = [
    {
        "role": "system",
        "content": (
            "When you call the receipt tool it will return item names and prices—"
            "you must sum those prices yourself and report back the total."
        )
    },
    {
        "role": "user",
        "content": "Please give me a receipt for order number 1017."
    },
]

# Ask model which tool to use
response = client.chat.completions.create(
    model=model,
    messages=messages,
    tools=tools,
)

# Extract tool call and its arguments
tool_call = response.choices[0].message.tool_calls[0]
args = json.loads(tool_call.function.arguments)
order_id = args["order_id"]

# Run your local function
receipt = generate_receipt(order_id)

# Package the tool-call acknowledgment
assistant_tool_call = {
    "role": "assistant",
    "tool_calls": [
        {
            "id": tool_call.id,
            "type": tool_call.type,
            "function": tool_call.function
        }
    ]
}

# Send back the tool’s result
function_result_message = {
    "role": "tool",
    "content": json.dumps(receipt),
    "tool_call_id": tool_call.id
}

# Finally—let the LLM compute the total itself
final_response = client.chat.completions.create(
    model=model,
    messages=[
        messages[0],
        messages[1],
        assistant_tool_call,
        function_result_message
    ],
)

print("\nFinal model response:\n")
print(final_response.choices[0].message.content, flush=True)

