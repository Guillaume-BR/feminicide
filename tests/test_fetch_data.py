import json
from unittest.mock import patch

from scripts.fetch_data import (
    download_resource,
    get_yearly_resources,
    load_state,
    needs_update,
    save_state,
)


def test_get_yearly_resources():
    with patch("scripts.fetch_data.requests.get") as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            "resources": [
                {
                    "title": "Féminicides 2020",
                    "url": "https://example.com/feminicide_2020.csv",
                    "last_modified": "2024-01-01T00:00:00Z",
                },
                {
                    "title": "Féminicides 2021",
                    "url": "https://example.com/feminicide_2021.csv",
                    "last_modified": "2024-01-02T00:00:00Z",
                },
            ]
        }
        result = get_yearly_resources()
        expected = {
            "2020": {
                "url": "https://example.com/feminicide_2020.csv",
                "last_modified": "2024-01-01T00:00:00Z",
            },
            "2021": {
                "url": "https://example.com/feminicide_2021.csv",
                "last_modified": "2024-01-02T00:00:00Z",
            },
        }
        assert result == expected


def test_get_yearly_resources_no_years():
    with patch("scripts.fetch_data.requests.get") as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            "resources": [
                {
                    "title": "Some other resource",
                    "url": "https://example.com/other_resource.csv",
                    "last_modified": "2024-01-01T00:00:00Z",
                }
            ]
        }
        result = get_yearly_resources()
        expected = {}
        assert result == expected


def test_download_resource(tmp_path):
    url = "https://example.com/feminicide_2020.csv"
    year = "2020"
    content = b"col1,col2\nval1,val2"

    with patch("scripts.fetch_data.requests.get") as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.content = content

        dest_path = download_resource(year, url, dest_dir=tmp_path)
        assert dest_path.exists()
        assert dest_path.read_bytes() == content


def test_save_state(tmp_path):
    state = {"2020": "2024-01-01T00:00:00Z", "2021": "2024-01-02T00:00:00Z"}
    tmp_file = tmp_path / "state.json"
    save_state(tmp_file, state)
    assert tmp_file.exists()
    loaded_state = load_state(tmp_file)
    assert loaded_state == state


def test_load_state(tmp_path):
    state = {"2020": "2024-01-01T00:00:00Z", "2021": "2024-01-02T00:00:00Z"}
    tmp_file = tmp_path / "state.json"
    tmp_file.write_text(json.dumps(state))
    loaded_state = load_state(tmp_file)
    assert loaded_state == state

    # Test loading from a non-existent file
    non_existent_file = tmp_path / "non_existent.json"
    loaded_state = load_state(non_existent_file)
    assert loaded_state == {}


def test_needs_update():
    assert needs_update("2024-01-01T00:00:00Z", "2023-12-31T23:59:59Z")
    assert not needs_update("2024-01-01T00:00:00Z", "2024-01-01T00:00:00Z")
    assert needs_update("2023-12-31T23:59:59Z", "2024-01-01T00:00:00Z")
