tags = ["python", "coding", "example de caca"]
caption = ""

if tags: # Assuming 'tags' is a list of strings
    formatted_tags = " ".join([f"#{tag.strip().replace(' ', '_')}" for tag in tags if tag.strip()])
    if caption:
        caption += f" {formatted_tags}"
    else:
        caption = formatted_tags

print(caption)
