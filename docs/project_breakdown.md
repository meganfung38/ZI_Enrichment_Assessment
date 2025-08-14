## **Project 1– ZoomInfo Quality Assessment**

### **What is ZoomInfo?** 

* B2B data provider. They collect and maintain a large database of:   
  * Companies   
  * Contacts  
  * Technographic data (what tools a company uses)   
  * Buying intent signals   
  * Etc.  
* Used by sales, marketing, and recruiting teams to support:   
  * Outreach \+ targeting   
  * Personalization of messaging   
  * Lead prioritization  
* Streamlines data enrichment– process of taking a basic record (company name or email) → supplementing it with detailed information to make it more useful; ultimately helping sales reps reach the right people with the right context 

### **Problem Statement**

* The RC Marketing and Sales Department is uncertain about the reliability/ accuracy of data   
* Outdated, incomplete, incorrect information → low quality records potentially leading sales reps to waste time or make poor outreach decisions 

### **Solution**

* Conduct a quality assessment of ZoomInfo’s output by developing an AI driven confidence rating system for enriched records– paired with explanations to ensure transparency and actionability   
* Steps:    
1. Collect ZoomInfo-Enriched Records  
* Columns to query: 

| SFDC Column | Query ID  |
| :---- | :---- |
| *Demand Funnel : Lead : Lead ID* | Id |
| *Demand Funnel : Lead : Email (input information for enrichment)*  | Email |
| *RTLM Channel* | FIrst\_Channel\_\_c  |
| *Segment Name* | SegmentName\_\_r.Name |
| *Demand Funnel : Lead : Website*  | Website |
| *Demand Funnel : Lead : Company* | Company  |
| *Demand Funnel : Lead : No. of Employees*  | LS\_Company\_Size\_Range\_\_c |
| *Demand Funnel : Lead : ZI Website (enriched)* | ZI\_Website\_\_c |
| *Demand Funnel : Lead : Account Name (enriched)*  | ZI\_Company\_Name\_\_c |
| *Demand Funnel : Lead : ZI Employees (enriched)*  | ZI\_Employees\_\_c |

* Flags to look out for: 

| Flags | Meaning  |
| :---- | :---- |
| not\_in\_TAM ZI\_Employees\_\_c \> 100 but ZI\_Company\_Name\_\_c NOT Populated | Accounts in the RC TAM (total addressable market) base include all accounts with 100+ employees This account should be enriched with an account name or is being incorrectly enriched for employee number |
| suspicious\_enrichment Email has free email domain and Website NOT POPULATED and ZI\_Company\_Name\_\_c POPULATED and ZI\_Employees\_\_c \> 100 | Why are accounts with ambiguous email domains and no websites being enriched with an Account name (company) and other ZI data?  |

2. Verify Data Accuracy \+ Information Discovery    
* Inspect Website and ZI\_Employees\_\_c  
  * Try to populate ZI\_Company\_Name\_\_c for RC TAM base  
* Inspect Email  
  * If there is additional information (company name) in email domain → use to infer Website and ZI\_Company\_Name\_\_c  
  * Try to populate other fields using inferred information   
* Cross check each record with sources  
  * Public databases (LinkedIn, etc.), internal CRM or sales data  
  * Does the Email match the enriched data? 

    

3. Build a Confidence Model   
* Design either a rule based system, ML model, or prompt to LLM to:   
  * Assess freshness of data  
  * Compared against other trusted sources   
  * Evaluate internal consistency   
  * Incorporate outcome history, if applicable  
* Output a confidence score (%) for each record or data point   
4. Explainability   
* Provide clear and concise explanations for why a particular confidence level was assigned  
* Explanation layer should help build trust in the system and enable sales or operation teams to take actions accordingly  
* A correction for incorrect fields

### **Enhancing Current System**

* Use Joseph’s rule based system as a layer of intelligence in the process of assessing lead enrichment  
* Comparison between systems: 

|  | Joseph’s System  | Megan’s System  |
| :---- | :---- | :---- |
| **Approach**  | Deterministic scoring using predefined rules and fuzzy matching  | Contextual analysis using AI with external validation (world knowledge)  |
| **Components**  | 3 weighted pillars:  Acquisition 20% Enrichment 20%  Coherence 60% | Holistic assessment with explanation \+ corrections+ inferences |
| **Scoring** | Math heavy– uses conditionals and weighted averages  | LLM judgement \+ uses business reasoning  |
| **Validation** | Pattern matching, domain lists, phone regex, fuzzy string similarity  | External world knowledge \+ heuristic analysis |
| **Consistency**  | 100% reproducible results– only uses rule based logic so scoring should mathematically be consistent everytime | Somewhat consistent– 0.1 temperature for more deterministic analysis but does not guarantee 100% consistency across scores |


* Options: 

| Option  | Combined Approach  | Benefits |
| :---- | :---- | :---- |
| Weighted Hybrid Scoring | Run both systems and retrieve scores  Apply weighted combination– Joseph’s system 40% \+ Megan’s system 60%  Re-compute explanation to draw a conclusion for the combined scoring \*\*save logs \+ explanations for both scores computed independently and combine reasoning in last step | Combines rule based consistency with AI contextual intelligence  Bridges gaps each system misses alone  Balances mathematical rules \+ business reasoning  Joseph’s system grounds/ prevents AI hallucinations  Adjustable– can adjust weights based on validation data and use cases  |
| Rule Based Logic \+ AI Validator  | Leverage Joseph’s system as the primary scorer  Use current AI logic as a secondary validator. AI will be in charge of reviewing/ resolving rule based conflicts/ conclusions to provide adjustments 	 | Lead enrichment is assessed using deterministic rule based logic– more consistency across scores  Normalizes/ standardizes scoring logic  Focus AI power on addressing more complex cases that rule based logic cannot resolve  No AI hallucinations  Adjustable– can create conditional logic for what AI reviews |
| Focused Hybrid Scoring | Use Joseph’s system to validate all three pillars (acquisition, enrichment data coherence)  Use AI to handle contextual validation (external world knowledge, specific business logic)  Use weighted logic to compute a weighted final score 	 | Each system focuses on what it handles best (no overlap)  Easy to replace/ upgrade individual components  No confusion about which system handles what– easier to decipher scoring  Each component can be tuned independently  |
| Score Comparison | Run both systems and retrieve scores Build consensus logic to compare and combine results Instead of using weights, the scores will compete  Re-compute explanation to draw a conclusion for the combined scoring \*\*save logs \+ explanations for both scores computed independently and combine  | highlights/ identifies where the system disagrees and has logic to resolve conflicting conclusions  If one system fails to assess something accurately, the other provides fallback  |

  