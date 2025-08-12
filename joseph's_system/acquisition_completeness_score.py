import pandas as pd
import numpy as np

import logging

from .completeness_dependency_loader import CompletenessDependencyLoader


class AcquisitionCompletenessScorer:
    def __init__(self, config_path=None):
        """
        Initializes the Acquisition Completeness Scorer with necessary configurations.

        :param config_path: Path to the dependencies folder containing reference files.
                           Defaults to '../references/scoring' relative to the src/scoring/ directory.
        """

        # Initialize CompletenessDependencyLoader (config_path is optional)
        self.dependency_loader = CompletenessDependencyLoader(config_path)
        self.dependencies = self.dependency_loader.load()

        self.logger = self._initialize_logger()

    def _initialize_logger(self):
        """
        Sets up a logger for the scorer.
        """
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        handler.setFormatter(
            logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        )
        logger.addHandler(handler)
        return logger

    def score(
        self,
        df,
        column_mapping=None,
        column_weights=None,
        ruleset=None,
    ):
        """Scores acquisition completeness based on the input data.

        :param df: Input DataFrame to be scored.
        :param column_mapping: Dictionary mapping column names.
        :param column_weights: List of weights for each column.
        :param ruleset: Dictionary defining rules for scoring. If None, default ruleset is used.
        :return: DataFrame with acquisition completeness scores.
        """
        df = df.copy()

        # Default column mapping
        column_mapping = column_mapping or {
            "first_name": "first_name",
            "last_name": "last_name",
            "email_domain": "email_domain",
            "phone": "phone",
            "state_province": "state_province",
            "country": "country",
            # "employees": "employees",
            "sector": "sector",
            "company": "company",
            "website_domain": "website_domain",
        }

        # Default column weights
        column_weights = column_weights or [
            0.0625,
            0.0625,
            0.125,
            0.125,
            0.125,
            0.125,
            0.125,
            0.125,
            0.125,
        ]

        # Default explicit ruleset
        if ruleset is None:
            ruleset = {
                "first_name": {
                    "rules": [
                        df[column_mapping["first_name"]].isnull(),
                        df[column_mapping["first_name"]]
                        .astype(str)
                        .str.lower()
                        .isin(self.dependencies["invalid_names"]),
                    ],
                    "score_choice": [0, 0],
                    "score_default": 100,
                },
                "last_name": {
                    "rules": [
                        df[column_mapping["last_name"]].isnull(),
                        df[column_mapping["last_name"]]
                        .astype(str)
                        .str.lower()
                        .isin(self.dependencies["invalid_names"]),
                    ],
                    "score_choice": [0, 0],
                    "score_default": 100,
                },
                "email_domain": {
                    "rules": [
                        df[column_mapping["email_domain"]].isnull(),
                        df[column_mapping["email_domain"]]
                        .astype(str)
                        .str.lower()
                        .str.strip()
                        .isin(self.dependencies["invalid_domains"]),
                    ],
                    "score_choice": [0, 0],
                    "score_default": 100,
                },
                "phone": {
                    "rules": [
                        df[column_mapping["phone"]].isnull(),
                        ~df[column_mapping["phone"]]
                        .astype(str)
                        .str.match(
                            self.dependencies["invalid_phone_pattern"], na=False
                        ),
                    ],
                    "score_choice": [0, 0],
                    "score_default": 100,
                },
                "state_province": {
                    "rules": [
                        df[column_mapping["state_province"]].isnull(),
                        df[column_mapping["state_province"]]
                        .astype(str)
                        .str.lower()
                        .str.strip()
                        .isin(self.dependencies["states_in_rc_territories"]),
                        df[column_mapping["state_province"]].notnull(),
                    ],
                    "score_choice": [0, 100, 75],
                    "score_default": 50,
                },
                "country": {
                    "rules": [
                        df[column_mapping["country"]].isnull(),
                        df[column_mapping["country"]]
                        .astype(str)
                        .str.lower()
                        .str.strip()
                        .isin(self.dependencies["countries_google_list"]),
                        df[column_mapping["country"]].notnull(),
                    ],
                    "score_choice": [0, 100, 75],
                    "score_default": 50,
                },
                # "employees": {
                #     "rules": [
                #         df[column_mapping["employees"]].isnull(),
                #         df[column_mapping["employees"]] <= 0,
                #     ],
                #     "score_choice": [0, 100],
                #     "score_default": 100,
                # },
                "sector": {
                    "rules": [
                        df[column_mapping["sector"]].isnull(),
                        df[column_mapping["sector"]]
                        .astype(str)
                        .str.lower()
                        .str.strip()
                        .isin(self.dependencies["rc_sectors"]),
                        df[column_mapping["sector"]].notnull(),
                    ],
                    "score_choice": [0, 100, 75],
                    "score_default": 50,
                },
                "company": {
                    "rules": [
                        df[column_mapping["company"]].isnull(),
                        df[column_mapping["company"]]
                        .astype(str)
                        .str.lower()
                        .isin(self.dependencies["invalid_companies"]),
                    ],
                    "score_choice": [0, 0],
                    "score_default": 100,
                },
                "website_domain": {
                    "rules": [
                        df[column_mapping["website_domain"]].isnull(),
                        df[column_mapping["website_domain"]]
                        .astype(str)
                        .str.lower()
                        .str.strip()
                        .isin(self.dependencies["invalid_domains"]),
                    ],
                    "score_choice": [0, 0],
                    "score_default": 100,
                },
            }

        # Scoring logic
        output_cols = []
        for key in column_mapping.keys():
            if key not in ruleset:
                self.logger.warning(f"No rules defined for column: {key}")
                continue

            condlist = ruleset[key]["rules"]
            choicelist = ruleset[key]["score_choice"]
            df[f"{key}_score"] = np.select(
                condlist=condlist,
                choicelist=choicelist,
                default=ruleset[key]["score_default"],
            )
            output_cols.append(f"{key}_score")
            self.logger.info(f"Scored {key} successfully.")

        # Calculate final completeness score
        df["acquisition_completeness_score"] = np.rint(
            np.sum(df[output_cols].values * np.array(column_weights), axis=1)
        )
        self.logger.info("Successfully calculated acquisition completeness score.")
        return df


