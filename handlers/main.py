import tornado.ioloop
import tornado.web
import os
import databaseOperations
import errorCheck
import time
import hashlib
import random
import smtplib
from email.mime.text import MIMEText
import string
from PIL import Image

#Base Handler
class BaseHandler(tornado.web.RequestHandler):
	def get_current_user(self):
		return self.get_secure_cookie("user")

#Main Handler
class MainHandler(BaseHandler):
	def get(self):
		databaseOperations.connectToDatabase('../database/astrodb')
		news = []
		news.extend(databaseOperations.fetchAllNews(2))#to convert from sqlite3 object to list
		
		#modifyList adds a preview of the news to every new(new[3])
		def modifyList(new):
			path = '../news/' + str(new[0])
			newFile = open(path, 'r+')
			newContent = newFile.read()
			newFile.close()
			finalNew = []
			finalNew.extend(x for x in new[:3])
			finalNew.append(newContent)
			finalNew.extend(x for x in new[3:])
			return finalNew
	
		news = map(modifyList, news)
		
		self.render("../main.html", 
			userName=self.get_secure_cookie("user"), 
			isAdmin=databaseOperations.isAdmin(self.get_secure_cookie("user")),
			news=news)
		databaseOperations.closeConnectionToDatabase()

#Code Handler
class CodeHandler(BaseHandler):
	def get(self):
		databaseOperations.connectToDatabase('../database/astrodb')
		self.render("../code.html", userName=self.get_secure_cookie("user"), codes=databaseOperations.fetchCodes(2))
		databaseOperations.closeConnectionToDatabase()

#Gallery Handler
class GalleryHandler(BaseHandler):
	def get(self):
		databaseOperations.connectToDatabase('../database/astrodb')
		self.render("../gallery.html", userName=self.get_secure_cookie("user"), arts=databaseOperations.fetchArts(2))
		databaseOperations.closeConnectionToDatabase()

#About Handler
class AboutHandler(BaseHandler):
	def get(self):
		self.render("../about.html", userName=self.get_secure_cookie("user"))

#Contact Handler
class ContactHandler(BaseHandler):
	def get(self):
		self.render("../contact.html", userName=self.get_secure_cookie("user"))

#SendMessage Handler
class SendMessageHandler(BaseHandler):
	def get(self):
		self.redirect("/")
	
	def post(self):
		(name, message) = (self.get_argument("name", None), self.get_argument("message", None))
		date = time.strftime("%d %b %G %H:%M", time.localtime(time.time()))
		ip_address = self.request.remote_ip
		
		databaseOperations.connectToDatabase('../database/astrodb')
		try:
			databaseOperations.insertMessage(name, message, date, ip_address)
			databaseOperations.closeConnectionToDatabase()
			self.render("../message.html", userName=self.get_secure_cookie("user"), message="Message successfully sent")
		except:
			databaseOperations.closeConnectionToDatabase()
			self.render("../message.html", userName=self.get_secure_cookie("user"), message="Message was not sent due to an error")
			
#GFXHandler
class GFXHandler(BaseHandler):
	def get(self, art_id):
		self.render("../gfx.html", userName=self.get_secure_cookie("user"), art_id=art_id)
	
	def post(self):
		self.redirect("/")

#WebsitesHandler
class WebsitesHandler(BaseHandler):
	def get(self, art_id):
		databaseOperations.connectToDatabase('../database/astrodb')
		content_id = databaseOperations.getContentIDFromArtID(art_id)
		databaseOperations.closeConnectionToDatabase()
		self.render("../website.html", userName=self.get_secure_cookie("user"), art_id=art_id, content_id=content_id[0])
	
	def post(self):
		self.redirect("/")
		
#LoginHandler
class LoginHandler(BaseHandler):
	def get(self):
		self.render("../login.html", userName=self.get_secure_cookie("user"), errMsg = None)
		
	def post(self):
		(username, password) = (self.get_argument("user", None), self.get_argument("pwd", None))

		#Check for empty fields, wrong login, not verified, banned users
		databaseOperations.connectToDatabase('../database/astrodb')
		errMsg = errorCheck.checkLogin(username, password)
		if errMsg != None:
			databaseOperations.closeConnectionToDatabase()
			self.render("../login.html", userName=self.get_secure_cookie("user"), errMsg=errMsg)
			return
			
		databaseOperations.closeConnectionToDatabase()
		self.set_secure_cookie("user", username)
		self.redirect("/")
		return

