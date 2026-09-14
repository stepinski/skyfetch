import os
from urllib.parse import urlparse

from flask import Flask, jsonify, request
from seleniumbase import SB

app = Flask(__name__)


@app.get("/article")
def article():
    url = request.args.get("url", "")

    p = urlparse(url)
    if p.scheme != "https" or p.netloc != "news.sky.com":
        return jsonify({"error": "invalid URL"}), 400

    try:
        with SB(
            uc=True,
            headless2=True,
            locale="en",
        ) as browser:

            browser.open(url)

            # Give Sky/Akamai time to complete.
            browser.sleep(10)

            html = browser.get_page_source()

            debug = browser.execute_script("""
                (() => {
                    const html = document.documentElement
                        ? document.documentElement.outerHTML
                        : '';

                    return {
                        readyState: document.readyState,
                        title: document.title,
                        bodyLength: document.body
                            ? document.body.innerText.length
                            : 0,
                        htmlLength: html.length,
                        hasAkamai: /akamai|access denied/i.test(html),
                        hasHector: /Hector Patemore/i.test(html),
                        hasSkyNews: /Sky News/i.test(html),
                        hasArticleBody: /articleBody/i.test(html),
                        jsonLdCount: document.querySelectorAll(
                            'script[type="application/ld+json"]'
                        ).length,
                        bodyPreview: document.body
                            ? document.body.innerText.substring(0, 1000)
                            : '',
                        htmlPreview: html.substring(0, 1000)
                    };
                })()
            """)

            return jsonify({
                "url": browser.get_current_url(),
                "debug": debug,
                "htmlLengthPython": len(html),
            })

    except Exception as e:
        import traceback

        traceback.print_exc()

        return jsonify({
            "error": str(e),
            "type": type(e).__name__,
            "traceback": traceback.format_exc(),
        }), 500


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 10000)),
    )
