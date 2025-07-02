import openai
from config.config import Config
import json

# configure openAI access 
openai.api_key = Config.OPENAI_API_KEY
client = openai.OpenAI()  # creating client instance 

# System prompt for lead confidence scoring
LEAD_QA_SYSTEM_PROMPT = """You are a data quality assistant. Your job is to evaluate the accuracy of enriched company data provided by ZoomInfo for a Salesforce Lead record. You are given both internal data (which we trust to varying degrees) and enriched data. Based on these, you will return a 0-100 confidence score and a short explanation of how reliable the enrichment is. You will also make corrections or educated guesses (inferences) if something is clearly wrong or missing. 

## 1 Here is the lead data you are receiving: 

| Field  | Description  | Source | Trust Level  | How to Use  |
| :---- | :---- | :---- | :---- | :---- |
| Email  | The lead's email address | Provided by the lead directly | Trusted | Use to infer company identity  |
| First_Channel__c | Channel lead came in through  | Internal System  | Trusted | Use as context to determine if lead data was populated |
| SegmentName | Which sales segment the lead belongs to | Specified by lead themselves or sales rep working with the lead | Trusted but potentially inaccurate | Use to compare against enriched data |
| LS_Company_Size_Range__c | Internal guess at company size range | Specified by lead themselves or sales rep working with lead | Trusted but potentially inaccurate | Use to compare against enriched data |
| Website  | The company's website | Specified by the lead themselves or a sales rep working with the lead  | Trusted but potentially inaccurate | Use to compare against ZI_Website__c and ZI_Company__c  |
| ZI_Website__c | The company's website | Enriched by ZoomInfo | To be validated | Compare the email_domain, Website, and  ZI_Company_Name__c for consistency  |
| ZI_Company_Name__c | Company name  | Enriched by ZoomInfo  | To be validated | Compare against email_domain, Website, and ZI_Website__c for consistency |
| ZI_Employees__c | Employee count | Enriched by ZoomInfo | To be validated  | Compare against SegmentName and LS_Company_Size_Range__c for consistency and use to assess whether company is "large"  |
| not_in_TAM | This lead is supposedly associated with a large company (>= 100 employees), but enrichment has not identified a company associated with the lead and is not found in RingCentral's TAM dataset. This suggests enrichment may be incomplete or mismatched.  | Quality flag computed internally  | Trusted | Negative Indicator |
| suspicious_enrichment | The lead has a company name and a reported employee count >= 100, but lacks a website and uses a personal (free) email domain. This raises concern about the authenticity of the enriched company match.  | Quality flag computed internally  | Trusted | Strong Negative Indicator |
| email_domain  | The lead's email domain | Computed internally  | Trusted | Use to compare against Website and ZI_Company_Name__c |

## 2 Validation– Is the Enrichment Believable? 

1. Run quick heuristics: 

| Heuristic  | PASS (✅)	 | CAUTION (⚠️)	 | FAIL (❌) |
| :---- | :---- | :---- | :---- |
| Email domain, website, and company are consistent | Corporate domain matches either Website or ZI_Website__c and both match ZI_Company_Name__c | Partial match  | Obvious mismatch or free email domain with enterprise claim  |
| Employee count sanity | ZI_Employees__c within claimed segment size (use SegmentName, LS_Company_Size_Range__c if present) | Minor discrepancy (+/- segment)  | Major discrepancy (>= 2 segments) |
| Large company completeness (ZI_Employees__c >= 100)  | Website and ZI_Company_Name__c is populated and email_domain is corporate | Some gaps in enrichment | Very sparsely populated enrichment |
| Quality flags (not_in_TAM and suspicious_enrichment) | Both are false   | One or more is true |  |

2. Use external sources (Clearbit, LinkedIn, Hunter.io MX lookup, OpenCorporates, etc.) to support your evaluation. If none is provided, reason heuristically from public knowledge patterns. 

## 3 Inference and Correction– Can anything be fixed?

1. Using the trusted fields (Email, email_domain, etc.) and external sources (Clearbit, LinkedIn, Hunter.io MX lookup, OpenCorporates), infer the company name, primary website, and employee range associated with the lead.     
2. CORRECTIONS (high confidence fixes for conflicting data):   
* Only add to `corrections` if a ZoomInfo field CONFLICTS with trusted internal data or external sources       
* URL Formatting Rule: Do NOT correct URL formatting differences for the SAME domain:  
  * ❌ "example.com" → "https://example.com" (same domain)  
  * ❌ "www.site.org/" → "site.org" (same domain)  
* DO make corrections for meaningful conflicts:  
  * ✅ Wrong company name: "Runway Post" → "Virtuoso DesignBuild" (based on email domain)  
  * ✅ Drastically different employee count based on external sources  
  *  ✅ Wrong website domain: "facebook.com" → "virtuosodesignbuild.com" (if supported by email/external data)  
3. INFERENCES (Fill in MISSING data with high confidence):      
* Only add to `inferences` for ZoomInfo fields that are NULL/empty AND you have >= 0.40 confidence      
* URL Formatting Rule: Do NOT infer URL variations of the SAME domain:  
  * ❌ If Website="example.com" exists, do NOT infer ZI_Website__c="https://example.com"  
* DO make inferences for different domains/missing data:  
  * ✅ If Website="facebook.com/pages/..." and email="user@company.com", infer ZI_Website__c="company.com"  
  *  ✅ If ZI_Company_Name__c is null and email="user@company.com", infer company name  
  *  ✅ If ZI_Employees__c is null and external sources suggest a number, infer it  
* Domain Extraction Check: Extract core domain (remove protocol/www/paths) and only avoid if core domains match  
* VALIDATION EXAMPLES:  
  * FORBIDDEN (same domain): Website="aoreed.com" → infer ZI_Website__c="https://aoreed.com"  
  * ALLOWED (different domain): Website="facebook.com/pages/Company" → infer ZI_Website__c="company.com"   
  * ALLOWED (missing data): ZI_Company_Name__c=null → infer "Company Name" from email domain  
  * ALLOWED (conflicting data): ZI_Company_Name__c="Wrong Name" → correct to "Right Name" from email  
4. Final Check: Ask "Is this the same core domain/company or genuinely different information?" Only avoid it if it's the same.

## 4 Scoring– How Trustworthy is this record overall? 

1. Rate each pillar 0-25 points, then sum for `confidence_score`.   
* Completeness: are key enrichment fields non-null?   
* Internal Logic: does the lead data cohere?   
* Flag severity: how damaging are `not_in_TAM` and `suspicious_enrichment`?  
* Clamp to 0-100.   
* No deterministic math is exposed to the user; use judgement. 

## 5 Explanation– 3-5 Bullets (Why did the lead data get that score?) 

* Each <= 25 words, plain English, emoji cue:   
  * ✅ positive: strengthens or fixes data   
  * ⚠️ caution: creates a moderate double or needs follow up   
  * ❌ issue: severe mismatch, drives score down   
* State the logical reason, not the math.   
  * Here's are example bullets:   
    * "❌  Large firm (250 employees) missing from TAM lowers trust."    
    * "⚠️  Gmail address + no website raises authenticity doubts."    
    * "✅  LinkedIn shows 230 employees—matches enrichment."    
    * "⚠️  Website inferred from email but returned 404 on ping."  
    * "✅ ZI_Website__c and ZI_Company_Name__c both align with email domain — strong brand match."  
    * "✅ ZI_Employees__c consistent with SOHO segment ceiling; no size-range conflict."  
    * "⚠️ Website field blank; inferred primary site from ZoomInfo enrichment."  
    * "⚠️ Large-company completeness check: employee count present but website missing."  
* If a correction/ inference was made, mention it in a bullet.   
* CRITICAL REQUIREMENT: if confidence_score < 100, you MUST include at least one ⚠️caution or ❌bullet explaining why 

## 6 Output– Return ONLY this strict JSON 

{    
  "confidence_score": "<int 0-100>",    
  "explanation_bullets": ["<bullet1>", "<bullet2>", "..."],    
  "corrections": {  
    "<field_name>": "<corrected_value>"  
  },    
  "inferences": {  
    "<field_name>": "<inferred_value>"  
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

def validate_and_clean_assessment(assessment, lead_data):
    """
    Remove redundant corrections and inferences that are just URL formatting differences or cross-field duplicates
    """
    def extract_core_domain(url):
        """Extract core domain from URL, removing protocol, www, paths, etc."""
        if not url:
            return None
        
        # Convert to string and clean
        url = str(url).strip().lower()
        
        # Handle edge cases
        if url in ['null', 'none', 'n/a', '']:
            return None
        
        # Remove protocols
        url = url.replace('https://', '').replace('http://', '')
        
        # Remove www prefix
        if url.startswith('www.'):
            url = url[4:]
        
        # Remove trailing slash and paths
        url = url.split('/')[0]
        
        # Remove trailing dots
        url = url.rstrip('.')
        
        return url if url else None
    
    def are_same_domain(url1, url2):
        """Check if two URLs represent the same domain"""
        domain1 = extract_core_domain(url1)
        domain2 = extract_core_domain(url2)
        return domain1 and domain2 and domain1 == domain2
    
    def normalize_url_for_comparison(url):
        """Normalize URL for exact string comparison (handles case, whitespace)"""
        if not url:
            return None
        return str(url).strip().lower()
    
    # Get existing website values from lead data
    existing_websites = {
        'Website': lead_data.get('Website'),
        'ZI_Website__c': lead_data.get('ZI_Website__c')
    }
    
    # Clean corrections
    cleaned_corrections = {}
    for field, value in assessment.get('corrections', {}).items():
        should_keep = True
        
        if field in ['Website', 'ZI_Website__c']:
            # Check if this correction is just a formatting change of the same field
            existing_value = existing_websites.get(field)
            if existing_value and are_same_domain(existing_value, value):
                should_keep = False
                print(f"🧹 Removed redundant correction: {field} '{existing_value}' -> '{value}' (same domain)")
            
            # Check for exact string matches (case-insensitive)
            if should_keep and existing_value:
                if normalize_url_for_comparison(existing_value) == normalize_url_for_comparison(value):
                    should_keep = False
                    print(f"🧹 Removed redundant correction: {field} '{existing_value}' -> '{value}' (exact match)")
            
            # Also check if this correction matches any other website field (cross-field redundancy)
            if should_keep:
                for other_field, other_value in existing_websites.items():
                    if other_field != field and other_value:
                        # Check domain match
                        if are_same_domain(other_value, value):
                            should_keep = False
                            print(f"🧹 Removed redundant correction: {field} '{value}' (same domain as {other_field}: '{other_value}')")
                            break
                        # Check exact string match
                        if normalize_url_for_comparison(other_value) == normalize_url_for_comparison(value):
                            should_keep = False
                            print(f"🧹 Removed redundant correction: {field} '{value}' (exact match with {other_field}: '{other_value}')")
                            break
        
        if should_keep:
            cleaned_corrections[field] = value
    
    # Clean inferences
    cleaned_inferences = {}
    for field, value in assessment.get('inferences', {}).items():
        should_keep = True
        
        # First check if this inference is identical to a correction (cross-redundancy)
        if field in cleaned_corrections:
            correction_value = cleaned_corrections[field]
            if str(value).strip() == str(correction_value).strip():
                should_keep = False
                print(f"🧹 Removed redundant inference: {field} '{value}' (identical to correction)")
        
        if should_keep and field in ['Website', 'ZI_Website__c']:
            # Check if any existing website field has the same domain or exact match
            for existing_field, existing_value in existing_websites.items():
                if existing_value:
                    # Check domain match
                    if are_same_domain(existing_value, value):
                        should_keep = False
                        print(f"🧹 Removed redundant inference: {field} '{value}' (same domain as {existing_field}: '{existing_value}')")
                        break
                    # Check exact string match
                    if normalize_url_for_comparison(existing_value) == normalize_url_for_comparison(value):
                        should_keep = False
                        print(f"🧹 Removed redundant inference: {field} '{value}' (exact match with {existing_field}: '{existing_value}')")
                        break
        
        # For non-website fields, also check for exact string matches with corrections
        if should_keep and field not in ['Website', 'ZI_Website__c']:
            if field in cleaned_corrections:
                correction_value = cleaned_corrections[field]
                if str(value).strip() == str(correction_value).strip():
                    should_keep = False
                    print(f"🧹 Removed redundant inference: {field} '{value}' (identical to correction)")
        
        if should_keep:
            cleaned_inferences[field] = value
    
    # Update assessment
    assessment['corrections'] = cleaned_corrections
    assessment['inferences'] = cleaned_inferences
    
    return assessment

def generate_lead_confidence_assessment(lead_data):
    """Generate confidence assessment for lead data using OpenAI"""
    try:
        # Format the lead data for the prompt
        user_prompt = f"""Please analyze this lead data and provide a confidence assessment:

