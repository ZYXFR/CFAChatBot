def get_translation_prompt(
    json_string: str, target_language: str, analyzer_type: str
) -> str:
    prompt: str = ""
    if analyzer_type == "Options":
        prompt = (
            f"Given the JSON content below, translate it to the {target_language}. "
            "Keep technical terms like 'volatility', 'bias' in English. "
            "Don't translate the keys names ('title', 'introduction','explanation',"
            "'volatility','bias','skew','time structure','summary','questions','answers')."
            "Don't add any additional sentence."
            f"JSON content:\n{json_string}"
        )
    elif analyzer_type == "Technicals":
        prompt = (
            f"Given the json content below, translate it to the {target_language}. "
            "The json content is about financial information and its translation "
            f"to {target_language} should use corresponding financial expression. "
            "Keep momentum, oscillators, classic and candlestick pattern names in English. "
            "Don't translate the keys names ('title', 'introduction','explanation',"
            "'price','trend','momentum','pattern','summary','questions','answers')."
            "Don't add any additional sentence."
            f"JSON content:\n{json_string}"
        )
    return prompt


def get_markdown_prompt(json_string: str) -> str:
    return (
        "Convert the JSON content to markdown in beautiful format "
        "and replace HTML tags by their corresponding in mardown."
        "Don't add any additional sentence."
        "Questions and answers should be grouped: question 1 with answer 1,"
        "question 2 with answer 2, etc."
        f"JSON content:\n{json_string}"
    )
