import os
import sqlite3

#Connect to a database. Create it if it doesn't exist
def connectToDatabase(database):
	global dbConnection
	global dbCursor

	dbConnection = sqlite3.connect(database + '.db')
	dbCursor = dbConnection.cursor()
	
	if not dbConnection:
		print 'Connection to database', database, 'failed'
		return

	if not dbCursor:
		print 'Setting the cursor of database', database, 'failed'
		return
		
	#('PRAGMA foreign_keys = ON') must be executed with every connection

#Close the connection to a database.
def closeConnectionToDatabase():
	dbCursor.close()
	dbConnection.close()
		
#Initializes all the tables in the database
def initTables():
	global dbCursor
	
	#Drop tables in case they already exist
	try:
		dbCursor.execute('DROP TABLE users_table')
	except:
		pass
		
	try:
		dbCursor.execute('DROP TABLE content_table')
	except:
		pass
			
	try:
		dbCursor.execute('DROP TABLE comments_table')
	except:
		pass
	
	try:
		dbCursor.execute('DROP TABLE news_table')
	except:
		pass
		
	try:
		dbCursor.execute('DROP TABLE code_table')
	except:
		pass
		
	try:
		dbCursor.execute('DROP TABLE art_table')
	except:
		pass
		
	try:
		dbCursor.execute('DROP TABLE msgs_table')
	except:
		pass

	######################### users_table #########################
	dbCursor.execute('''CREATE TABLE users_table (
			user_id int,
			email varchar(50),
			username varchar(20),
			password varchar(128),
			ip_address varchar(15),
			verified int DEFAULT 0,
			admin int DEFAULT 0,
			banned int DEFAULT 0,
			resetCode varchar(15) DEFAULT 'aaaaaaaaaaaaaaa',
			PRIMARY KEY (user_id),
			UNIQUE (email)
			)''')
			
	dbCursor.execute('''INSERT INTO users_table
		VALUES (1, 'george_skouroupathis@hotmail.com', 'gs511',
		'3c9909afec25354d551dae21590bb26e38d53f2173b8d3dc3eee4c047e7ab1c1eb8b85103e3be7ba613b31bb5c9c36214dc9f14a42fd7a2fdb84856bca5c44c2',
		'142.23.31.2', 1, 1, 0, 'Fdd3aaaaaaaaaaa')
		''')

	dbCursor.execute('''INSERT INTO users_table
		VALUES (2, 'whateverasdfxxx@hotmail.com', 'gs512',
		'3c9909afec25354d551dae21590bb26e38d53f2173b8d3dc3eee4c047e7ab1c1eb8b85103e3be7ba613b31bb5c9c36214dc9f14a42fd7a2fdb84856bca5c44c2',
		'142.23.31.3', 1, 0, 0, 'Gbbeaaaaaaaaaaa')
		''')

	######################### content_table #########################
	dbCursor.execute('''CREATE TABLE content_table (
			content_id int,
			content_type varchar(4),
			PRIMARY KEY (content_id),
			CHECK (content_type IN ("news", "code", "art"))
			)''')
	
	dbCursor.execute('''INSERT INTO content_table
		VALUES (1, 'news')
		''')
	
	dbCursor.execute('''INSERT INTO content_table
		VALUES (2, 'news')
		''')
	
	dbCursor.execute('''INSERT INTO content_table
		VALUES (3, 'news')
		''')
	
	dbCursor.execute('''INSERT INTO content_table
		VALUES (4, 'news')
		''')
	
	dbCursor.execute('''INSERT INTO content_table
		VALUES (5, 'code')
		''')
	
	dbCursor.execute('''INSERT INTO content_table
		VALUES (6, 'code')
		''')
	
	dbCursor.execute('''INSERT INTO content_table
		VALUES (7, 'code')
		''')
	
	dbCursor.execute('''INSERT INTO content_table
		VALUES (8, 'art')
		''')
	
	dbCursor.execute('''INSERT INTO content_table
		VALUES (9, 'art')
		''')
	
	dbCursor.execute('''INSERT INTO content_table
		VALUES (10, 'art')
		''')
	
	######################### comments_table #########################
	dbCursor.execute('''CREATE TABLE comments_table (
			comment_id int,
			content_id int,
			user_id int,
			comment varchar(255),
			date text(20),
			PRIMARY KEY (comment_id),
			FOREIGN KEY (content_id) REFERENCES content_table (content_id)
				ON UPDATE CASCADE ON DELETE CASCADE,
			FOREIGN KEY (user_id) REFERENCES users_table (user_id)
				ON UPDATE CASCADE ON DELETE CASCADE
			)''')
	
	dbCursor.execute('''INSERT INTO comments_table
		VALUES  (1, 1, 1, 'This is my comment', '31 Aug 2012 18:59')
		''')
		
	dbCursor.execute('''INSERT INTO comments_table
		VALUES  (2, 5, 1, 'This is another comment', '31 Aug 2012 18:59')
		''')
	
	dbCursor.execute('''INSERT INTO comments_table
		VALUES  (3, 8, 2, 'This is some comment', '31 Aug 2012 18:59')
		''')
		
	######################### news_table #########################
	dbCursor.execute('''CREATE TABLE news_table (
			news_id int,
			content_id int,
			title varchar(100),
			date text(20),
			PRIMARY KEY (news_id),
			FOREIGN KEY (content_id) REFERENCES content_table (content_id)
				ON UPDATE CASCADE ON DELETE CASCADE
			)''')

	dbCursor.execute('''INSERT INTO news_table
		VALUES  (1, 1, 'fucknews', '31 Aug 2012 18:59')
		''')

	dbCursor.execute('''INSERT INTO news_table
		VALUES  (2, 2, 'bullnews', '31 Aug 2012 18:59')
		''')

	dbCursor.execute('''INSERT INTO news_table
		VALUES  (3, 3, 'Crazy news', '31 Aug 2012 18:59')
		''')

	dbCursor.execute('''INSERT INTO news_table
		VALUES  (4, 4, 'More crazy news', '31 Aug 2012 18:59')
		''')

	######################### code_table #########################
	dbCursor.execute('''CREATE TABLE code_table (
			code_id int,
			content_id int,
			title varchar(100),
			code_type text(15),
			description varchar(250),
			PRIMARY KEY (code_id),
			FOREIGN KEY (content_id) REFERENCES content_table (content_id)
				ON UPDATE CASCADE ON DELETE CASCADE
			)''')

	dbCursor.execute('''INSERT INTO code_table
		VALUES  (1, 5, 'python fucker', 'python', 'this is how python fucks. i like this very much. i am high right now')
		''')

	dbCursor.execute('''INSERT INTO code_table
		VALUES  (2, 6, 'phper', 'php', 'this is how phps fucks. i like this very much. i am high right now')
		''')

	dbCursor.execute('''INSERT INTO code_table
		VALUES  (3, 7, 'condomer', 'python', 'this is pussy. conan obrien')
		''')
	
	######################### art_table #########################
	dbCursor.execute('''CREATE TABLE art_table (
			art_id int,
			content_id int,
			description varchar(200),
			art_type text(15),
			PRIMARY KEY (art_id),
			FOREIGN KEY (content_id) REFERENCES content_table (content_id)
				ON UPDATE CASCADE ON DELETE CASCADE
			)''')

	dbCursor.execute('''INSERT INTO art_table
		VALUES  (1, 8, 'This is a tree', 'gfx')
		''')

	dbCursor.execute('''INSERT INTO art_table
		VALUES  (2, 9, 'This is a boob', 'gfx')
		''')

	dbCursor.execute('''INSERT INTO art_table
		VALUES  (3, 10, 'I love this site', 'website')
		''')
	
	######################### msgs_table #########################
	dbCursor.execute('''CREATE TABLE msgs_table (
			msg_id int,
			name varchar(30),
			content varchar(255),
			date text(20),
			ip_address varchar(15),
			PRIMARY KEY (msg_id)
			)''')
	
	dbCursor.execute('''INSERT INTO msgs_table
		VALUES  (1, "Pombos", "This is a nice message", '30 Aug 2012 18:59', "21.26.20.3")
		''')

	dbConnection.commit()

