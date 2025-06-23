from typing import Any, Protocol, TypeVar
from pathlib import Path
import csv
import json

# Define protocols
class FileReader(Protocol):
    def read(self, filepath: str) -> Any: ...

class FileProcessor(Protocol):
    def process(self, data: Any) -> Any: ...

class FileWriter(Protocol):
    def write(self, data: Any, filepath: str) -> None: ...

T = TypeVar('T')

class ProcessingPipeline:
    def __init__(
        self,
        reader: FileReader,
        processor: FileProcessor,
        writer: FileWriter
    ):
        self.reader = reader
        self.processor = processor
        self.writer = writer

    def run(self, input_path: str, output_path: str) -> None:
        data = self.reader.read(input_path)
        processed_data = self.processor.process(data)
        self.writer.write(processed_data, output_path)

# CSV Implementations
class CSVReader:
    def read(self, filepath: str) -> list[dict]:
        with open(filepath) as f:
            return list(csv.DictReader(f))

class CSVValidator:
    def process(self, data: list[dict]) -> list[dict]:
        if not all(isinstance(row, dict) for row in data):
            raise ValueError("Invalid CSV data format")
        return data

class CSVWriter:
    def write(self, data: list[dict], filepath: str) -> None:
        with open(filepath, 'w') as f:
            writer = csv.DictWriter(f, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)

# JSON Implementations
class JSONReader:
    def read(self, filepath: str) -> Any:
        with open(filepath) as f:
            return json.load(f)

class JSONTransformer:
    def process(self, data: Any) -> Any:
        if isinstance(data, dict):
            return {k.upper(): v for k, v in data.items()}
        return data

class JSONWriter:
    def write(self, data: Any, filepath: str) -> None:
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)

# Text Implementations
class TextReader:
    def read(self, filepath: str) -> str:
        return Path(filepath).read_text()

class TextReverser:
    def process(self, data: str) -> str:
        return data[::-1]

class TextWriter:
    def write(self, data: str, filepath: str) -> None:
        Path(filepath).write_text(data)

# Example Usage
if __name__ == "__main__":
    # CSV Pipeline
    csv_pipeline = ProcessingPipeline(
        CSVReader(),
        CSVValidator(),
        CSVWriter()
    )
    csv_pipeline.run("input.csv", "output.csv")

    # JSON Pipeline
    json_pipeline = ProcessingPipeline(
        JSONReader(),
        JSONTransformer(),
        JSONWriter()
    )
    json_pipeline.run("input.json", "output.json")

    # Text Pipeline
    text_pipeline = ProcessingPipeline(
        TextReader(),
        TextReverser(),
        TextWriter()
    )
    text_pipeline.run("input.txt", "output.txt")
