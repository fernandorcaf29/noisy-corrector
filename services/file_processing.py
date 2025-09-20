import json


def read_txt_paragraphs(filepath):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
    except UnicodeDecodeError:
        with open(filepath, "r", encoding="latin-1") as f:
            content = f.read()

    paragraphs = [p.strip() for p in content.split("\n\n") if p.strip()]

    return paragraphs


def read_json_and_extract_text(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, list):
        raise ValueError("JSON data should be an array of objects")

    return " ".join(item["text"] for item in data if "text" in item)
