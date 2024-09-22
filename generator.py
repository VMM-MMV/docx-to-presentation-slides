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
    
def replace_css(html_content, slide_html):
    start = slide_html.find("<head>")
    end = slide_html.find("</head>") + len("</head>")

    slide_head_content = slide_html[start:end]

    start = html_content.find("<head>")
    end = html_content.find("</head>") + len("</head>")

    html_head_content = html_content[start:end]

    html_content = html_content.replace(html_head_content, slide_head_content)
    return html_content
    
def get_top_and_bottom_of_slide(slide_html):
    def calculate_top_of_slide(slide_html):
        slide_html = slide_html.split("</")[0]
        start = slide_html.find("<")
        end = slide_html.rfind(">")
        slide_html = slide_html[start:end+1]
        return slide_html

    def calculate_bottom_of_slide(slide_html, slide_html_top):
        slide_html = slide_html.replace(slide_html_top, "")
        slide_html = re.sub(r'\s+', '', slide_html)
        return slide_html

    # get rid of the body in the slide
    body_start_end = get_body_start_end(slide_html) + 1

    slide_html = slide_html[body_start_end:]
    slide_html = slide_html.replace("</body>", "")

    slide_html_top = calculate_top_of_slide(slide_html)
    slide_html_bottom = calculate_bottom_of_slide(slide_html, slide_html_top)
    return slide_html_top, slide_html_bottom

def add_slides(html_content, slide_html):
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

    slides_html_top, slides_html_bottom = get_top_and_bottom_of_slide(slide_html)

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

def get_body_start(html_content):
    body_pointer = html_content.find("body class")
    return body_pointer

def get_body_start_end(html_content):
    html_body_start = get_body_start(html_content)
    html_body_start = html_content.find(">", html_body_start)
    return html_body_start

def get_body_end(html_content):
    body_pointer = html_content.find("</body>")
    return body_pointer

def add_css_body(html_content):
    start = get_body_start_end(html_content) + 1
    html_content = html_content[:start] + '<div class="body">' + html_content[start:]

    end = get_body_end(html_content)
    html_content = html_content[:end] + '</div>' + html_content[end:]

    return html_content

def add_script(html_content):
    end = get_body_end(html_content)
    html_content = html_content[:end] + '<script src="script.js"></script>' + html_content[end:]

    return html_content

def add_slides_class_body(html_content, slide_html):
    slides_body_start = get_body_start(slide_html) 
    slides_body_end = get_body_start_end(slide_html)

    slide_html_class_body = slide_html[slides_body_start:slides_body_end].split("=")[1]

    html_body_start = get_body_start_end(html_content)

    html_content = html_content[:html_body_start] +  f' class = {slide_html_class_body}' + html_content[html_body_start:] 
    return html_content

html_content = read_file("CursJavaFundamentals.html")

slide_html = read_file(SLIDE_HTML_PATH)

html_content = replace_css(html_content, slide_html)

html_content = add_slides_class_body(html_content, slide_html)

html_content = add_css_body(html_content)

html_content = add_slides(html_content, slide_html)

html_content = add_script(html_content)

write_file("jora.html", html_content)