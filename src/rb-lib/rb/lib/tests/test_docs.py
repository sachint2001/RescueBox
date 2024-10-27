from rb.lib.docs import download_reference_doc


def test_download_reference_doc():
    reference_doc = download_reference_doc()
    assert reference_doc is not None
    assert "rescuebox" in reference_doc
