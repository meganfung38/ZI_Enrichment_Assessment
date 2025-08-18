import logging
import os

import numpy as np
import pandas as pd


class CompletenessDependencyLoader:
    def __init__(self, config_path=None):
        """
        Initializes the CompletenessDependencyLoader with a config path.
        :param config_path: Path to the dependencies folder containing reference files.
        """
        if config_path is None:
            self.config_path = os.path.join(
                os.path.dirname(__file__), "../../references/scoring"
            )
        else:
            self.config_path = config_path

        self.logger = self._initialize_logger()

    def _initialize_logger(self):
        """Initializes the logger."""
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        handler.setFormatter(
            logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        )
        logger.addHandler(handler)
        return logger

    def load(self):
        """Loads all necessary reference files and returns them as a dictionary."""
        dependencies = {}

        try:
            # Load invalid domains
            dependencies["invalid_domains"] = self._load_invalid_domains()

            # Load states and territories
            dependencies["states_in_rc_territories"] = (
                self._load_states_in_rc_territories()
            )

            # Load countries
            dependencies["countries_google_list"] = self._load_countries()

            # Load sectors
            dependencies["rc_sectors"] = self._load_sectors()

            # Load invalid names
            dependencies["invalid_names"] = self._load_invalid_names()

            # Load phone pattern
            dependencies["invalid_phone_pattern"] = self._load_invalid_phone_pattern()

            # Load invalid companies (merge with invalid names)
            dependencies["invalid_companies"] = (
                self._load_invalid_companies() + dependencies["invalid_names"]
            )

            self.logger.info("Dependencies loaded successfully.")
            return dependencies

        except Exception as e:
            self.logger.error(f"Error loading dependencies: {e}")
            raise

    def _load_invalid_domains(self):
        """Loads the invalid domains from the CSV file."""
        try:
            file = "bad_domains_latest_2025_01_27.csv"
            df_invalid_domains = pd.read_csv(os.path.join(self.config_path, file))
            return (
                df_invalid_domains["bad_domains"]
                .str.lower()
                .str.strip()
                .unique()
                .tolist()
            )
        except Exception as e:
            self.logger.error(f"Error loading invalid domains: {e}")
            raise

    def _load_states_in_rc_territories(self):
        """Loads the states and territories from the CSV file."""
        try:
            file = "territory_country_state_abbreviations_mapping_2024_11_11.csv"
            df_territory = pd.read_csv(os.path.join(self.config_path, file))
            state_columns = ["state"] + list(
                df_territory.columns[df_territory.columns.str.contains("abbrev")]
            )
            states = list(
                set(df_territory[state_columns].values.ravel())
                - {None, "NaN", float("nan"), np.nan}
            )
            return [i.strip().lower() for i in states]
        except Exception as e:
            self.logger.error(f"Error loading states and territories: {e}")
            raise

    def _load_countries(self):
        """Loads the list of countries from the CSV file."""
        try:
            file = "countries_google_dataset_2024_11_11.csv"
            df_country = pd.read_csv(os.path.join(self.config_path, file))
            countries = list(
                set(df_country[["country", "name"]].values.ravel())
                - {None, "NaN", float("nan"), np.nan}
            )
            return [i.strip().lower() for i in countries]
        except Exception as e:
            self.logger.error(f"Error loading countries: {e}")
            raise

    def _load_sectors(self):
        """Loads the RC sectors from the CSV file."""
        try:
            file = "ZI_industry_cross-walk.csv"
            df_rc_sector = pd.read_csv(os.path.join(self.config_path, file))
            return df_rc_sector["RC Re-Mapped Sector"].str.lower().str.strip().tolist()
        except Exception as e:
            self.logger.error(f"Error loading sectors: {e}")
            raise

    def _load_invalid_names(self):
        """Returns a list of invalid names."""
        return [
            "nan",
            "firstname",
            "name",
            "fname",
            "unavailable",
            "fuck",
            "asshole",
            "ringcentral",
            "SDFWASD",
            "Dennis Talamine",
            "ali ali",
            "alaa raed",
            "wrgwrg",
            "fgfhgj",
            "bdfndfd",
            "Something New",
            "Something",
            "ass hole",
            "nigga",
            "nigger",
            "shit",
            "motherfucker",
            "fucker",
            "mother fucker",
            "faggot",
            "cunt",
            "tits",
            "ass hole",
            "null",
            "Null",
            "Unavailable",
            "unavailable",
        ]

    def _load_invalid_phone_pattern(self):
        """Returns the invalid phone pattern."""
        return r"^\+?(\(?\d{1,3}\)?)[ \-]?\(?\d{1,4}\)?[ \-]?\d{1,4}[ \-]?\d{1,4}[ \-]?\d{1,4}(?:[ \-]?(?:ext|Ext|ex:|EX:|ext\.|Ext\.|x)[ \-:]?\d{1,5})?$"

    def _load_invalid_companies(self):
        """Returns a list of invalid company names."""
        return [
            "unavailable",
            "not provided",
            "[not provided]",
            "notprovided",
            "new company",
            "null",
            "Null",
        ]
