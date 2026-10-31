import os
import json
import argparse
from pathlib import Path

import pandas as pd
from datasets import load_from_disk
from langsmith import traceable

from src.utils import Utils


class Translate:
    def __init__(self):
        self.utils = Utils()

    def _generate_content(self, prompt):
        """Send a fully constructed prompt to Gemini."""
        gemini_model = self.utils.get_gemini_model()
        response = gemini_model.generate_content(prompt)
        return response.text.strip()

    @traceable(name="translation_result", run_type="llm")
    def _generate_translation_result(self, prompt):
        """Generate and trace a translation result."""
        return self._generate_content(prompt)

    @traceable(name="revision_result", run_type="llm")
    def _generate_revision_result(self, prompt):
        """Generate and trace a revision result."""
        return self._generate_content(prompt)

    def translate_to_tetun(self, text):
        """Translate English text to Tetun using the Gemini model."""
        translation_prompt_template = self.utils.read_markdown(
            "prompts/en-tdt-translation-prompt.md"
        )
        prompt = f"""
            {translation_prompt_template}

            Translate the following English text to Tetun, providing only the translated text:

            English: {text}

            Tetun:
        """
        return self._generate_translation_result(prompt)

    def revise_translation(self, text):
        """Revise Tetun translation using the Gemini model."""
        revision_prompt_template = self.utils.read_markdown(
            "prompts/tetun-revision-prompt.md"
        )
        prompt = f"""
            {revision_prompt_template}

            **Output requirements**
            Return only the revised text, without explanations, labels, comments, or additional quotation marks. If no corrections are needed, return the original text exactly as provided.

            **Tetun text to review**

            {text}

            **Revised Tetun:**
        """
        return self._generate_revision_result(prompt)

    @traceable(name="translation_revision", run_type="chain")
    def translate_and_revise(self, text):
        """Translate English text to Tetun and revise it before saving."""
        translated_text = self.translate_to_tetun(text)
        return self.revise_translation(translated_text)

    def translate_record(self, original_input, original_output):
        """Translate and revise both fields in the current record."""
        revised_input = self.translate_and_revise(original_input)
        revised_output = self.translate_and_revise(original_output)
        return revised_input, revised_output

    @staticmethod
    def _write_json(filepath, data):
        """Write JSON data atomically enough for checkpoint recovery."""
        temporary_filepath = f"{filepath}.tmp"
        with open(temporary_filepath, 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=2, ensure_ascii=False)
            file.flush()
            os.fsync(file.fileno())
        os.replace(temporary_filepath, filepath)

    @staticmethod
    def _dataset_cache_path(dataset_name):
        """Return the local cache path for a Hugging Face dataset."""
        cache_name = dataset_name.replace("/", "__").replace("\\", "__")
        translation_directory = Path(__file__).resolve().parent
        return translation_directory / "HF_dataset_to_translate" / cache_name

    def _load_or_download_dataset(self, dataset_name):
        """Load a cached dataset or download and cache it once."""
        cache_path = self._dataset_cache_path(dataset_name)
        if cache_path.exists():
            print(f"Loading cached dataset from {cache_path}")
            return load_from_disk(str(cache_path))

        print(f"Downloading dataset {dataset_name}")
        dataset = self.utils.load_dataset_from_huggingface(dataset_name)
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        dataset.save_to_disk(str(cache_path))
        print(f"Saved dataset cache to {cache_path}")
        return dataset

    @staticmethod
    def _load_output_records(output_filepath):
        """Load output records needed to resume from a checkpoint."""
        if not os.path.exists(output_filepath):
            return []

        with open(output_filepath, 'r', encoding='utf-8') as file:
            records = json.load(file)
        if not isinstance(records, list):
            raise ValueError(f"Output file must contain a JSON list: {output_filepath}")
        return records

    def _save_checkpoint(
        self,
        checkpoint_filepath,
        dataset_name,
        init_range,
        end_range,
        next_index,
    ):
        """Save only the next source index and run metadata for resuming."""
        self._write_json(
            checkpoint_filepath,
            {
                "dataset_name": dataset_name,
                "init_range": init_range,
                "end_range": end_range,
                "next_index": next_index,
            },
        )

    def run(
        self,
        dataset_name: str,
        init_range: int,
        end_range: int,
        output_dir: str,
        output_filename: str,
        checkpoint_filepath: str = None,
    ):
        """Run the translation process for a given text."""
        if not dataset_name or not dataset_name.strip() or dataset_name == "None":
            raise ValueError(
                "A dataset must be defined with the dataset_name argument."
            )
        if init_range < 0:
            raise ValueError("init_range must be non-negative.")
        if end_range is not None and end_range <= init_range:
            raise ValueError("end_range must be greater than init_range.")

        # Load the dataset from the local cache or download it once.
        dataset = self._load_or_download_dataset(dataset_name)
        if end_range is None:
            end_range = len(dataset)
        if end_range > len(dataset):
            raise ValueError(
                f"end_range ({end_range}) cannot exceed dataset length ({len(dataset)})."
            )
        dataset_df = dataset.select(range(init_range, end_range)).to_pandas()[['input', 'output']]

        # Define the output directory and filename
        output_filepath = os.path.join(output_dir, output_filename)
        if checkpoint_filepath is None:
            output_root, _ = os.path.splitext(output_filepath)
            checkpoint_filepath = f"{output_root}_checkpoint.json"

        # Create the directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        checkpoint_directory = os.path.dirname(checkpoint_filepath)
        if checkpoint_directory:
            os.makedirs(checkpoint_directory, exist_ok=True)

        all_translated_flashcards = []
        next_index = init_range
        if os.path.exists(checkpoint_filepath):
            with open(checkpoint_filepath, 'r', encoding='utf-8') as file:
                checkpoint = json.load(file)

            expected_configuration = {
                "dataset_name": dataset_name,
                "init_range": init_range,
                "end_range": end_range,
            }
            actual_configuration = {
                key: checkpoint.get(key)
                for key in expected_configuration
            }
            if actual_configuration != expected_configuration:
                raise ValueError(
                    f"Checkpoint configuration does not match this run: "
                    f"{checkpoint_filepath}"
                )

            next_index = checkpoint.get("next_index", init_range)
            if not init_range <= next_index <= end_range:
                raise ValueError(
                    f"Checkpoint next_index ({next_index}) is outside the requested range."
                )
            if next_index > init_range and not os.path.exists(output_filepath):
                raise ValueError(
                    f"Output file is missing for checkpoint: {output_filepath}"
                )
            all_translated_flashcards = self._load_output_records(output_filepath)
            print(f"Resuming from dataset row {next_index}.")

        total_rows = end_range - init_range

        print("Starting row-by-row translation...")
        for offset, (_, row) in enumerate(dataset_df.iterrows()):
            source_index = init_range + offset
            if source_index < next_index:
                continue

            original_input = row['input']
            original_output = row['output']

            # Skip missing, NaN, empty, or whitespace-only rows
            if (
                pd.isna(original_input)
                or pd.isna(original_output)
                or str(original_input).strip() == ""
                or str(original_output).strip() == ""
            ):
                print(
                    f"  Skipping row {offset + 1}/{total_rows} "
                    "due to missing or empty input/output."
                )
            else:
                # Translate and revise both fields in the current record.
                revised_input, revised_output = self.translate_record(
                    original_input,
                    original_output,
                )
                print(
                    f"  Translated and revised input for row "
                    f"{offset + 1}/{total_rows}"
                )

                print(
                    f"  Translated and revised output for row "
                    f"{offset + 1}/{total_rows}"
                )

                all_translated_flashcards.append({
                    'input': original_input,
                    'input_tdt': revised_input,
                    'output': original_output,
                    'output_tdt': revised_output
                })
                self._write_json(output_filepath, all_translated_flashcards)

            next_index = source_index + 1
            self._save_checkpoint(
                checkpoint_filepath,
                dataset_name,
                init_range,
                end_range,
                next_index,
            )
            print(f"  Saved checkpoint after dataset row {source_index + 1}")

        self._write_json(output_filepath, all_translated_flashcards)
        self._save_checkpoint(
            checkpoint_filepath,
            dataset_name,
            init_range,
            end_range,
            end_range,
        )
        print(f"Saved completed translations to {output_filepath}")
        print("Translation complete for all rows.")


if __name__ == "__main__":
    """Translate English flashcards to Tetun using the Gemini model."""
    parser = argparse.ArgumentParser(
        description="Translate and revise a Hugging Face medical QA dataset."
    )
    parser.add_argument(
        "--dataset-name",
        default=None,
        help="Hugging Face dataset repository to translate.",
    )
    parser.add_argument("--init-range", type=int, default=0)
    parser.add_argument("--end-range", type=int, default=None)
    parser.add_argument("--output-dir", default="translated_docs")
    parser.add_argument("--output-filename", default="translated_docs.json")
    parser.add_argument(
        "--checkpoint-file",
        default=None,
        help="Checkpoint path. Defaults to <output-file> with _checkpoint.json.",
    )
    args = parser.parse_args()
    if not args.dataset_name or not args.dataset_name.strip():
        parser.error("A dataset must be defined with --dataset-name.")

    translator = Translate()
    translator.run(
        dataset_name=args.dataset_name,
        init_range=args.init_range,
        end_range=args.end_range,
        output_dir=args.output_dir,
        output_filename=args.output_filename,
        checkpoint_filepath=args.checkpoint_file,
    )
