import sh

class Screenshot:
    def __init__(self, **kw):
        phantomjs_path = kw.get(
            'phantomjs',
            '/usr/local/lib/node_modules/phantomjs/'
        )
        screenshot_script = kw.get(
            'screenshot',
            'tools/screenshot.js'
        )
        url = kw.get(
            'url',
            None
        )
        output_dir = kw.get(
            'output_dir',
            None
        )

        if not url:
            raise ValueError('Need URL to continue')

        self._phantomjs_bin = phantomjs_path + '/bin/phantomjs'
        self._command_path = self._phantomjs_bin + ' ' + screenshot_script
        self._command = sh.Command(self._phantomjs_bin)

        if not output_dir:
            self._command_output = self._command(
                screenshot_script,
                url
            )
        else:
            self._command_output = self._command(
                screenshot_script,
                url,
                output_dir
            )
