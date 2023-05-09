from uuid import uuid4

import pytest


@pytest.mark.usefixtures("generic_viewset")
async def test_list_generic_api_view(client, dummy_data):
    response = await client.get("/test")
    assert response.json() == [dummy_data]
    assert response.status_code == 200


@pytest.mark.usefixtures("generic_viewset")
async def test_retrieve_generic_api_view(client, dummy_data):
    response = await client.get(f"/test/{uuid4()}")
    assert response.json() == dummy_data
    assert response.status_code == 200


@pytest.mark.usefixtures("generic_viewset")
async def test_create_generic_api_view(client, dummy_data):
    response = await client.post("/test", json={"x": "test"})
    assert response.json() == dummy_data
    assert response.status_code == 201


@pytest.mark.usefixtures("generic_viewset")
async def test_destroy_generic_api_view(client):
    response = await client.delete(f"/test/{uuid4()}")
    assert response.status_code == 204
