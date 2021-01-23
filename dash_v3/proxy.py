from flask import Flask, render_template
from collections import defaultdict

app = Flask(__name__)
routes = {
    "": {"template": "index.html", 
                 "url": "http://localhost:8881",
                 "title": "Single"},
    "single": {"template": "index.html", 
                 "url": "http://localhost:8881",
                 "title": "Single"},
    "multiple": {"template": "index.html",
                 "url": "http://localhost:8882",
                 "title": "Multiple"}
}


class RoutingError(dict):
    pass


class Error404(RoutingError):
    def __init__(self):
        super().__init__({"template": "404.html", "url": "", "title": "404 Error"})


router = defaultdict(Error404, routes)

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def proxy(path, routes=routes):
  proxied = router[path]
  print(f"Route is: {proxied['url']}")
  return render_template(proxied['template'], iframe=proxied['url'], routes=routes)
  
def run_proxy():
    app.run(port=8080, use_reloader=False)

if __name__ == '__main__':
  run_proxy()