if __name__ == "__main__":
    # Example 1: All valid data
    data_1 = {
        "first_name": ["John", "Alice", "Robert"],
        "last_name": ["Doe", "Smith", "Johnson"],
        "email_domain": ["example.com", "sample.org", "company.net"],
        "phone": ["123-456-7890", "987-654-3210", "555-555-5555"],
        "state_province": ["California", "New York", "Texas"],
        "country": ["USA", "USA", "USA"],
        # "employees": [200, 50, 500],
        "sector": ["Technology", "Healthcare", "Finance"],
        "company": ["TechCorp", "HealthInc", "FinCo"],
        "website_domain": ["techcorp.com", "healthinc.org", "finco.net"],
    }
    df_1 = pd.DataFrame(data_1)

    # Example 2: Missing values and invalid data
    data_2 = {
        "first_name": [None, "Mike", "NaN"],
        "last_name": ["", "Brown", "invalid"],
        "email_domain": [None, "invalidemail.com", "bademail@domain"],
        "phone": [None, "000-000-0000", "invalid_phone"],
        "state_province": ["California", None, "unkown_state"],
        "country": [None, "United States", "countrynotfound"],
        # "employees": [None, -1, 0],
        "sector": ["", "Unknown", None],
        "company": ["", "BigCorp", "InvalidCompany"],
        "website_domain": ["", "badwebsite.com", None],
    }
    df_2 = pd.DataFrame(data_2)

    # Example 3: Invalid domain names and invalid sectors
    data_3 = {
        "first_name": ["James", "Sarah", "Paul"],
        "last_name": ["Taylor", "Lee", "White"],
        "email_domain": ["unknown.com", "spam.com", "fake.com"],
        "phone": ["111-222-3333", "444-555-6666", "777-888-9999"],
        "state_province": ["New Jersey", "Ohio", "Colorado"],
        "country": ["USA", "USA", "Canada"],
        # "employees": [100, 10, 1000],
        "sector": ["Retail", "Manufacturing", "Tourism"],
        "company": ["RetailInc", "ManufactureLLC", "TourismCo"],
        "website_domain": ["retailinc.com", "manufacturellc.com", "tourismco.ca"],
    }
    df_3 = pd.DataFrame(data_3)

    # Example 4: Mixed valid and invalid data with numbers as values
    data_4 = {
        "first_name": ["Tom", "NaN", "Jake"],
        "last_name": ["Hanks", "NotFound", "Sullivan"],
        "email_domain": ["domain.com", "invalid.com", "valid.org"],
        "phone": ["999-888-7777", "123-123-1234", "none"],
        "state_province": ["Alabama", "Not Available", "Missouri"],
        "country": ["Canada", "USA", "Canada"],
        # "employees": [0, None, 0],
        "sector": ["Media", "Technology", "Healthcare"],
        "company": ["MediaCorp", "TechGiant", "HealthPro"],
        "website_domain": ["mediacorp.com", "techgiant.org", "healthpro.net"],
    }
    df_4 = pd.DataFrame(data_4)

    # Example 5: Only invalid email domains and invalid company names
    data_5 = {
        "first_name": ["Lucy", "Bill", "Sam"],
        "last_name": ["Adams", "Clark", "Johnson"],
        "email_domain": ["wrong.com", "spam.com", "fake.com"],
        "phone": ["111-000-2222", "333-444-5555", "666-777-8888"],
        "state_province": ["New York", "California", "Texas"],
        "country": ["USA", "USA", "USA"],
        # "employees": [50, 100, 200],
        "sector": ["Retail", "Manufacturing", "Technology"],
        "company": ["NoCompany", "SpamInc", "FakeCorp"],
        "website_domain": ["", "spam.com", "fake.com"],
    }
    df_5 = pd.DataFrame(data_5)

    # Running the scorer on each of the above examples
    scorer = AcquisitionCompletenessScorer()

    result_1 = scorer.score(df_1)
    print("Example 1 - All valid data")
    print("Result 1:")
    print(result_1)

    result_2 = scorer.score(df_2)
    print("Example 2 - Missing values and invalid data")
    print("\nResult 2:")
    print(result_2)

    result_3 = scorer.score(df_3)
    print("Example 3 - Invalid domains and sectors")
    print("\nResult 3:")
    print(result_3)

    result_4 = scorer.score(df_4)
    print("Example 4 - Mixed valid and invalid data")
    print("\nResult 4:")
    print(result_4)

    result_5 = scorer.score(df_5)
    print("Example 5 - Invalid email domains and invalid company names")
    print("\nResult 5:")
    print(result_5)
