import markdown
import re
import xml.dom.minidom
import xml.etree.ElementTree as etree

from holosophos.files import WORKSPACE_DIR_PATH

start_single_quote_re = re.compile("(^|\s|\")'")
start_double_quote_re = re.compile("(^|\s|'|`)\"")
end_double_quote_re = re.compile("\"(,|\.|\s|$)")

def inline_html_latex(text):
    out = text
    if re.search(r'&ldquo;.*?&rdquo;', text, flags=re.DOTALL):
        out = out.replace('&ldquo;', '\enquote{').replace('&rdquo;', '}')
    if re.search(r'&lsquo;.*?&rsquo;', text, flags=re.DOTALL):
        out = out.replace('&lsquo;', '\enquote{').replace('&rsquo;', '}')
    if re.search(r'&ldquo;.*?&ldquo;', text, flags=re.DOTALL):
        out = out.replace('&ldquo;', '\enquote{', 1).replace('&ldquo;', '}', 1)
    if re.search(r'&laquo;.*?&raquo;', text, flags=re.DOTALL):
        out = out.replace('&laquo;', '\enquote{').replace('&raquo;', '}')
    out = out.replace("...", "\dots")
    out = out.replace("&hellip;", "\dots")
    out = out.replace("&ndash;", "--")
    out = out.replace("&mdash;", "---")
    out = out.replace("\|", '|')
    return out

def unescape_html_entities(text):
    out = text.replace('&amp;', '&')
    out = out.replace('&lt;', '<')
    out = out.replace('&gt;', '>')
    out = out.replace('&quot;', '"')
    return out

def escape_latex_entities(text):
    out = text
    out = unescape_html_entities(out)
    out = out.replace('%', '\%')
    out = out.replace('&', '\\&')
    out = out.replace('#', '\\#')
    out = start_single_quote_re.sub(r'\g<1>`', out)
    out = start_double_quote_re.sub(r'\g<1>``', out)
    out = end_double_quote_re.sub("''\g<1>", out)
    return out

def unescape_latex_entities(text):
    return text.replace('\\&', '&')

def makeExtension(configs=None):
    return LaTeXExtension(configs=configs)

class LaTeXExtension(markdown.Extension):
    def __init__(self, configs=None):
        self.reset()

    def extendMarkdown(self, md):
        self.md = md
        latex_tp = LaTeXTreeProcessor()
        math_pp = MathTextPostProcessor()
        table_pp = TableTextPostProcessor()
        image_pp = ImageTextPostProcessor()
        link_pp = LinkTextPostProcessor()
        unescape_html_pp = UnescapeHtmlTextPostProcessor()

        md.treeprocessors.register(latex_tp, 'latex', 20)
        md.postprocessors.register(unescape_html_pp, 'unescape_html', 20)
        md.postprocessors.register(math_pp, 'math', 20)
        md.postprocessors.register(image_pp, 'image', 20)
        md.postprocessors.register(table_pp, 'table', 20)
        md.postprocessors.register(link_pp, 'link', 20)

    def reset(self):
        pass