Lead Data:
- Id: {lead_data.get('Id', 'N/A')}
- Email: {lead_data.get('Email', 'null')}
- First_Channel__c: {lead_data.get('First_Channel__c', 'null')}
- SegmentName: {lead_data.get('SegmentName', 'null')}
- LS_Company_Size_Range__c: {lead_data.get('LS_Company_Size_Range__c', 'null')}
- Website: {lead_data.get('Website', 'null')}
- ZI_Website__c: {lead_data.get('ZI_Website__c', 'null')}
- ZI_Company_Name__c: {lead_data.get('ZI_Company_Name__c', 'null')}
- ZI_Employees__c: {lead_data.get('ZI_Employees__c', 'null')}
- not_in_TAM: {lead_data.get('not_in_TAM', False)}
- suspicious_enrichment: {lead_data.get('suspicious_enrichment', False)}
- email_domain: {lead_data.get('email_domain', 'null')}

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
        
        response_content = completion.choices[0].message.content
        if response_content is None:
            response_content = ""
        else:
            response_content = response_content.strip()
        
        # Try to parse the JSON response
        try:
            assessment = json.loads(response_content)
            
            # 🧹 VALIDATE AND CLEAN the assessment to remove redundant URL corrections/inferences
            assessment = validate_and_clean_assessment(assessment, lead_data)
            
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