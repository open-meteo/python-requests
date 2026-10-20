"""Offline tests for size-prefixed weather responses."""

from __future__ import annotations

from unittest.mock import AsyncMock, Mock

import pytest
from flatbuffers import Builder
from niquests import AsyncSession, Response, Session

from openmeteo_requests import AsyncClient, Client, OpenMeteoRequestsError
from openmeteo_requests.Client import _process_response


@pytest.fixture
def message() -> bytes:
    builder = Builder(64)
    builder.StartObject(2)
    builder.PrependFloat32Slot(0, 52.5, 0.0)
    builder.PrependFloat32Slot(1, 13.4, 0.0)
    root = builder.EndObject()
    builder.FinishSizePrefixed(root)
    return bytes(builder.Output())


def response_with(data: bytes) -> Response:
    response = Response()
    response._content = data  # noqa: SLF001
    return response


def test_complete_messages(message: bytes) -> None:
    responses = _process_response(response_with(message + message))

    assert len(responses) == 2
    for response in responses:
        assert response.Latitude() == pytest.approx(52.5)
        assert response.Longitude() == pytest.approx(13.4)


def test_empty_response() -> None:
    assert _process_response(response_with(b"")) == []


@pytest.mark.parametrize("prefix_length", [1, 2, 3])
def test_truncated_prefix(message: bytes, prefix_length: int) -> None:
    with pytest.raises(OpenMeteoRequestsError, match="[Tt]runcated.*prefix"):
        _process_response(response_with(message + message[:prefix_length]))


@pytest.mark.parametrize("preceding_message", [False, True])
def test_truncated_message(message: bytes, *, preceding_message: bool) -> None:
    data = (message if preceding_message else b"") + message[:-1]

    with pytest.raises(OpenMeteoRequestsError, match="[Tt]runcated.*message"):
        _process_response(response_with(data))


@pytest.mark.parametrize("length", [0, 1, 2, 3])
def test_invalid_message_length(message: bytes, length: int) -> None:
    data = length.to_bytes(4, byteorder="little") + message[4:]

    with pytest.raises(OpenMeteoRequestsError, match="[Ii]nvalid.*length"):
        _process_response(response_with(data))


def test_oversized_message_length(message: bytes) -> None:
    data = len(message).to_bytes(4, byteorder="little") + message[4:]

    with pytest.raises(OpenMeteoRequestsError, match="[Tt]runcated.*message"):
        _process_response(response_with(data))


@pytest.mark.parametrize("preceding_message", [False, True])
def test_stream_error(message: bytes, *, preceding_message: bool) -> None:
    error = b"Unexpected error while streaming data: timeoutReached"
    data = (message if preceding_message else b"") + error

    with pytest.raises(OpenMeteoRequestsError, match=error.decode()):
        _process_response(response_with(data))


def test_client_rejects_truncated_response(message: bytes) -> None:
    response = response_with(message[:-1])
    response.status_code = 200
    session = Mock(spec=Session)
    session.get.return_value = response

    with pytest.raises(OpenMeteoRequestsError, match="failed to request.*Truncated"):
        Client(session).weather_api("https://example.com/forecast", params={})


@pytest.mark.asyncio
async def test_async_client_rejects_truncated_response(message: bytes) -> None:
    response = response_with(message[:-1])
    response.status_code = 200
    session = AsyncMock(spec=AsyncSession)
    session.get.return_value = response

    with pytest.raises(OpenMeteoRequestsError, match="failed to request.*Truncated"):
        await AsyncClient(session).weather_api("https://example.com/forecast", params={})
