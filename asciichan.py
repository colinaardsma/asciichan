import os, webapp2, urllib2
import jinja2
from xml.dom import minidom
from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                               autoescape = True)

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

IP_URL = "http://api.hostip.info/?ip="
def get_coords(ip):
    url = IP_URL + ip
    content = None
    try:
        content = urllin2.urlopen(url).read()
    except URLError:
        return

    if content:
        #parse xml and find coordinates
        p = minidom.parseString(xml)
        coords = p.getElementsByTagName('gml:coordinates')
        if coords and coords[0].childNodes[0].nodeValue:
            lon = coords[0].childNodes[0].nodeValue.split(",")[0]
            lat = coords[0].childNodes[0].nodeValue.split(",")[1]
            loc = lat + ", " + lon
        print lat, lon
        return lat, lon

class Art(db.Model):
    title = db.StringProperty(required = True) #sets title to a string and makes it required
    art = db.TextProperty(required = True) #sets title to a text and makes it required (text is same as string but can be more than 500 characters and cannot be indexed)
    created = db.DateTimeProperty(auto_now_add = True) #sets created to equal current date/time

class MainPage(Handler):
    def render_front(self, title="", art="", error="", arts=""):
        arts = db.GqlQuery("SELECT * FROM Art ORDER BY created DESC") #table is named Art because class is named Art (the class creates the table)
        self.render("front.html", title=title, art=art, error=error, arts=arts)

    def get(self):
        self.render_front()

    def post(self):
        title = self.request.get("title")
        art = self.request.get("art")

        if title and art:
            a = Art(title = title, art = art) #creates new art object named a
            #lookup user's coordinates from IP

            a.put() #stores a in database
            self.redirect("/") #sends you back to main page
        else:
            error = "we need both a title and some artwork!"
            self.render_front(title, art, error)

app = webapp2.WSGIApplication([
    ('/', MainPage)
], debug=True)
