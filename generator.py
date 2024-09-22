import sys
import re

SLIDE_HTML_PATH = "slide.html"

def get_argv():
    if len(sys.argv) > 2:
        arg1 = sys.argv[1]
        arg2 = sys.argv[2]
        return arg1, arg2
    else:
        print("Please provide two arguments.")

def read_file(file_path):
    with open(file_path, 'r') as f:
        return f.read()
    
def write_file(file_path, file_content):
    with open(file_path, 'w') as f:
        return f.write(file_content)
    
def find_style(html_content):
    pattern = r'<style\b[^>]*>(.*?)<\/style>'

    matches = re.findall(pattern, html_content, re.DOTALL)
    return matches[0]

def replace_css(html_content, docx_css_name = "docx.css", new_css_name = "style.css"):
    css = find_style(html_content)

    write_file(docx_css_name, css)
    # write_file(new_css_name, "")

    html_content = html_content.replace(css, "")
    html_content = html_content.replace('<style type="text/css"></style>', f"""<link rel="stylesheet" href="{docx_css_name}"><link rel="stylesheet" href="{new_css_name}">""")
    return html_content
    
def get_top_and_bottom_of_slide(slide_html_path=SLIDE_HTML_PATH):
    def calculate_top_of_slide(slide_html):
        slide_html = slide_html.split("</")
        return slide_html[0]

    def calculate_bottom_of_slide(slide_html, slide_html_top):
        slide_html = slide_html.replace(slide_html_top, "")
        slide_html = re.sub(r'\s+', '', slide_html)
        return slide_html

    slide_html = read_file(slide_html_path)

    slide_html_top = calculate_top_of_slide(slide_html)
    slide_html_bottom = calculate_bottom_of_slide(slide_html, slide_html_top)
    return slide_html_top, slide_html_bottom

def add_slides(html_content):
    def get_start_end_of_slide(html_content, start):
        left_bracket_occurance, right_bracket_occurance = 0, 0
        left_pointer, right_pointer = start, start
        while left_bracket_occurance != 2:
            left_pointer -= 1
            if html_content[left_pointer] == "<":
                left_bracket_occurance += 1

        while right_bracket_occurance != 2:
            right_pointer += 1
            if html_content[right_pointer] == ">":
                right_bracket_occurance += 1

        return left_pointer, right_pointer+1
    
    slide_start_marker = "<!-- slide start -->"
    slide_end_marker = "<!-- slide end -->"

    slides_html_top, slides_html_bottom = get_top_and_bottom_of_slide()

    start_occurrence = html_content.find("vmm-slide-start")
    while start_occurrence != -1:
        left, right = get_start_end_of_slide(html_content, start_occurrence)
        html_content = html_content.replace(html_content[left:right], slide_start_marker + slides_html_top + slide_start_marker)
        start_occurrence = html_content.find("vmm-slide-start")
    
    end_occurrence = html_content.find("vmm-slide-end")
    while end_occurrence != -1:
        left, right = get_start_end_of_slide(html_content, end_occurrence)
        html_content = html_content.replace(html_content[left:right], slide_end_marker + slides_html_bottom + slide_end_marker)
        end_occurrence = html_content.find("vmm-slide-end")
    
    return html_content

def find_body_start(html_content):
    body_pointer = html_content.find("body class")
    while True:
        if html_content[body_pointer] == ">":
            break
        body_pointer += 1
    return body_pointer + 1

def find_body_end(html_content):
    body_pointer = html_content.find("</body>")
    return body_pointer

def add_css_body(html_content):
    start = find_body_start(html_content)
    html_content = html_content[:start] + '<div class="body">' + html_content[start:]

    end = find_body_end(html_content)
    html_content = html_content[:end] + '</div>' + html_content[end:]

    return html_content

html_content = read_file("CursJavaFundamentals.html")

html_content = replace_css(html_content)

html_content = add_css_body(html_content)

html_content = add_slides(html_content)

write_file("jora.html", html_content)