#!/usr/bin/env python

import os

from google.appengine.ext import webapp
from google.appengine.api import users
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db

from roadmate.handlers.baserequesthandler import BaseRequestHandler
from roadmate.models.rideoffer import RideOffer
from roadmate.models.rideoffer import RideOfferForm

# ----------------------------------------------------------------------------
#  Request Handlers
# ----------------------------------------------------------------------------

class IndexPageHandler(BaseRequestHandler):
	"""
		RoadMate RequestHandler
		
		Pages:
			/index.html
	"""
	
	def generate_template_values(self, page_path):
		"""
			generate_template_values
			
			Generates a dictionary of template values required by the pages
			served from this request handler.
			
		"""
		
		
		# --------------------------------------------------------------------
		# Generate Template Values
		# --------------------------------------------------------------------
		template_values = BaseRequestHandler.generate_template_values(self, 
			page_path)

		rides = db.GqlQuery("SELECT * FROM RideOffer ORDER BY date DESC LIMIT 10")
		
		# --------------------------------------------------------------------
		# Store Template Values
		# --------------------------------------------------------------------
		
		template_values['rides'] = rides
		
		return template_values
		
		
	def get(self):
		# --------------------------------------------------------------------
		# Generate Template Values
		# --------------------------------------------------------------------
		template_values = self.generate_template_values(self.request.url)

		template_values['logout_url'] = users.create_logout_url('/')

		# --------------------------------------------------------------------
		# Render and Server Template
		# --------------------------------------------------------------------
		page_path = os.path.join(os.path.dirname(__file__), 'index.html')
		self.response.out.write(template.render(page_path, template_values))
		
# ----------------------------------------------------------------------------
#  Program Entry Point
# ----------------------------------------------------------------------------

def main():
	
	# Instalise web application
	application = webapp.WSGIApplication(
		[
		 ('/', IndexPageHandler),
		 ('/index.html', IndexPageHandler)
		], debug=True)
	run_wsgi_app(application)


if __name__ == '__main__':
  main()