#LogoutHandler
class LogoutHandler(BaseHandler):
	def get(self):
		self.clear_all_cookies()
		self.redirect("/")
	
	def post(self):
		self.redirect("/")
					
#RegisterHandler
class RegisterHandler(BaseHandler):
	def get(self):
		self.render("../register.html", userName=self.get_secure_cookie("user"), errMsg = None)
		
	def post(self):
		try:
			(email, username, password) = (self.get_argument("email", None), self.get_argument("username", None), self.get_argument("password", None))
		
			#Check for empty fields & already existing users
			databaseOperations.connectToDatabase('../database/astrodb')
			errMsg = errorCheck.checkRegister(email, username, password)
			databaseOperations.closeConnectionToDatabase()
			if errMsg != None:
				self.render("../register.html", userName=self.get_secure_cookie("user"), errMsg=errMsg)
				return
				
			hashedPwd = hashlib.sha512(password).hexdigest()
			ip_address = self.request.remote_ip
			databaseOperations.connectToDatabase('../database/astrodb')
			databaseOperations.register(email, username, hashedPwd, ip_address)
			databaseOperations.closeConnectionToDatabase()
			
			#Construct the verification code
			r = str(random.randint(0,1000))
			verificationCode = hashlib.sha512(username + hashedPwd + r).hexdigest()[:35]
			#Construct the URL and EMAIL CONTENTS
			url = "http://www.astrocamel.com/verify?u=%s&c=%s&r=%s" %(username, verificationCode, r)
			msg =  MIMEText("You have successfully registers at AstroCamel.com. Visit " + url + " to verify your registration.")
			msg['Subject'] = 'Registration at AstroCamel'
			msg['From'] = 'donotreply@astrocamel.com'
			msg['To'] = email
		
		
			#Send the email
			s = smtplib.SMTP('localhost')
			s.sendmail('donotreply@astrocamel.com', [email], msg.as_string())
			s.quit()
			self.render("../message.html", userName=self.get_secure_cookie("user"), message="Register complete. Check your email for the verification code")
		except:
			self.render("../message.html", userName=self.get_secure_cookie("user"), message="Registration could not be complete due to an error")
			
#VerifyHandler
class VerifyHandler(BaseHandler):
	def get(self):
		u = str(self.get_argument("u", None))
		c = str(self.get_argument("c", None))
		r = str(self.get_argument("r", None))
		
		databaseOperations.connectToDatabase('../database/astrodb')
		verified = databaseOperations.isVerified(u)
		databaseOperations.closeConnectionToDatabase()
		if verified:
			self.render("../message.html", userName=self.get_secure_cookie("user"), message=u + " is already verified")
		try:
			databaseOperations.connectToDatabase('../database/astrodb')
			password = databaseOperations.getPasswordFromUser(u)[0]
			databaseOperations.closeConnectionToDatabase()
		except:
			self.render("../message.html", userName=self.get_secure_cookie("user"), message="Could not validate username " + u)
			return
		
		correctValidationCode = hashlib.sha512(u + password + r).hexdigest()[:35]

		if c == correctValidationCode:
			databaseOperations.connectToDatabase('../database/astrodb')
			databaseOperations.verify(u)
			databaseOperations.closeConnectionToDatabase()
			message="Verification complete. You can now log in"
		else:
			message="Could not validate username" + u
		
		self.render("../message.html", userName=self.get_secure_cookie("user"), message=message)
			
	def post(self):
		self.redirect("/")

