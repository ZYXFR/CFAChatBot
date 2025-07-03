from .general_prompt import get_general_prompt
from .fundamental_prompt import get_fundation_prompt
from .cfa_events_prompt import get_cfa_events_prompt




# Define a dictionary of Prompts
PROMPTS = {
    "General Questions": get_general_prompt,
    "Foundation Questions": get_fundation_prompt,
    "CFA France Events": get_cfa_events_prompt,
}

# Function to generate translation prompt
