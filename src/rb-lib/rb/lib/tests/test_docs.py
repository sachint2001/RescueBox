from rb.lib.docs import download_all_wiki_pages


def test_download_all_wiki_pages():
    wiki_content = download_all_wiki_pages()

    # Ensure that at least one wiki page is retrieved
    assert wiki_content is not None, "Failed: No wiki content retrieved"
    assert isinstance(wiki_content, dict), "Failed: Returned data is not a dictionary"
    assert len(wiki_content) > 0, "Failed: No pages found in the wiki"

    # Check that at least one page contains expected keywords
    found_valid_page = any(
        "RescueBox" in content or "UMass" in content
        for content in wiki_content.values()
    )
    assert found_valid_page, "Failed: No retrieved pages contain expected content"
