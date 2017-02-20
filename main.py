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
import os
import webapp2
import jinja2

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape = True)

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

class Post(db.Model):
    title = db.StringProperty(required = True)
    post = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)

class New(Handler):
    def render_new(self, title="", post="", error=""):
        self.render("new.html", title=title, post=post, error=error)

    def get(self):
        self.render_new()

    def post(self):
        title = self.request.get("title")
        post = self.request.get("post")

        if title and post:
            p = Post(title = title, post = post)
            p.put()

            self.redirect("/")
        else:
            error = "we need both a title and a post!"
            self.render_new(title, post, error = error)

class ViewPostHandler(webapp2.RequestHandler):
    def get(self, id):
        key = Post.get_by_id( int(id) )
        t = jinja_env.get_template("single-blog.html")
        #id = int(id)
        #post = db.GqlQuery("SELECT * FROM Post WHERE id =%s" % key)

        #q = Post.all().filter("id", int(id))
        #post = q.get()
        title = key.title
        post = key.post

        if not key:
            self.response.write("Sorry there is no blog post here")
        else:
            content = t.render(title = title, post = post)
            self.response.write(content)

class FakeMainPage(Handler):
    def get(self):
        self.redirect("/blog")
    def post(self):
        self.redirect("/blog")

class MainPage(Handler):
    def render_front(self, title="", post=""):
        posts = db.GqlQuery("SELECT * FROM Post ORDER BY created DESC LIMIT 5")

        self.render("front.html", title=title, post=post, posts=posts)

    def get(self):
        self.render_front()
    def post(self):
        self.redirect("/blog")

def get_posts(limit, offset):
    posts = db.GqlQuery("SELECT * FROM Post ORDER BY created DESC LIMIT limit OFFSET offset")

app = webapp2.WSGIApplication([
    ('/', FakeMainPage),
    ('/blog', MainPage),
    ('/new', New),
    webapp2.Route('/blog/<id:\d+>', ViewPostHandler)
], debug=True)
