var page = require('webpage').create();
var sys = require('system');
var crypto = require('crypto');

var url = '', img_b64 = '', sha1sum = '';
var hash = crypto.createHash('sha1');

hash.setEncoding('hex');

function print_usage () {
    console.log('Usage: phantomjs screenshot.js <url>');
}

if (sys.args.length === 1) {
    print_usage();
    phantom.exit();
} else {
    url = sys.args[1];
}

page.open(url, function () {
    img_b64 = page.renderBase64('png');
    hash.write(img_b64);
    hash.end();
    sha1sum = hash.read();
    page.render(sha1sum + '_img.png');
    phantom.exit();
});
