import webapp2
import os
import jinja2
import hmac
import time
import datetime
import operator
from PIL import Image

hashcode="YOUTHOUGHTYOUWERESLICK"

from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.api import images

#template_dir=os.path.join(os.path.dirname(__file__),'templates')
jinja_env=jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)), autoescape=True)

def hash_str(s):
    return hmac.new(hashcode, s).hexdigest()

def make_secure_val(s):
    return "%s|%s" % (s, hash_str(s))

def check_secure_val(h):
    val=h.split('|')[0]
    if h==make_secure_val(val):
        return val

def render_str(template, **params):
    t = jinja_env.get_template(template)
    return t.render(params)


def isLoggedIn(s):
    if s==None or s=="None":
        return False
    else:
        return True

def xHoursAgo(x):
    fmt = '%a %b %d %H:%M:%S +0000 %Y'
    time.strftime(fmt)
    createdat = x
    createdtim = time.strptime(createdat, fmt)
    hoursago = (time.time() - time.mktime(createdtim)) / 3600
    return int(hoursago)

def timesince(x):
    y=x
    fmt = '%a %b %d %H:%M:%S +0000 %Y'
    time.strftime(fmt)
    createdat = x.strftime(fmt)
    createdtim = time.strptime(createdat, fmt)
    secsago = (time.time() - time.mktime(createdtim))
    minsago = (time.time() - time.mktime(createdtim)) / 60
    hoursago = (time.time() - time.mktime(createdtim)) / 3600
    daysago = (time.time() - time.mktime(createdtim)) / (3600*24)
    weeksago = (time.time() - time.mktime(createdtim)) / (3600*24*7)
    if minsago < 1:
        return "%ds ago" % int(int(secsago)+1)
    elif hoursago < 1:
        return "%dm ago" % int(int(minsago))
    elif hoursago >=1 and hoursago < 24:
        return "%dh ago" % int(int(hoursago))
    elif hoursago >= 24 and daysago < 7:
        return y.strftime("%A")
    elif daysago >= 7:
        return "%dw ago" % int(int(weeksago)+1)
    else:
        return "Couldn't calculate the time"
    return int(hoursago)


#----------------------------------------

class custFunc(webapp2.RequestHandler):
    def main(self, the_file, needposts=None, **params):
        user_cookie_str = self.request.cookies.get("user")
        user=0
        final_posts=[]
        if user_cookie_str:
            user_val=check_secure_val(user_cookie_str)
            if user_val:
                user=str(user_val)
                u=Users.by_user(user)
                if u:
                    if needposts:
                        posts=db.GqlQuery("SELECT * FROM Post ORDER by created DESC ")
                        for i in posts:
                            i.xcreated = timesince(i.created)
                            final_posts.append(i)
                            #i.comment.sort(key=lambda x: x.commenttime, reverse=True)
                        return self.render(the_file, posts=final_posts, settingslink="/user/editme/general", settings="Settings",
                            accountlink="/usr/%s" % user, account="My Account", newpostlink="/newpost", newpost="Write",
                            trendinglink="/trending", trending="Trending", logoutlink="/signout", logout="Logout", **params)
                    return self.render(the_file, settingslink="/user/editme/general", settings="Settings",
                        accountlink="/usr/%s" % user, account="My Account", newpostlink="/newpost", newpost="Write",
                        trendinglink="/trending", trending="Trending", logoutlink="/signout", logout="Logout", **params)
                else:
                    self.response.headers.add_header('Set-Cookie', 'user=None; path=/')
                    return self.redirect("/signin")
            else:
                self.response.headers.add_header('Set-Cookie', 'user=None; path=/')
                return self.redirect("/")
        else:
            self.response.headers.add_header('Set-Cookie', 'user=None; path=/')
            return self.redirect("/")

