import requests

DOCS_GITHUB_URL = "https://github.com/jagath-jaikumar/RescueBox/wiki"
REFERENCE_RAW_MARKDOWN_URL = (
    "https://raw.githubusercontent.com/wiki/jagath-jaikumar/RescueBox/Reference.md"
)


def download_reference_doc():
    response = requests.get(REFERENCE_RAW_MARKDOWN_URL)
    return response.text