class LaTeXTreeProcessor(markdown.treeprocessors.Treeprocessor):
    def run(self, doc):
        latex_text = self.tolatex(doc)
        doc.clear()
        latex_node = etree.Element('plaintext')
        latex_node.text = latex_text
        doc.append(latex_node)

    def tolatex(self, ournode):
        buffer = ""
        subcontent = ""

        if ournode.text:
            subcontent += escape_latex_entities(ournode.text)

        for child in list(ournode):
            subcontent += self.tolatex(child)

        tag = ournode.tag
        if tag == 'h1':
            buffer += '\n\\title{%s}\n' % subcontent
            buffer += """
% ----------------------------------------------------------------
\\maketitle
% ----------------------------------------------------------------
"""
        elif tag == 'h2':
            buffer += '\n\n\\section{%s}\n' % subcontent
        elif tag == 'h3':
            buffer += '\n\n\\subsection{%s}\n' % subcontent
        elif tag == 'h4':
            buffer += '\n\\subsubsection{%s}\n' % subcontent
        elif tag == 'hr':
            buffer += '\\noindent\\makebox[\\linewidth]{\\rule{\\linewidth}{0.4pt}}'
        elif tag == 'ul':
            buffer += """
\\begin{itemize}%s
\\end{itemize}
""" % subcontent
        elif tag == 'ol':
            buffer += "\\begin{enumerate}"
            if 'start' in ournode.attrib:
                start = int(ournode.attrib['start']) - 1
                buffer += "\\setcounter{enumi}{" + str(start) + "}"
            buffer += """
%s
\\end{enumerate}
""" % subcontent
        elif tag == 'li':
            buffer += "\n  \\item %s" % subcontent.strip()
        elif tag == 'blockquote':
            buffer += """
\\begin{quotation}
%s
\\end{quotation}
""" % subcontent.strip()
        elif tag == 'pre' or (tag == 'pre' and ournode.parent.tag != 'pre'):
            buffer += """
\\begin{verbatim}
%s
\\end{verbatim}
""" % subcontent.strip()
        elif tag == 'q':
            buffer += "`%s'" % subcontent.strip()
        elif tag == 'p':
            buffer += '\n%s\n' % subcontent.strip()
        elif tag == 'sup':
            buffer += '\\footnote{%s}' % subcontent.strip()
        elif tag == 'strong':
            buffer += '\\textbf{%s}' % subcontent.strip()
        elif tag == 'em':
            buffer += '\\emph{%s}' % subcontent.strip()
        elif tag == 'table':
            buffer += '\n\n<table>%s</table>\n\n' % subcontent
        elif tag == 'thead':
            buffer += '<thead>%s</thead>' % subcontent
        elif tag == 'tbody':
            buffer += '<tbody>%s</tbody>' % subcontent
        elif tag == 'tr':
            buffer += '<tr>%s</tr>' % subcontent
        elif tag == 'th':
            buffer += '<th>%s</th>' % subcontent
        elif tag == 'td':
            buffer += '<td>%s</td>' % subcontent
        elif tag == 'img':
            buffer += '<img src="%s" alt="%s" />' % (ournode.get('src'), ournode.get('alt'))
        elif tag == 'a':
            buffer += '<a href="%s">%s</a>' % (escape_latex_entities(ournode.get('href')), subcontent)
        else:
            buffer = subcontent

        if ournode.tail:
            buffer += escape_latex_entities(ournode.tail)

        return buffer

class UnescapeHtmlTextPostProcessor(markdown.postprocessors.Postprocessor):
    def run(self, text):
        return unescape_html_entities(inline_html_latex(text))

class MathTextPostProcessor(markdown.postprocessors.Postprocessor):
    def run(self, instr):
        instr = re.sub(r'\$\$([^\$]*)\$\$', r'\\[\1\\]', instr)
        instr = re.sub(r'\$([^\$]*)\$', r'\\(\1\\)', instr)
        instr = instr.replace('\\lt', '<').replace(' * ', ' \\cdot ').replace('\\del', '\\partial')
        return instr

class TableTextPostProcessor(markdown.postprocessors.Postprocessor):
    def run(self, instr):
        converter = Table2Latex()
        new_blocks = []
        for block in instr.split('\n\n'):
            stripped = block.strip()
            if stripped.startswith('<table') and stripped.endswith('</table>'):
                new_blocks.append(converter.convert(stripped).strip())
            elif re.match(r'\|.*\|', stripped):  # Check for Markdown table
                new_blocks.append(converter.convert_markdown_table(stripped).strip())
            else:
                new_blocks.append(block)
        return '\n\n'.join(new_blocks)

