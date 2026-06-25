import csv
import io


def parse_csv(csv_content: str) -> list[dict]:
    """
    Parses raw CSV text into a list of plain dicts, one per row.
    Keys come directly from the CSV header row, values are raw strings —
    no cleaning/normalization happens here, that's cleaning.py's job.
    """
    reader = csv.DictReader(io.StringIO(csv_content))
    return list(reader)