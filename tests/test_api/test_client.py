"""Tests for API client module"""

import pytest
import responses
from requests.exceptions import Timeout, ConnectionError
from hypothesis import given, strategies as st
from src.api.client import decode_vin_values_extended
from src.api.models import VINDecodeResult
from src.exceptions import APIError, NetworkError, InvalidVINError


class TestDecodeVINValuesExtended:
    """Tests for decode_vin_values_extended function"""

    @responses.activate
    def test_successful_decode(self, valid_vin, sample_api_response):
        """Test successful VIN decode"""
        responses.add(
            responses.GET,
            f"https://vpic.nhtsa.dot.gov/api/vehicles/DecodeVinValuesExtended/{valid_vin}",
            json=sample_api_response,
            status=200,
        )

        result = decode_vin_values_extended(valid_vin)

        assert isinstance(result, VINDecodeResult)
        assert result.vin == valid_vin
        assert result.make == "BMW"
        assert result.model == "X3"
        assert result.model_year == "2011"

    @responses.activate
    def test_decode_normalizes_vin(self, valid_vin_lowercase, sample_api_response):
        """Test that VIN is normalized before API call"""
        responses.add(
            responses.GET,
            f"https://vpic.nhtsa.dot.gov/api/vehicles/DecodeVinValuesExtended/{valid_vin_lowercase.upper()}",
            json=sample_api_response,
            status=200,
        )

        result = decode_vin_values_extended(valid_vin_lowercase)
        assert isinstance(result, VINDecodeResult)

    @responses.activate
    def test_invalid_vin_raises_error(self, invalid_vin_short):
        """Test that invalid VIN raises InvalidVINError"""
        with pytest.raises(InvalidVINError):
            decode_vin_values_extended(invalid_vin_short)

    def test_api_timeout(self, valid_vin, mocker):
        """Test handling of API timeout"""
        # Clear cache first
        decode_vin_values_extended.cache_clear()

        mocker.patch('requests.get', side_effect=Timeout("Connection timeout"))

        with pytest.raises(NetworkError, match="Failed to reach NHTSA API"):
            decode_vin_values_extended(valid_vin)

    def test_api_connection_error(self, valid_vin, mocker):
        """Test handling of connection error"""
        decode_vin_values_extended.cache_clear()
        mocker.patch('requests.get', side_effect=ConnectionError("Connection refused"))

        with pytest.raises(NetworkError, match="Failed to reach NHTSA API"):
            decode_vin_values_extended(valid_vin)

    @responses.activate
    def test_api_http_error(self, valid_vin):
        """Test handling of HTTP error status codes"""
        decode_vin_values_extended.cache_clear()
        responses.add(
            responses.GET,
            f"https://vpic.nhtsa.dot.gov/api/vehicles/DecodeVinValuesExtended/{valid_vin}",
            json={"error": "Internal Server Error"},
            status=500,
        )

        with pytest.raises(NetworkError, match="Failed to reach NHTSA API"):
            decode_vin_values_extended(valid_vin)

    @responses.activate
    def test_api_no_results(self, valid_vin):
        """Test handling when API returns no results"""
        decode_vin_values_extended.cache_clear()
        responses.add(
            responses.GET,
            f"https://vpic.nhtsa.dot.gov/api/vehicles/DecodeVinValuesExtended/{valid_vin}",
            json={"Count": 0, "Results": []},
            status=200,
        )

        with pytest.raises(APIError, match="No results returned from API"):
            decode_vin_values_extended(valid_vin)

    @responses.activate
    def test_api_error_code_nonzero(self, valid_vin):
        """Test handling when API returns error code"""
        decode_vin_values_extended.cache_clear()
        error_response = {
            "Count": 1,
            "Results": [
                {
                    "VIN": valid_vin,
                    "ErrorCode": "1",
                    "ErrorText": "Check digit validation failed",
                }
            ],
        }
        responses.add(
            responses.GET,
            f"https://vpic.nhtsa.dot.gov/api/vehicles/DecodeVinValuesExtended/{valid_vin}",
            json=error_response,
            status=200,
        )

        with pytest.raises(APIError, match="API Error: Check digit validation failed"):
            decode_vin_values_extended(valid_vin)

    @responses.activate
    def test_caching(self, valid_vin, sample_api_response):
        """Test that results are cached"""
        # Clear cache first
        decode_vin_values_extended.cache_clear()

        responses.add(
            responses.GET,
            f"https://vpic.nhtsa.dot.gov/api/vehicles/DecodeVinValuesExtended/{valid_vin}",
            json=sample_api_response,
            status=200,
        )

        # First call
        result1 = decode_vin_values_extended(valid_vin)
        assert len(responses.calls) == 1

        # Second call should use cache
        result2 = decode_vin_values_extended(valid_vin)
        assert len(responses.calls) == 1  # Still 1, not 2

        assert result1.vin == result2.vin

    @responses.activate
    def test_api_with_wildcard_vin(self, sample_api_response):
        """Test API call with wildcard VIN"""
        wildcard_vin = "5UXWX7C50BA******"
        responses.add(
            responses.GET,
            f"https://vpic.nhtsa.dot.gov/api/vehicles/DecodeVinValuesExtended/{wildcard_vin}",
            json=sample_api_response,
            status=200,
        )

        result = decode_vin_values_extended(wildcard_vin)
        assert isinstance(result, VINDecodeResult)

    @responses.activate
    def test_empty_string_fields_converted_to_none(self, valid_vin):
        """Test that empty string fields are converted to None by Pydantic validator"""
        decode_vin_values_extended.cache_clear()
        response_with_empty_strings = {
            "Count": 1,
            "Results": [
                {
                    "VIN": valid_vin,
                    "Make": "BMW",
                    "Model": "",  # Empty string
                    "ModelYear": "2011",
                    "Trim": "",  # Empty string
                    "ErrorCode": "0",
                }
            ],
        }
        responses.add(
            responses.GET,
            f"https://vpic.nhtsa.dot.gov/api/vehicles/DecodeVinValuesExtended/{valid_vin}",
            json=response_with_empty_strings,
            status=200,
        )

        result = decode_vin_values_extended(valid_vin)
        assert result.model is None
        assert result.trim is None
        assert result.make == "BMW"


class TestCacheClearing:
    """Tests for cache management"""

    @responses.activate
    def test_cache_info(self, valid_vin, sample_api_response):
        """Test cache info reporting"""
        decode_vin_values_extended.cache_clear()

        responses.add(
            responses.GET,
            f"https://vpic.nhtsa.dot.gov/api/vehicles/DecodeVinValuesExtended/{valid_vin}",
            json=sample_api_response,
            status=200,
        )

        cache_info = decode_vin_values_extended.cache_info()
        assert cache_info.hits == 0
        assert cache_info.misses == 0

        decode_vin_values_extended(valid_vin)
        cache_info = decode_vin_values_extended.cache_info()
        assert cache_info.misses == 1

        decode_vin_values_extended(valid_vin)
        cache_info = decode_vin_values_extended.cache_info()
        assert cache_info.hits == 1
