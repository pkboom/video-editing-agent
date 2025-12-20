import asyncio
from pathlib import Path

import pytest

from app_tabs import split_tab


class UploadedFileStub:
    def __init__(self, name: str = "demo.mp4", data: bytes = b"video-bytes"):
        self.name = name
        self._data = data

    def getbuffer(self) -> bytes:
        return self._data


class SessionState(dict):
    def __getattr__(self, key):
        return self[key]

    def __setattr__(self, key, value):
        self[key] = value


class ProgressStub:
    def __init__(self, store: list[float]):
        self.values = store

    def progress(self, value: float) -> None:
        self.values.append(value)


class StatusStub:
    def __init__(self, messages: list[str]):
        self.messages = messages

    def text(self, message: str) -> None:
        self.messages.append(message)


class StreamlitStub:
    def __init__(self):
        self.session_state = SessionState()
        self.errors: list[str] = []
        self.warnings: list[str] = []
        self.successes: list[str] = []
        self.writes: list[str] = []
        self.downloads: list[dict] = []
        self.progress_calls: list[float] = []
        self.status_messages: list[str] = []

    def progress(self, value: float) -> ProgressStub:
        self.progress_calls.append(value)
        return ProgressStub(self.progress_calls)

    def empty(self) -> StatusStub:
        return StatusStub(self.status_messages)

    def error(self, message: str) -> None:
        self.errors.append(message)

    def write(self, message: str) -> None:
        self.writes.append(message)

    def success(self, message: str) -> None:
        self.successes.append(message)

    def warning(self, message: str) -> None:
        self.warnings.append(message)

    def download_button(self, **kwargs) -> None:
        self.downloads.append(kwargs)


class FakeClip:
    def __init__(self, duration: float):
        self.duration = duration
        self.subclip_calls: list[tuple[float, float]] = []
        self.written_paths: list[Path] = []
        self.closed_segments: list[tuple[float, float]] = []
        self.closed = False

    def subclipped(self, start: float, end: float) -> "FakeSegment":
        self.subclip_calls.append((start, end))
        return FakeSegment(self, start, end)

    def close(self) -> None:
        self.closed = True


class FakeSegment:
    def __init__(self, parent: FakeClip, start: float, end: float):
        self.parent = parent
        self.start = start
        self.end = end
        self.closed = False

    def write_videofile(self, path: str, **_: object) -> None:
        path_obj = Path(path)
        path_obj.parent.mkdir(parents=True, exist_ok=True)
        path_obj.write_bytes(b"segment")
        self.parent.written_paths.append(path_obj)

    def close(self) -> None:
        self.closed = True
        self.parent.closed_segments.append((self.start, self.end))


def setup_split_env(monkeypatch: pytest.MonkeyPatch, tmp_path: Path, duration: float):
    st_stub = StreamlitStub()
    st_stub.session_state["split_zip_file_path"] = "old.zip"

    fake_clip = FakeClip(duration)

    async def fake_zip(exports_directory: str, temp_directory: str) -> str:
        zip_path = Path(temp_directory) / "fake.zip"
        zip_path.write_bytes(b"zip-bytes")
        return str(zip_path)

    monkeypatch.setattr(split_tab, "st", st_stub)
    monkeypatch.setattr(split_tab, "VideoFileClip", lambda _: fake_clip)
    monkeypatch.setattr(split_tab, "zip_and_download_files", fake_zip)
    monkeypatch.chdir(tmp_path)

    return st_stub, fake_clip


def test_split_video_writes_segments_and_zip(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    st_stub, fake_clip = setup_split_env(monkeypatch, tmp_path, duration=10)
    uploaded_file = UploadedFileStub("demo.mp4", b"file-bytes")

    asyncio.run(split_tab.split_video(uploaded_file, 3))

    exports_dirs = list((tmp_path / "exports").iterdir())
    assert len(exports_dirs) == 1
    run_dir = exports_dirs[0]
    part_names = sorted(path.name for path in run_dir.iterdir())
    assert part_names == [
        "split_demo.mp4_part_01.mp4",
        "split_demo.mp4_part_02.mp4",
        "split_demo.mp4_part_03.mp4",
    ]

    assert fake_clip.subclip_calls[0][0] == 0
    assert fake_clip.subclip_calls[0][1] == pytest.approx(10 / 3)
    assert fake_clip.subclip_calls[1][0] == pytest.approx(10 / 3)
    assert fake_clip.subclip_calls[1][1] == pytest.approx(20 / 3)
    assert fake_clip.subclip_calls[2][0] == pytest.approx(20 / 3)
    assert fake_clip.subclip_calls[2][1] == 10
    assert len(fake_clip.closed_segments) == 3
    assert fake_clip.closed is True

    assert st_stub.session_state["split_zip_file_path"].endswith("fake.zip")
    assert st_stub.downloads[-1]["file_name"] == "split_files.zip"
    assert st_stub.downloads[-1]["data"] == b"zip-bytes"
    assert "old.zip" not in st_stub.session_state.values()

    assert not st_stub.errors
    assert st_stub.successes


def test_split_video_handles_zero_duration(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    st_stub, fake_clip = setup_split_env(monkeypatch, tmp_path, duration=0)
    uploaded_file = UploadedFileStub("demo.mp4", b"file-bytes")

    asyncio.run(split_tab.split_video(uploaded_file, 2))

    assert any("no duration" in err.lower() for err in st_stub.errors)
    assert "split_zip_file_path" not in st_stub.session_state
    assert not st_stub.downloads
    assert fake_clip.closed is True
