# TITLE: LLM Chatbot
# TITLE_VI: Chatbot LLM
# LEVEL: Advanced
# ICON: 💬
# COLOR: #f97316
# DESC: Build a chat AI that understands you. Explore NLP, prompt logic, and context.
# DESC_VI: Xây dựng AI trò chuyện hiểu bạn. Khám phá NLP, logic prompt và ngữ cảnh.
# ORDER: 3
# ============================================================


def simple_llm_logic(user_input: str) -> str:
    # Most LLMs translate input into lowercase for consistency!
    prompt = user_input.lower()
    
    # Simple rule-based logic to mimic AI responses 
    if "hello" in prompt or "hi" in prompt:
        return "Hi there! I'm your AI Education Lab bot. How can I help you learn AI today?"
    elif "who are you" in prompt:
        return ("I'm a simple Large Language Model wrapper designed for students "
                "to understand NLP (Natural Language Processing).")
    elif "what is ai" in prompt:
        return ("Artificial Intelligence (AI) is the ability for a computer "
                "to mimic human behavior, like learning and reasoning.")
    elif "thank you" in prompt:
        return "You're very welcome! Keep practicing your Python coding!"
    else:
        # Fallback for complex queries — explaining context understanding
        return (f"I see you said '{user_input}'. In a real LLM like Gemini or GPT, "
                "I would search billions of parameters to find the best response for this!")

def start_chatbot():
    print("AI Lab: Simple LLM Chatbot Started.")
    print("Type something to talk to me! (Type 'quit' to exit)")
    
    while True:
        user_input = input("You: ")
        if user_input.lower() == 'quit':
            print("AI Bot: Goodbye! Happy coding!")
            break
            
        bot_response = simple_llm_logic(user_input)
        print(f"AI Bot: {bot_response}")

if __name__ == "__main__":
    start_chatbot()
