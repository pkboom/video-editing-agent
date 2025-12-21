import asyncio
from pathlib import Path

import pytest

from lib import cut_video
from lib.llm import VideoEdit


class FakeSegment:
    def __init__(self, start: float, end: float):
        self.start = start
        self.end = end
        self.write_calls: list[str] = []

    def write_videofile(self, path: str, **_: object) -> None:
        path_obj = Path(path)
        path_obj.parent.mkdir(parents=True, exist_ok=True)
        path_obj.write_bytes(b"segment")
        self.write_calls.append(path)


class FakeClip:
    def __init__(self, duration: float):
        self.duration = duration
        self.subclip_calls: list[tuple[float, float]] = []
        self.segments: list[FakeSegment] = []

    def subclipped(self, start: float, end: float) -> FakeSegment:
        self.subclip_calls.append((start, end))
        segment = FakeSegment(start, end)
        self.segments.append(segment)
        return segment

    def close(self) -> None:
        pass


class CombinedClip:
    def __init__(self, clips: list[FakeSegment]):
        self.clips = clips
        self.write_calls: list[str] = []

    def write_videofile(self, path: str, **_: object) -> None:
        Path(path).write_bytes(b"final")
        self.write_calls.append(path)


@pytest.mark.parametrize(
    "start, end, duration, expected_range",
    [
        (5.0, 10.0, 20.0, (3.0, 12.0)),  # trims start and end by 2 seconds
        (1.0, 14.0, 15.0, (0.0, 15.0)),  # clamps to bounds when near edges
    ],
)
def test_cut_video_segments_exports_segments(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    start: float,
    end: float,
    duration: float,
    expected_range: tuple[float, float],
) -> None:
    fake_clip = FakeClip(duration)
    concat_calls: list[list[tuple[float, float]]] = []
    combined_holder: dict[str, CombinedClip] = {}

    def fake_video_file_clip(_: str) -> FakeClip:
        return fake_clip

    def fake_concatenate(clips: list[FakeSegment]) -> CombinedClip:
        concat_calls.append([(c.start, c.end) for c in clips])
        combined = CombinedClip(clips)
        combined_holder["clip"] = combined
        return combined

    monkeypatch.setattr(cut_video, "VideoFileClip", fake_video_file_clip)
    monkeypatch.setattr(cut_video, "concatenate_videoclips", fake_concatenate)
    monkeypatch.chdir(tmp_path)

    edits = [VideoEdit(start=start, end=end, targeted_script_snippet="line")]  # type: ignore[arg-type]

    output_path = asyncio.run(
        cut_video.cut_video_segments(str(tmp_path / "video.mp4"), edits)
    )

    assert fake_clip.subclip_calls == [expected_range]

    expected_segment_name = (
        f"segment_001_{expected_range[0]:.1f}s-{expected_range[1]:.1f}s.mp4"
    )
    segment_path = tmp_path / "exports" / expected_segment_name
    assert segment_path.exists()

    assert concat_calls == [[expected_range]]
    assert combined_holder["clip"].write_calls == [output_path]
    assert Path(output_path).exists()

    with open(segment_path, "rb") as fh:
        assert fh.read() == b"segment"


def test_cut_video_segments_accepts_result_wrapper(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    fake_clip = FakeClip(duration=8.0)

    class Wrapped:
        def __init__(self, edits: list[VideoEdit]):
            self.content = type("Content", (), {"edits": edits})

    def fake_video_file_clip(_: str) -> FakeClip:
        return fake_clip

    def fake_concatenate(clips: list[FakeSegment]) -> CombinedClip:
        return CombinedClip(clips)

    monkeypatch.setattr(cut_video, "VideoFileClip", fake_video_file_clip)
    monkeypatch.setattr(cut_video, "concatenate_videoclips", fake_concatenate)
    monkeypatch.chdir(tmp_path)

    edits = [VideoEdit(start=2, end=4, targeted_script_snippet="line")]  # type: ignore[arg-type]
    wrapped = Wrapped(edits)

    asyncio.run(cut_video.cut_video_segments(str(tmp_path / "video.mp4"), wrapped))

    assert fake_clip.subclip_calls == [(0, 6)]

    expected_segment = tmp_path / "exports" / "segment_001_0.0s-6.0s.mp4"
    assert expected_segment.exists()
