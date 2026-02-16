import pytest

from data_availability_validator import DataAvailabilityValidator
from llm_output_validator import LLMOutputValidator
from safe_statistics_engine import SafeStatisticsEngine


class MockCaseRepository:
    def __init__(self, num_cases=0):
        self.num_cases = num_cases

    def count_cases(self, filter=None):
        return self.num_cases

    def get_cases(self, filter=None):
        return [{"outcome": "won" if i % 2 == 0 else "lost"} for i in range(self.num_cases)]


class TestStatisticsValidation:
    def test_single_case_no_statistics(self):
        repo = MockCaseRepository(num_cases=1)
        validator = DataAvailabilityValidator(repo)

        result = validator.validate_statistic_generation("win_rate")

        assert result["can_generate"] is False
        assert result["available_cases"] == 1
        assert result["required_cases"] == 5

    def test_five_cases_basic_statistics(self):
        repo = MockCaseRepository(num_cases=5)
        validator = DataAvailabilityValidator(repo)

        result = validator.validate_statistic_generation("win_rate")

        assert result["can_generate"] is True
        assert result["available_cases"] == 5

    def test_insufficient_data_warning(self):
        repo = MockCaseRepository(num_cases=1)
        validator = DataAvailabilityValidator(repo)

        result = validator.validate_statistic_generation("trend_analysis")

        assert result["can_generate"] is False
        assert "Insufficient data" in (result.get("warning") or "")

    def test_statistics_engine_refuses_single_case(self):
        repo = MockCaseRepository(num_cases=1)
        engine = SafeStatisticsEngine(repo)

        result = engine.calculate_win_rate()

        assert result["success"] is False
        assert "Insufficient data" in (result.get("warning") or "")

    def test_output_validator_detects_fabricated_statistics(self):
        text = "In most cases, the win rate is 75%, and average compensation is $50,000."
        validator = LLMOutputValidator({"total_cases_available": 1})
        result = validator.validate_output(text)

        assert result["is_valid"] is False
        assert len(result["issues_found"]) > 0

    def test_general_advice_without_data_ok(self):
        text = (
            "Insufficient data for statistical analysis. "
            "Recommend collecting more precedents and relying on legal principles."
        )
        validator = LLMOutputValidator({"total_cases_available": 1})
        result = validator.validate_output(text)

        assert result["is_valid"] is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

