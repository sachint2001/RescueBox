from text_summary.main import app as cli_app, APP_NAME, task_schema
from rb.lib.common_tests import RBAppTest
from rb.api.models import AppMetadata


class TestTextSummary(RBAppTest):
    def setup_method(self):
        self.set_app(cli_app, APP_NAME)

    def get_metadata(self):
        return AppMetadata(
            name="Text Summarization",
            author="UMass Rescue",
            version="0.1.0",
            info="Summarize text and PDF files in a directory.",
        )

    def get_all_ml_services(self):
        return [
            (0, "summarize", "Text Summarization", task_schema()),
        ]
