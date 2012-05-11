import sys
import json
import ghost

try:
    from PyQt4.QtWebKit import QWebSettings
except ImportError:
    from PySide.QtWebKit import QWebSettings
    

if __name__ == '__main__':
    url = sys.argv[1]
    _ghost = ghost.Ghost(wait_timeout=60)

    QWebSettings.globalSettings().setAttribute(QWebSettings.AutoLoadImages, False)
    QWebSettings.globalSettings().setAttribute(QWebSettings.PluginsEnabled, False)
    page, resources = _ghost.open(url)
    print json.dumps({'url': url, 'headers': page.headers, 'html': unicode(_ghost.main_frame.toHtml())})

