#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.ext.webapp import template
from google.appengine.api import users
from google.appengine.ext import db
from google.appengine.api import mail
import cgi



import os

class Campaign(db.Model):
	author = db.UserProperty()
	

class Feedback(db.Model):
	"Model of an individual feedback "
	message = db.StringProperty(multiline=True)
	date = db.DateTimeProperty(auto_now_add=True)


class FeedbackHandler(webapp.RequestHandler):
	def get(self, key):
		campaign = db.get(key)
		if campaign is None:
			self.response.out.write("No item found")
			return
		
		path = os.path.join(os.path.dirname(__file__), 'templates/feedback.html')
		self.response.out.write(template.render(path, {'campaign': campaign }))
	
	def post(self, key):
		content = cgi.escape(self.request.get('content'))
		campaign = db.get(key)
		
		feedback = Feedback(parent=campaign)
		feedback.message = content
		feedback.put()
		
		# Send email
		path = os.path.join(os.path.dirname(__file__), 'templates/email.txt')
		mail_body = template.render(path, {'feedback': feedback })
		
		mail.send_mail(sender="FeedbackMe <nvquanghuy@gmail.com>", to=campaign.author.email(),
              subject="Someone Wrote You A Feedback", body=mail_body)

		self.response.out.write('Done. You can close the form now.')

class CreateHandler(webapp.RequestHandler):
	def get(self):
		user = users.get_current_user()
		if not user: self.redirect(users.create_login_url(self.request.uri))
		
		campaign = Campaign()
		campaign.author = user
		campaign.put()
		
		path = os.path.join(os.path.dirname(__file__), 'templates/create.html')
		self.response.out.write(template.render(path, {'key': campaign.key() }))


class MainHandler(webapp.RequestHandler):
	def get(self):
		path = os.path.join(os.path.dirname(__file__), 'templates/index.html')
		self.response.out.write(template.render(path, {}))

def main():
	application = webapp.WSGIApplication([('/', 					MainHandler),
																				('/create',			CreateHandler),
																				('/f/(.*)',			FeedbackHandler),
																				], debug=True)
	util.run_wsgi_app(application)


if __name__ == '__main__':
	main()