class Table2Latex:
    def get_text(self, element):
        if element.nodeType == element.TEXT_NODE:
            return escape_latex_entities(element.data)
        result = ''
        for child in element.childNodes:
            result += self.get_text(child)
        return result

    def process_cell(self, element):
        subcontent = self.get_text(element)
        if element.tagName == 'th':
            subcontent = '\\textbf{%s}' % subcontent
        colspan = int(element.getAttribute('colspan')) if element.hasAttribute('colspan') else 1
        buffer = ' \multicolumn{%s}{|c|}{%s}' % (colspan, subcontent) if colspan > 1 else ' %s' % subcontent
        if element.nextSibling and element.nextSibling.nodeType == element.ELEMENT_NODE:
            buffer += ' &'
        self.numcols += colspan
        return buffer

    def tolatex(self, element):
        buffer = ""
        if element.tagName == 'tr':
            self.maxcols = max(self.numcols, self.maxcols)
            self.numcols = 0
            buffer += '\\hline\n%s \\\\' % ''.join([self.tolatex(child) for child in element.childNodes])
        elif element.tagName in ['td', 'th']:
            buffer = self.process_cell(element)
        else:
            buffer += ''.join([self.tolatex(child) for child in element.childNodes])
        return buffer

    def convert(self, instr):
        self.numcols = 0
        self.maxcols = 0
        dom = xml.dom.minidom.parseString(instr)
        core = self.tolatex(dom.documentElement)
        caption = self.get_text(dom.documentElement.getElementsByTagName('caption')[0]) if dom.documentElement.getElementsByTagName('caption') else ''
        return """
\\begin{table}[h]
\\begin{tabular}{|l%s|}
%s
\\hline
\\end{tabular}
\\\\[5pt]
\\caption{%s}
\\end{table}
""" % ('|l' * (self.maxcols - 1), core, caption)

    def convert_markdown_table(self, instr):
        lines = instr.split('\n')
        headers = lines[0].strip('|').split('|')
        cols = len(headers)
        buffer = "\\begin{table}[h]\n\\centering\n\\begin{tabular}{|" + "|".join(['l'] * cols) + "|}\n\\hline\n"
        buffer += " & ".join([f"\\textbf{{{header.strip()}}}" for header in headers]) + " \\\\\n\\hline\n"
        for line in lines[2:]:
            cells = line.strip('|').split('|')
            buffer += " & ".join([cell.strip() for cell in cells]) + " \\\\\n\\hline\n"
        buffer += "\\end{tabular}\n\\end{table}"
        return buffer

class ImageTextPostProcessor(markdown.postprocessors.Postprocessor):
    def run(self, instr):
        converter = Img2Latex()
        new_blocks = []
        for block in instr.split("\n\n"):
            stripped = block.strip()
            if stripped.startswith('<img'):
                new_blocks.append(converter.convert(stripped).strip())
            else:
                new_blocks.append(block)
        return '\n\n'.join(new_blocks)

class Img2Latex:
    def convert(self, instr):
        dom = xml.dom.minidom.parseString(instr)
        img = dom.documentElement
        src = img.getAttribute('src')
        alt = img.getAttribute('alt')
        return """
\\begin{figure}[H]
\\centering
\\includegraphics[max width=\\linewidth]{%s}
\\caption{%s}
\\end{figure}
""" % (src, alt)

class LinkTextPostProcessor(markdown.postprocessors.Postprocessor):
    def run(self, instr):
        converter = Link2Latex()
        new_blocks = []
        for block in instr.split("\n\n"):
            stripped = block.strip()
            matches = re.findall(r'<a[^>]*>[^<]+</a>', stripped)
            if matches:
                for match in matches:
                    stripped = stripped.replace(match, converter.convert(match).strip())
                new_blocks.append(stripped)
            else:
                new_blocks.append(block)
        return '\n\n'.join(new_blocks)

class Link2Latex:
    def convert(self, instr):
        dom = xml.dom.minidom.parseString(instr)
        link = dom.documentElement
        href = link.getAttribute('href')
        desc = re.search(r'>([^<]+)', instr).group(1)
        return r'\href{%s}{%s}' % (href, desc) if href != desc else r'\url{%s}' % href

def convert_md_to_latex(input_path, output_path):
    with open(f'{WORKSPACE_DIR_PATH}/{input_path}', 'r', encoding='utf-8') as infile:
        md_content = infile.read()

    md = markdown.Markdown(extensions=[LaTeXExtension()])
    latex_content = md.convert(md_content)

    latex_content = re.sub(r'<\/?plaintext[^>]*>', '', latex_content, flags=re.IGNORECASE)

    latex_content = f"""\\documentclass{{article}}
\\usepackage[utf8]{{inputenc}}
\\usepackage{{graphicx}}
\\usepackage{{enumitem}}
\\usepackage{{quoting}}
\\usepackage{{booktabs}}
\\usepackage{{caption}}
\\usepackage{{siunitx}}
\\sisetup{{
  group-separator = {{,}},
  output-decimal-marker = {{.}}
}}
\\usepackage{{hyperref}}

\\author{{Holosophos}}

\\begin{{document}}

{latex_content}

\\end{{document}}"""

    with open(f'{WORKSPACE_DIR_PATH}/{output_path}', 'w', encoding='utf-8') as outfile:
        outfile.write(latex_content)
