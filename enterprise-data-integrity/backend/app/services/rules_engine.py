"""
Data Quality Rules Engine - Module 2
Core service for executing data quality checks
"""
import pandas as pd
from typing import List, Dict, Any, Tuple
from datetime import datetime
import re


class DataQualityRule:
    """Base class for data quality rules"""

    def __init__(self, name: str, description: str, severity: str):
        self.name = name
        self.description = description
        self.severity = severity

    def execute(self, df: pd.DataFrame) -> Tuple[bool, List[Dict], str]:
        """
        Execute the rule on a dataframe

        Returns:
            (passed, issues, message)
        """
        raise NotImplementedError


class DuplicateEmployeesRule(DataQualityRule):
    """Check for duplicate employee records"""

    def __init__(self):
        super().__init__(
            name="Duplicate Employees",
            description="Detects duplicate employee records based on employee ID",
            severity="critical",
        )

    def execute(self, df: pd.DataFrame) -> Tuple[bool, List[Dict], str]:
        if "employee_id" not in df.columns:
            return True, [], "employee_id column not found, skipping"

        duplicates = df[df.duplicated(subset=["employee_id"], keep=False)]

        if len(duplicates) == 0:
            return True, [], f"No duplicate employees found"

        issues = []
        for emp_id in duplicates["employee_id"].unique():
            dup_records = duplicates[duplicates["employee_id"] == emp_id]
            issues.append(
                {
                    "employee_id": emp_id,
                    "count": len(dup_records),
                    "records": dup_records.to_dict("records"),
                }
            )

        return False, issues, f"Found {len(issues)} duplicate employee IDs"


class MissingMandatoryFieldsRule(DataQualityRule):
    """Check for missing mandatory fields"""

    def __init__(self, mandatory_fields: List[str] = None):
        super().__init__(
            name="Missing Mandatory Fields",
            description="Detects records with missing mandatory fields",
            severity="high",
        )
        self.mandatory_fields = mandatory_fields or [
            "employee_id",
            "first_name",
            "last_name",
            "email",
        ]

    def execute(self, df: pd.DataFrame) -> Tuple[bool, List[Dict], str]:
        issues = []

        for field in self.mandatory_fields:
            if field not in df.columns:
                continue

            missing = df[df[field].isna() | (df[field] == "")]
            if len(missing) > 0:
                issues.append(
                    {
                        "field": field,
                        "missing_count": len(missing),
                        "affected_records": missing.index.tolist()[:100],  # Limit to 100
                    }
                )

        if len(issues) == 0:
            return True, [], "All mandatory fields are populated"

        total_missing = sum(issue["missing_count"] for issue in issues)
        return False, issues, f"Found {total_missing} records with missing mandatory fields"


class InvalidEmailRule(DataQualityRule):
    """Check for invalid email addresses"""

    def __init__(self):
        super().__init__(
            name="Invalid Email Addresses",
            description="Detects invalid email address formats",
            severity="medium",
        )
        self.email_pattern = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")

    def execute(self, df: pd.DataFrame) -> Tuple[bool, List[Dict], str]:
        if "email" not in df.columns:
            return True, [], "email column not found, skipping"

        # Filter out null/empty emails first
        valid_emails = df[df["email"].notna() & (df["email"] != "")]

        invalid = valid_emails[~valid_emails["email"].apply(lambda x: bool(self.email_pattern.match(str(x))))]

        if len(invalid) == 0:
            return True, [], "All email addresses are valid"

        issues = [
            {
                "email": row["email"],
                "employee_id": row.get("employee_id", "N/A"),
                "index": idx,
            }
            for idx, row in invalid.iterrows()
        ]

        return False, issues[:100], f"Found {len(invalid)} invalid email addresses"


class ManagerHierarchyLoopRule(DataQualityRule):
    """Check for loops in manager hierarchy"""

    def __init__(self):
        super().__init__(
            name="Manager Hierarchy Loops",
            description="Detects circular references in manager-employee relationships",
            severity="critical",
        )

    def execute(self, df: pd.DataFrame) -> Tuple[bool, List[Dict], str]:
        if "employee_id" not in df.columns or "manager_id" not in df.columns:
            return True, [], "Required columns not found, skipping"

        issues = []

        # Build manager map
        manager_map = dict(zip(df["employee_id"], df["manager_id"]))

        for emp_id in df["employee_id"]:
            visited = set()
            current = emp_id

            while current and pd.notna(current):
                if current in visited:
                    # Found a loop
                    issues.append(
                        {
                            "employee_id": emp_id,
                            "loop_chain": list(visited) + [current],
                        }
                    )
                    break

                visited.add(current)
                current = manager_map.get(current)

        if len(issues) == 0:
            return True, [], "No manager hierarchy loops detected"

        return False, issues, f"Found {len(issues)} manager hierarchy loops"


