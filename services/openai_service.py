import openai
from config.config import Config

# configure openAI access 
openai.api_key = Config.OPENAI_API_KEY
client = openai.OpenAI()  # creating client instance 

def test_openai_connection():
    """Test OpenAI connection by listing available models"""
    try:
        models = client.models.list()
        model_list = list(models)
        return True, f"OpenAI connection successful - {len(model_list)} models available"
    except Exception as e:
        return False, f"OpenAI connection failed: {str(e)}"

def test_openai_completion(prompt="Hello! Please respond with 'OpenAI connection test successful.'"):
    """Test OpenAI completion generation"""
    try:
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            temperature=0,
            messages=[
                {"role": "user", "content": prompt}
            ],
            max_tokens=100
        )
        return completion.choices[0].message.content, "Completion generated successfully"
    except Exception as e:
        return None, f"Error generating completion: {str(e)}"

def ask_openai(openai_client, system_prompt, user_prompt):
    """calls openai"""
    try:
        completion = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            temperature=0,
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": user_prompt
                }
            ]
        )
        return completion.choices[0].message.content
    # debugging
    except Exception as openai_error:
        return f"Unexpected error: {openai_error}"

def get_openai_config():
    """Get current OpenAI configuration"""
    return {
        "model": "gpt-3.5-turbo",
        "max_tokens": Config.OPENAI_MAX_TOKENS,
        "api_key_configured": bool(Config.OPENAI_API_KEY)
    }