#LostPasswordHandler
class LostPasswordHandler(BaseHandler):
	def get(self):
		self.render("../lostpassword.html", userName=self.get_secure_cookie("user"), errMsg = None)
		
	def post(self):
		try:
			username = self.get_argument("user", None)
		
			#Check for empty field
			if not username:
				self.render("../message.html", userName=self.get_secure_cookie("user"), message="Username was left blank")			
				return
				
			databaseOperations.connectToDatabase('../database/astrodb')
			email = databaseOperations.getEmailFromUsername(username)
			
			if not email:
				self.render("../message.html", userName=self.get_secure_cookie("user"), message="Cannot reset password for this user")			
				return
			else:
				email = email[0]
				
			#Create reset code
			chars = string.ascii_lowercase + string.ascii_uppercase + string.digits
			resetCode =  ''.join( random.choice(chars) for r in range(15) )
			databaseOperations.changeResetCode(username, resetCode)
			databaseOperations.closeConnectionToDatabase()
		
			#Construct the URL
			url = "http://www.astrocamel.com/resetpassword?u=%s&c=%s" %(username, resetCode)
		
			#Construct the EMAIL CONTENTS
			msg =  MIMEText("You have requested a password reset. Please follow the link: " + url + " to reset your password.")
			print msg
			msg['Subject'] = 'Password Lost - AstroCamel'
			msg['From'] = 'donotreply@astrocamel.com'
			msg['To'] = email
		
			#Send the email
			s = smtplib.SMTP('localhost')
			s.sendmail('donotreply@astrocamel.com', [email], msg.as_string())
			s.quit()
			self.render("../message.html", userName=self.get_secure_cookie("user"), message="An email has been sent to your address with further instructions on how to reset your password")
		except:
			self.render("../message.html", userName=self.get_secure_cookie("user"), message="Cannot reset password for this user")

#ResetPasswordHandler
class ResetPasswordHandler(BaseHandler):
	def get(self):
		#try:
		u = self.get_argument("u", None)
		c = self.get_argument("c", None)
	
		databaseOperations.connectToDatabase('../database/astrodb')
		resetCode = databaseOperations.getResetCodeFromUsername(u)
		
		if not resetCode:
			self.render("../message.html", userName=self.get_secure_cookie("user"), message="Cannot reset password for this user")			
			return
		else:
			resetCode = resetCode[0]
			
		#Reset code
		if resetCode == c:
			hashedPwd = hashlib.sha512(u).hexdigest()
			databaseOperations.ResetPassword(u, hashedPwd)
			databaseOperations.closeConnectionToDatabase()
			self.render("../message.html", userName=self.get_secure_cookie("user"), message="Your password has been reset to: %s" %u)
			return
		else:
			databaseOperations.closeConnectionToDatabase()
			self.render("../message.html", userName=self.get_secure_cookie("user"), message="Cannot reset password for this user")
			return
	
	def post(self):
		self.redirect("/")
		
#BanHandler
class BanHandler(BaseHandler):
	def get(self):
		self.redirect("/")
	
	def post(self):
		try:
			bannedUser = self.get_argument("bannedUser")
			user = self.get_secure_cookie("user")
			databaseOperations.connectToDatabase('../database/astrodb')
			if not databaseOperations.isAdmin(user):
				self.redirect("/")
			
			databaseOperations.ban(bannedUser)
			userList = []
			userList.extend(databaseOperations.fetchAllUsers())#to convert from sqlite3 object to list
			msgs = []
			msgs.extend(databaseOperations.fetchMsgs(2))#to convert from sqlite3 object to list

			self.render("../admin.html", userName=user, userList = userList, msgs=msgs, errMsg = "User " + bannedUser + " succesfully banned")
			databaseOperations.closeConnectionToDatabase()
			return
		except:
			userList = []
			userList.extend(databaseOperations.fetchAllUsers())#to convert from sqlite3 object to list
			msgs = []
			msgs.extend(databaseOperations.fetchMsgs(2))#to convert from sqlite3 object to list

			bannedUser = self.get_argument("bannedUser")
			self.render("../admin.html", userName=self.get_secure_cookie("user"), userList = userList, msgs=msgs, errMsg = "Error banning user " + bannedUser)
			return
		
