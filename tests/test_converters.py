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


def test_convert_anchors():
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


def test_convert_conflicting_anchors():
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


def test_convert_noop():
    text = (
        "Hello, (nothing needs converting here) [I mean, really].\n"
        "[A link][ref] to prove it.\n"
        "\n"
        "[ref]: something\n"
    )
    assert AnchorConverter(text).to_reference_links() == text