#Returns a list with the users
def fetchAllUsers():
	global dbCursor
	
	return dbCursor.execute('SELECT * FROM users_table ORDER BY username ASC')
	
#Returns a list with the news
def fetchAllNews(n):
	global dbCursor
	
	#return dbCursor.execute('SELECT * FROM news_table ORDER BY date LIMIT %d' %n)
	return dbCursor.execute('SELECT * FROM news_table ORDER BY news_id DESC')

def fetchCodes(n):
	global dbCursor
	
	#return dbCursor.execute('SELECT * FROM code_table ORDER BY code_id DESC LIMIT %d' %n)
	return dbCursor.execute('SELECT * FROM code_table ORDER BY code_id DESC')

def fetchArts(n):
	global dbCursor
	
	#return dbCursor.execute('SELECT * FROM art_table ORDER BY art_id DESC LIMIT %d' %n)
	return dbCursor.execute('SELECT * FROM art_table ORDER BY art_id DESC')

def fetchMsgs(n):
	global dbCursor
	
	return dbCursor.execute('SELECT * FROM msgs_table ORDER BY msg_id DESC')

#login is only used in checkLogin
def login(username, hashedPwd):
	global dbCursor
	
	dbCursor.execute('SELECT * FROM users_table WHERE username=? AND password=?', (username, hashedPwd))
	return len( dbCursor.fetchall() )

