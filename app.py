import os
from urllib.parse import urlparse

from flask import Flask, jsonify, request
from seleniumbase import SB

app = Flask(__name__)


@app.get("/article")
def article():
    url = request.args.get("url", "")

    # Only allow Sky News article URLs
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
            browser.sleep(3)

            # Diagnostic information about the page we actually received.
            debug = browser.execute_script("""
                (() => {
                    const scripts = [...document.querySelectorAll(
                        'script[type="application/ld+json"]'
                    )];

                    return scripts.map((s, i) => ({
                        index: i,
                        length: s.textContent?.length || 0,
                        hasArticleBody: /articleBody/i.test(
                            s.textContent || ''
                        ),
                        hasHector: /Hector Patemore/i.test(
                            s.textContent || ''
                        ),
                        preview: (s.textContent || '').substring(0, 500)
                    }));
                })()
            """)

            return jsonify({
                "url": browser.get_current_url(),
                "title": browser.get_title(),
                "debug": debug,
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
