from mdanchors import AnchorConverter


def test_find_existing_anchors():
    text = (
        "Hello, [this article][article] looks great.\n"
        "And [this one][not referenced] goes nowhere.\n"
        "\n"
        "[article]: uri://hello\n"
        "   [unused]:uri://not_in_use_poorly_formatted.abc\n"
    )
    assert (AnchorConverter(text).find_anchors()
            == {'article', 'not referenced', 'unused'})


def test_convert_to_ref():
    text = (
        "Hello, [this article](uri://hello) looks great.\n"
        "And [this one](uri://other) looks great too.\n"
        "[The same] (uri://hello) again!\n"
    )
    assert AnchorConverter(text).to_reference_links() == (
        "Hello, [this article][1] looks great.\n"
        "And [this one][2] looks great too.\n"
        "[The same] [1] again!\n"
        "\n"
        "[1]: uri://hello\n"
        "[2]: uri://other\n"
    )


def test_convert_to_ref_conflicting():
    text = (
        "Hello, [this article](uri://hello) looks great.\n"
        "And [this one](uri://other) looks great too.\n"
        "\n"
        "[2]: some stuff to annoy you\n"
        "[3]: more stuff to annoy you\n"
    )
    assert AnchorConverter(text).to_reference_links() == (
        "Hello, [this article][1] looks great.\n"
        "And [this one][4] looks great too.\n"
        "\n"
        "[2]: some stuff to annoy you\n"
        "[3]: more stuff to annoy you\n"
        "\n"
        "[1]: uri://hello\n"
        "[4]: uri://other\n"
    )


def test_convert_to_ref_noop():
    text = (
        "Hello, (nothing needs converting here) [I mean, really].\n"
        "[A link][ref] to prove it.\n"
        "\n"
        "[ref]: something\n"
    )
    assert AnchorConverter(text).to_reference_links() == text


def test_convert_to_inline():
    text = (
        "Hello, [this article][1] looks great.\n"
        "And [this one](uri://hello) looks great too.\n"
        "[The same] [1] again!\n"
        "And [this][10] goes nowhere.\n"
        "A [last one][2].\n"
        "\n"
        "[1]: uri://hi\n"
        "[2]: uri://other\n"
        "[3]: uri://unused\n"
    )
    assert AnchorConverter(text).to_inline_links() == (
        "Hello, [this article](uri://hi) looks great.\n"
        "And [this one](uri://hello) looks great too.\n"
        "[The same] (uri://hi) again!\n"
        "And [this][10] goes nowhere.\n"
        "A [last one](uri://other).\n"
    )


def test_convert_to_inline_noop():
    text = (
        "Hello, (nothing needs converting here) (I mean, really).\n"
        "[A link](something) to prove it.\n"
        "Plus [this][ref].\n"
    )
    assert AnchorConverter(text).to_inline_links() == text


def test_get_uris():
    text = (
        "Hello, [this article][1] looks great.\n"
        "And [this one](uri://hello) looks great too.\n"
        "\n"
        "[1]: uri://hi\n"
        "[2]: uri://other\n"
        "[3]: uri://unused\n"
    )
    assert AnchorConverter(text).uris == {
        "uri://hello",
        "uri://hi",
        "uri://other",
        "uri://unused"
    }


def test_get_uris_brakets():
    text = (
        "Hello, [something][1] (some more info).\n"
        "Some [other stuff][2][hey].\n"
        "\n"
        "[1]: uri://hello\n"
        "[2]: uri://other\n"
    )
    assert AnchorConverter(text).uris == { "uri://hello", "uri://other" }


def test_get_uris_crlf():
    text = (
        "Hello, [inline link][1], [inline link][2].\r\n"
        "\r\n"
        "[1]: uri://hi\r\n"
        "[2]: uri://other\r\n"
    )
    assert AnchorConverter(text).uris == { "uri://hi", "uri://other" }


def test_get_uris_none():
    text = (
        "Hello, (no uris here) [I mean, really].\n"
        "[A link][ref] to nothing.\n"
    )
    assert AnchorConverter(text).uris == set()