def checkLogin(username, hashedPwd):
	global dbCursor
	
	if login(username, hashedPwd) == 0:
		return "Wrong username/password compination"
	elif not isVerified(username):
		return "Username " + username + " is not verified"
	elif isBanned(username):
		return "Username " + username + " is banned"
	else:
		return None
		
def register(email, username, hashedPwd, ip_address):
	global dbCursor
	

	dbCursor.execute('INSERT INTO users_table(user_id, email, username, password, ip_address) \
		VALUES((SELECT MAX(user_id) FROM users_table)+1, ?, ?, ?, ?)', (email, username, hashedPwd, ip_address))
	dbConnection.commit()

def checkRegister(email, username):
	global dbCursor

	dbCursor.execute('SELECT * FROM users_table WHERE email=? AND username=?', (email, username))
	if len( dbCursor.fetchall() ) != 0:
		return "This email and username are already in use"

	dbCursor.execute('SELECT * FROM users_table WHERE email=?', (email,))
	if len( dbCursor.fetchall() ) != 0:
		return "This email is already in use"		
		
	dbCursor.execute('SELECT * FROM users_table WHERE username=?', (username,))
	if len( dbCursor.fetchall() ) != 0:
		return "This username is already in use"
	
	return None

##VERIFIED, ADMIN, BANNED TESTS####################################################
def isVerified(username):
	global dbCursor
	
	dbCursor.execute('SELECT * FROM users_table WHERE username=? AND verified=1', (username,))
	if len( dbCursor.fetchall() ) == 1:
		return True
	else:
		return False

def verify(username):
	global dbCursor
	
	dbCursor.execute('UPDATE users_table SET verified=1 WHERE username=?', (username,))
	dbConnection.commit()
			
def isAdmin(username):
	global dbCursor
	
	dbCursor.execute('SELECT * FROM users_table WHERE username=? AND admin=1', (username,))
	if len( dbCursor.fetchall() ) == 1:
		return True
	else:
		return False

def giveAdmin(username):
	global dbCursor
	
	dbCursor.execute('UPDATE users_table SET admin=1 WHERE username=?', (username,))
	dbConnection.commit()

def removeAdmin(username):
	global dbCursor
	
	dbCursor.execute('UPDATE users_table SET admin=0 WHERE username=?', (username,))
	dbConnection.commit()
	
def isBanned(username):
	global dbCursor
	
	dbCursor.execute('SELECT * FROM users_table WHERE username=? AND banned=1', (username,))
	if len( dbCursor.fetchall() ) == 1:
		return True
	else:
		return False

def ban(username):
	global dbCursor
	
	dbCursor.execute('UPDATE users_table SET banned=1 WHERE username=?', (username,))
	dbConnection.commit()

def unban(username):
	global dbCursor
	
	dbCursor.execute('UPDATE users_table SET banned=0 WHERE username=?', (username,))
	dbConnection.commit()	
###################################################################################
	
def getIDFromUser(username):
	global dbCursor
	
	return dbCursor.execute('SELECT user_id FROM users_table WHERE username=?', (username,)).fetchone()

def getPasswordFromUser(username):
	global dbCursor
	
	return dbCursor.execute('SELECT password FROM users_table WHERE username=?', (username,)).fetchone()
	
def getContentTypeFromID(content_id):
	global dbCursor
	
	return dbCursor.execute('SELECT content_type FROM content_table WHERE content_id=?', (content_id,)).fetchone()

def getContentIDFromCommentID(comment_id):
	global dbCursor
	
	return dbCursor.execute('SELECT content_id FROM comments_table WHERE comment_id=?', (comment_id,)).fetchone()

def getUserFromCommentID(comment_id):
	global dbCursor
	
	return dbCursor.execute('SELECT username FROM comments_table NATURAL JOIN users_table WHERE comment_id=?', (comment_id,)).fetchone()

def getContentIDFromArtID(art_id):
	global dbCursor
	
	return dbCursor.execute('SELECT content_id FROM art_table WHERE art_id=?', (art_id,)).fetchone()

def getEmailFromUsername(username):
	global dbCursor
	
	return dbCursor.execute('SELECT email FROM users_table WHERE username=?', (username,)).fetchone()

def getResetCodeFromUsername(username):
	global dbCursor
	
	return dbCursor.execute('SELECT resetCode FROM users_table WHERE username=?', (username,)).fetchone()

def ResetPassword(username, hashedPwd):
	global dbCursor
	
	dbCursor.execute('UPDATE users_table SET password=? WHERE username=?', (hashedPwd, username))
	
	dbConnection.commit()	
	
