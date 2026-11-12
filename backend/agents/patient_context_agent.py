
import logging
import re

from backend.models.patient_schema import (
    PatientContext,
    DeidentifiedPatientContext
)

logger = logging.getLogger(__name__)


class PatientContextAgent:

    @staticmethod
    def _normalize_context(context: dict) -> dict:
        """Normalize frontend data before Pydantic validation."""

        if not isinstance(context, dict):
            raise TypeError(
                "Patient context must be a dictionary."
            )

        data = dict(context)

        # Map frontend field names to schema field names
        if "age" in data and "age_group" not in data:
            age = data.pop("age")

            if age is not None:
                data["age_group"] = (
                    "Child" if age < 18 else
                    "Adult" if age < 65 else
                    "Older Adult"
                )

        if "gender" in data and "sex" not in data:
            data["sex"] = data.pop("gender")

        if "medical_history" in data and "clinical_history" not in data:
            data["clinical_history"] = data.pop(
                "medical_history"
            )

        if "current_medications" in data and "relevant_medications" not in data:
            data["relevant_medications"] = data.pop(
                "current_medications"
            )

        # Normalize list fields
        list_fields = [
            "relevant_conditions",
            "relevant_medications",
            "allergies"
        ]

        for field in list_fields:
            value = data.get(field, [])

            if value is None or value == "":
                data[field] = []

            elif isinstance(value, str):
                data[field] = [
                    item.strip()
                    for item in value.split(",")
                    if item.strip()
                ]

            elif not isinstance(value, list):
                data[field] = [str(value)]

        # Preserve additional clinical measurements
        extra_fields = [
            "blood_pressure",
            "hba1c",
            "egfr"
        ]

        extra_context = data.get(
            "additional_context", ""
        ) or ""

        if isinstance(extra_context, dict):
            extra_context = str(extra_context)

        for field in extra_fields:
            value = data.pop(field, None)

            if value:
                extra_context += (
                    f"\n{field.replace('_', ' ').title()}: {value}"
                )

        if extra_context:
            data["additional_context"] = extra_context

        return data

    def run(self, context: dict) -> dict:

        try:
            logger.info(
                "Patient Context Agent started"
            )

            normalized_data = self._normalize_context(
                context
            )

            patient = PatientContext.model_validate(
                normalized_data
            )

            data = patient.model_dump()

            warnings = []

            if data.get("clinical_history"):
                data["clinical_history"] = self._deidentify(
                    data["clinical_history"]
                )

            if data.get("additional_context"):
                data["additional_context"] = self._deidentify(
                    data["additional_context"]
                )

            if data.get("age_group") is None:
                warnings.append(
                    "Age group not provided."
                )

            result = DeidentifiedPatientContext.model_validate(
                data
            )

            logger.info(
                "Patient Context Agent completed successfully"
            )

            return {
                "patient_context": result.model_dump(),
                "deidentified": True,
                "warnings": warnings
            }

        except Exception:
            logger.exception(
                "Patient Context Agent failed"
            )
            raise

    @staticmethod
    def _deidentify(text):

        if not text:
            return text

        text = re.sub(
            r"\b[\w.+-]+@[\w.-]+\.[a-zA-Z]{2,}\b",
            "[REDACTED_EMAIL]",
            text
        )

        text = re.sub(
            r"\b(?:\+?\d{1,3}[- ]?)?\d{10}\b",
            "[REDACTED_PHONE]",
            text
        )

        text = re.sub(
            r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b",
            "[REDACTED_DATE]",
            text
        )

        text = re.sub(
            r"\b(?:MRN|Patient ID|Aadhaar|SSN)"
            r"\s*[:#-]?\s*[A-Za-z0-9-]+\b",
            "[REDACTED_IDENTIFIER]",
            text,
            flags=re.IGNORECASE
        )

        return text


patient_context_agent = PatientContextAgent()
