from html.parser import HTMLParser
from urllib.request import urlopen
from urllib import parse
import sys

# initial from here:
# http://www.netinstructions.com/how-to-make-a-web-crawler-in-under-50-lines-of-python-code/
# but some parts ripped apart. Honestly works pretty well...

# We are going to create a class called LinkParser that inherits some
# methods from HTMLParser which is why it is passed into the definition
class LinkParser(HTMLParser):

    # This is a function that HTMLParser normally has
    # but we are adding some functionality to it
    def handle_starttag(self, tag, attrs):
        # We are looking for the begining of a link. Links normally look
        # like <a href="www.someurl.com"></a>
        if tag == 'a':
            for (key, value) in attrs:
                if key == 'href':
                    # We are grabbing the new URL. We are also adding the
                    # base URL to it. For example:
                    # www.netinstructions.com is the base and
                    # somepage.html is the new URL (a relative URL)
                    #
                    # We combine a relative URL with the base URL to create
                    # an absolute URL like:
                    # www.netinstructions.com/somepage.html
                    print("base: {0}, value: {1}".format(self.baseUrl, value))
                    newUrl = parse.urljoin(self.baseUrl, value)
                    print("and finally... {0}".format(newUrl))
                    # And add it to our colection of links:
                    self.links = self.links + [newUrl]
        elif tag == 'form':
            for (key, value) in attrs:
                if key == 'action':
                    newUrl = parse.urljoin(self.baseUrl, value)
                    print("form? {0}".format(newUrl))
                    self.links = self.links + [newUrl]

    # This is a new function that we are creating to get links
    # that our spider() function will call
    def getLinks(self, url):
        print("here")
        self.links = []
        # Remember the base URL which will be important when creating
        # absolute URLs
        self.baseUrl = url
        # Use the urlopen function from the standard Python 3 library
        response = urlopen(url)
        print(response)
        # Make sure that we are looking at HTML and not other things that
        # are floating around on the internet (such as
        # JavaScript files, CSS, or .PDFs for example)
        print(response.getheader('Content-Type'))
        print(response.getheaders())
        if response.getheader('Content-Type').startswith('text/html'):
            htmlBytes = response.read()
            # Note that feed() handles Strings well, but not bytes
            # (A change from Python 2.x to Python 3.x)
            htmlString = htmlBytes.decode("utf-8")
            self.feed(htmlString)
            return htmlString, self.links
        else:
            return "",[]

def samescope(u0, u1):
    try:
        p0 = parse.urlparse(u0)
        p1 = parse.urlparse(u1)
        return p1.netloc == p0.netloc
    except:
        return False

def spider(url, maxPages, restrictScope=True):
    pagesToVisit = [url]
    numberVisited = 0
    seen = set()

    while pagesToVisit != []:
        numberVisited = numberVisited +1
        url = pagesToVisit[0]
        pagesToVisit = pagesToVisit[1:]
        try:
            print(numberVisited, "Visiting:", url)
            parser = LinkParser()
            data, links = parser.getLinks(url)

            for link in links:

                if link in seen:
                    continue

                if restrictScope:
                    if samescope(link, url):
                        pagesToVisit.append(link)
                else:
                    pagesToVisit.append(link)

                seen.add(link)

            #print(data)
            print(pagesToVisit)
            print(" **Success!**")
        except Exception as e:
            print(e)
            print(" **Failed!**")

    print(seen)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: oispider [url(s)]")
        sys.exit(0)

    for arg in sys.argv[1:]:
        spider(arg, 10)