#UnbanHandler
class UnbanHandler(BaseHandler):
	def get(self):
		self.redirect("/")
	
	def post(self):
		try:
			unbannedUser = self.get_argument("unbannedUser")
			user = self.get_secure_cookie("user")
			databaseOperations.connectToDatabase('../database/astrodb')
			if not databaseOperations.isAdmin(user):
				self.redirect("/")
			
			databaseOperations.unban(unbannedUser)
			userList = []
			userList.extend(databaseOperations.fetchAllUsers())#to convert from sqlite3 object to list
			msgs = []
			msgs.extend(databaseOperations.fetchMsgs(2))#to convert from sqlite3 object to list

			self.render("../admin.html", userName=user, userList = userList, msgs=msgs, errMsg = "User " + unbannedUser + " succesfully unbanned")
			databaseOperations.closeConnectionToDatabase()
			return
		except:
			userList = []
			userList.extend(databaseOperations.fetchAllUsers())#to convert from sqlite3 object to list
			msgs = []
			msgs.extend(databaseOperations.fetchMsgs(2))#to convert from sqlite3 object to list
			
			unbannedUser = self.get_argument("unbannedUser")
			self.render("../admin.html", userName=self.get_secure_cookie("user"), userList = userList, msgs=msgs, errMsg = "Error unbanning user " + unbannedUser)
			return
			
#AdminHandler
class AdminHandler(BaseHandler):
	def get(self):
		databaseOperations.connectToDatabase('../database/astrodb')
		username = self.get_secure_cookie("user")
		if not databaseOperations.isAdmin(username) or databaseOperations.isBanned(username) or not databaseOperations.isVerified(username):
			databaseOperations.closeConnectionToDatabase()
			self.redirect("/")
		else:
			userList = []
			userList.extend(databaseOperations.fetchAllUsers())#to convert from sqlite3 object to list
			msgs = []
			msgs.extend(databaseOperations.fetchMsgs(2))#to convert from sqlite3 object to list
			
			self.render("../admin.html", userName=self.get_secure_cookie("user"), userList=userList, msgs=msgs, errMsg = None)
			databaseOperations.closeConnectionToDatabase()
		
	def post(self):
		self.redirect("/")

#ControlPanelHandler
class ControlPanelHandler(BaseHandler):
	def get(self):
		if not self.current_user:
			self.redirect("/")
		else:			
			self.render("../controlpanel.html", userName=self.get_secure_cookie("user"), errMsg = None)
		
	def post(self):
		self.redirect("/")

#ChangeEmailHandler
class ChangeEmailHandler(BaseHandler):
	def get(self):
		self.redirect("/")
		
	def post(self):
		if not self.current_user:
			self.redirect("/")
		else:
			username = self.get_secure_cookie("user")
			email = self.get_argument("email", "notvalid")
			if not errorCheck.checkEmail(email):
				self.render("../controlpanel.html", userName=self.get_secure_cookie("user"), errMsg = "This is not a valid email address")
				return
			try:
				databaseOperations.connectToDatabase('../database/astrodb')
				databaseOperations.changeEmailAddress(username, email)
				databaseOperations.closeConnectionToDatabase()
				self.render("../controlpanel.html", userName=self.get_secure_cookie("user"), errMsg = "Email address successfully changed")
			except:
				self.render("../controlpanel.html", userName=self.get_secure_cookie("user"), errMsg = "Error changing email address")

#ChangePasswordHandler
class ChangePasswordHandler(BaseHandler):
	def get(self):
		self.redirect("/")
		
	def post(self):
		if not self.current_user:
			self.redirect("/")
		else:
			username = self.get_secure_cookie("user")
			cpassword = self.get_argument("cpassword", None)
			npassword = self.get_argument("npassword", None)
			rnpassword = self.get_argument("rnpassword", None)

			databaseOperations.connectToDatabase('../database/astrodb')
			errMsg = errorCheck.checkChangePassword(username, cpassword, npassword, rnpassword)
			if errMsg != None:
				databaseOperations.closeConnectionToDatabase()
				self.render("../controlpanel.html", userName=self.get_secure_cookie("user"), errMsg=errMsg)
				return
			hashedcPwd = hashlib.sha512(cpassword).hexdigest()
			hashednPwd = hashlib.sha512(npassword).hexdigest()
			hashedrnPwd = hashlib.sha512(rnpassword).hexdigest()
			try:
				databaseOperations.connectToDatabase('../database/astrodb')
				databaseOperations.changePassword(username, hashednPwd)
				databaseOperations.closeConnectionToDatabase()
				self.render("../controlpanel.html", userName=self.get_secure_cookie("user"), errMsg = "Password successfully changed")
			except:
				self.render("../controlpanel.html", userName=self.get_secure_cookie("user"), errMsg = "Error changing password")
				
