"""Integration tests for Transip"""
import re
from unittest import TestCase

import pytest

from lexicon.tests.providers.integration_tests import (
    IntegrationTestsV2,
    vcr_integration_test,
)

FAKE_KEY = """
-----BEGIN RSA PRIVATE KEY-----
MIIEpAIBAAKCAQEAxV08IlJRwNq9WyyGO2xRyT0F6XIBD2R5CrwJoP7gIHVU/Mhk
KeK8//+MbUZtKFoeJi9lI8Cbkqe7GVk9yab6R2/vVzV21XRh+57R79nEh+QTf/vZ
dg+DjUn62U4lcgoVp3sHddIi/Zi58xz2a2lGGIdolsv1x0/PmAQPULt721IG/osp
RBjTtaZ8niXrOTfjH814i8kgXu74CCGu0X6kJBIezMA2wqY1ZKZYRMpfrxkEZe0t
45pEM1CmSTCqyDMpwYou9wJaDHn0ts1KvKkKBfmO4B0nqfW9Sv9rkmpBCLTtMobj
dQ8EwWv1L1g9uddkPALgRODEpR4fq7PTmq2VEQIDAQABAoIBAFf4wwEZaE9qMNUe
94YtNhdZF/WCV26g/kMGpdQZR5WwNv2l5N+2rT/+jH140tcVtDKZFZ/mDnJESWV3
Hc9wmkaVYj2hGyLyCWq61CDxFGTuCLMXc0roh17HBwUtjAtU62oHsL+XtvkKxnfT
BRPDjPcKBFiS+S6qKII97QWzS/XpxL47VpXcYboVunzUncIKghC93LdvPp3ukh6x
HIarqyctqkksLJtLgH5ffuABCJLChetpOIfcfspjtMoji43CXXd7Y3rGWy3EzSHA
s4mNb4K6r8MOlJj3HiTn9bEgL2V2q3OHSYHYXexir67vkQeN+NsC80G0uODt6Uuo
Cd1RobECgYEA+O+nZYRc22jI8oqRoQeCx6cTWJoaf4OYDXcaerRMIiE7yigHNgmX
LGs9RYTVrWXzjM5KHVvPvavpm/zIBoa5fA7uqdH9BjuZVLm1COXzKxF5hevZuAxr
zGQWDbdvzdsihPBvwlf0dKScA/WIRW0KCqUmC6IlS/An4Y0nI05P+KsCgYEAyvby
cfUPgeanBnYE3GGou3cLiurzvK3vHuQl6vVE3DcheUj/5tKTwG5Q3/7y51MKHnfH
xEc/X2IePXYVy0JwpC6NHzkyJPuJ1zYlkQGSs81TUbYOk9SKi3SL9bM+3vRzYFoL
GMLJuvEqIscxLNqR0xQB5eBkg8T+AVJiA7cTITMCgYEAn5/ND2OYx3ihoiUIzOEs
EyonVaE7bJjNX5UH/bavOxNka3TPau8raOg7GeDbw5ykV53QGJNO2qjp24R0Hvs0
5UAN+gcU4HJHF/UdCN+q1esWqbFaopIUbbOgEJuXrcDembAzecM8la8X+9Ht19bb
oYfUpZELqW4NpKwGdLU6wpECgYAfn3hI3xjKcYiGji7Vs3WZt8OZol/VfvgpxPxP
bmWLNh/GCOSuLxMMQWPicpOgDSUfeCQs5bjvAJebleFxaOmp+wLL4Zp5fqOMX4hc
3nTgBNa9fXMp/0ySy9besk3SaR3s3jqqYfcSZG7fOk/kIC3mSFC/Y0Xl7fRxekeB
Mq4NVwKBgQDQ+3+cgZph5geq0PUuKMvMECDuCEnG8rrr4jTCe+sRP34y1IaxJ2w6
S6p+kvTBePSqV2wWZCls6p7mhGEto+8H9b4pWdmSqccn0vFu4kekm/OU4+IxqzWQ
KPeh76yhdzsFwzh+0LBPfkFgFn3YlHp0eoywNpm57MFxWx8u3U2Hkw==
-----END RSA PRIVATE KEY-----
"""

# Currently TransipProviderTests class is configured to use a fake key so that the CI system does
# not need an actual key when integration tests are run with the recorded cassettes.
# If you want to run again manually the integration tests against the live API, and so use a valid
# a real key, please modify the following elements in this file:
#  - comment out the setUp function,
#  - comment out the tearDown function,
#  - remove auth_api_key entry from the dict returned by _test_parameters_overrides function.


class TransipProviderTests(TestCase, IntegrationTestsV2):
    """TestCase for Transip"""

    provider_name = "transip"
    domain = "nuvius.nl"

    @vcr_integration_test
    def test_provider_when_calling_create_record_for_CNAME_with_valid_name_and_content(
        self,
    ):
        provider = self._construct_authenticated_provider()
        # TransIP CNAME records values must be a FQDN with trailing dot for external domains.
        assert provider.create_record("CNAME", "docs", "docs.example.com.")

    @pytest.fixture(autouse=True)
    def _generate_fake_key(self, tmp_path):
        self._fake_key = tmp_path / "key.pem"
        self._fake_key.write_text(FAKE_KEY)

    def _filter_headers(self):
        return ["Signature", "Authorization"]

    def _filter_post_data_parameters(self):
        return ["login"]

    def _filter_response(self, response):
        response["body"]["string"] = re.sub(
            rb'"token":"[\w.-]+"',
            b'"token":"TOKEN"',
            response["body"]["string"],
        )
        response["body"]["string"] = re.sub(
            rb'"authCode":"[\w.-]+"',
            b'"authCode":"AUTH_CODE"',
            response["body"]["string"],
        )
        return response

    def _test_parameters_overrides(self):
        return {"auth_api_key": str(self._fake_key), "auth_key_is_global": True}
