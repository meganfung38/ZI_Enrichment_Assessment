import logging

import numpy as np
import pandas as pd
from fuzzywuzzy import fuzz

from .PhoneValidation_BrianChiosi import validate_phone_number

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class CoherenceScorer:
    def __init__(self, df, column_mapping=None, column_weights=None):
        self.df = df

        self.column_mapping = column_mapping or {
            "name_validation_score": "name_validation_score",
            "email_vs_website_similarity_score": "email_vs_website_similarity_score",
            "email_vs_zi_website_similarity_score": "email_vs_zi_website_similarity_score",
            "website_vs_zi_website_similarity_score": "website_vs_zi_website_similarity_score",
            "owner_segment_vs_segment_master_score": "owner_segment_vs_segment_master_score",
            "zi_segment_vs_segment_master_score": "zi_segment_vs_segment_master_score",
            "phone_validation_score": "phone_validation_score",
            "company_vs_zi_company_similarity_score": "company_vs_zi_company_similarity_score",
        }
        self.column_weights = column_weights or [
            0.125,
            0.125,
            0.125,
            0.125,
            0.125,
            0.125,
            0.125,
            0.125,
        ]

    @staticmethod
    def calculate_similarity(s1, s2):
        try:
            # Handle NaN or None values explicitly
            if pd.isna(s1) or pd.isna(s2) or not str(s1).strip() or not str(s2).strip():
                return 0

            # Calculate similarity using fuzz.ratio
            return np.round(
                fuzz.ratio(str(s1).strip().lower(), str(s2).strip().lower()), 4
            )
        except Exception as e:
            logger.error(f"Error in calculate_similarity: {str(e)}")
            return None

    def coherence_name_validation(
        self, df, name_cols=["first_name", "last_name"], output_rules=False
    ):
        logger.info("Starting name validation")
        df = df.copy()
        output_cols = []

        for col in name_cols:
            logger.info(f"Validating {col}")
            normal_name = df[col].str.match(r"^[A-Za-z ,.'-]+$", na=False)
            # common naming convention allowing for commas, periods, apostrophes, and hyphens
            # True = valid, False = invalid

            valid_char_mask = df[col].str.contains(
                r"[0-9@?#$%^&*\"\\\/()\[\]]", na=False
            )
            # checks if name has numbers or special characters
            # has to be reversed because original will flag True=invalid, False=valid

            valid_char = ~valid_char_mask  # Reversed boolean for valid character check

            if output_rules:
                df[f"{col}_normal_name"] = normal_name
                df[f"{col}_invalid_char"] = valid_char

            condlist = [
                df[f"{col}_score"] == 0,
                ~(normal_name)
                & ~(valid_char),  # Condition 1: Not normal and not valid characters
                (normal_name)
                & ~(valid_char),  # Condition 2: Normal but not valid characters
                ~(normal_name)
                & (valid_char),  # Condition 3: Not normal and all valid characters
                (normal_name)
                & (valid_char),  # Condition 4: Normal and all valid characters
            ]

            choicelist = [0, 0, 50, 50, 100]

            output_cols.append(f"{col}_validation_score")
            df[f"{col}_validation_score"] = np.select(condlist, choicelist, default=-1)
            logger.info(f"Successfully scored {col}")

        df["name_validation_score"] = np.sum(
            df[output_cols] * (1 / len(output_cols)), axis=1
        )
        logger.info("Successfully scored full name validation score")

        return df.drop(columns=output_cols) if not output_rules else df

    def coherence_similarity_score(
        self,
        df,
        pairs_to_score=[
            ("email_domain", "website_domain"),
            ("email_domain", "zi_website_domain"),
            ("website_domain", "zi_website_domain"),
            ("company", "zi_company_name"),
        ],
        output_score_names=[
            "email_vs_website_similarity_score",
            "email_vs_zi_website_similarity_score",
            "website_vs_zi_website_similarity_score",
            "company_vs_zi_company_similarity_score",
        ],
    ):
        logger.info("Starting similarity score calculations")
        df = df.copy()

        # Comparison of the columns
        for (col1, col2), score_col in zip(pairs_to_score, output_score_names):
            logger.info(f"Comparing {col1} and {col2}")
            df[score_col] = np.where(
                (df[f"{col1}_score"] == 0) | (df[f"{col2}_score"] == 0),
                0,
                df.apply(
                    lambda row: self.calculate_similarity(row[col1], row[col2]), axis=1
                ),
            )
            logger.info(f"Completed scoring for {score_col}")

        return df

    def generate_segment(
        self,
        df,
        country_emp_source_pairs=[
            ("zi_company_country", "zi_employees"),
        ],
        output_columns=["zi_segment"],
    ):
        logger.info("Generating segments")
        df = df.copy()
        uscan = ["United States", "Canada"]

        for (country, employee), output in zip(
            country_emp_source_pairs, output_columns
        ):
            logger.info(f"Generating segment for {output}")
            condlist = [
                (df[employee].isnull()),
                (df[country].isin(uscan)) & (df[employee] >= 0) & (df[employee] <= 19),
                (df[country].isin(uscan)) & (df[employee] >= 20) & (df[employee] <= 99),
                (df[country].isin(uscan))
                & (df[employee] >= 100)
                & (df[employee] <= 399),
                (df[country].isin(uscan))
                & (df[employee] >= 400)
                & (df[employee] <= 4999),
                (df[country].isin(uscan)) & (df[employee] >= 5000),
                (~df[country].isin(uscan)) & (df[employee] >= 0) & (df[employee] <= 19),
                (~df[country].isin(uscan))
                & (df[employee] >= 20)
                & (df[employee] <= 99),
                (~df[country].isin(uscan))
                & (df[employee] >= 100)
                & (df[employee] <= 4999),
                (~df[country].isin(uscan)) & (df[employee] >= 5000),
            ]
            choicelist = [
                "No Employee Count",
                "SOHO",
                "Small Business",
                "Mid Market",
                "Majors",
                "Enterprise",
                "SOHO",
                "Small Business",
                "Majors",
                "Enterprise",
            ]
            df[output] = np.select(condlist, choicelist, default="No Employee Count")
            logger.info(f"Successfully segmented {output}")

        return df

    def coherence_segment_score(
        self,
        df,
        pairs_to_score=[
            ("rtlm_mql_owner_vp_segment", "segment_name"),
            ("zi_segment", "segment_name"),
        ],
        output_score_names=[
            "owner_segment_vs_segment_master_score",
            "zi_segment_vs_segment_master_score",
        ],
    ):
        logger.info("Scoring segment matches")

        df = self.generate_segment(df)

        if len(pairs_to_score) != len(output_score_names):
            raise ValueError(
                "The number of column pairs must match the number of output score names"
            )

        # Loop through the pairs of columns and their corresponding output names
        for (segment1, segment2), output in zip(pairs_to_score, output_score_names):
            # Make sure columns exist in the DataFrame before applying np.where
            if segment1 not in df.columns or segment2 not in df.columns:
                logger.warning(
                    f"Columns {segment1} or {segment2} not found in the DataFrame"
                )
                continue  # Skip to the next iteration if columns are missing

            rules = [
                (df[segment1] == "No Employee Count")
                | (df[segment2] == "No Employee Count"),
                (df[segment1] == "MME")
                & (df[segment2].isin(["Enterprise", "Majors", "Mid Market"])),
                (df[segment1] == "SMB")
                & (df[segment2].isin(["Small Business", "SOHO"])),
                (df[segment1].isin(["Small Business", "SOHO"]))
                & (df[segment2] == "Small Business")
                & (df[f"{segment2}_override"] == "Linked to Franchise Account"),
                df[segment1] == df[segment2],
            ]

            scores = [0, 100, 100, 100, 100]

            df[output] = np.select(condlist=rules, choicelist=scores, default=0)

            logger.info(f"Successfully scored {output}")

        return df

    def coherence_phone_validation_score(
        self, df, phone_col="phone", output_col="phone_validation_score"
    ):
        logger.info("Validating phone numbers")
        df = df.copy()
        df["phone"] = df[phone_col].fillna(0)

        validation_results = []
        for index, row in df.iterrows():
            validation_results.append(validate_phone_number(row))

        phone_status = [item["nStatus"] for item in validation_results]
        df["phone_validation_results"] = phone_status

        condlist = [
            df["phone_score"] == 0,
            df["phone_validation_results"] == "Valid",
            df["phone_validation_results"] == "Maybe Valid",
            df["phone_validation_results"] == "Likely Not Valid",
            df["phone_validation_results"] == "Invalid",
        ]
        choicelist = [0, 100, 75, 25, 0]

        df[output_col] = np.select(condlist, choicelist, default=-1)
        logger.info(f"Successfully scored {output_col}")

        return df

    def compute_coherence_score(self):
        logger.info("Starting coherence scoring process")

        # Pass self.df to each scoring function
        logger.info("Scoring Coherence - Name validation")
        df = self.coherence_name_validation(self.df)
        # logger.info(f"Columns after name validation scoring: {df.columns}")

        logger.info("Scoring Coherence - Domain and Company Name Similarity")
        df = self.coherence_similarity_score(df)
        # logger.info(f"Columns after similarity scoring: {df.columns}")

        logger.info("Scoring Coherence - Segment Match")
        df = self.coherence_segment_score(df)
        # logger.info(f"Columns after segment scoring: {df.columns}")

        logger.info("Scoring Coherence - Phone Validation")
        df = self.coherence_phone_validation_score(df)
        # logger.info(f"Columns after phone validation: {df.columns}")

        logger.info("Calculating Coherence Component Score")

        # Ensure required columns are present for the final score calculation
        required_columns = list(self.column_mapping.values())
        missing_columns = [col for col in required_columns if col not in df.columns]

        if missing_columns:
            logger.error(
                f"Missing columns for coherence score calculation: {missing_columns}"
            )
            raise KeyError(
                "All columns must be present for successful coherence scoring"
            )

        # Sum weighted scores for final coherence score
        df["coherence_score"] = np.rint(
            np.sum(df[required_columns] * self.column_weights, axis=1)
        )

        logger.info("Successfully scored data coherence component")

        # Update the instance DataFrame
        self.df = df

        return df


