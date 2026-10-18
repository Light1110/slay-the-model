"""Disabled-option enforcement and optional-selection skipping across input modes."""
import asyncio
import concurrent.futures
from types import SimpleNamespace
from typing import Any, cast

import pytest
from textual.app import App, ComposeResult
from textual.widgets import Button

from actions.base import LambdaAction
from actions.display import InputRequestAction, build_selected_options
from engine.game_state import game_state
from engine.input_protocol import InputRequest
from localization import set_language, t
from tui.app import SelectionPanel
from tui.handlers.selection_handler import SelectionHandler
from utils.option import Option, match_option_command, selection_error


def choices(executed):
    return [
        Option('Locked', [LambdaAction(lambda: executed.append('locked'))], enabled=False, commands=['locked'], disabled_reason='Need 50 gold'),
        Option('Available', [LambdaAction(lambda: executed.append('available'))], commands=['available']),
        Option('Other', [LambdaAction(lambda: executed.append('other'))]),
    ]


@pytest.mark.parametrize('indices', [[0], [1, 0], [1, 1], [1, 3], [-1], [True], [1, 'bad']])
def test_final_builder_rejects_entire_invalid_selection(indices):
    executed = []
    options = choices(executed)
    assert build_selected_options(options, indices) == {}
    submission = game_state.runtime_context.default_build_submission(options, indices)
    for action in submission.actions:
        action.execute()
    assert executed == []
    assert game_state.last_select_idx == -1


def test_builder_preserves_original_index_and_order_for_valid_multi_select():
    executed = []
    options = choices(executed)
    assert list(build_selected_options(options, [2, 1])) == [2, 1]
    submission = game_state.runtime_context.default_build_submission(options, [2, 1])
    for action in submission.actions:
        action.execute()
    assert executed == ['other', 'available']
    assert game_state.last_select_idx == 2


@pytest.mark.parametrize('indices,maximum,required', [
    ([], 1, True), ([1], 2, True), ([1, 2], 1, False), ([1, 1], 2, True),
])
def test_shared_validation_checks_required_and_maximum_counts(indices, maximum, required):
    assert selection_error(choices([]), indices, maximum, required) is not None


def test_select_all_counts_enabled_options_and_aliases_keep_original_indices():
    options = choices([])
    assert selection_error(options, [1, 2], -1, True) is None
    assert match_option_command('locked', options) is None
    assert match_option_command('available', options) == [1]


@pytest.mark.parametrize('raw', ['1', 'locked', '2,2', '2,1', '2,4', '2,,3', '0,2'])
def test_cli_reprompts_for_locked_or_invalid_input(monkeypatch, raw):
    game_state.config.mode = 'human'
    game_state.config.auto_select = False
    executed = []
    inputs = iter([raw, '2'])
    monkeypatch.setattr('builtins.input', lambda prompt: next(inputs))
    submission = game_state.resolve_input_request(InputRequest(options=choices(executed)))
    for action in submission.actions:
        action.execute()
    assert executed == ['available']


@pytest.mark.parametrize('language', ['en', 'zh'])
def test_cli_optional_skip_is_explicit_and_runs_no_actions(monkeypatch, capsys, language):
    set_language(language)
    game_state.config.mode = 'human'
    game_state.config.auto_select = False
    prompts = []
    monkeypatch.setattr('builtins.input', lambda prompt: prompts.append(prompt) or '0')
    submission = game_state.resolve_input_request(InputRequest(options=choices([]), must_select=False))
    assert submission.actions == []
    assert game_state.last_select_idx == -1
    assert f'0. {t("ui.selection_skip")}' in capsys.readouterr().out
    assert '0-' in prompts[0]
    assert t('ui.selection_skip').lower() in prompts[0].lower()


def test_cli_required_selection_rejects_skip_and_displays_locked_reason(monkeypatch, capsys):
    game_state.config.mode = 'human'
    game_state.config.auto_select = False
    inputs = iter(['0', 'available'])
    prompts = []
    monkeypatch.setattr('builtins.input', lambda prompt: prompts.append(prompt) or next(inputs))
    submission = game_state.resolve_input_request(InputRequest(options=choices([])))
    assert len(submission.actions) == 1
    output = capsys.readouterr().out
    assert 'Need 50 gold' in output
    assert '0. Skip' not in output
    assert all('0-' not in prompt for prompt in prompts)


@pytest.mark.parametrize('select_type,expected', [('first', [1]), ('last', [2]), ('random', None)])
def test_debug_never_selects_locked_options(select_type, expected):
    game_state.config.mode = 'debug'
    game_state.config.debug['select_type'] = select_type
    request = InputRequest(options=choices([]))
    indices = game_state.runtime_context.default_resolve_debug_selection(request)
    assert indices == expected if expected is not None else indices[0] in (1, 2)
    game_state.config.debug['select_type'] = 'first'
    request.max_select = -1
    assert game_state.runtime_context.default_resolve_debug_selection(request) == [1, 2]


def test_debug_heuristic_ignores_high_scoring_locked_option(monkeypatch):
    game_state.config.debug['select_type'] = 'random'
    cast(Any, game_state).current_combat = SimpleNamespace()
    monkeypatch.setattr(game_state, '_score_debug_option', lambda option: 100 if not option.enabled else 1)
    result = game_state.runtime_context.default_resolve_debug_selection(InputRequest(options=choices([])))
    assert result == [1]


