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
  * *Demand Funnel : Lead : Lead ID*   
  * *RTLM Country*   
  * *RTLM Channel*   
  * *Demand Funnel : Lead : Account Name* (enriched)   
  * *Demand Funnel : Lead : Email* (input information for enrichment)   
  * *Demand Funnel : Lead : Website* (enriched or filled out by seller)   
  * *Demand Funnel : Lead : ZI Employees* (enriched)   
  * *Demand Funnel : Lead : ZI Enrichment Status* (whether lead was enriched)  
* Flags to look out for:   
  * *Demand Funnel : Lead : ZI Employees* \> 100 but *Demand Funnel : Lead : Account Name* NOT POPULATED  
    * Accounts in the RC TAM (total addressable market) base include all accounts with 100+ employees  
    * This account should be enriched with an account name or is being incorrectly enriched for employee number  
  * *Demand Funnel : Lead : Email* has free email domain (hotmail, gmail, etc.) and *Demand Funnel : Lead : Website* NOT POPULATED and enriching with *Demand Funnel : Lead : Account Name* POPULATED and *Demand Funnel : Lead : ZI Employees* \> 100   
    * Why are accounts with ambiguous email domains and no websites being enriched with an Account name (company) and other ZI data?   
2. Verify Data Accuracy \+ Information Discovery    
* Inspect *Demand Funnel : Lead : Website* and *Demand Funnel : Lead : ZI Employees*  
  * Try to populate *Demand Funnel : Lead : Account Name* for RC TAM base  
* Inspect *Demand Funnel : Lead : Email*  
  * If there is additional information (company name) in email domain → use to infer *Demand Funnel : Lead : Website* and *Demand Funnel : Lead : Account Name*  
  * Try to populate other fields using inferred information   
* Cross check each record with sources  
  * Public databases (LinkedIn, etc.), internal CRM or sales data  
  * Does the *Demand Funnel : Lead : Email* match the enriched data?   
3. Impact Assessment   
* Evaluate whether ZoomInfo enriched data has led to better sales outcomes in the past  
* Cohorts:  
  * ZoomInfo-Enriched Leads– *Demand Funnel : Lead : ZI Enrichment Status* is SUCCESS  
  * Non-ZoomInfo Leads– *Demand Funnel : Lead : ZI Enrichment Status* is not SUCCESS  
  *   
* Analyze key sales metrics:  
  * Conversion rate– % of leads that turn into opportunities or deals   
  * Speed to contact– how quickly a rep follows up with a lead   
  * Sales cycle length– how long it takes to close a deal   
  * Win rate– deals closed vs deals lost   
  * Revenue influenced– total revenue from ZoomInfo- enriched leads   
* These outcomes can be used in two ways:   
  * Global weight– apply overall historical performance of ZoomInfo enrichment across the board   
4. Build a Confidence Model   
* Design either a rule based system, ML model, or prompt to LLM to:   
  * Assess freshness of data  
  * Compared against other trusted sources   
  * Evaluate internal consistency   
  * Incorporate outcome history, if applicable  
* Output a confidence score (%) for each record or data point   
5. Explainability   
* Provide clear and concise explanations for why a particular confidence level was assigned  
* Explanation layer should help build trust in the system and enable sales or operation teams to take actions accordingly  
* A correction for incorrect fields

### **Tokens**

* OPENAI\_API\_KEY=sk-proj-h\_nRtJ0rlXpHxYUPy14YMJk2Mycddr74btgo7Y6Q8UqsjM1tC\_TEbQPxlr6YeB5CkP2H9u6f\_VT3BlbkFJqaGCrJjT0tUmUV33syJ2BL5PUEvYgltfi4cSG1GPee-Cg3niLI7Yy4\_iayQnl4rQ2mgqgo9n8A

### 

### **Questions** 

* Access  
  * Where can I access ZoomInfo enriched records?   
  * Will I need access to both SFDC and any intermediate systems to gather these records (other internal systems/ dbs)?   
* Implementation   
  * What format would you prefer this tool to take?   
    * An API with UI?   
    * A script/ backend tool/ prompt?   
    * A report?   
* Enrichment Identification   
  * Is there a way to identify whether a specific SFDC lead or opportunity was enriched by ZoomInfo?   
    * Which fields/ metadata should I be checking to confirm ZoomInfo involvement?   
* Verification Sources   
  * What external/ internal sources would you recommend I use to verify the accuracy of ZoomInfo data?   
* Data Impact Evaluation   
  * Do we track performance metrics for how much impact ZoomInfo records make?   
  * Can you show me an example of what a ZoomInfo record looks like– what input information does RC provide and what information does ZoomInfo return?