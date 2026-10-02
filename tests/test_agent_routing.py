import pytest
from agent_graph import route_macro_to_micro, route_setup_to_trigger, dispatch_all_reports

class TestRoutingLogic:
    def test_route_macro_proceeds_on_bullish(self):
        state = {"macro_trend_h1": "BULLISH"}
        assert route_macro_to_micro(state) == "proceed_to_m15"

    def test_route_macro_proceeds_on_bearish(self):
        state = {"macro_trend_h1": "BEARISH"}
        assert route_macro_to_micro(state) == "proceed_to_m15"

    def test_route_macro_aborts_on_sideways(self):
        state = {"macro_trend_h1": "SIDEWAYS"}
        assert route_macro_to_micro(state) == "abort_to_dispatch"

    def test_route_macro_aborts_on_empty_or_unknown(self):
        state = {"macro_trend_h1": ""}
        assert route_macro_to_micro(state) == "abort_to_dispatch"

    def test_route_setup_proceeds_when_valid(self):
        state = {"is_m15_setup_valid": True}
        assert route_setup_to_trigger(state) == "proceed_to_m5"

    def test_route_setup_aborts_when_invalid(self):
        state = {"is_m15_setup_valid": False}
        assert route_setup_to_trigger(state) == "abort_to_dispatch"


class TestDispatchLogic:
    def test_dispatch_sets_sideways_final_action(self, monkeypatch):
        # Prevent actual network calls
        monkeypatch.setattr("agent_graph.send_telegram_report", lambda s: {"execution_logs": ["tg_mock"]})
        monkeypatch.setattr("agent_graph.send_web_report", lambda s: {"execution_logs": ["web_mock"]})

        state = {
            "macro_trend_h1": "SIDEWAYS",
            "is_m15_setup_valid": False,
            "final_action": "IDLE"
        }
        res = dispatch_all_reports(state)
        assert res["final_action"] == "STANDBY_SIDEWAYS_MARKET"

    def test_dispatch_sets_no_setup_final_action(self, monkeypatch):
        monkeypatch.setattr("agent_graph.send_telegram_report", lambda s: {"execution_logs": ["tg_mock"]})
        monkeypatch.setattr("agent_graph.send_web_report", lambda s: {"execution_logs": ["web_mock"]})

        state = {
            "macro_trend_h1": "BULLISH",
            "is_m15_setup_valid": False,
            "final_action": "IDLE"
        }
        res = dispatch_all_reports(state)
        assert res["final_action"] == "STANDBY_NO_VALID_SETUP"