class Handler(webapp2.RequestHandler):
    def write(self,*a, **kw):
        self.response.out.write(*a,**kw)
    def render_str(self,template,**params):
        t=jinja_env.get_template(template)
        return t.render(params)
    def render(self,template,**kw):
        self.write(self.render_str(template,**kw))
    def login(self, username, password):
        new_user_val=make_secure_val(str(username))
        self.response.headers.add_header('Set-Cookie','user=%s' % new_user_val)
    def delete(self, todelete, property, name):
        u=db.GqlQuery("SELECT * FROM %s WHERE %s='%s'" % (todelete, property, name))
        db.delete(u)
    def signout(self):
        self.response.headers.add_header('Set-Cookie', 'user=None; path=/')
        self.redirect("/")
    def verifyForms(self, type, var):
        valid_name='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ '
        valid_username='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890-_.'
        valid_email='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890-_.@'
        valid_number='+0123456789'
        if type=="name":
            if len(var)<4:
                return None
            for i in var:
                if i not in valid_name:
                    return None
            return "Valid"
        if type=="username":
            if len(var)<=3:
                return None
            for i in var:
                if i not in valid_username:
                    return None
            return "Valid"
        if type=="email":
            for i in var:
                if i not in valid_email:
                    return None
            return "Valid"
        if type=="number":
            if len(var)!=10:
                return None
            for i in var:
                if i not in valid_number:
                    return None
            return "Valid"
        if type=='password':
            if len(var)<=7:
                return None
            return "Valid"
        else:
            return None

    def getLoginInfo(self):
        user_cookie_str = self.request.cookies.get("user")
        if user_cookie_str=="None" or user_cookie_str==None:
            return None
        if user_cookie_str:
            user_val=check_secure_val(user_cookie_str)
            if user_val:
                return str(user_val)

def render_post(response, post):
    response.out.write('<b>' + post.subject + '</b><br>')
    response.out.write(post.content)

def blog_key(name = 'default'):
    return db.Key.from_path('blogs', name)

class Post(db.Model):
    title=db.StringProperty()
    content=db.TextProperty()
    author=db.StringProperty(required = True)
    authorid=db.StringProperty()
    created=db.DateTimeProperty(auto_now_add = True)
    views=db.IntegerProperty()
    image=db.BlobProperty()

    def render(self):
        self._render_text = self.content.replace('\n', '<br>')
        return render_str("post.html", p = self)


class Comment(db.Model):
    post=db.ReferenceProperty(Post, collection_name='comment')
    commenttime=db.StringProperty()
    postid=db.StringProperty()
    commentor=db.StringProperty()
    comments=db.StringProperty()

class Like(db.Model):
    post=db.ReferenceProperty(Post, collection_name='like')
    postid=db.StringProperty()
    liker=db.StringProperty()
    likes=db.StringProperty()

class Unlike(db.Model):
    post=db.ReferenceProperty(Post, collection_name='unlike')
    postid=db.StringProperty()
    unliker=db.StringProperty()
    unlikes=db.StringProperty()

class React(Handler):
    def post(self):
        response=self.getLoginInfo()
        if response:
            reaction=self.request.get("reaction")
            #if reaction=="like":


class postImage(webapp2.RequestHandler):
    def get(self, postid):
        print "Got it"
        key = db.Key.from_path('Post', int(postid), parent=blog_key())
        post = db.get(key)
        if post.image:
            self.response.headers['Content-Type'] = 'image/jpeg'
            self.response.out.write(post.image)
            return
        else:
            print "No image"
            self.response.out.write('No image')

class userImage(webapp2.RequestHandler):
    def get(self, username):
        print "Got it"
        user = Users.all().filter('username =', username).get()
        if user.photo:
            self.response.headers['Content-Type'] = 'image/jpeg'
            self.response.out.write(user.photo)
            return
        else:
            print "No image"
            self.response.out.write('No image')

class NewPost(Handler, custFunc):
    def get(self):
        response = self.getLoginInfo()
        if not response:
            self.main("signin.html", error="You need to login to create a post!")
        elif response:
            #custFunc.main(self,"newpost.html")
            self.main("newpost.html", username=response)

    def post(self):
        title=self.request.get("title")
        content=self.request.get("content")
        if len(str(title)) > 100:
            return self.main("newpost.html", title=title, content=content, error="The title is too long! ")
        if len(title) > 2000:
            return self.main("newpost.html", title=title, content=content, error="The description is too long! ")
        image = self.request.POST.get("image", None)
        try:
            image.value
            image = images.resize(image.value, 702,702)
        except AttributeError:
            image=None
        response = self.getLoginInfo()
        if response:
            if title or content or image:
                authorid=Users.all().filter('username =', response).get()
                content = content.replace('\n', '<br>')
                a = Post(parent=blog_key(), title=title, content=content, author=response,
                image=image, authorid=str(authorid.key().id()))
                a.put()
                self.redirect("/p/%s" % str(a.key().id()))
            else:
                custFunc.main(self,"newpost.html",error="What do you want to post? ")
        else:
            self.redirect('/signin')

