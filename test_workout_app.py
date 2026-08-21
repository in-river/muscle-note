import importlib.util
from pathlib import Path

MODULE_PATH = Path(__file__).with_name("workout_app.py")
spec = importlib.util.spec_from_file_location("workout_app", MODULE_PATH)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def test_default_exercise_categories_are_present():
    exercise_map = module.get_default_exercise_map()
    assert set(exercise_map) == {"プッシュ", "プル", "スクワット"}
    assert "ベンチプレス" in exercise_map["プッシュ"]
    assert "チンニング" in exercise_map["プル"]
    assert "スクワット" in exercise_map["スクワット"]


def test_history_records_include_date_and_measurements():
    sample = [
        {
            "日付": "2026-08-21",
            "種目": "ベンチプレス",
            "重量": 60.0,
            "回数": 8,
            "セット数": 3,
        }
    ]
    rows = module.build_history_rows(sample)
    assert rows[0]["日付"] == "2026-08-21"
    assert rows[0]["種目"] == "ベンチプレス"
    assert rows[0]["重量"] == 60.0
    assert rows[0]["回数"] == 8