class InvalidCountryCodeRule(DataQualityRule):
    """Check for invalid country codes"""

    def __init__(self):
        super().__init__(
            name="Invalid Country Codes",
            description="Detects invalid ISO country codes",
            severity="medium",
        )
        # Common ISO 3166-1 alpha-2 codes
        self.valid_codes = {
            "US",
            "GB",
            "DE",
            "FR",
            "IN",
            "CN",
            "JP",
            "CA",
            "AU",
            "BR",
            "MX",
            "IT",
            "ES",
            "NL",
            "SE",
            "NO",
            "DK",
            "FI",
            "IE",
            "CH",
            "AT",
            "BE",
            "PL",
            "CZ",
            "SG",
            "HK",
            "NZ",
            "ZA",
        }

    def execute(self, df: pd.DataFrame) -> Tuple[bool, List[Dict], str]:
        if "country_code" not in df.columns:
            return True, [], "country_code column not found, skipping"

        # Filter non-null values
        valid_entries = df[df["country_code"].notna() & (df["country_code"] != "")]

        invalid = valid_entries[~valid_entries["country_code"].str.upper().isin(self.valid_codes)]

        if len(invalid) == 0:
            return True, [], "All country codes are valid"

        issues = [
            {
                "country_code": row["country_code"],
                "employee_id": row.get("employee_id", "N/A"),
                "index": idx,
            }
            for idx, row in invalid.iterrows()
        ]

        return False, issues[:100], f"Found {len(invalid)} invalid country codes"


class DataQualityEngine:
    """Main engine for executing data quality rules"""

    def __init__(self):
        self.builtin_rules = {
            "duplicate_employees": DuplicateEmployeesRule(),
            "missing_mandatory_fields": MissingMandatoryFieldsRule(),
            "invalid_emails": InvalidEmailRule(),
            "manager_hierarchy_loops": ManagerHierarchyLoopRule(),
            "invalid_country_codes": InvalidCountryCodeRule(),
        }

    def get_available_rules(self) -> List[Dict[str, str]]:
        """Get list of available built-in rules"""
        return [
            {
                "id": rule_id,
                "name": rule.name,
                "description": rule.description,
                "severity": rule.severity,
            }
            for rule_id, rule in self.builtin_rules.items()
        ]

    def execute_rules(
        self, df: pd.DataFrame, rule_ids: List[str] = None
    ) -> Dict[str, Any]:
        """
        Execute selected rules on the dataframe

        Args:
            df: DataFrame to check
            rule_ids: List of rule IDs to execute. If None, execute all.

        Returns:
            Dictionary with execution results
        """
        if rule_ids is None:
            rule_ids = list(self.builtin_rules.keys())

        results = {
            "total_records": len(df),
            "rules_executed": 0,
            "rules_passed": 0,
            "rules_failed": 0,
            "total_issues": 0,
            "execution_details": [],
        }

        for rule_id in rule_ids:
            if rule_id not in self.builtin_rules:
                continue

            rule = self.builtin_rules[rule_id]
            start_time = datetime.utcnow()

            try:
                passed, issues, message = rule.execute(df)
                execution_time = (datetime.utcnow() - start_time).total_seconds() * 1000

                results["rules_executed"] += 1
                if passed:
                    results["rules_passed"] += 1
                else:
                    results["rules_failed"] += 1
                    results["total_issues"] += len(issues)

                results["execution_details"].append(
                    {
                        "rule_id": rule_id,
                        "rule_name": rule.name,
                        "severity": rule.severity,
                        "passed": passed,
                        "issues_found": len(issues),
                        "issues": issues,
                        "message": message,
                        "execution_time_ms": int(execution_time),
                    }
                )

            except Exception as e:
                results["execution_details"].append(
                    {
                        "rule_id": rule_id,
                        "rule_name": rule.name,
                        "severity": rule.severity,
                        "passed": False,
                        "error": str(e),
                        "execution_time_ms": 0,
                    }
                )

        return results
