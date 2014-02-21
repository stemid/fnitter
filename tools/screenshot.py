from os import path
from sys import path as pythonpath
from argparse import ArgumentParser

parentdir = path.dirname(path.dirname(path.abspath(__file__)))
pythonpath.insert(0,parentdir)

from Driver.Screenshot import Screenshot

parser = ArgumentParser(
    description = 'Take twitter screenshots',
    epilog = 'by Stefan Midjich'
)

parser.add_argument(
    '-o', '--output',
    metavar = 'OUTPUT_DIR',
    default = './',
    dest = 'output_dir',
    help = 'Destination output directory for the screenshot'
)

parser.add_argument(
    'url',
    metavar = 'URL',
    nargs = '+',
    help = 'URL to take screenshot of'
)

opts = parser.parse_args()

s = Screenshot(
    phantomjs_path = '/usr/local/lib/node_modules/phantomjs/lib/phantom',
    url = opts.url,
    output_dir = opts.output_dir
)
