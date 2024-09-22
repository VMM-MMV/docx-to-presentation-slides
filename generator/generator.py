import sys
import re

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
    write_file(new_css_name, "")

    html_content = html_content.replace(css, "")
    html_content = html_content.replace('<style type="text/css"></style>', f"""<link rel="stylesheet" href="{docx_css_name}"><link rel="stylesheet" href="{new_css_name}">""")
    return html_content
    
html_content = read_file("CursJavaFundamentals.html")

html_content = replace_css(html_content)

write_file("jora.html", html_content)