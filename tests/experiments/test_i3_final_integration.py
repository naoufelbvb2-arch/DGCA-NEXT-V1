"""Cross-milestone production acceptance; no fixture learning or topology."""

from i3_final_integration import run_chain


def test_one_database_cold_learning_novelty_and_atomic_rewiring(tmp_path):
    trace = run_chain(tmp_path / "integrated.sqlite")
    assert trace["local"]["state"] == "CONSOLIDATED"
    assert trace["local"]["count"] >= 2 and trace["associative"]["count"] >= 2
    assert trace["age"] == 100 and trace["serial"] == 104
    assert trace["novelty_q6"] >= 300_000 and trace["changes"]
