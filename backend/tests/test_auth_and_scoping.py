import pytest

routes = [
    ("/upload", "post", 401),
    ("/ingest", "post", 401),
    ("/chat", "post", 401),
    ("/files", "get", 401),
]


@pytest.mark.parametrize("route,method,expected_code", routes)
def test_protected_routes_missing_auth(client, route, method, expected_code):
    """Requests without auth should return 401 Unauthorized."""
    res = getattr(client, method)(route)
    assert res.status_code == expected_code
    assert "error" in res.json or res.data


@pytest.mark.parametrize("route,method,_", routes)
def test_protected_routes_with_auth(client, auth_headers, route, method, _):
    """Requests with valid auth should not return 401 Unauthorized."""
    res = getattr(client, method)(route, headers=auth_headers)
    assert res.status_code in [
        200,
        201,
        204,
        400,
        403,
    ]  # Acceptable codes for protected endpoints