class MainPage(Handler, custFunc):
    def get(self):
        user_cookie_str=self.request.cookies.get('user')
        if user_cookie_str=="None" or user_cookie_str==None:
            return self.redirect('/signin')
        self.main("index.html", needposts="True!")

    def post(self):
        q=self.request.get("q")
        if q:
            posts=db.GqlQuery("SELECT * FROM Post ORDER BY created DESC")
            final_posts=[]
            for i in posts:
                if q.upper() in (i.title).upper() or q.upper() in (i.content).upper() or q.upper() in (i.author).upper():
                    final_posts.append(i)
            if final_posts==[]:
                return self.main("index.html", error="No matching results for %s" % q,
                end="Results for %s" % q, search=q)
            return self.main("index.html", posts=final_posts, end="Results for %s" % q, search=q)
        return self.redirect('/')

class Trending(Handler, custFunc):
    def get(self):
        user_cookie_str=self.request.cookies.get("user")
        posts=db.GqlQuery("SELECT * FROM Post ORDER BY views DESC LIMIT 20")
        final_posts=[]
        if user_cookie_str:
            user_val=check_secure_val(user_cookie_str)
            if user_val:
                user=str(user_val)
                for i in posts:
                    i.xcreated = timesince(i.created)
                    final_posts.append(i)
                    #i.comment.sort(key=lambda x: x.commenttime, reverse=True)
                self.main("index.html", end="Trending Posts", posts=final_posts)
            else:
                self.response.headers.add_header('Set-Cookie', 'user=None; path=/')
                return self.redirect("/")
        else:
            self.response.headers.add_header('Set-Cookie', 'user=None; path=/')
            return self.redirect("/")



class Google(Handler):
    def get(self):
        user=users.get_current_user()
        if user:
            self.render("register.html", username=user.user_id(), value_email=user.email())
        else:
            self.redirect(users.create_login_url(self.request.uri))


class AboutPage(Handler, custFunc):
    def get(self):
        response=self.getLoginInfo()
        if response:
            self.render('about.html', url2="/signout", text2="log-out",
                url1="/usr/%s" % response, text1="person", url3="/newpost", text3="edit")
        else:
            self.render('about.html')

class PostPage(Handler, custFunc):
    def get(self, post_id):
        key = db.Key.from_path('Post', int(post_id), parent=blog_key())
        post = db.get(key)
        if not post:
            self.error(404)
            return
        if post.views:
            post.views = int(post.views) + 1
        else:
            post.views = int(1)
        post.put()
        response=self.getLoginInfo()
        if response:
            post.xcreated = timesince(post.created)
            self.main('permalink.html', post=post)
        else:
            self.render('permalink.html', post=post)
    def post(self, post_id):
        comment = self.request.get('commenti')
        if not comment.isspace() and comment!="":
            key = db.Key.from_path('Post', int(post_id), parent=blog_key())
            post = db.get(key)
            post.views=int(post.views) + 1
            post.put()
            response = self.getLoginInfo()
            if response:
                idd=str(post_id)+str(time.time())
                Comment(key_name=str(idd), post = post, commenttime=str(int(time.time())), comments=comment, commentor=response).put()
                commenthtml='<div class="comment"><div class="post-comment-author"><a href="usr/%s">%s</a></div><div class="post-comment">%s</div></div>' % (response, response, comment)
                ret="%s %s" % (post_id, commenthtml)
                self.response.out.write(ret)
                #return self.redirect('/p/%s' % int(post_id))
            else:
                self.render('permalink.html', post=post, error="Don't you think you should login first?")


class Users(db.Model):
    name=db.StringProperty()
    username=db.StringProperty(required = True)
    password=db.StringProperty(required = True)
    photo=db.BlobProperty()
    bio=db.TextProperty()
    website=db.StringProperty()
    carrier=db.StringProperty()
    gender=db.StringProperty()
    verified=db.StringProperty()
    email=db.EmailProperty()
    number=db.PhoneNumberProperty()
    registered=db.DateTimeProperty(auto_now_add = True)


    def trender(self):
        return render_str("user.html", u = self)

    @classmethod
    def by_user(cls, name):
        return Users.all().filter('username =', name).get()


class Follow(db.Model):
    user = db.ReferenceProperty(Users, collection_name='following')
    followings = db.StringProperty()


class Follower(db.Model):
    user = db.ReferenceProperty(Users, collection_name='follower')
    followers = db.StringProperty()


class Notify(db.Model):
    user = db.ReferenceProperty(Users, collection_name='notification')
    notifications = db.StringProperty()


