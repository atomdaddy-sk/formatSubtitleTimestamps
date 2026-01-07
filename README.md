# YouTube Transcript (.txt) → SRT Converter

This Python script converts a YouTube-style transcript text file into an `.srt` subtitle file by normalizing timestamps, generating end times, and inserting sequential block numbers.
(User must first copy a transcript from a YouTube video and save it as a .txt file.)

## Features

- Converts short timestamps like `m:ss` / `mm:ss` into full `HH:MM:SS.fff` (example: `1:05` → `00:01:05.000`).
- Generates a complete SRT-style time range for every timestamp line (`start --> end`).
- Sets each cue’s end time to **10 ms before** the next cue’s start time.
- If the final timestamp has no following timestamp, it assigns a default duration of **3 seconds** (3000 ms).
- Inserts SRT block numbers (`1`, `2`, `3`, ...) with blank lines between blocks.

## Requirements

- Python 3.x (no third-party packages; uses only the Python standard library).

## Input format (expected)

The script expects a `.txt` file containing timestamp lines and subtitle text lines, just as one sees and can copy from the YouTube "Show transcript" function found in the description of a YouTube video. For example:

```txt
0:01
Hello

00:00:05.000
Another line
```

Notes:

- Timestamp lines may be either `m:ss` / `mm:ss` or full `HH:MM:SS.fff`.
- Non-timestamp lines are treated as subtitle text and are passed through unchanged.


## Output

- Creates an `.srt` file next to the input file by replacing the `.txt` extension with `.srt`.
- Output cues look like:

```txt
1
00:00:01.000 --> 00:00:04.990
Hello
```


## How to run

1. Save the script (for example as `FormatSubtitleTimestamps.py`).
2. Run it from a terminal:
```bash
python FormatSubtitleTimestamps.py
```

3. When prompted, paste the full path to the `.txt` transcript file.
    - If your path is wrapped in quotes, no problem; the script removes surrounding `"` automatically.

## Notes \& limitations

- The script assumes that each timestamp line marks the start of a new subtitle cue.
- The final cue duration is fixed at 3 seconds; change `add_ms(current_ts, 3000)` if a different default is preferred.
- The timestamp format used is `HH:MM:SS.fff` (dot + milliseconds), which many tools accept, but some strict SubRip workflows expect `HH:MM:SS,mmm` (comma).


## Customization

- Default last-cue duration: change `3000` in `add_ms(current_ts, 3000)` to another value in milliseconds.
- Gap before next cue: change the `subtract_ten_ms()` logic if you want a bigger/smaller gap than 10 ms.
