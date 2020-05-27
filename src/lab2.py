import socket
import ssl
import tkinter

def request(url):
    scheme, url = url.split("://", 1)
    assert scheme in ["http", "https"], \
        "Unknown scheme {}".format(scheme)

    host, path = url.split("/", 1)
    path = "/" + path
    port = 80 if scheme == "http" else 443

    if ":" in host:
        host, port = host.split(":", 1)
        port = int(port)

    s = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM, proto=socket.IPPROTO_TCP)
    s.connect((host, port))

    if scheme == "https":
        ctx = ssl.create_default_context()
        s = ctx.wrap_socket(s, server_hostname=host)

    s.send(("GET {} HTTP/1.0\r\n".format(path) +
            "Host: {}\r\n\r\n".format(host)).encode("utf8"))
    response = s.makefile("r", encoding="utf8", newline="\r\n")

    statusline = response.readline()
    version, status, explanation = statusline.split(" ", 2)
    assert status == "200", "{}: {}".format(status, explanation)

    headers = {}
    while True:
        line = response.readline()
        if line == "\r\n": break
        header, value = line.split(":", 1)
        headers[header.lower()] = value.strip()

    body = response.read()
    s.close()

    return headers, body

def lex(source):
    text = ""
    in_angle = False
    for c in source:
        if c == "<":
            in_angle = True
        elif c == ">":
            in_angle = False
        elif not in_angle:
            text += c
    return text

WIDTH = 800
HEIGHT = 600

HSTEP = 13
VSTEP = 18

SCROLL_STEP = 100

def layout(text):
    display_list = []
    x, y = HSTEP, VSTEP
    for c in text:
        display_list.append((x, y, c))
        x += GRID
        if x >= WIDTH - HSTEP:
            y += VSTEP
            x = HSTEP
    return display_list

class Browser:
    def __init__(self, text):
        self.window = tkinter.Tk()
        self.canvas = tkinter.Canvas(window, width=WIDTH, height=HEIGHT)
        self.canvas.pack()

        self.text = text
        self.layout()

        self.scrolly = 0
        window.bind("<Down>", self.scrolldown)

    def layout(self):
        self.display_list = layout(self.text)
        self.render()

    def render(self):
        self.canvas.delete("all")
        for x, y, c in self.display_list:
            self.canvas.create_text(x, y - self.scrolly, text=c)

    def scrolldown(self, e):
        self.scrolly += SCROLL_STEP
        self.render()

if __name__ == "__main__":
    import sys
    headers, body = request(sys.argv[1])
    text = lex(body)
    browser = Browser(text)
    tkinter.mainloop()