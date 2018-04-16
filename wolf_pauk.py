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
                    newurl = parse.urljoin(self.baseurl, value)
                    print("\nbase: {0}, value: {1}".format(self.baseurl,
                                                           value))
                    print("result: {0}".format(newurl))
                    # And add it to our colection of links:
                    self.links = self.links + [newurl]
        elif tag == 'form':
            for (key, value) in attrs:
                if key == 'action':
                    newurl = parse.urljoin(self.baseUrl, value)
                    print("form action: {0}".format(newurl))
                    self.links = self.links + [newurl]

    # This is a new function that we are creating to get links
    # that our spider() function will call
    def get_links(self, url):
        self.links = []
        # Remember the base URL which will be important when creating
        # absolute URLs
        self.baseurl = url
        # Use the urlopen function from the standard Python 3 library
        response = urlopen(url)
        # Make sure that we are looking at HTML and not other things that
        # are floating around on the internet (such as
        # JavaScript files, CSS, or .PDFs for example)
        print("## Headers")
        for k, v in response.getheaders():
            print("- {0}: {1}".format(k, v))

        if response.getheader('Content-Type').startswith('text/html'):
            htmlbytes = response.read()
            # Note that feed() handles Strings well, but not bytes
            # (A change from Python 2.x to Python 3.x)
            htmlstring = htmlbytes.decode("utf-8")
            self.feed(htmlstring)
            return htmlstring, self.links
        else:
            return "", []


def samescope(u0, u1):
    try:
        p0 = parse.urlparse(u0)
        p1 = parse.urlparse(u1)
        return p1.netloc == p0.netloc
    except:
        return False


def add_unique_params(u0, unique_params):
    if unique_params:
        return u0
    else:
        return u0.split("?", 1)[0]


def spider(url, max_pages, restrict_scope=True, no_unique_params=True):
    pages_to_visit = [url]
    number_visited = 0
    seen = set()

    while pages_to_visit != []:
        number_visited = number_visited + 1
        url = pages_to_visit[0]
        pages_to_visit = pages_to_visit[1:]

        try:
            print("\n#", number_visited, "Visiting:", url)
            parser = LinkParser()
            data, links = parser.get_links(url)
            seen.add(url)

            for link in links:

                if link in seen:
                    continue

                if no_unique_params:
                    link = link.split("?", 1)[0]
                    if link in seen:
                        continue

                if link in pages_to_visit:
                    continue

                if restrict_scope:
                    if samescope(link, url):
                        pages_to_visit.append(link)
                else:
                    pages_to_visit.append(link)

            # print(data)
            # print(pagesToVisit)
            # print(" **Success!**")
        except Exception as e:
            print(e)
            # print(" **Failed!**")

    print("## Links Seen:")
    for item in seen:
        print("- {0}".format(item))
    # print(seen)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: oispider [url(s)]")
        sys.exit(0)

    for arg in sys.argv[1:]:
        spider(arg, 100)
        print("# End {0}\n-----".format(arg))
