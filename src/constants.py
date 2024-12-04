BATCH_SIZE: int = 20
OUTPUT_FORMAT: list = ["markdown", "json"]
TARGET_LANGUAGES: dict = {
    "English": "en",
    "Arabic": "",
    "Chinese": "zh-CN",
    "Dutch": "",
    "French": "fr",
    "German": "",
    "Japanese": "",
    "Portuguese": "pt",
    "Russian": "",
    "Spanish": "es",
    "Thai": "",
    "Turkish": "",
}
SUPPORTS_AND_RESISTANCES: list = [
    "resistance40",
    "resistance250",
    "resistance500",
    "support40",
    "support250",
    "support500",
]
OSCILLATORS: list = ["bollinger", "cci", "kst", "macd", "momentum", "rsi", "williams"]
SMAS: list = ["sma4", "sma9", "sma21", "sma50", "sma200"]
JSON_RESPONSE_SCHEMA: dict = {
    "Options": {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "properties": {
            "title": {
                "type": "string",
            },
            "introduction": {
                "type": "string",
            },
            "explanation": {
                "type": "object",
                "properties": {
                    "volatility": {
                        "type": "string",
                    },
                    "skew": {
                        "type": "string",
                    },
                    "time structure": {
                        "type": "string",
                    },
                },
                "required": ["volatility", "skew", "time structure"],
            },
            "summary": {
                "type": "string",
            },
            "questions": {
                "type": "array",
            },
            "answers": {
                "type": "array",
            },
        },
        "required": [
            "title",
            "introduction",
            "explanation",
            "summary",
            "questions",
            "answers",
        ],
    },
    "Technicals": {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "properties": {
            "title": {
                "type": "string",
            },
            "introduction": {
                "type": "string",
            },
            "explanation": {
                "type": "object",
                "properties": {
                    "price": {
                        "type": "string",
                    },
                    "trend": {
                        "type": "string",
                    },
                    "momentum": {
                        "type": "string",
                    },
                    "pattern": {
                        "type": "string",
                    },
                },
                "required": ["price", "trend", "momentum", "pattern"],
            },
            "summary": {
                "type": "string",
            },
            "questions": {
                "type": "array",
            },
            "answers": {
                "type": "array",
            },
        },
        "required": [
            "title",
            "introduction",
            "explanation",
            "summary",
            "questions",
            "answers",
        ],
    },
}
