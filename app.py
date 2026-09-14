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
            browser.sleep(3)

            body = browser.execute_script("""
                for (const s of document.querySelectorAll(
                    'script[type="application/ld+json"]'
                )) {
                    try {
                        const d = JSON.parse(s.textContent || '');
                        const items = Array.isArray(d) ? d : [d];

                        for (const x of items) {
                            if (x && x.articleBody) {
                                return x.articleBody;
                            }
                        }
                    } catch (e) {}
                }

                return '';
            """)

            return jsonify({
                "articleBody": body or "",
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
