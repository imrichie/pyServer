from http.server import BaseHTTPRequestHandler, HTTPServer
import cgi

# import CRUD Operations from Lesson 1
from database_setup import Base, Restaurant, MenuItem
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Create session and connect to DB
engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


class WebServerHandle(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            if self.path.endswith("/restaurants/new"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                output = ""
                output += "<html><head><style>body {font-family: Helvetica, Arial; color: #333}</style></head>"
                output += "<body><h2>Add new Restaurant</h2>"
                output += "<form method='POST' enctype='multipart/form-data' action='/restaurants/new'>"
                output += "<input name='newRestaurantName' type='text' placeholder='Add New Restaurant'> "
                output += "<input type='submit' value='Create'>"
                output += "</form></html></body>"
                self.wfile.write(bytes(output, "utf-8"))
                return

            if self.path.endswith("/edit"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                output = "<html><body>"
                output += "<h1>"
                output += "Hi"
                output += "</h1>"
                output += "<form method='POST' enctype='multipart/form-data' action = '/restaurants/%s/edit' >" % restaurantIDPath
                output += "<input name = 'newRestaurantName' type='text' placeholder = '%s' >" % myRestaurantQuery.name
                output += "<input type = 'submit' value = 'Rename'>"
                output += "</form>"
                output += "</body></html>"

                # print("The path is: ",self.path)
                # restaurantIDPath = self.path.split("/")[2]
                # myRestaurantQuery = session.query(Restaurant).filter_by(
                #     id=restaurantIDPath).one()
                # if myRestaurantQuery:
                #     self.send_response(200)
                #     self.send_header('Content-type', 'text/html')
                #     self.end_headers()
                #     output = "<html><body>"
                #     output += "<h1>"
                #     output += myRestaurantQuery.name
                #     output += "</h1>"
                #     output += "<form method='POST' enctype='multipart/form-data' action = '/restaurants/%s/edit' >" % restaurantIDPath
                #     output += "<input name = 'newRestaurantName' type='text' placeholder = '%s' >" % myRestaurantQuery.name
                #     output += "<input type = 'submit' value = 'Rename'>"
                #     output += "</form>"
                #     output += "</body></html>"

                self.wfile.write(bytes(output, "utf-8"))

            if self.path.endswith("/restaurants"):
                restaurants = session.query(Restaurant).all()
                output = ""
                output += "<a href = '/restaurants/new'> Make a New Restaurant Here </a></br></br>"
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                output += "<html><body>"
                for restaurant in restaurants:
                    output += str(restaurant.name)
                    output += "</br>"
                    output += "<a href='/edit'>Edit</a> "
                    output += "</br>"
                    output += "<a href='#'>Delete</a>"
                    output += "</br></br></br>"
                output += "</html></body>"
                self.wfile.write(bytes(output, "utf-8"))
                return
        except IOError:
            self.send_error(404, 'File Not Found: %s' % self.path)

    def do_POST(self):
        try:
            #edit restaurants name
            if self.path.endswith("/edit"):
                ctype, pdict = cgi.parse_header(self.headers['content-type'])
                pdict['boundary'] = bytes(pdict['boundary'], "utf-8")
                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)
                    print("Fields value is", fields)
                    messagecontent = fields.get('newRestaurantName')
                    print("New restaurant name is", messagecontent[0].decode("utf-8"))
                    restaurantIDPath = self.path.split("/")[2]

                    myRestaurantQuery = session.query(
                        Restaurant).filter_by(id=restaurantIDPath).one()
                    if myRestaurantQuery != []:
                        myRestaurantQuery.name = messagecontent[0].decode("utf-8")
                        session.add(myRestaurantQuery)
                        session.commit()

                        self.send_response(301)
                        self.send_header('Content-type', 'text/html')
                        self.send_header('Location', '/restaurants')
                        self.end_headers()

            #update new restaurant 
            if self.path.endswith("/restaurants/new"):
                ctype, pdict = cgi.parse_header(self.headers['content-type'])
                pdict['boundary'] = bytes(pdict['boundary'], "utf-8")
                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)
                    print("Fields value is", fields)
                    messagecontent = fields.get('newRestaurantName')
                    print("Restaurant name is", messagecontent[0].decode("utf-8"))

                    # Create new Restaurant object
                    newRestaurant = Restaurant(name=messagecontent[0].decode("utf-8"))
                    session.add(newRestaurant)
                    session.commit()

                    self.send_response(301)
                    self.send_header('Content-type', 'text/html')
                    self.send_header('Location', '/restaurants')
                    self.end_headers()
        except:
            print("Inside the exception block")

def main():
    try:
        server = HTTPServer(('', 8080), WebServerHandle)
        print("Starting web server on the port 8080..")
        server.serve_forever()
    except KeyboardInterrupt:
        print('^C entered. Shutting down the server..')
        server.socket.close()

if __name__ == '__main__':
    main()