class FollowWeb(Handler):
    def get(self):
        user_cookie_str=self.request.cookies.get('user')
        if user_cookie_str:
            user_val=check_secure_val(user_cookie_str)
            if user_val:
                cookie_user=str(user_val)
                user=Users.all().filter('username =', cookie_user).get()
                self.render('follow.html', user = user)
    def post(self):
        tounfollow = self.request.get("tounfollow")
        if tounfollow:
            u=db.GqlQuery('SELECT * FROM Follow')
            db.delete(u)
            return self.render('follow.html')
        users=Users.all().get()
        user_cookie_str=self.request.cookies.get('user')
        if user_cookie_str:
            user_val=check_secure_val(user_cookie_str)
            if user_val:
                cookie_user=str(user_val)
                user=Users.all().filter('username =', cookie_user).get()
                userkey=str(user.key().id())
                tofollow=self.request.get('tofollow')
                tofollowuser=Users.all().filter('username =', tofollow).get()
                tofollowuserkey=str(tofollowuser.key().id())
                if tofollow in users.username:
                    Follow(user=user,followings=tofollowuserkey).put()
                    Follower(user=tofollowuser, followers=userkey)
                    Notify(user=user, notifications="%s is now following you!" % user_val)
                    return self.render("follow.html", user=user)
                else:
                    return self.render("follow.html", user=user, error="User already exists")

class UserPage(Handler, custFunc):
    def get(self, user_id):
        #key = db.Key.from_path('Users', int(user_id))
        #user = db.get(key)
        tuser = Users.all().filter('username =', user_id).get()
        posts = db.GqlQuery("SELECT * FROM Post WHERE author = '%s' ORDER BY created DESC" % tuser.username)
        a=self.getLoginInfo()
        if not tuser:
            self.error(404)
            return
        final_posts=[]
        for i in posts:
            i.xcreated = timesince(i.created)
            final_posts.append(i)
        if posts:
            if a==tuser.username:
                return self.main("userlink.html", user = tuser, final_posts=final_posts, owner="True!")
            return self.main("userlink.html", user = tuser, final_posts=final_posts)
        if a==tuser.username:
            return self.main("userlink.html", user = tuser, owner="True!")
        return self.main("userlink.html", user = tuser)

class EditUser(Handler, custFunc):
    def get(self):
        response = self.getLoginInfo()
        if response:
            user = Users.all().filter('username =', response).get()
            self.main("edituser.html", user=user)
        else:
            return self.redirect('/')
    def post(self):
        response = self.getLoginInfo()
        if response:
            user =  Users.all().filter('username =', response).get()
            name = self.request.get("name")
            email = self.request.get("email")
            number = self.request.get("number")
            bio = self.request.get("bio")
            website = self.request.get("website")
            gender = self.request.get("gender")
            photo = self.request.POST.get("image", None)
            try:
                photo.value
                photo = images.resize(photo.value, 512,512)
                print "\n\n\nNew Photo found\n\n\n"
            except AttributeError:
                print "\n\n\nPhoto set to original photo\n\n\n"
                photo=user.photo
            if self.verifyForms('name', name)==None:
                return self.main("edituser.html", user=user,
                            error="Names only have alphabetical characters! ")
            if self.verifyForms('email', email)==None:
                return self.main("edituser.html", user=user,
                            error="Valid e-mail can contain only latin letters, numbers, '@' and '.' ")
            if self.verifyForms('number', number)==None:
                return self.main("edituser.html", user=user,
                            error="Numbers only have digits! ")
            if not None:
                user.name = name
                user.email = email
                user.number = number
                user.bio = bio
                user.website = website
                user.gender = gender
                user.photo = photo
                user.put()
                return self.main("edituser.html", user=user,
                            success="Changes were saved!")

class ChangePassword(Handler, custFunc):
    def get(self):
        response = self.getLoginInfo()
        if response:
            user = Users.all().filter('username =', response).get()
            self.main("changepassword.html",
                        username=user.username)
        else:
            return self.redirect('/signin')

    def post(self):
        response = self.getLoginInfo()
        if response:
            password = self.request.get("password")
            newpassword = self.request.get("newpassword")
            retypepassword = self.request.get("retypepassword")
            user =  Users.all().filter('username =', response).get()
            if password==user.password:
                if self.verifyForms(type='password', var=newpassword) != None:
                    if newpassword==retypepassword:
                        user.password=newpassword
                        user.put()
                        return self.main("changepassword.html", username=user.username, success="Changes were saved!")
                    else:
                        self.render("changepassword.html", username=user.username, error="Passwords do not match!")
                else:
                    self.render("changepassword.html", username=user.username, error="Password must be at least 8 characters!")
            else:
                self.render("changepassword.html", username=user.username, error="Password is not correct!")


