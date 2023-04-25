import pytest


@pytest.mark.usefixtures("list_view")
async def test_list_api_view(client, dummy_data):
    response = await client.get("/test")
    assert response.json() == [dummy_data]
    assert response.status_code == 200


@pytest.mark.usefixtures("retrieve_view")
async def test_retrieve_api_view(client, dummy_data):
    response = await client.get("/test")
    assert response.json() == dummy_data
    assert response.status_code == 200


@pytest.mark.usefixtures("create_view")
async def test_create_api_view(client, dummy_data):
    response = await client.post("/test")
    assert response.json() == dummy_data
    assert response.status_code == 201


# @pytest.mark.usefixtures("destroy_view")
# async def test_destroy_api_view(client):
#     response = await client.delete("/test")
#     assert response.status_code == 204
