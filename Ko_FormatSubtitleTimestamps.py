import re

# ---------- Timestamp Fixer Functions ----------


def convert_timestamp_line(line):
    """
    First Pass: If a line is exactly a short timestamp (m:ss or mm:ss),
    convert it to full format: 00:MM:SS.000. If it's already full (HH:MM:SS.fff),
    leave it unchanged.
    """
    stripped = line.strip()
    # Already a full timestamp? (e.g. "00:00:01.000")
    if re.fullmatch(r"\d{2}:\d{2}:\d{2}\.\d{3}", stripped):
        return line
    # Match exactly m:ss or mm:ss (e.g. "0:01" or "00:01")
    if re.fullmatch(r"\d{1,2}:\d{2}", stripped):
        parts = stripped.split(":")
        minute = parts[0]
        sec = parts[1]
        minute_padded = minute.zfill(2)
        return f"00:{minute_padded}:{sec}.000\n"
    # Otherwise, leave the line unchanged.
    return line


def subtract_ten_ms(ts):
    """
    Given a timestamp in the form HH:MM:SS.fff, subtract 10 milliseconds.
    The function properly handles borrowing across seconds, minutes, and hours.
    """
    hh = int(ts[0:2])
    mm = int(ts[3:5])
    ss = int(ts[6:8])
    fff = int(ts[9:12])
    total_ms = ((hh * 3600) + (mm * 60) + ss) * 1000 + fff
    new_total_ms = max(total_ms - 10, 0)
    new_hh = new_total_ms // 3600000
    rem = new_total_ms % 3600000
    new_mm = rem // 60000
    rem = rem % 60000
    new_ss = rem // 1000
    new_fff = rem % 1000
    return f"{new_hh:02d}:{new_mm:02d}:{new_ss:02d}.{new_fff:03d}"


def add_ms(ts, delta_ms):
    """
    Given a timestamp in the form HH:MM:SS.fff, add delta_ms milliseconds.
    """
    hh = int(ts[0:2])
    mm = int(ts[3:5])
    ss = int(ts[6:8])
    fff = int(ts[9:12])

    total_ms = ((hh * 3600) + (mm * 60) + ss) * 1000 + fff
    new_total_ms = max(total_ms + delta_ms, 0)

    new_hh = new_total_ms // 3600000
    rem = new_total_ms % 3600000
    new_mm = rem // 60000
    rem = rem % 60000
    new_ss = rem // 1000
    new_fff = rem % 1000

    return f"{new_hh:02d}:{new_mm:02d}:{new_ss:02d}.{new_fff:03d}"


def second_pass(lines):
    """
    Second Pass: For every line that is exactly a full timestamp (HH:MM:SS.fff),
    look ahead for the next full timestamp line. Append to the current timestamp line
    " --> " and the modified (10 ms subtracted) version of the next timestamp.
    """
    new_lines = []
    full_ts_pattern = re.compile(r"^\d{2}:\d{2}:\d{2}\.\d{3}$")
    for i, line in enumerate(lines):
        if full_ts_pattern.fullmatch(line.strip()):
            current_ts = line.strip()
            next_ts = None
            # Look ahead for the next full timestamp line.
            for j in range(i + 1, len(lines)):
                if full_ts_pattern.fullmatch(lines[j].strip()):
                    next_ts = lines[j].strip()
                    break
            # If a full timestamp pattern, the subtract time to make a new end stamp on previous pattern
            if next_ts:
                end_ts = subtract_ten_ms(next_ts)
            # If no end stamp at end of text, then add one with a default of 3000 ms or 3 seconds
            else:
                end_ts = add_ms(current_ts, 3000)

            # Create a complete timestamp pattern for every line including last line
            new_line = f"{current_ts} --> {end_ts}\n"
            new_lines.append(new_line)
        else:
            new_lines.append(line)
    return new_lines


def third_pass(lines):
    """
    Third Pass: Insert block numbers before each timestamp block.
    A timestamp block is identified by a line that matches:
       HH:MM:SS.fff --> HH:MM:SS.fff
    For the first block, insert the block number with no extra preceding blank line.
    For subsequent blocks, insert exactly one blank line before the block number.
    """
    new_lines = []
    timestamp_pattern = re.compile(
        r"^\d{2}:\d{2}:\d{2}\.\d{3}\s*-->\s*\d{2}:\d{2}:\d{2}\.\d{3}"
    )
    block_number = 1
    for line in lines:
        if timestamp_pattern.match(line):
            if block_number == 1:
                new_lines.append(f"{block_number}\n")
            else:
                new_lines.append("\n")
                new_lines.append(f"{block_number}\n")
            new_lines.append(line)
            block_number += 1
        else:
            new_lines.append(line)
    return new_lines


# ---------- Main Program ----------


def main():
    # Ask user for the input SRT file
    user_input = input(
        'YouTube 자막 파일의 전체 경로를 .txt 형식으로 입력하세요(경로 내 ""는 자동으로 제거됩니다): '
    ).strip()

    input_filename = user_input.strip('"')

    # ---------- First Part: Timestamp Processing ----------
    with open(input_filename, "r", encoding="utf-8") as infile:
        lines = infile.readlines()

    # Convert any short timestamp lines to full HH:MM:SS.fff format.
    first_pass_lines = [convert_timestamp_line(line) for line in lines]
    second_pass_lines = second_pass(first_pass_lines)
    third_pass_lines = third_pass(second_pass_lines)

    # Combine processed lines into a single content string.
    content = "".join(third_pass_lines)

    # Remove file extension from path
    delete_extension = input_filename[:-3]

    output_path = delete_extension + "srt"
    with open(output_path, "w", encoding="utf-8") as outfile:
        outfile.write(content)
    print("서식이 적용된 자막 파일이 저장되었습니다:", output_path)


if __name__ == "__main__":
    main()