def test_ai_sees_locked_state_and_skip_and_retries_invalid_choice():
    game_state.config.mode = 'ai'
    game_state.config.auto_select = False
    seen = []
    class AI:
        def make_decision(self, title, option_text, context, max_select):
            seen.append((title, option_text, context))
            return [0] if len(seen) == 1 else [1]
    cast(Any, game_state).decision_engine = AI()
    submission = game_state.resolve_input_request(InputRequest(options=choices([]), must_select=False))
    assert len(seen) == 2
    assert 'Locked' in seen[0][1][0]
    assert '[]' in seen[0][0]
    assert seen[0][2]['disabled_indices'] == [0]
    assert not seen[0][2]['must_select']
    assert len(submission.actions) == 1


def test_ai_can_skip_optional_request_with_empty_list():
    game_state.config.mode = 'ai'
    game_state.config.auto_select = False
    cast(Any, game_state).decision_engine = SimpleNamespace(make_decision=lambda *args: [])
    assert game_state.resolve_input_request(InputRequest(options=choices([]), must_select=False)).actions == []


def test_ai_repeated_invalid_output_fails_without_partial_execution():
    game_state.config.mode = 'ai'
    game_state.config.auto_select = False
    executed = []
    cast(Any, game_state).decision_engine = SimpleNamespace(make_decision=lambda *args: [1, 0])
    with pytest.raises(ValueError):
        game_state.resolve_input_request(InputRequest(options=choices(executed), max_select=2))
    assert executed == []


def test_validation_runs_before_overridden_submission_builder(monkeypatch):
    game_state.config.mode = 'debug'
    game_state.config.auto_select = False
    calls = []
    monkeypatch.setattr(game_state, '_resolve_debug_selection', lambda request: [1, 0])
    monkeypatch.setattr(game_state, '_build_submission', lambda *args: calls.append(args))
    with pytest.raises(ValueError):
        game_state.resolve_input_request(InputRequest(options=choices([]), max_select=2))
    assert calls == []


def test_single_locked_option_is_not_auto_executed():
    game_state.config.auto_select = True
    request = InputRequest(options=[Option('Locked', [], enabled=False)])
    with pytest.raises(ValueError):
        game_state.resolve_input_request(request)
    request.must_select = False
    assert game_state.resolve_input_request(request).actions == []


def test_legacy_handler_blocks_locked_clicks_and_supports_optional_zero():
    app = SimpleNamespace(show_selection=lambda *args, **kwargs: None)
    handler = SelectionHandler(app)
    handler.show_selection(InputRequestAction(options=choices([]), must_select=False))
    assert not handler.select_by_index(0)
    assert handler.get_result() is None
    assert handler.select_by_index(1)
    assert handler.get_result() == 1
    assert handler.handle_input('0')
    assert handler.get_result() == []
    handler.show_selection(InputRequestAction(options=choices([])))
    assert not handler.handle_input('0')


def test_panel_rejects_invalid_numbers_aliases_and_direct_callbacks(monkeypatch):
    panel = SelectionPanel()
    panel._options_data = choices([])
    panel._must_select = True
    errors = []
    monkeypatch.setattr(panel, '_show_validation_error', errors.append)
    future: concurrent.futures.Future[list[int]] = concurrent.futures.Future()
    panel._selection_future = future
    for raw in ('1', 'locked', '2,2', '0', '2,,3'):
        assert panel._parse_indices(raw) is None
    assert not panel.select_by_index(0)
    panel._resolve_selection([0])
    assert not future.done()
    assert errors
    assert panel._parse_indices('available') == [1]
    panel._must_select = False
    assert panel._parse_indices('0') == []


@pytest.mark.parametrize('language', ['en', 'zh'])
def test_panel_localizes_skip_and_locked_status_without_renumbering(language):
    set_language(language)
    panel = SelectionPanel()
    text = '\n'.join(panel._build_selection_lines('Pick', choices([]), 1, False))
    assert f'0.[/cyan] {t("ui.selection_skip")}' in text
    assert '1.' in text and '2.' in text and '3.' in text
    assert t('ui.selection_locked', name='Locked') in text
    assert 'Need 50 gold' in text
    mandatory = '\n'.join(panel._build_selection_lines('Pick', choices([]), 1, True))
    assert '0.' not in mandatory


def test_tui_skip_button_resolves_empty_future_and_is_hidden_for_required_selection():
    class TestApp(App):
        CSS = 'SelectionPanel { height: auto; } #selection-content { height: auto; }'

        def compose(self) -> ComposeResult:
            yield SelectionPanel(id='panel')
    async def exercise():
        app = TestApp()
        async with app.run_test() as pilot:
            panel = app.query_one(SelectionPanel)
            future: concurrent.futures.Future[list[int]] = concurrent.futures.Future()
            panel.set_selection('Pick', choices([]), must_select=False, future=future)
            button = app.query_one('#selection-skip', Button)
            assert button.display
            await pilot.pause()
            await pilot.click('#selection-skip')
            await pilot.pause()
            assert future.done()
            assert future.result(timeout=1) == []
            panel.set_selection('Required', choices([]), must_select=True)
            assert not button.display
    asyncio.run(exercise())
