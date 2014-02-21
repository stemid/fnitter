var page = require('webpage').create();
var sys = require('system');

var url = '', img_b64 = '', md5sum = '', output_dir = '';

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
  if (!phantom.injectJs('md5.js')) {
    phantom.exit();
  }
  img_b64 = page.renderBase64('png');
  md5sum = CryptoJS.MD5(img_b64);

  if (output_dir === undefined) {
    output_file = md5sum + '_img.png';
  } else {
    output_file = output_dir + '/' + md5sum + '_img.png';
  }

  page.render(output_file);
  phantom.exit();
});