def insertNews(title, date):
	global dbCursor
	
	dbCursor.execute('''INSERT INTO content_table
		VALUES ((SELECT MAX(content_id) FROM content_table)+1, 'news')
		''')
		
	dbCursor.execute('''INSERT INTO news_table
		VALUES ((SELECT MAX(news_id) FROM news_table)+1, (SELECT MAX(content_id) FROM content_table), ?, ?)
		''', (title, date))	
		
	dbConnection.commit()

def insertCode(title, code_type, description):
	global dbCursor
	
	dbCursor.execute('''INSERT INTO content_table
		VALUES ((SELECT MAX(content_id) FROM content_table)+1, 'code')
		''')
		
	dbCursor.execute('''INSERT INTO code_table
		VALUES ((SELECT MAX(code_id) FROM code_table)+1, (SELECT MAX(content_id) FROM content_table), ?, ?, ?)
		''', (title, code_type, description))	
		
	dbConnection.commit()

def insertGfx(description):
	global dbCursor
	
	dbCursor.execute('''INSERT INTO content_table
		VALUES ((SELECT MAX(content_id) FROM content_table)+1, 'art')
		''')
		
	dbCursor.execute('''INSERT INTO art_table
		VALUES ((SELECT MAX(art_id) FROM art_table)+1, (SELECT MAX(content_id) FROM content_table), ?, 'gfx')
		''', (description,))	
		
	dbConnection.commit()
	
def insertComment(content_id, user_id, comment, date):
	global dbCursor
	
	dbCursor.execute('''INSERT INTO comments_table
		VALUES ((SELECT MAX(comment_id) FROM comments_table)+1, ?, ?, ?, ?)
		''', (content_id, user_id, comment, date))
	
	dbConnection.commit()

def insertMessage(name, message, date, ip_addess):
	global dbCursor
	
	dbCursor.execute('''INSERT INTO msgs_table
		VALUES ((SELECT MAX(msg_id) FROM msgs_table)+1, ?, ?, ?, ?)
		''', (name, message, date, ip_addess))
	
	dbConnection.commit()
	
def deleteComment(comment_id):
	global dbCursor
	
	dbCursor.execute('DELETE FROM comments_table WHERE comment_id=?', (comment_id,))
	
	dbConnection.commit()

def deleteNews(news_id):
	global dbCursor
	
	dbCursor.execute('DELETE FROM news_table WHERE news_id=?', (news_id,))
	
	dbConnection.commit()
	
def fetchNews(content_id):
	global dbCursor
	
	dbCursor.execute('SELECT * FROM news_table where content_id=?', (content_id,))
	return 	dbCursor.fetchone()
	
def fetchArt(content_id):
	global dbCursor
	
	dbCursor.execute('SELECT * FROM art_table where content_id=?', (content_id,))
	return 	dbCursor.fetchone()
	
def fetchCode(content_id):
	global dbCursor
	
	dbCursor.execute('SELECT * FROM code_table where content_id=?', (content_id,))
	return 	dbCursor.fetchone()

def fetchComments(content_id):
	global dbCursor
		
	return dbCursor.execute('SELECT comment_id, content_id, user_id, username, comment, date FROM comments_table NATURAL JOIN users_table WHERE content_id=? ORDER BY comment_id DESC', (content_id,))
	
def fetchCommentNum(content_id):
	global dbCursor

	return dbCursor.execute('SELECT count(*) FROM comments_table where content_id=?', (content_id,)).fetchone()
	
def getNextNewsID():
	global dbCursor
	
	dbCursor.execute('SELECT MAX(news_id)+1 FROM news_table')	
	return dbCursor.fetchone()[0]
	
def getNextCodeID():
	global dbCursor
	
	dbCursor.execute('SELECT MAX(code_id)+1 FROM code_table')	
	return dbCursor.fetchone()[0]

def getNextArtID():
	global dbCursor
	
	dbCursor.execute('SELECT MAX(art_id)+1 FROM art_table')	
	return dbCursor.fetchone()[0]
	
def changeResetCode(username, resetCode):
	global dbCursor
	
	dbCursor.execute('UPDATE users_table SET resetCode=? WHERE username=?', (resetCode, username))
	
	dbConnection.commit()
	
def changeEmailAddress(username, email):
	global dbCursor
	
	dbCursor.execute('UPDATE users_table SET email=? WHERE username=?', (email, username))
	
	dbConnection.commit()

def changePassword(username, hashedPwd):
	global dbCursor
	
	dbCursor.execute('UPDATE users_table SET password=? WHERE username=?', (hashedPwd, username))
	
	dbConnection.commit()
