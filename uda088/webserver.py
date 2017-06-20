from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import cgi
from database_setup import Base, Restaurant, MenuItem, engine
from sqlalchemy.orm import sessionmaker
Session = sessionmaker(bind=engine)
session = Session()
rests = session.query(Restaurant).all()


class webServerHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path.endswith("/new"):
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            output = ""
            output += "<html><body>"
            output += "<h1>Make a New Restaurant</h1>"
            output += "<form method = 'POST' enctype='multipart/form-data'>"
            output += "<input name = 'newrest' type = 'text' placeholder = 'New Restaurant Name' > "
            output += "<input type='submit' value='Create'>"
            output += "</form></body></html>"
            self.wfile.write(output)
            return

        if self.path.endswith("/rest"):
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            output = ""
            output += "<html><body>"
            output += "<a href='/new'>add new Restaurant </a><br>"
            for rest in rests:
                output += rest.name
                output += "<br>"
                output += "<a href='#'>del</a>"
                output += "<br>"
                output += "<a href='/rest/%d/edit'>edit</a>"% rest.id
                output += "<br>"
            output += "</body></html>"
            self.wfile.write(output)
            return

        if self.path.endswith('/edit'):
            restQuery = session.query(Restaurant).filter_by(id=self.path.split('/')[2]).one()
            if restQuery:
                self.send_response(200)
                self.send_header('content-type', 'text/html')
                self.end_headers()
                output = ''
                output += '<html><body>'
                output += '<h2> %s <h2>'% restQuery.name
                output += "<form method = 'POST' enctype='multipart/form-data'>"
                output += "<input name='editrest' type='text'>"
                output += "<input type='submit' value='edit'>"
                output += '</from></body></html>'
                self.wfile.write(output)
            return
        else:
            self.send_error(404, 'file not found %s' % self.path)

    def do_POST(self):
        try:
            if self.path.endswith("/new"):
                print 'POST DECTIVE'
                ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)
                    messagecontent = fields.get('newrest')

                    # Create new Restaurant Object
                    newRestaurant = Restaurant(name=messagecontent[0])
                    session.add(newRestaurant)
                    session.commit()

                    self.send_response(301)
                    self.send_header('Content-type', 'text/html')
                    self.send_header('Location', '/rest')
                    self.end_headers()

            if self.path.endswith('/edit'):
                editQuery = session.query(Restaurant).filter_by(id=self.path.split('/')[2]).one()
                if editQuery:
                    ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
                    if ctype == 'multipart/form-data':
                        fields = cgi.parse_multipart(self.rfile, pdict)
                        messagecontent = fields.get('editrest')
                        # change Restaurant name
                        editQuery.name=messagecontent[0]
                        session.add(editQuery)
                        session.commit()

                        self.send_response(301)
                        self.send_header('Content-type', 'text/html')
                        self.send_header('Location', '/rest')
                        self.end_headers()
                        print 'ID:%d changed into %s'%(editQuery.id, editQuery.name)



        except:
            pass


def main():
    try:
        port = 8080
        server = HTTPServer(('', port), webServerHandler)
        print "web server runing on %s" % port
        server.serve_forever()
    except KeyboardInterrupt:
        print "Kill the webserver"
        server.socket.close()


if __name__ == '__main__':
    main()
