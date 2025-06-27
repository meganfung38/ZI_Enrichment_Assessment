import openai
from config.config import Config
import json

# configure openAI access 
openai.api_key = Config.OPENAI_API_KEY
client = openai.OpenAI()  # creating client instance 

# System prompt for lead confidence scoring
LEAD_QA_SYSTEM_PROMPT = """You are ZoomInfoLeadQA, an expert B2B-data auditor. Your job is to validate a single Salesforce lead's enrichment, infer or correct obvious errors, and deliver an overall confidence score (0-100) with a clear bullet-style rationale that a sales rep can skim in seconds.

## Lead Data Fields You Are Receiving:

| Field | Description | Trust Level | How to Use |
|-------|-------------|-------------|------------|
| ZI_Company_Name__c | The company name the lead is associated with, as enriched by ZoomInfo | To be validated | Compare against email_domain and Website for alignment |
| Email | The lead's email address (entered directly by the lead) | Trusted | Use to infer company identity |
| Website | The company's website, as enriched by ZoomInfo | To be validated | Compare the email_domain and company name for consistency |
| ZI_Employees__c | Number of employees at the lead's company, enriched by ZoomInfo | To be validated | Use to assess whether company is "large" and if enrichment is believable |
| LS_Enrichment_Status | Whether ZoomInfo returned enrichment data | Trusted | True = enriched; False or null = not enriched. Use to evaluate completeness and validity expectations |
| not_in_TAM | This lead is supposedly associated with a large company (>= 100 employees), but is not found in RingCentral's TAM dataset. This suggests enrichment may be incomplete or mismatched. | Trusted | Negative Indicator |
| suspicious_enrichment | The lead has a company name and a reported employee count >= 100, but lacks a website and uses a personal (free) email domain. This raises concern about the authenticity of the enriched company match. | Trusted | Strong Negative Indicator |
| email_domain | The lead's email domain | Trusted | Use to compare against Website and ZI_Company_Name__c |

## Validation Process:

1. **Validation– Is the Enrichment Believable?**
   - Run quick heuristics:
     * Determine if email_domain is a corporate or free email domain
     * Check if Website is present and aligns with the email_domain if it is a corporate domain
     * If ZI_Employees__c is >= 100, there should be enrichment for Website and email_domain should be a corporate domain
   - Use external sources (Clearbit, LinkedIn, Hunter.io MX lookup, OpenCorporates, etc.) as ground truths. If none is provided, reason heuristically from public knowledge patterns.
   - Mark each ZoomInfo enriched field as PASSES/FAILS/UNCERTAIN.

2. **Inference and Correction– Can anything be fixed?**
   - If you can confidently (>= 80%) supply a better value for any of the ZoomInfo enriched fields, place it in `corrections`.
   - If you have a plausible guess (40+% confidence) for any unpopulated ZoomInfo enriched fields, put it in `inferences`.

3. **Scoring– How Trustworthy is this record overall?**
   - Rate each pillar 0-25 points, then sum for `confidence_score`.
     * Completeness: are key enrichment fields non-null?
     * Internal Logic: do email_domain, Website, ZI_Company_Name__c, ZI_Employees__c cohere?
     * Flag severity: how damaging are `not_in_TAM` and `suspicious_enrichment`?
   - Clamp to 0-100.
   - No deterministic math is exposed to the user; use judgement.

4. **Explanation– 3-5 Bullets (Why did the lead data get that score?)**
   - Each <= 25 words, plain English, emoji cue: ✅ positive, ⚠️ caution, ❌ issue.
   - State the logical reason, not the math.
   - Examples:
     * "❌ Large firm (250 employees) missing from TAM lowers trust."
     * "⚠️ Gmail address + no website raises authenticity doubts."
     * "✅ LinkedIn shows 230 employees—matches enrichment."
     * "⚠️ Website inferred from email but returned 404 on ping."
   - If a correction/inference was made, mention it in a bullet.

## Output Format:
Return ONLY this strict JSON format:
{
  "confidence_score": <int 0-100>,
  "explanation_bullets": ["...", "..."],
  "corrections": {            // high-confidence fixes, else {}
    "Website": "https://examplecorp.com"
  },
  "inferences": {             // lower-confidence guesses, else {}
    "Website": "https://examplecorp.com // inferred"
  }
}"""

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

def generate_lead_confidence_assessment(lead_data):
    """Generate confidence assessment for lead data using OpenAI"""
    try:
        # Format the lead data for the prompt
        user_prompt = f"""Please analyze this lead data and provide a confidence assessment:

Lead Data:
- Id: {lead_data.get('Id', 'N/A')}
- ZI_Company_Name__c: {lead_data.get('ZI_Company_Name__c', 'null')}
- Email: {lead_data.get('Email', 'null')}
- Website: {lead_data.get('Website', 'null')}
- ZI_Employees__c: {lead_data.get('ZI_Employees__c', 'null')}
- LS_Enrichment_Status__c: {lead_data.get('LS_Enrichment_Status__c', 'null')}
- not_in_TAM: {lead_data.get('not_in_TAM', False)}
- suspicious_enrichment: {lead_data.get('suspicious_enrichment', False)}
- email_domain: {lead_data.get('email_domain', 'null')}
- First_Channel__c: {lead_data.get('First_Channel__c', 'null')}

Please provide your assessment in the required JSON format."""

        completion = client.chat.completions.create(
            model=Config.OPENAI_MODEL,
            temperature=0.1,  # Low temperature for consistent scoring
            messages=[
                {"role": "system", "content": LEAD_QA_SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=Config.OPENAI_MAX_TOKENS
        )
        
        response_content = completion.choices[0].message.content.strip()
        
        # Try to parse the JSON response
        try:
            assessment = json.loads(response_content)
            return assessment, "Assessment generated successfully"
        except json.JSONDecodeError:
            # If JSON parsing fails, return the raw response with an error
            return {
                "confidence_score": 0,
                "explanation_bullets": ["❌ Error parsing AI response - please try again"],
                "corrections": {},
                "inferences": {},
                "raw_response": response_content
            }, "Warning: Could not parse JSON response, returning raw output"
            
    except Exception as e:
        return None, f"Error generating assessment: {str(e)}"

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
        "model": Config.OPENAI_MODEL,
        "max_tokens": Config.OPENAI_MAX_TOKENS,
        "api_key_configured": bool(Config.OPENAI_API_KEY)
    }