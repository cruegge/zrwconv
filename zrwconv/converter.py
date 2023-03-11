import mammoth
import mammoth.html as html
import mammoth.documents
import mammoth.writers
import mammoth.results

LITERATURE_HEADINGS = frozenset(
    [
        "Literatur",
        "Literatur und Quellen",
        "Quellen",
    ]
)

FOOTNOTE_HEADING = "Anmerkungen"

# NOTE These styles appear to be used somewhat inconsistently in the .docx file, so we can't
# really use them for conversion purposes. Therefore, we default most of them simply to
# p:fresh for paragraphs and empty for run, primarily to suppress warning messages. The ones
# that are not defaulted are at the top.
#
# “Kleindrucktext” appears to be used for quotations, but transforming them to
# "blockquote:fresh" makes them appear way too large. Another option might be "p:fresh > q",
# but that adds a level of quotation marks, which often already appears in the quotes
# themselves. So stick to <p> with a class.

STYLE_MAP = """
# Special

p[style-name='B_Überschrift (Rubrik:Beitrag)'] => h1:fresh
p[style-name='B_Untertitel (Rubrik:Beitrag)'] => h2:fresh
p[style-name='B_Kleindrucktext (Rubrik:Beitrag)'] => p.quote:fresh
p[style-name='B_Kleindrucktext_o_Einzug (Rubrik:Beitrag)'] => p.quote:fresh

r[style-name='Italic'] => i
r[style-name='Semibold'] => strong

# Default

p[style-name='_Fußnote (Rubrik:Beitrag)'] => p:fresh
p[style-name='Artikel_Autor (Rubrik:Artikel)'] => p:fresh
p[style-name='Artikel_Fließtext (Rubrik:Artikel)'] => p:fresh
p[style-name='Autorenangaben (Rubrik:Artikel)'] => p:fresh
p[style-name='B_Author (Rubrik:Beitrag)'] => p:fresh
p[style-name='B_Fließtext (Rubrik:Beitrag)'] => p:fresh
p[style-name='B_Hervorhebung (Rubrik:Beitrag)'] => p:fresh
p[style-name='B_Literaturliste_G (Rubrik:Beitrag)'] => p:fresh
p[style-name='B_Literaturliste_oG (Rubrik:Beitrag)'] => p:fresh

r[style-name='Fußnotenziffer'] =>
r[style-name='Fußnotenziffer_unten'] =>
r[style-name='Artikel_Spitzmarke'] =>
"""


class Converter(mammoth.conversion._DocumentConverter):
    def __init__(self, **options):
        super().__init__(**options)
        self._literature = []
        self._collecting_literature = False

    def visit_note_reference(self, note_reference, context):
        self._note_references.append(note_reference)
        return [html.text(note_reference.note_id)]

    def visit_note(self, note, context):
        note_html = self._visit_all(note.body, context)
        if len(note_html) == 1 and note_html[0].tag_name == "p":
            # Unpack unneeded single paragraphs
            note_html = note_html[0].children
        return [html.element("li", {}, note_html)]

    def visit_paragraph(self, paragraph, context):
        result = []
        for elem in super().visit_paragraph(paragraph, context):
            if elem.tag.tag_name == "h3":
                self._collecting_literature = (
                    extract_text_from_node(elem) in LITERATURE_HEADINGS
                )
            if self._collecting_literature:
                if elem.tag.tag_name == "p":
                    elem.tag.attributes["class"] = "ezw-citation"
                self._literature.append(elem)
            else:
                result.append(elem)
        return result

    def visit_document(self, document, context):
        nodes = self._visit_all(document.children, context)
        self._collecting_literature = False
        if footnotes := self._visit_all(
            map(document.notes.resolve, self._note_references), context
        ):
            nodes.append(html.element("h3", {}, [html.text(FOOTNOTE_HEADING)]))
            nodes.append(html.element("ol", {"class": "ezw-footnotes"}, footnotes))
        if self._literature:
            nodes.extend(self._literature)
        return nodes


def extract_text_from_node(node):
    try:
        return node.value
    except AttributeError:
        return "".join(extract_text_from_node(child) for child in node.children)


def heading_heuristic(paragraph):
    runs = mammoth.transforms.get_descendants_of_type(paragraph, mammoth.documents.Run)
    if runs and all(
        run.is_bold or mammoth.extract_raw_text_from_element(run).isspace()
        for run in runs
    ):
        for run in runs:
            run.is_bold = False
        return mammoth.documents.Paragraph(
            children=runs,
            style_id="Heading3",
            style_name="Heading 3",
            numbering=None,
            alignment=None,
            indent=None,
        )
    else:
        return paragraph


def ensure_superscript_footnote_refs(paragraph):
    for run in mammoth.transforms.get_descendants_of_type(
        paragraph, mammoth.documents.Run
    ):
        if any(isinstance(c, mammoth.documents.NoteReference) for c in run.children):
            run.vertical_alignment = "superscript"
    return paragraph


def convert_file(fileobj):
    messages = []

    def collect(result):
        messages.extend(result.messages)
        return result.value

    options = collect(
        mammoth.options.read_options(
            {
                "style_map": STYLE_MAP,
                "embedded_style_map": mammoth.read_style_map(fileobj),
            }
        )
    )

    document = collect(mammoth.docx.read(fileobj))
    document = mammoth.transforms.paragraph(heading_heuristic)(document)
    document = mammoth.transforms.paragraph(ensure_superscript_footnote_refs)(document)

    converter = Converter(
        messages=messages,
        convert_image=lambda *args, **kwargs: {},
        id_prefix="",
        note_references=[],
        comments={},
        **options,
    )
    nodes = converter.visit(
        document, mammoth.conversion._ConversionContext(is_table_header=False)
    )

    writer = mammoth.writers.HtmlWriter()
    html.write(writer, html.collapse(html.strip_empty(nodes)))
    result_html = writer.as_string()

    return result_html, messages
