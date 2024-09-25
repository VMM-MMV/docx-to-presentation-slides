import sys
import re
import logging

ROOT = "prerequisites"
SLIDE_HTML_PATH = f"{ROOT}/slide.html"
DOCX_CSS_PATH = f"{ROOT}/docx.css"
SCRIPT_PATH = f"{ROOT}/script.js"

logging.basicConfig(level=logging.WARNING)
log = logging.getLogger(__name__)

def get_argv():
    if len(sys.argv) > 2:
        arg1 = sys.argv[1]
        arg2 = sys.argv[2]
        return arg1, arg2
    else:
        log.warning("Please provide two arguments.")

def read_file(file_path):
    with open(file_path, 'r') as f:
        return f.read()
    
def write_file(file_path, file_content):
    with open(file_path, 'w') as f:
        return f.write(file_content)
    
def replace_css(html_content, slide_html):
    """Replace the <head> content from html_content with slide_html."""
    def extract_head(html):
        start = html.find("<head>")
        end = html.find("</head>") + len("</head>")
        return html[start:end]

    old_css = extract_head(html_content)
    old_css_start = old_css.find('<style type="text/css"') + len('<style type="text/css">')
    old_css_end = old_css.find('</style>')
    write_file(DOCX_CSS_PATH, old_css[old_css_start:old_css_end])
    
    return html_content.replace(old_css, extract_head(slide_html))
    
def get_top_and_bottom_of_slide(slide_html):
    """Extract the top and bottom of the slide content, ignoring <body> and <head> tags."""
    def get_top_of_slide(slide_html):
        slide_html = slide_html.split("</")[0]
        start = slide_html.find("<")
        end = slide_html.rfind(">")
        slide_html = slide_html[start:end+1]
        return slide_html

    def get_bottom_of_slide(slide_html, slide_html_top):
        slide_html = slide_html.replace(slide_html_top, "")
        slide_html = re.sub(r'\s+', '', slide_html)
        return slide_html

    # get rid of the body and head in the slide
    body_start_end = get_body_start_end(slide_html)
    if body_start_end == -1:
        body_start_end = slide_html.find("</head>") + len("</head>")
    else:
        body_start_end += 1

    slide_html = slide_html[body_start_end:]
    slide_html = slide_html.replace("</body>", "")

    slide_html_top = get_top_of_slide(slide_html)
    slide_html_bottom = get_bottom_of_slide(slide_html, slide_html_top)
    return slide_html_top, slide_html_bottom

def add_slides(html_content, slide_html):
    """Insert slide contents into placeholders in html_content."""
    def get_slide_bounds(content, index):
        left_brackets, right_brackets = 0, 0
        left, right = index, index

        while left_brackets < 2:
            left -= 1
            if content[left] == "<":
                left_brackets += 1

        while right_brackets < 2:
            right += 1
            if content[right] == ">":
                right_brackets += 1

        return left, right + 1
    
    def replace_slide_marker(html_content, slide_marker, replace_with):
        while (start_occurrence := html_content.find(slide_marker)) != -1:
            left, right = get_slide_bounds(html_content, start_occurrence)
            html_content = html_content.replace(html_content[left:right], replace_with)
        return html_content
    
    slides_html_top, slides_html_bottom = get_top_and_bottom_of_slide(slide_html)

    html_content = replace_slide_marker(html_content, "vmm-slide-start", "<!-- slide start -->" + slides_html_top + "<!-- slide start -->")
    html_content = replace_slide_marker(html_content, "vmm-slide-end", "<!-- slide end -->" + slides_html_bottom + "<!-- slide end -->")
    
    return html_content

def get_body_start(html_content):
    body_pointer = html_content.find("body class")
    return body_pointer

def get_body_start_end(html_content):
    """Find the position right after the <body> tag start."""
    html_body_start = get_body_start(html_content)
    if html_body_start == -1: 
        log.warning("No <body class='...'> found")
        return -1
    
    html_body_start = html_content.find(">", html_body_start)
    return html_body_start

def get_body_end(html_content):
    body_pointer = html_content.find("</body>")
    return body_pointer

def add_css_body(html_content):
    """Wrap the body content in a <div class='body'> tag."""
    start = get_body_start_end(html_content) + 1
    end = get_body_end(html_content)

    return html_content[:start]+ '<div class="body flex flex-col items-center justify-center">' + html_content[start:end] + '</div>' + html_content[end:]

def add_script(html_content):
    """Append a script tag before the closing </body> tag."""
    end = get_body_end(html_content)
    return html_content[:end] + f'<script src="{SCRIPT_PATH}"></script>' + html_content[end:]

def add_slides_class_body(html_content, slide_html):
    """Transfer the body class from slide_html to html_content."""
    slides_body_start = get_body_start(slide_html) 
    slides_body_end = get_body_start_end(slide_html)

    if slides_body_start == -1 or slides_body_end == -1:
        log.warning("class body non existent" + f" slides_body_start = {slides_body_start}, " + f"slides_body_end = {slides_body_end}") 
        return html_content
    
    slide_html_class_body = slide_html[slides_body_start:slides_body_end].split("=")[1]

    html_body_start = get_body_start_end(html_content)

    html_content = html_content[:html_body_start] +  f' class = {slide_html_class_body}' + html_content[html_body_start:] 
    return html_content

html_name, output_name = get_argv()

html_content = read_file(html_name)

slide_html = read_file(SLIDE_HTML_PATH)

html_content = replace_css(html_content, slide_html)

html_content = add_slides_class_body(html_content, slide_html)

html_content = add_css_body(html_content)

html_content = add_slides(html_content, slide_html)

html_content = add_script(html_content)

write_file(f"{output_name}.html", html_content)