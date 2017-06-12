#!/usr/bin/env python

import pdfquery
import json
import os

from flask import Flask
from flask import request
from flask import make_response

# Flask app should start in global layout
app = Flask(__name__)

@app.route('/ordemoapp2', methods=['POST'])
def ordemoapp2():
    req = request.get_json(silent=True, force=True)

    print("Request:")
    print(json.dumps(req, indent=4))

    res = processRequest(req)

    res = json.dumps(res, indent=4)
    # print(res)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r


def processRequest(req):
    if req.get("result").get("action") != "searchPDF":
        return {}

    result = req.get("result")
    parameters = result.get("parameters")
    searchText = parameters.get("searchText")
    if searchText is None:
        return {}
    strTxt = 'LTTextLineHorizontal:contains("' + str(searchText) + '")'

    from pdfquery.cache import FileCache
    pdf = pdfquery.PDFQuery("RMS16_og2.pdf",
                            parse_tree_cacher=FileCache("tmp/"))
    pdf.load()
    results = []
    count = 0
    
    for pq1 in pdf.pq(strTxt):
        page_pq = pq1.iterancestors('LTPage').next()   # Use just the first ancestor
        if pq1.text is None:
            results.append({"page#" : page_pq.get("pageid"),
                            "txt" : pq1[0].text})
        else:
            results.append({"page#" : page_pq.get("pageid"),
                            "txt" : pq1.text})
        count = count + 1
        if count == 5:
            break

    res = makeResult(results)
    return res


def makeResult(results):
    print(results)
    if len(results) == 0:
        return {
            "speech": "No result found",
            "displayText": "No result found",
            "source": "ordemoapp2"
            }

    data = json.dumps(results)
    speech = "First few results are: " + data

    print("Response:")
    print(speech)

    return {
        "speech": speech,
        "displayText": speech,
        "source": "ordemoapp2"
    }


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))

    print("Starting app on port %d" % port)

    app.run(debug=True, port=port, host='0.0.0.0')
