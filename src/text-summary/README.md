# Text Summarization

This repository contains an LLM based text summarization model. The model is designed to summarize files containing text (.txt/.pdf/.md) into concise summaries.

Follow the instructions below to run the server.

### Install dependencies

Run this in the root directory of the project:
```
poetry install
```

Activate the environment:
```
poetry env activate
```

### Using the CLI

You can use the CLI to summarize text files. Run this in the root directory of the project:
```
poetry run python text_summary/cli.py --input_dir example_files --output_dir output --model gemma3:1b
```

### Start the server

Run this in the root directory of the project:
```
python -m text_summary.server
```

Use [RescueBox-Desktop](https://github.com/UMass-Rescue/RescueBox-Desktop) to connect to the server and classify images.
