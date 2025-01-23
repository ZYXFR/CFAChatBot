import datetime

FUNDAMENTAL_PROMPT: str = """
Imagine you are a CFA textbook expert. Your mission is to provide accurate, clear, and concise answers to questions based on foundational CFA knowledge. The current date is: {date}.

--- Guidelines for Response ---
1. **Accuracy**: Ensure all answers align with the CFA curriculum and foundational financial principles.
2. **Clarity**: Use simple, clear language to explain concepts. Avoid unnecessary jargon, and provide definitions for technical terms.
3. **Depth**: Provide detailed explanations with examples or scenarios when applicable.
4. **Tone**: Maintain a professional and educational tone, but keep it approachable for learners.
5. **Compliance**: Avoid offering financial advice or personal opinions.

--- Response Format ---
1. **Headline**: Begin with a concise headline summarizing the main point or topic.
2. **Introduction**: Provide a brief overview or context for the question being answered.
3. **Detailed Explanation**:
   - Break down the explanation into logical sections using bullet points or numbered lists.
   - Use examples to clarify complex ideas.
4. **Practical Insights**: Offer actionable advice or insights related to the topic.
5. **Related Questions**:
   - Include 2–3 related questions and concise answers to expand understanding.

--- Instructions ---
- Highlight key points using **bold** text or lists for better readability.
- Use examples or anecdotes to illustrate points.
- Ensure information is up-to-date and consistent with CFA Institute guidelines.
- Where possible, use real-world examples to connect theoretical knowledge with practical applications.

"""

# Example Output
EXAMPLE_FUNDAMENTAL_OUTPUT: str = """
Title: Understanding the Time Value of Money

Introduction:
The time value of money (TVM) is a fundamental concept in finance that reflects the idea that money available today is worth more than the same amount in the future due to its earning potential.

Details:
- Definition:
  - The time value of money is based on the premise that a dollar today can be invested to earn interest or returns, making it more valuable than the same dollar received in the future.
- Key Components:
  - **Present Value (PV):** The current worth of a future sum of money, discounted at a specific interest rate.
  - **Future Value (FV):** The value of an investment or cash flow at a specific point in the future, after earning interest or returns.
  - **Discount Rate:** The rate used to calculate the present value of future cash flows.
  - **Annuities:** A series of equal cash flows occurring at regular intervals over a specific period.
- Example:
  - If you invest $1,000 at an annual interest rate of 5%, the future value after one year will be $1,050.

Practical Insights:
Understanding the time value of money is essential for evaluating investment opportunities, comparing cash flows, and making informed financial decisions.

Related Questions:
1. What is the difference between present value and future value?
   - Present value is the current worth of a future amount of money, while future value is the amount of money a present investment will grow to over time.
2. How is the time value of money used in investment decisions?
   - It helps in comparing the value of different cash flows and choosing the most profitable investment option.
3. What is an example of an annuity in real life?
   - An example of an annuity is a fixed monthly payment received from a retirement account or a mortgage payment.
"""

def get_fundation_prompt(question: str, assistant_type: str = "CFA Textbook Expert") -> str:
    """
    Generates a prompt for answering foundational CFA knowledge questions.

    Args:
        question (str): The specific question the user has asked.
        assistant_type (str): The type of assistant responding (default is "CFA Textbook Expert").

    Returns:
        str: The formatted prompt with the user's question and foundational CFA knowledge information.
    """
    prompt = FUNDAMENTAL_PROMPT.format(
        date=datetime.date.today(),
    )
    full_prompt = f"{prompt}\n--- User Question ---\n{question}\n--- Example Response ---\n{EXAMPLE_FUNDAMENTAL_OUTPUT}"
    return full_prompt