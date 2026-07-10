"""Tests for router."""

from astra_d.routing.router import Router
from astra_d.routing.types import Intent


def test_router_returns_chat():
    router = Router()
    assert router.route("Hello") is Intent.CHAT


def test_router_returns_help():
    router = Router()
    assert router.route("help") is Intent.HELP


def test_router_returns_task():
    router = Router()
    assert router.route("task list") is Intent.TASK


def test_router_returns_exit():
    router = Router()
    assert router.route("exit") is Intent.EXIT