class SignIn(Handler):
    def get(self):
        response=self.getLoginInfo()
        if response:
            self.render('signin.html', user=response)
        else:
            self.render('signin.html')
    def post(self):
        username=self.request.get("username")
        password=self.request.get("password")
        if username and password:
            u=Users.by_user(username)
            if u:
                if u.password==password:
                    self.login(username, password)
                    return self.redirect("/")
                else:
                    self.render("signin.html", error="Sorry, your password was incorrect", username=username)
            else:
                error="Sorry, your username was incorrect"
                self.render("signin.html", error=error)
        else:
            error="I couldn't connect to ThoughtsJournal"
            self.render("signin.html", error=error, username=username, password=password)

class Test(Handler):
    def get(self):
        self.render('test.html')

class signout(Handler):
    def get(self):
        self.signout()

class DeletePost(Handler):
    def get(self):
        return self.error(404)
    def post(self):
        response=self.getLoginInfo()
        post_id=self.request.get('postid')
        key = db.Key.from_path('Post', int(post_id), parent=blog_key())
        post = db.get(key)
        if post.author==response:
            for i in post.comment:
                db.delete(i)
            db.delete(post)
        else:
            return

class Delete(Handler):
    def get(self):
        self.render("delete.html")
    def post(self):
        user_cookie_str=self.request.cookies.get("user")
        if user_cookie_str:
            user_val=check_secure_val(user_cookie_str)
            if user_val:
                user=str(user_val)
                self.response.headers.add_header('Set-Cookie', 'user=None; path=/')
                self.delete('Users', 'username', user)
                #db.delete(db.GqlQuery('SELECT * FROM Post '))
                return

class SignUp(Handler):
    def get(self):
        response = self.getLoginInfo()
        if response:
            self.render('signin.html', user=response)
        else:
            self.render('signup.html')

    def post(self):
        username=self.request.get("username")
        email=self.request.get("email")
        number=self.request.get("number")
        password=self.request.get("password")
        u = Users.by_user(username)
        if username and password:
            isError = None
            error = ""
            if self.verifyForms(type='username', var=username) == None:
                isError = True
                error += 'The username is not valid!'
            if self.verifyForms(type='email', var=email) == None:
                isError = True
                error += 'The email is not valid!'
            if self.verifyForms(type='number', var=number) == None:
                isError = True
                error += 'The number is not valid!'
            if self.verifyForms(type='password', var=password) == None:
                isError = True
                error += 'The password does not qualify!'
            if isError:
                return self.render("signup.html", error=error, username=username, email=email, number=number,
                password=password)
            if u:
                error="You cannot use this username as it is already in use!"
                self.render("signup.html", error=error)
            else:
                s = Users(name="Unknown", username = username, password = password, email = email, number = number,
                bio="I use ThoughtsJournal!", website="http://thoughts-journal.appspot.com")
                s.put()
                Follow(user=s, followings = str(s.key().id())).put()
                Notify(user=s, notifications="Your very first notification! All of your notifications will appear here.")
                self.login(username, password)
                time.sleep(0.1)
                self.redirect('/user/editme/general')
                return
                #p=hash_str(password)
        else:
            return self.render("signup.html", errors='Please fill all the boxes',
                                   username=username, email=email, number=number, password=password)

class Verify(Handler):
    def get(self):
        self.render('verify.html')

class Admin(Handler):
    def get(self):
        response = self.getLoginInfo()
        if response=='admin':
            self.render("admin.html")
        else:
            self.error(404)
    def post(self):
        delete = self.request.get('delete')
        if delete:
            db.delete(db.GqlQuery("SELECT * FROM Follow"))
            db.delete(db.GqlQuery("SELECT * FROM Post"))
            db.delete(db.GqlQuery("SELECT * FROM Follower"))
            db.delete(db.GqlQuery("SELECT * FROM Notify"))
            db.delete(db.GqlQuery("SELECT * FROM Comment"))
            db.delete(db.GqlQuery("SELECT * FROM Users"))
            self.signout()
            return self.redirect('/signin')


app = webapp2.WSGIApplication([
('/', MainPage),
('/trending', Trending),
('/newpost', NewPost),
('/signup', SignUp),
('/signout', signout),
('/signin', SignIn),
('/follow', FollowWeb),
('/user/editme/general', EditUser),
('/user/editme/security', ChangePassword),
('/usr/([a-z0-9]+)', UserPage),
('/delete', Delete),
('/delete-post', DeletePost),
('/admin', Admin),
('/verify', Verify),
('/test', Test),
('/p/([0-9]+)', PostPage),
('/p/img/([^/]+)', postImage),
('/usr/img/([a-z0-9]+)', userImage),
('/google', Google)],
 debug=True)
