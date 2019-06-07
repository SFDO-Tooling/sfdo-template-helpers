from unittest.mock import patch
import datetime
import logging
from types import SimpleNamespace

from sfdo_template_helpers.logfmt_utils import JobIDFilter, LogfmtFormatter


def test_job_id_filter():
    with patch("sfdo_template_helpers.logfmt_utils.get_current_job") as get_id:
        get_id.return_value.id = 123
        log_filter = JobIDFilter()
        record = SimpleNamespace()
        log_filter.filter(record)
        assert record.job_id == 123


def test_job_id_filter__no_job():
    with patch("sfdo_template_helpers.logfmt_utils.get_current_job") as get_id:
        get_id.return_value = None
        log_filter = JobIDFilter()
        record = SimpleNamespace()
        log_filter.filter(record)
        assert record.job_id == "no-job-id"


def test_formatter__record_id():
    record = logging.LogRecord(
        "name", logging.INFO, "module", 1, "Some message", (), None
    )
    record.request_id = 123
    result = LogfmtFormatter().format(record)
    assert "id=123" in result


def test_formatter__job_id():
    record = logging.LogRecord(
        "name", logging.INFO, "module", 1, "Some message", (), None
    )
    record.job_id = 321
    result = LogfmtFormatter().format(record)
    assert "id=321" in result


def test_formatter_format():
    record = logging.LogRecord(
        "name", logging.INFO, "module", 1, "Some message", (), None
    )
    time = datetime.datetime.fromtimestamp(record.created).strftime(
        "%Y-%m-%d %H:%M:%S.%f"
    )

    result = LogfmtFormatter().format(record)
    expected = " ".join(
        [
            f"id=unknown",
            f"at=INFO",
            f'time="{time}"',
            f"tag=external",
            f"module=module",
            f'msg="Some message"',
        ]
    )

    assert result == expected


def test_formatter_format_line():
    extra = {"none": None, "bool": True, "number": 1, "dict": {}, "str": "str"}
    result = LogfmtFormatter().format_line(extra)
    expected = 'none= bool=true number=1 dict="{}" str="str"'

    assert result == expected


def test_formatter_tag():
    record = logging.LogRecord(
        "name", logging.INFO, "module", 1, "Some message", (), None
    )

    record.tag = "some-tag"

    result = LogfmtFormatter()._get_tag(record)
    expected = '"some-tag"'

    assert result == expected


def test_parsed_msg():
    record = logging.LogRecord(
        "name", logging.INFO, "logging_middleware", 1, "foo=bar baz=qux", (), None
    )
    time = datetime.datetime.fromtimestamp(record.created).strftime(
        "%Y-%m-%d %H:%M:%S.%f"
    )

    result = LogfmtFormatter().format(record)
    expected = " ".join(
        [
            f"id=unknown",
            f"at=INFO",
            f'time="{time}"',
            f"tag=external",
            f"module=logging_middleware",
            f"foo=bar",
            f"baz=qux",
        ]
    )

    assert result == expected
