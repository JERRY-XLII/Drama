import mistletoe

from ruqqus.classes import *
from flask import g
from .markdown import *
from .sanitize import *
from .get import get_comment

def send_notification(vid, user, text):

	text = text.replace('r/', 'r\/').replace('u/', 'u\/')
	with CustomRenderer() as renderer:
		text_html = renderer.render(mistletoe.Document(text))

	text_html = sanitize(text_html, linkgen=True)
	
	new_comment = Comment(author_id=vid,
							parent_submission=None,
							distinguish_level=6,
							)
	g.db.add(new_comment)

	g.db.flush()

	new_aux = CommentAux(id=new_comment.id,
						 body=text,
						 body_html=text_html,
						 )
	g.db.add(new_aux)

	notif = Notification(comment_id=new_comment.id,
						 user_id=user.id)
	g.db.add(notif)
	g.db.commit()


def send_pm(vid, user, text):

	with CustomRenderer() as renderer: text_html = renderer.render(mistletoe.Document(text))

	text_html = sanitize(text_html, linkgen=True)

	new_comment = Comment(author_id=vid,
							parent_submission=None,
							sentto=user.username
							)
	g.db.add(new_comment)

	g.db.flush()

	new_aux = CommentAux(id=new_comment.id, body=text, body_html=text_html)
	g.db.add(new_aux)

	notif = Notification(comment_id=new_comment.id, user_id=user.id)
	g.db.add(notif)
	g.db.commit()


def send_reply(v, id, message):

	with CustomRenderer() as renderer: text_html = renderer.render(mistletoe.Document(message))
	
	text_html = sanitize(text_html, linkgen=True)
	parent = get_comment(id, v=v)
	new_comment = Comment(author_id=v.id,
							parent_submission=None,
							parent_fullname=parent.fullname,
							parent_comment_id=id,
							level=parent.level + 1,
							)

	g.db.add(new_comment)
	g.db.flush()
	print("1")
	new_aux = CommentAux(id=new_comment.id, body=message, body_html=text_html)
	print("2")
	g.db.add(new_aux)
	print("3")
	notif = Notification(comment_id=new_comment.id, user_id=user.id)
	print("4")
	g.db.add(notif)
	print("5")
	g.db.commit()
	print("6")


def send_follow_notif(vid, user, text):

	with CustomRenderer() as renderer:
		text_html = renderer.render(mistletoe.Document(text))
	text_html = sanitize(text_html, linkgen=True)
	
	new_comment = Comment(author_id=1046,
							parent_submission=None,
							distinguish_level=6,
							)
	g.db.add(new_comment)
	g.db.flush()

	new_aux = CommentAux(id=new_comment.id,
						 body=text,
						 body_html=text_html,
						 )
	g.db.add(new_aux)

	notif = Notification(comment_id=new_comment.id,
						 user_id=user,
						 followsender=vid)
	g.db.add(notif)
	g.db.commit()
	
def send_unfollow_notif(vid, user, text):

	with CustomRenderer() as renderer:
		text_html = renderer.render(mistletoe.Document(text))
	text_html = sanitize(text_html, linkgen=True)
	
	new_comment = Comment(author_id=1046,
							parent_submission=None,
							distinguish_level=6,
							)
	g.db.add(new_comment)
	g.db.flush()

	new_aux = CommentAux(id=new_comment.id,
						 body=text,
						 body_html=text_html,
						 )
	g.db.add(new_aux)

	notif = Notification(comment_id=new_comment.id,
						 user_id=user,
						 unfollowsender=vid)
	g.db.add(notif)
	g.db.commit()