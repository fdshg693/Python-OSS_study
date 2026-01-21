from openai import OpenAI
import base64

client = OpenAI() 

response = client.responses.create(
    model="gpt-4.1-mini",
    input="Generate an image of gray cat",
    tools=[{"type": "image_generation"}],
)


# Save the image to a file
image_data = [
    output.result
    for output in response.output
    if output.type == "image_generation_call"
]

if image_data:
    image_base64 = image_data[0]
    assert isinstance(image_base64, str)
    with open("gray_cat.png", "wb") as f:
        f.write(base64.b64decode(image_base64))