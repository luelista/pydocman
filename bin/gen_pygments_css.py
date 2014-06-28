# Call it this way:
# python gen_css.py pygments.css
import sys

from pygments.formatters import HtmlFormatter

f = open(sys.argv[1], 'w')

# You can change style and the html class here:
f.write(HtmlFormatter(style='monokai').get_style_defs('.highlight'))

f.close()