#PostNewsHandler
class PostNewsHandler(BaseHandler):
	def get(self):
		self.redirect("/")
	
	def post(self):
		username = self.get_secure_cookie("user")
		databaseOperations.connectToDatabase('../database/astrodb')
		if not databaseOperations.isAdmin(username) or databaseOperations.isBanned(username) or not databaseOperations.isVerified(username):
			databaseOperations.closeConnectionToDatabase()
			self.redirect("/")		
		#try:
		title = self.get_argument("title", None)
		date = time.strftime("%d %b %G %H:%M", time.localtime(time.time()))

		newsFile = self.request.files['newsFile'][0]
		path = "../news/" + str(databaseOperations.getNextNewsID())
		newsPath = open(path, "w")
		newsPath.write(newsFile['body'])
		
		newsimg = self.request.files['newsimg'][0]
		path = "../imgs/news/" + str(databaseOperations.getNextNewsID()) + ".jpg"
		imgPath = open(path, "w")
		imgPath.write(newsimg['body'])
		
		databaseOperations.insertNews(title, date)

		userList = []
		userList.extend(databaseOperations.fetchAllUsers())#to convert from sqlite3 object to list
		msgs = []
		msgs.extend(databaseOperations.fetchMsgs(2))#to convert from sqlite3 object to list

		databaseOperations.closeConnectionToDatabase()
			
		self.render("../admin.html", userName=self.get_secure_cookie("user"), userList=userList, msgs=msgs, errMsg = "News posted succesfully!")
		
#UploadCodeHandler
class UploadCodeHandler(BaseHandler):
	def get(self):
		self.redirect("/")
	
	def post(self):
		username = self.get_secure_cookie("user")
		databaseOperations.connectToDatabase('../database/astrodb')
		if not databaseOperations.isAdmin(username) or databaseOperations.isBanned(username) or not databaseOperations.isVerified(username):
			databaseOperations.closeConnectionToDatabase()
			self.redirect("/")		
		
		title = self.get_argument("title", None)
		code_type = self.get_argument("codeType", None)
		description = self.get_argument("description", None)

		codeFile = self.request.files['codeFile'][0]
		path = "../code/" + str(databaseOperations.getNextCodeID())
		codePath = open(path, "w")
		codePath.write(codeFile['body'])
		
		databaseOperations.insertCode(title, code_type, description)

		userList = []
		userList.extend(databaseOperations.fetchAllUsers())#to convert from sqlite3 object to list
		msgs = []
		msgs.extend(databaseOperations.fetchMsgs(2))#to convert from sqlite3 object to list

		databaseOperations.closeConnectionToDatabase()
			
		self.render("../admin.html", userName=self.get_secure_cookie("user"), userList=userList, msgs=msgs, errMsg = "Code uploaded succesfully!")
		
#UploadGfxHandler
class UploadGfxHandler(BaseHandler):
	def get(self):
		self.redirect("/")
	
	def post(self):
		username = self.get_secure_cookie("user")
		databaseOperations.connectToDatabase('../database/astrodb')
		if not databaseOperations.isAdmin(username) or databaseOperations.isBanned(username) or not databaseOperations.isVerified(username):
			databaseOperations.closeConnectionToDatabase()
			self.redirect("/")		
		
		description = self.get_argument("description", None)
		nextArtID = str(databaseOperations.getNextArtID())
		#upload gfx
		gfxFile = self.request.files['gfxFile'][0]
		path = "../imgs/art/gfx/" + nextArtID + ".jpg"
		gfxPath = open(path, "w")
		gfxPath.write(gfxFile['body'])
		
		#resize gfx and put in directory
		size = 250, 80
		bigImage = Image.open(path)
		try:
			bigImage.load()
		except:
			bigImage = bigImage.rotate(30)
		bigImage.save("../imgs/art/" + nextArtID + "small.jpg", "JPEG")
		
		#insert gfx into db
		databaseOperations.insertGfx(description)

		userList = []
		userList.extend(databaseOperations.fetchAllUsers())#to convert from sqlite3 object to list
		msgs = []
		msgs.extend(databaseOperations.fetchMsgs(2))#to convert from sqlite3 object to list

		databaseOperations.closeConnectionToDatabase()
	
		self.render("../admin.html", userName=self.get_secure_cookie("user"), userList=userList, msgs=msgs, errMsg = "GFX uploaded succesfully!")
		
