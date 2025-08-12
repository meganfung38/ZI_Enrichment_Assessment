import pandas as pd
import numpy as np

import logging

from .completeness_dependency_loader import CompletenessDependencyLoader


class EnrichmentCompletenessScorer:
    def __init__(self, config_path=None):
        """
        Initializes the Enrichment Completeness Scorer with necessary configurations.

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
            "account_name_zi_cdp": "account_name_zi_cdp",
            "zi_company_name": "zi_company_name",
            "zi_website_domain": "zi_website_domain",
            "zi_company_state": "zi_company_state",
            "zi_company_country": "zi_company_country",
            "zi_employees": "zi_employees",
            "segment_name": "segment_name",
        }

        # Default column weights
        column_weights = column_weights or [0.10, 0.18, 0.18, 0.18, 0.18, 0.18]

        # Default explicit ruleset
        if ruleset is None:
            ruleset = {
                "account_name_zi_cdp": {
                    "rules": [
                        (
                            df[column_mapping["segment_name"]].isin(
                                ["Small Business", "SOHO"]
                            )
                        )
                        & (df[column_mapping["account_name_zi_cdp"]].isnull()),
                        df[column_mapping["account_name_zi_cdp"]].isnull(),
                    ],
                    "score_choice": [75, 0],
                    "score_default": 100,
                },
                "zi_company_name": {
                    "rules": [
                        (
                            df[column_mapping["segment_name"]].isin(
                                ["Small Business", "SOHO"]
                            )
                        )
                        & (df[column_mapping["zi_company_name"]].isnull()),
                        df[column_mapping["zi_company_name"]].isnull(),
                        df[column_mapping["zi_company_name"]]
                        .astype(str)
                        .str.lower()
                        .isin(self.dependencies["invalid_companies"]),
                    ],
                    "score_choice": [75, 0, 0],
                    "score_default": 100,
                },
                "zi_website_domain": {
                    "rules": [
                        (
                            df[column_mapping["segment_name"]].isin(
                                ["Small Business", "SOHO"]
                            )
                        )
                        & (df[column_mapping["zi_website_domain"]].isnull()),
                        df[column_mapping["zi_website_domain"]].isnull(),
                        df[column_mapping["zi_website_domain"]]
                        .astype(str)
                        .str.lower()
                        .str.strip()
                        .isin(self.dependencies["invalid_domains"]),
                    ],
                    "score_choice": [75, 0, 0],
                    "score_default": 100,
                },
                "zi_company_state": {
                    "rules": [
                        (
                            df[column_mapping["segment_name"]].isin(
                                ["Small Business", "SOHO"]
                            )
                        )
                        & (df[column_mapping["zi_company_state"]].isnull()),
                        df[column_mapping["zi_company_state"]].isnull(),
                        df[column_mapping["zi_company_state"]]
                        .astype(str)
                        .str.lower()
                        .str.strip()
                        .isin(self.dependencies["states_in_rc_territories"]),
                        df[column_mapping["zi_company_state"]].notnull(),
                    ],
                    "score_choice": [75, 0, 100, 75],
                    "score_default": 50,
                },
                "zi_company_country": {
                    "rules": [
                        (
                            df[column_mapping["segment_name"]].isin(
                                ["Small Business", "SOHO"]
                            )
                        )
                        & (df[column_mapping["zi_company_country"]].isnull()),
                        df[column_mapping["zi_company_country"]].isnull(),
                        df[column_mapping["zi_company_country"]]
                        .astype(str)
                        .str.lower()
                        .isin(self.dependencies["invalid_companies"]),
                    ],
                    "score_choice": [75, 0, 0],
                    "score_default": 100,
                },
                "zi_employees": {
                    "rules": [
                        (
                            df[column_mapping["segment_name"]].isin(
                                ["Small Business", "SOHO"]
                            )
                        )
                        & (df[column_mapping["zi_employees"]].isnull()),
                        df[column_mapping["zi_employees"]].isnull(),
                        df[column_mapping["zi_employees"]] <= 0,
                    ],
                    "score_choice": [75, 0, 100],
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
        df["enrichment_completeness_score"] = np.rint(
            np.sum(df[output_cols].values * np.array(column_weights), axis=1)
        )
        self.logger.info("Successfully calculated enrichment completeness score.")
        return df


if __name__ == "__main__":
    # Create sample DataFrame
    data = {
        "account_name_zi_cdp": [
            None,
            "Acme Corp",
            "Tech Co",
            "Example Ltd",
            None,
            None,
        ],
        "zi_company_name": ["Acme Corp", None, "Tech Co", "Invalid Corp", None, None],
        "zi_website_domain": [
            "acme.com",
            None,
            "techco.com",
            "invalid.com",
            None,
            None,
        ],
        "zi_company_state": ["California", None, "New York", "Texas", None, None],
        "zi_company_country": ["USA", "USA", "USA", None, None, None],
        "zi_employees": [250, 0, 500, 100, None, None],
        "segment_name": [
            "Majors",
            "SOHO",
            "Enterprise",
            "Mid Market",
            "Small Business",
            "Enterprise",
        ],
    }
    df = pd.DataFrame(data)

    scorer = EnrichmentCompletenessScorer()
    scored_df = scorer.score(df)

    print(scored_df)
