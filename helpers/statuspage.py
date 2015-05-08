#!/usr/bin/env python

import cherrypy
import psycopg2
import logging
import threading
import time

class StatusPage:

    def __init__(self, keywords={'database' : 'test'}):
        self.http_port = 8081
        if 'http_port' in keywords:
            self.http_port = keywords['http_port']
            del keywords['http_port']

        if len(keywords) == 0:
            keywords = {'host' : 'localhost'}

        self.libpq_keywords = keywords

    @cherrypy.expose
    def master(self):
        if self.pg_is_in_recovery():
            cherrypy.response.status = 404
        else:
            cherrypy.response.status = 200

    @cherrypy.expose
    def slave(self):
        if self.pg_is_in_recovery():
            cherrypy.response.status = 200
        else:
            cherrypy.response.status = 404
            

    @cherrypy.expose
    def status(self):
        return "Status"

    def connect(self):
        conn = psycopg2.connect(**self.libpq_keywords)
        conn.set_session(readonly=True)
        conn.cursor().execute("SET application_name TO 'Governor: health check'")
        return conn

    def connect(self):
        conn = psycopg2.connect(**self.libpq_keywords)
        conn.set_session(readonly=True)
        conn.cursor().execute("SET application_name TO 'Governor: health check'")
        return conn

    def pg_is_in_recovery(self):
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT pg_is_in_recovery()")
            is_in_recovery = cursor.fetchone()[0]
            cursor.close()
        except (psycopg2.OperationalError, psycopg2.InterfaceError):
            logging.exception('Error occured while querying postgres')
            self.conn = self.connect()
            return None

        return is_in_recovery

    def start(self):
        self.conn = self.connect()

        cherrypy.server.socket_port = self.http_port
        cherrypy.quickstart(self)
    
    def stop(self):
        pass

if __name__ == '__main__':
    import sys
    logging.basicConfig(format='%(levelname)-6s %(asctime)s - %(message)s', level=logging.DEBUG)
    logging.debug("Starting as a standalone application")

    keywords = {}
    for arg in sys.argv[1:]:
        parameter = arg.split('=',1)
        keywords[parameter[0]] = parameter[1]

    logging.debug("Supplied keywords: {}".format(keywords))
    sp = StatusPage(keywords)

    thread = threading.Thread(target=sp.start)
    thread.daemon = True

    thread.start()

    try:
        while thread.isAlive():
            thread.join(1)
        logging.debug("The Status Page thread ended by itself")
    except:
        sp.stop()
        logging.exception('')