# Test the class
if __name__ == "__main__":
    # Create a sample DataFrame for testing
    data = {
        "first_name": ["John", "Jane", "Alice", "Bob"],
        "last_name": ["Doe", "Smith", "Johnson", "Brown"],
        "email_domain": [
            "john@example.com",
            "jane@sample.com",
            "alice@domain.com",
            "bob@domain.com",
        ],
        "website_domain": ["example.com", "sample.com", "domain.com", "domain.com"],
        "zi_website_domain": [
            "zi_example.com",
            "zi_sample.com",
            "zi_domain.com",
            "zi_domain.com",
        ],
        "company": ["John Corp", "Jane Ltd", "Alice Inc", "Bob LLC"],
        "zi_company_name": ["John Corp", "Jane Ltd", "Alice LLC", "Bob LLC"],
        "phone": ["123-456-7890", "987-654-3210", "555-555-5555", "444-444-4444"],
        "country": ["United States", "Canada", "United States", "Canada"],
        "zi_employees": [45, 200, 15, 5100],
        "zi_company_country": [
            "United States",
            "Canada",
            "United States",
            "Canada",
        ],
        "segment_name": ["Small Business", "SOHO", "Enterprise", "Mid Market"],
        "rtlm_mql_owner_vp_segment": ["SOHO", "SMB", "MME", "SOHO"],
        "segment_name_override": ["Linked to Franchise Account", None, None, None],
    }

    df = pd.DataFrame(data)

    # Create an instance of CoherenceCompletenessScorer
    scorer = CoherenceScorer(df)

    # Compute the coherence score
    result_df = scorer.compute_coherence_score()

    # Show the result
    print(result_df)
