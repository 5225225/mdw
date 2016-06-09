import os
import time
import uuid
import difflib

import bottle
import hoep
import pygments
import pygments.lexers
import pygments.formatters


ROOT = os.path.expanduser("~/src/mdw")


def get_title(fname):
    head = open("wiki/{}".format(fname)).readline()
    if head.startswith("# "):
        head = head[2:]
        head = head.strip()
        return head
    else:
        return fname


def valid(path, basedir):
    return os.path.abspath(path).startswith(basedir)


def log_edit(request, before, after):
    result = ""

    before = before.split("\n")
    after = after.split("\n")

    addr = request.remote_addr
    date = time.strftime("%Y-%m-%d %H:%M:%S")
    path = request.path
    edit_uuid = str(uuid.uuid4())

    result += "=== BEGIN EDIT {} ===\n".format(edit_uuid)
    result += "{} {} {}\n".format(date, addr, path)
    for line in difflib.unified_diff(
            before,
            after,
            lineterm="",
            ):

        result += line + "\n"

    result += "=== END EDIT {} ===\n".format(edit_uuid)

    with open("logs/edit.log", "a") as f:
        f.write(result)


extensions = hoep.EXT_AUTOLINK | \
             hoep.EXT_FENCED_CODE | \
             hoep.EXT_DISABLE_INDENTED_CODE | \
             hoep.EXT_FOOTNOTES | \
             hoep.EXT_HIGHLIGHT | \
             hoep.EXT_SPACE_HEADERS | \
             hoep.EXT_NO_INTRA_EMPHASIS | \
             hoep.EXT_STRIKETHROUGH | \
             hoep.EXT_SUPERSCRIPT | \
             hoep.EXT_TABLES

render_flags = hoep.HTML_ESCAPE | \
               hoep.HTML_EXPAND_TABS


class MyRenderer(hoep.Hoep):
    def __init__(self, extensions=0, render_flags=0):
        super(MyRenderer, self).__init__(extensions, render_flags)

    def block_code(self, text, tag):
        lexer = None
        language = None
        filename = None

        if tag is not None:
            language, *filename = tag.split("|")
            filename = "|".join(filename)

            if language == "":
                language = None
            if filename == "":
                filename = None

        if language is not None:
            try:
                lexer = pygments.lexers.get_lexer_by_name(language)
            except pygments.util.ClassNotFound:
                lexer = pygments.lexers.get_lexer_by_name("text")

        formatter = pygments.formatters.HtmlFormatter(
                    linenos="table",
        )

        hlblock = pygments.highlight(text, lexer, formatter)

        return """<table class=codeblock>
        <tr><td>{fname}</td></tr>
        <tr><td>{code}</td></tr>
        </table>""".format(
            fname="<span class=filename>{filename}</span>".format(
                filename=filename
            ),
            code=hlblock,
        )

    def header(self, text, level):
        short_name = text.replace(" ", "_")

        return """<h{level} id="{short_name}">{text}
        <a class="headlink" href="#{short_name}">#</a></h{level}>\n""".format(
            text=text,
            level=level,
            short_name=short_name)

markdown = MyRenderer(extensions, render_flags)

app = bottle.Bottle()

base_plate = bottle.SimpleTemplate(
    open("templates/base.html").read(),
    noescape=True)

wiki_plate = bottle.SimpleTemplate(
    base_plate.render(
        body=open("templates/wiki.html").read(),
        title="{{title}}"),
    noescape=True)

edit_plate = bottle.SimpleTemplate(
    base_plate.render(
        body=open("templates/edit.html").read(),
        title="{{title}}"),
    noescape=True)

upload_plate = bottle.SimpleTemplate(
    base_plate.render(
        body=open("templates/upload.html").read(),
        title="{{title}}"),
    noescape=True)

uploaded_plate = bottle.SimpleTemplate(
    base_plate.render(
        body=open("templates/uploaded.html").read(),
        title="{{title}}"),
    noescape=True)


@app.route("/wiki/<page>")
def wiki(page):
    fname = os.path.splitext(page)[0]
    try:
        with open("wiki/{}.md".format(fname)) as f:
            md = f.read()
    except FileNotFoundError:
        md = "This page does not exist."

    md_body = markdown.render(md)

    rendered = wiki_plate.render(
        body=md_body,
        fname=fname,
        title=get_title(fname + ".md"))

    return rendered


@app.get("/edit/<page>")
def get_edit(page):
    fname = os.path.splitext(page)[0]

    try:
        with open("wiki/{}.md".format(fname)) as f:
            md = f.read()
    except FileNotFoundError:
        md = ""

    rendered = edit_plate.render(
                                 markdown=md,
                                 fname=fname,
                                 title="editing {}".format(fname + ".md"))

    return rendered


@app.post("/edit/<page>")
def post_edit(page):
    fname = os.path.splitext(page)[0]

    try:
        with open("wiki/{}.md".format(fname)) as f:
            old_md = f.read()
    except FileNotFoundError:
        old_md = ""

    new_md = bottle.request.forms.get("markdown")
    new_md = new_md.replace("\r\n", "\n")
    # Fix windows newlines.

    log_edit(bottle.request, old_md, new_md)

    with open("wiki/{}.md".format(fname), "w") as f:
        f.write(new_md)

    return bottle.redirect("/wiki/{}".format(fname))


@app.route("/css/<filename>")
def css(filename):
    return bottle.static_file(filename, root=ROOT + "/css")


@app.route("/files/<filename>")
def files(filename):
    return bottle.static_file(filename, root=ROOT + "/files")


@app.route("/files")
def files_listing():
    filenames = []
    for fname in os.listdir("files"):
        filenames.append("<a href=/files/{}>{}</a>".format(
            fname, fname
        ))
    return base_plate.render(
        body="</br>".join(filenames)).render(title="Files")


@app.route("/list")
def wiki_listing():
    filenames = []
    for fname in os.listdir("wiki"):
        filenames.append("<a href=/wiki/{}>{}</a>".format(
            fname,
            get_title(fname)
        ))
    return base_plate.render(
        body="</br>".join(filenames).render(title="Wiki Pages"))


@app.route("/editlog")
def logs():
    return bottle.static_file("edit.log", root=ROOT + "/logs")


@app.route("/MathJax/<filename:path>")
def mathjax(filename):
    return bottle.static_file(filename, root=ROOT + "/MathJax")


@app.get("/upload")
def get_upload():
    return upload_plate.render(title="Upload")


@app.post("/upload")
def post_upload():

    uploaded = bottle.request.files.uploaded

    filename = bottle.request.forms.filename or \
        bottle.request.files.uploaded.filename

    # Use the given filename as an override, fallback to the original.

    filename = filename.replace("/", "_")

    # Done to prevent directory traversal. Another option would be to
    # detect it and return a 403.

    try:
        uploaded.save(ROOT + "/files/{}".format(filename))
    except OSError:
        return base_plate.render(
            body="File already exists").render(title="Upload Error")

    return uploaded_plate.render(fname=filename, title="Uploaded")


@app.route("/")
def home():
    return bottle.redirect("/wiki/homepage")


bottle.run(app,
           host="",
           port=8888,
           debug=True,
           )
