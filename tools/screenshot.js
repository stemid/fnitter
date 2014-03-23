// Take screenshots of webpages with PhantomJS
// By Stefan Midjich
//
var page = require('webpage').create();
var sys = require('system');

var url = '', output_dir = '';

function print_usage () {
  console.log('Usage: phantomjs screenshot.js <url> [output dir]');
}

if (sys.args.length === 1) {
  print_usage();
  phantom.exit();
} else {
  url = sys.args[1];
  output_dir = sys.args[2];
}

page.open(url, function () {
  var img_b64 = '', md5sum = '', filename = '';

  if (!phantom.injectJs('md5.js')) {
    phantom.exit();
  }
  img_b64 = page.renderBase64('png');
  md5sum = CryptoJS.MD5(img_b64);

  filename = md5sum + '_img.png';

  if (output_dir === undefined) {
    output_file = filename;
  } else {
    output_file = output_dir + '/' + filename;
  }

  page.render(output_file);
  console.log(filename);
  phantom.exit();
});
