import tempfile
import shlex
import subprocess

CMD = '/bin/tex2png -b "rgb 1 1 1" -T -D 150 -o "{}"'


def render_png(tex):
    _, fname = tempfile.mkstemp(text=False)
    proc = subprocess.Popen(
        shlex.split(CMD.format(fname)),
        stdin=subprocess.PIPE,
    )

    proc.communicate(tex.encode("UTF-8"))

    with open(fname, "rb") as f:
        return f.read()
