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

IP_URL = "http://freegeoip.net/xml/"
def get_coords(ip): #determines coordinates based on IP provided (doesn't work when running locally)
    ip = "4.2.2.2"
    url = IP_URL + ip
    content = None
    try:
        content = urllib2.urlopen(url).read()
    except urllib2.URLError:
        return

    if content:
        #parse xml and find coordinates
        p = minidom.parseString(content)
        lat = p.getElementsByTagName('Latitude')[0].childNodes[0].nodeValue
        lon = p.getElementsByTagName('Longitude')[0].childNodes[0].nodeValue
        return db.GeoPt(lat, lon)


class Art(db.Model):
    title = db.StringProperty(required = True) #sets title to a string and makes it required
    art = db.TextProperty(required = True) #sets title to a text and makes it required (text is same as string but can be more than 500 characters and cannot be indexed)
    created = db.DateTimeProperty(auto_now_add = True) #sets created to equal current date/time
    coords = db.GeoPtProperty() #if you make something

class MainPage(Handler):
    def render_front(self, title="", art="", error="", arts=""):
        arts = db.GqlQuery("SELECT * FROM Art ORDER BY created DESC") #table is named Art because class is named Art (the class creates the table)
        arts = list(arts) #turns the db query above into a list object so that it doesnt run a new db search each time it is called

        mapUrl = "https://maps.googleapis.com/maps/api/staticmap?size=600x300&maptype=roadmap"

        for art in arts: #find which arts have coords
            if art.coords:  #if we have any arts coords, make an image url
                marker = "&markers=" + str(art.coords)
                mapUrl += marker

        #dsiplay the image url
        self.render("front.html", title=title, art=art, error=error, arts=arts, mapUrl=mapUrl)

    def get(self):
        self.write(self.request.remote_addr)
        self.write(repr(get_coords(self.request.remote_addr))) #displays coords for reqeusting IP (repr removes <> from python value so it will print correctly in html)
        self.render_front()

    def post(self):
        title = self.request.get("title")
        art = self.request.get("art")

        if title and art:
            a = Art(title = title, art = art) #creates new art object named a
            #lookup user's coordinates from IP
            coords = get_coords(self.request.remote_addr)
            if coords:
                a.coords = coords
            #if we have coordinates, add them to the Art

            a.put() #stores a in database
            self.redirect("/") #sends you back to main page
        else:
            error = "we need both a title and some artwork!"
            self.render_front(title, art, error)

app = webapp2.WSGIApplication([
    ('/', MainPage)
], debug=True)
