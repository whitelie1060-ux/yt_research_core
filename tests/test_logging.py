import logging
from yt_research_core.logging import setup_logger


def test_setup_logger_no_duplicate_handlers(tmp_path):
    name = "yt_core_test_dedup"
    logging.getLogger(name).handlers.clear()
    l1 = setup_logger(name, log_dir=tmp_path)
    l2 = setup_logger(name, log_dir=tmp_path)
    assert l1 is l2
    assert len(l2.handlers) == 2  # file + stream


def test_setup_logger_creates_log_dir(tmp_path):
    target = tmp_path / "nested" / "logs"
    setup_logger("yt_core_test_mkdir", log_dir=target)
    assert target.is_dir()
