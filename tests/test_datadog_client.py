from unittest.mock import patch

from doghouse.datadog_client import DatadogClient

config = {
    'app_key': 'test_app_key',
    'api_key': 'test_api_key'
}


@patch('doghouse.datadog_client.yaml.safe_load', return_value=config)
def test_load_yaml(mocked_yaml):
    d = DatadogClient()
    mocked_yaml.assert_called()
    assert d.api_key == 'test_api_key'
    assert d.app_key == 'test_app_key'


@patch('doghouse.datadog_client.yaml.dump')
@patch('doghouse.datadog_client.DatadogClient._load_config', return_value=None)
@patch('builtins.input', return_value="api_or_app_key")
@patch('doghouse.datadog_client.DatadogClient.default_config_file', return_value=".")
def test_no_config_file(input_func, load_config, mocked_yaml_create, mocked_file):
    d = DatadogClient()
    assert d.api_key == 'api_or_app_key'
    assert d.app_key == 'api_or_app_key'
