import mistletoe

from ruqqus.classes import *
from flask import g
from .markdown import *
from .sanitize import *

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