#PostCommentHandler
class PostCommentHandler(BaseHandler):
	def get(self):
		self.redirect("/")
	
	def post(self, content_id):
		try:
			username = self.get_secure_cookie("user")
			databaseOperations.connectToDatabase('../database/astrodb')
			if not self.current_user or databaseOperations.isBanned(username) or not databaseOperations.isVerified(username):
				self.redirect("/login")
				return
			(comment, user) = (self.get_argument("comment", None), self.current_user)
			date = time.strftime("%d %b %G %H:%M", time.localtime(time.time()))
			user_id = databaseOperations.getIDFromUser(user)[0]
			content_type = databaseOperations.getContentTypeFromID(content_id)[0]
			databaseOperations.insertComment(content_id, user_id, comment, date)
			databaseOperations.closeConnectionToDatabase()
			self.redirect( "/show%s/%s" %(content_type, str(content_id)) )
		except:
			print "Error posting comment"

#DeleteCommentHandler
class DeleteCommentHandler(BaseHandler):
	def get(self, comment_id):
		try:
			if not self.current_user:
				self.redirect("/login")
				return
				
			databaseOperations.connectToDatabase('../database/astrodb')
			
			content_id = databaseOperations.getContentIDFromCommentID(comment_id)[0]
			content_type = databaseOperations.getContentTypeFromID(content_id)[0]
			contentPath = "/show%s/%s" %(content_type, str(content_id))
			user = databaseOperations.getUserFromCommentID(comment_id)[0]

			if user == self.get_secure_cookie("user") or databaseOperations.isAdmin(self.get_secure_cookie("user")):
			#if user is the author of the comment, or if admin
				databaseOperations.deleteComment(comment_id)
	
			databaseOperations.closeConnectionToDatabase()
			self.redirect( contentPath )
			
		except:
			print "Error deleting comment with comment id", comment_id
	def post(self):
		self.redirect("/")

#DeleteNewsHandler
class DeleteNewsHandler(BaseHandler):
	def get(self, news_id):
		try:
			if not self.current_user:
				
				self.redirect("/login")
				return
			databaseOperations.connectToDatabase('../database/astrodb')
			if not databaseOperations.isAdmin( self.get_secure_cookie("user") ):
				databaseOperations.closeConnectionToDatabase()
				self.redirect("/")
				return

			databaseOperations.deleteNews(news_id)
	
			databaseOperations.closeConnectionToDatabase()
			self.redirect("/")
			
		except:
			print "Error deleting news with news id", news_id
	def post(self):
		self.redirect("/")
							
#ShowNewsHandler
class ShowNewsHandler(BaseHandler):
	def get(self, content_id):
		databaseOperations.connectToDatabase('../database/astrodb')
		
		if self.current_user:
			sessionUserID = databaseOperations.getIDFromUser(self.get_secure_cookie("user"))[0]
		else:
			sessionUserID = -1
		
		news = databaseOperations.fetchNews(content_id)
		if news:
			path = '../news/' + str(news[0])
			newsFile = open(path, 'r+')
			newsContent = newsFile.read()
			newsFile.close()
		else:
			newsContent = None
			
		self.render("../shownews.html", 
			userName=self.get_secure_cookie("user"),
			news=news,
			newsContent = newsContent,
			sessionUserID = sessionUserID,
			isAdmin=databaseOperations.isAdmin(self.get_secure_cookie("user")),
			commentNum=databaseOperations.fetchCommentNum(content_id), 
			comments=databaseOperations.fetchComments(content_id), 
			contentID=content_id )
		databaseOperations.closeConnectionToDatabase()
	
	def post(self):
		self.redirect("/")
		
