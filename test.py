import re

def read_file(file_path):
    with open(file_path, 'r') as f:
        return f.read()

def calculate_top_of_slide(slide_html):
    slide_html = slide_html.split("</")
    return slide_html[0]

def calculate_bottom_of_slide(slide_html, slide_html_top):
    slide_html = slide_html.replace(slide_html_top, "")
    slide_html = re.sub(r'\s+', '', slide_html)
    return slide_html


def find_body_start(html_content):
    body_pointer = html_content.find("body class")
    while True:
        if html_content[body_pointer] == ">":
            break
        body_pointer += 1
    return body_pointer + 1

def add_css_body(html_content):
    start = find_body_start(html_content) + 1
    html_content = html_content[:start] + '<div class="body">' + html_content[start:]
    return html_content

html_body = read_file("CursJavaFundamentals.html")

add_css_body(html_body)

ht