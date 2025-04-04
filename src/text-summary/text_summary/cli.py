import argparse
from text_summary.model import SUPPORTED_MODELS
from text_summary.summarize import process_files

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Summarize text and PDF files in a directory."
    )
    parser.add_argument(
        "--input_dir", help="Path to input directory containing the input files"
    )
    parser.add_argument(
        "--output_dir", help="Path to output directory for summary files"
    )
    parser.add_argument(
        "--model",
        choices=SUPPORTED_MODELS,
        default="gemma3:1b",
        help="Model to use for summarization (default: gemma3:1b)",
    )
    args = parser.parse_args()

    process_files(args.model, args.input_dir, args.output_dir)
