from flask import Flask, render_template, url_for, request, jsonify
import os
import twitterWeb
import webpage_demo

app = Flask(__name__)

@app.route("/")
def index():
    """ Open the main website page """
    return render_template("index.html")
    
@app.route('/twitter')
def generateTwitter():
    """ 
        Grab information from the website UI, run it through the algorithm,
        and return a dictionary containing the generated tweets.
    """
    response = ""
    username = request.args.get("username")
    amount = request.args.get("amount")
    which = request.args.get("which")
    file = twitterWeb.TwitterData(username).execute()
    response = webpage_demo.twitter(file, 5, int(amount), str(which))
    os.remove(file)
    toReturn = {}
    for i in range(len(response)):
        toReturn[str(i)] = response[i]
    return jsonify(result=toReturn)
    
@app.route('/yelp')
def generateYelp():
    """
        Grab information from the website UI, run it through the algorithm,
        and return a dictionary containing the generated Yelp reviews.
    """
    response = ""
    amount = request.args.get("amount")
    which = request.args.get("which")
    file = os.path.abspath("data/yelp_1000r_50l.tags")
    response = webpage_demo.yelp_or_gutenberg(file, 5, int(amount), str(which))
    toReturn = {}
    for i in range(len(response)):
        toReturn[str(i)] = response[i]
    return jsonify(result=toReturn)
    
@app.route('/gutenberg')
def generateGutenberg():
    """
        Grab information from the website UI, run it through the algorithm,
        and return a dictionary containing the generated sentences.
    """
    response = ""
    amount = request.args.get("amount")
    which = request.args.get("which")
    file = os.path.abspath("data/hp_and_the_ss.tags")
    response = webpage_demo.yelp_or_gutenberg(file, 5, int(amount), str(which))
    toReturn = {}
    for i in range(len(response)):
        toReturn[str(i)] = response[i]
    return jsonify(result=toReturn)


@app.context_processor
def override_url_for():
    """ Used to fix web cache issues wheh modifying JS and CSS while testing website """
    return dict(url_for=dated_url_for)

def dated_url_for(endpoint, **values):
    """ Used to fix web cache issues when modifying JS and CSS while testing website """
    if endpoint == 'static':
        filename = values.get('filename', None)
        if filename:
            file_path = os.path.join(app.root_path, endpoint, filename)
            values['q'] = int(os.stat(file_path).st_mtime)
    return url_for(endpoint, **values)
    
if __name__ == "__main__":
    app.run()
