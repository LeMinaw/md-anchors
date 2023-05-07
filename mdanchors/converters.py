"""Module to perform conversion operations on Markdown / CommonMark anchors."""

import re


def replace_at(span, string, pattern):
    """Return a copy of `string` where the `span` range is replaced by
    `pattern`.
    """
    start, end = span
    return string[:start] + pattern + string[end:]


def offset_span(span, inf, sup=None):
    """Return a copy of the input `span` with offset inferior and superior
    bounds.

    If a single offset is specified, both bounds will be equally offset.
    """
    if sup is None:
        sup = inf

    return (x + offset for x, offset in zip(span, (inf, sup)))


class AnchorConverter:
    """Class allowing to perform anchor conversions operations on a Markdown /
    CommonMark source text.
    """
    # Match inline URIs
    inlines_exp = re.compile(r'[^]]\s*\[[^()[\]]*\]\s?\((?P<uri>[^()[\]]+)\)')
    # Match inline anchors identifiers
    anchors_exp = re.compile(r'\[[^()[\]]*\]\s?\[(?P<ref>[^()[\]]+)\]')
    # Match reference-style anchors
    references_exp = re.compile(
        r'^\s*\[(?P<ref>[^()[\]]+)\]\s*:\s*(?P<uri>[^\r\n]*)\s*$', re.M
    )

    def __init__(self, text):
        self.text = text

    @property
    def uris(self):
        """Get a set of all URIs of the markdown document, both inline or
        reference-style.

        Unused references will also be returned.
        """
        return self._find_inline_uris() | self._find_ref_uris()

    def _find_inline_uris(self):
        return set(self.inlines_exp.findall(self.text))

    def _find_ref_uris(self):
        return set(
            match.group('uri').strip()  # This will remove trailing
            for match in self.references_exp.finditer(self.text)
        )

    def find_anchors(self):
        """Get a set of all existing reference-style anchor identifiers in the
        markdown document.

        This searches identifiers in both the markdown "body" and existing
        references.
        """
        return set(
            self.anchors_exp.findall(self.text)
            + [m.group('ref') for m in self.references_exp.finditer(self.text)]
        )

    def to_reference_links(self):
        """Return a copy of the markdown document, where inline links are moved
        to reference-style links.
        """
        text = self.text
        uris = {} # Format: {uri: anchor}
        existing_anchors = self.find_anchors()
        last_anchor_idx = 0

        for match in self.inlines_exp.finditer(text):
            uri = match.group('uri')
            # Because links are replaced by anchors identifiers, the length of
            # the document changes over iterations. This corrects the span of
            # the matched group to reflect this.
            offset = len(text) - len(self.text)
            span = offset_span(match.span(1), offset)
            # Correct the span to take into account starting `(` and ending `)`
            span = offset_span(span, -1, 1)

            # If it exists, use the previous anchor for this URI, else generate
            # a new one.
            if uri in uris:
                anchor = uris[uri]
            else:
                last_anchor_idx += 1
                anchor = str(last_anchor_idx)
            # Check if the found/generated anchor is not already used somewhere
            # else in the document, and change it if needed.
            while anchor in existing_anchors:
                last_anchor_idx += 1
                anchor = str(last_anchor_idx)

            uris[uri] = anchor
            text = replace_at(span, text, f'[{anchor}]')

        # Add new references at the end of the document
        if uris:
            text += '\n'
        for uri, anchor in uris.items():
            text += f'[{anchor}]: {uri}\n'

        return text

    def to_inline_links(self):
        """Return a copy of the markdown document, where reference links are
        moved to inline-style links.

        If a reference can't be resolved, it will be kept as-is.
        """
        text = self.text
        inline_matches = tuple(self.anchors_exp.finditer(text))

        for match in self.references_exp.finditer(text):
            anchor, uri = map(str.strip, match.groups())

            for inline_match in inline_matches:
                if inline_match.group('ref') == anchor:
                    offset = len(text) - len(self.text)
                    span = offset_span(
                        inline_match.span(1), offset - 1, offset + 1
                    )

                    text = replace_at(span, text, f"({uri})")

        # Remove reference-style anchor
        text = re.sub(self.references_exp, '', text)

        return text.rstrip('\n') + '\n'