#ShowArtHandler
class ShowArtHandler(BaseHandler):
	def get(self, content_id):
		databaseOperations.connectToDatabase('../database/astrodb')
		
		if self.current_user:
			sessionUserID = databaseOperations.getIDFromUser(self.get_secure_cookie("user"))[0]
		else:
			sessionUserID = -1
		
		self.render("../showart.html", 
			userName=self.get_secure_cookie("user"),
			art=databaseOperations.fetchArt(content_id), 
			sessionUserID = sessionUserID,
			isAdmin=databaseOperations.isAdmin(self.get_secure_cookie("user")),
			commentNum=databaseOperations.fetchCommentNum(content_id), 
			comments=databaseOperations.fetchComments(content_id), 
			contentID=content_id)
		databaseOperations.closeConnectionToDatabase()
	
	def post(self):
		self.redirect("/")

#ShowCodeHandler
class ShowCodeHandler(BaseHandler):
	def get(self, content_id):
		databaseOperations.connectToDatabase('../database/astrodb')
		
		if self.current_user:
			sessionUserID = databaseOperations.getIDFromUser(self.get_secure_cookie("user"))[0]
		else:
			sessionUserID = -1
		
		code=databaseOperations.fetchCode(content_id)
		if code:
			path = '../code/' + str(code[0])
			codeFile = open(path, 'r+')
			codeContent = codeFile.read()
			codeFile.close()
		else:
			codeContent = None
		
		self.render("../showcode.html", 
			userName=self.get_secure_cookie("user"),
			code=code, 
			codeContent = codeContent, 
			sessionUserID = sessionUserID,
			isAdmin=databaseOperations.isAdmin(self.get_secure_cookie("user")),
			commentNum=databaseOperations.fetchCommentNum(content_id), 
			comments=databaseOperations.fetchComments(content_id), 
			contentID=content_id)
		databaseOperations.closeConnectionToDatabase()
	
	def post(self):
		self.redirect("/")
	
settings = {
	"static_path": os.path.join(os.path.dirname(__file__), ".."),
	"cookie_secret": "VVoVTzKXQAGZYdkL5fEmGeJ3FuYh1EQnp2XdTP1o/Vo2",
	"xsrf_cookies": True,
}

application = tornado.web.Application([
	(r"/", MainHandler),
	(r"/code", CodeHandler),
	(r"/gallery", GalleryHandler),
	(r"/about", AboutHandler),
	(r"/contact", ContactHandler),
	(r"/sendmessage", SendMessageHandler),
	(r"/gfx/([0-9]+)", GFXHandler),
	(r"/website/([0-9]+)", WebsitesHandler),
	(r"/login", LoginHandler),
	(r"/logout", LogoutHandler),
	(r"/register", RegisterHandler),
	(r"/verify", VerifyHandler),
	(r"/lostpassword", LostPasswordHandler),
	(r"/resetpassword", ResetPasswordHandler),
	(r"/ban", BanHandler),
	(r"/unban", UnbanHandler),
	(r"/admin", AdminHandler),
	(r"/controlpanel", ControlPanelHandler),
	(r"/changeemail", ChangeEmailHandler),
	(r"/changepassword", ChangePasswordHandler),
	(r"/postnews", PostNewsHandler),
	(r"/uploadcode", UploadCodeHandler),
	(r"/uploadgfx", UploadGfxHandler),
	(r"/postcomment/([0-9]+)", PostCommentHandler),
	(r"/deletecomment/([0-9]+)", DeleteCommentHandler),
	(r"/deletenews/([0-9]+)", DeleteNewsHandler),
	(r"/shownews/([0-9]+)", ShowNewsHandler),
	(r"/showart/([0-9]+)", ShowArtHandler),
	(r"/showcode/([0-9]+)", ShowCodeHandler),
], **settings)



if __name__ == "__main__":
	application.listen(7776)
	print "Starting server"
	#######For the first time#######
	databaseOperations.connectToDatabase('../database/astrodb')
	databaseOperations.initTables()
	databaseOperations.closeConnectionToDatabase()
	print "Database Tables Created"
	################################
	tornado.ioloop.IOLoop.instance().start()
