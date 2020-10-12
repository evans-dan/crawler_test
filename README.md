# crawler_test

This will act like an API for a threaded web crawler.

Requirements:
- request a number of threads and number of URLs to be crawled
- for each URL requested, return a list of image files (.gif, .png and 
.jp(e)g)
- the list of URLs to be crawled is recursively built, going to a 
hard limit depth of two.
- crawling request is sent via web request, usable through cURL.
- crawl requests are responded to with a job identifier immediately 
(i.e., not after the crawl is complete)
- default number of threads is one, but may be adjusted upwards
- list of URLs is at least one
- status of the submission may be requested by ID
- results of submission may be requested by ID

Usage:

To request a job:
- POST a value called "data" to http://localhost:5000 which is a 
comma-delimited string of URLs. This is required.
- OPTIONAL: include a value called "num_threads" to adjust the number of 
worker threads upwards from the default value of 1. This is optional.

Example with cURL:
curl -X POST http://localhost:5000 -F "num_threads=2" -F "data=https://www.golang.org,www.python.org"

Response: a JSON object summarizing the request and including a job_id

To request status:
curl -X GET http://localhost:5000/status/<job_id>

Response: a JSON object summarizing the number of requests made, the 
number complete, and the number in progress -OR- an error message.

To request results:
curl -X GET http://localhost:5000/result/<job_id>

Response: a JSON object summarising the available results of the request 
-OR- an error message.

A Definition:

- crawling a URL "to the second level" means crawling the URL _and_ each 
page that is on that page. I.e., a request to foo.com will crawl 
foo.com and any page with a link on foo.com, and no deeper.

Known Limitations:

- not all images will be found. This design will only catch the above 
image files that are hard-coded into the HTML. It will not catch 
any image that is displayed encoded into the HTML, nor will it dig 
through images displayed through CSS styling.

- not all "links" will be found. This design will only catch <a> tags 
with an href included in them. Anything effected through JS to act like 
a link without an href will not be found.

Design Decisions:

- requesting the results of an incomplete request will render incomplete 
results. Users should be aware that "incomplete" is not synonymous with 
"unavailable".

Future development:

- authentication. Strict separation of users and requested jobs. 
Possible that User A should not have access to User B's crawling 
requests, even if User A has a job ID from User B.

- testing, testing, testing. Unit test of the link finder and img 
finder. Unit test of a supplied set of mocked up web pages at various 
results to check the discovered data structure versus the "gold 
standard".

- ensure that the number of threads is sensible. No reason to allow for 
more threads than URLs. This number is a design decision that should 
take the architecture and use cases of the server into account.

- longer term storage of results. No reason that results for a URL 
cannot be cached to disk. Consider a simple database or flat file with a 
URL-depth-timestamp-results design, to hasten the return of results.

- "aging out" of cached results. If results are cached, a time limit 
should be set before honouring a request to re-crawl it.

- link following. Right now the crawler will leave the requested domain; 
a switch could be given to ignore links that leave the base request URL 
(e.g. requesting a company site may yield a link to a twitter page; 
returning results there could be controlled).

- better logging. Messages just appear in the terminal where the 
script is running; actual logging of the results (and control of logging 
level) could be greatly improved.

- output control: allowing the user to choose what the output of the 
various requests actually is: a JSON object, plain text, a web page, 
etc.

- error handling. Right now bad URLs are returned with zero results. 
This behaviour could be modified based on user request (silently drop, 
cancel the whole job, e.g.).

- deeper reading of html source. Consider finding CSS definitions and 
parsing them for image content.
