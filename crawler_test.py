#!/usr/bin/python3

# crawler_test.py

from flask import Flask, request,  jsonify
import json
from datetime import datetime
import re
import threading,  queue
from bs4 import BeautifulSoup
import urllib.request
import validators

#
# some global values/defaults
#

default_thread_count = 1
maximum_depth = 2
url_regex = re.compile(r"^https?://")
img_regex = re.compile(r"gif|png|jpe?g$")
submitted_jobs = {}
completed_thread_counter = {}
final_results = {}
q = queue.Queue()

def get_job_id():
        """create a job ID to track submissions to the server"""
        now = datetime.now()
        digits = str(now.strftime("%s"))
        job_id = digits[:3] + '-' + digits[4:]
        return job_id

def get_href_list(url):
    """Return a list of all the href links in the supplied html URL
    Takes a well-formed URL as input, returns a list of links as output"""
    link_list = [] # the list to builid and return
    #req = urllib.request.Request(url)
    
    if validators.url(url): # check to make sure this is a sane url
        
        #try: urllib.request.urlopen(req) # try to open the URL
        try: urllib.request.urlopen(url) # try to open the URL
        except urllib.error.URLError as e:
            print("ERROR! the url: {0} the reason {1}".format(url,  e.reason))
            
        else:
            # read the url and store it in a scalar
            with urllib.request.urlopen(url) as response:
                html = response.read()

            link_soup = BeautifulSoup(html,  'html.parser') # use bs4 to grab all the links with an href and return them as a list
            for one_href in link_soup.find_all('a',  href=True):
                if url_regex.match(one_href['href']):
                    link_list.append(one_href['href'])
    
    return link_list

def get_img_list(url):
    """return all gif, png, jpe*g links from the passed in URL. Takes a well-formed 
    URL as input, returns a list of image src texts as output"""
    
    img_list = [] # the list of images to build and return
    #req = urllib.request.Request(url)
    
    if validators.url(url): # check to make sure this is a sane url
        try: urllib.request.urlopen(url) # try to open the URL
        except urllib.error.URLError as e:
            print("ERROR! The url: {0} t he reason {1}".format(url,  e.reason))
        else: # read the url and store it in a scalar
            with urllib.request.urlopen(url) as response:
                html = response.read()

            img_soup = BeautifulSoup(html,  'html.parser') # use bs4 to grab all the imgs and return them as a list
            
            for one_img in img_soup.find_all('img'):
                if one_img.has_attr('src') == False:
                    continue
                
                if img_regex.search(one_img['src']):
                    img_list.append(one_img['src'])

    return img_list

def recursive_crawl(depth,  url,  recursive_result):
    """ recursively build a list  of images in the HTML source of the passed in URL, to the given 
    depth. The supplied url is at depth 1, so depth=2 means go down one level, 3 means two,
    etc."""

    if recursive_result is None:
        recursive_result = {}
        
    img_list = get_img_list(url)
    if depth == 1:  # we're at maximum depth, so dig back out
        recursive_result[url] = img_list
        return
        
    else:
        one_url_list = get_href_list(url)
        for page_url in one_url_list:
            recursive_crawl(depth-1, page_url,  recursive_result)
            
    return recursive_result

def worker(name, job_id,  depth):
    """a worker thread"""
    print("worker called with name {0} job_id {1} and depth {2}".format(name,  job_id, depth))
    
    while True:
        url = q.get()
        print("worker {0} doing url {1}".format(name,  url))
        results = recursive_crawl(depth,  url,  None)
        print(f'worker {name} finished {url}')
        final_results[job_id].append({url:results})
        q.task_done()

#
# the interface to flask: api routes, etc.
#

app = Flask(__name__)
@app.route('/', methods=['GET',  'POST'])
  
def index():
    if request.method == 'GET': # base page creation
        return """<h1>The Form</h1><form id='crawl' name='crawl' action='/' method='POST'>
    <tt>url_list</tt>: <textarea id='data' rows='4' cols='40' name='data'></textarea>a list of 1 or more URLs, one per line<br />
    <tt>num_threads (default 1)</tt>: <input type='text' name='num_threads' value='1'> the number of threads (max 5)<br />
    <input type='submit' name='submit' value='Submit'>
    </form>"""

    else: # deal with submission
        if "num_threads" in request.form:
            num_threads = int(request.form.get('num_threads'))
        else:
            num_threads = default_thread_count

        url_list = re.split("[\,\s\n]+",  request.form.get('data'))
        for u in url_list: # populate the URLs to crawl
            q.put(u)
        
        # set some info for tracking progress/results
        one_job_id = get_job_id()
        final_results[one_job_id] = []
        submitted_jobs[one_job_id] = url_list
        
        for t in range(num_threads):
            one_thread = threading.Thread(target=worker,  args=(str(t), one_job_id,  maximum_depth),   daemon=True)
            one_thread.start()
        return jsonify({'job_id':one_job_id, 'threads': num_threads,  'urls': url_list})

# 
# requesting the status of a job
#

@app.route('/status/<job_id>')
def status(job_id):
    if job_id in submitted_jobs:
        url_req_count = len(submitted_jobs[job_id])
        completed_url_count = len(final_results[job_id])
        in_progress_count = url_req_count - completed_url_count
        return jsonify({'urls_requested':url_req_count, 'completed': completed_url_count,  'in_progress':in_progress_count})
        
    else:
        return jsonify({'status':'error','message':'That is not a recognized job_id','id':job_id})
    
# 
# fetching results
#

@app.route('/result/<job_id>')
def result(job_id):
    """return the results of the requested job"""
    if job_id not in submitted_jobs:
        return jsonify({'status':'error', 'message':'That is not a recognized job ID', 'id': job_id})
    else:
        if job_id in final_results:
            return jsonify(json.dumps(final_results[job_id]))
        else:
            return jsonify({'status':'waiting','message':'Job still in process', 'id':job_id})
        
#
# actually start the app
#
  

if __name__ == '__main__':
    #app.run(host="0.0.0.0", port=int("5000"))
    app.run()
