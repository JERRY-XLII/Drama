from urllib.parse import urlparse
from sqlalchemy import func
from bs4 import BeautifulSoup
import pyotp
import qrcode
import io
import gevent
from datetime import datetime

from ruqqus.helpers.alerts import *
from ruqqus.helpers.wrappers import *
from ruqqus.helpers.base36 import *
from ruqqus.helpers.sanitize import *
from ruqqus.helpers.filters import *
from ruqqus.helpers.embed import *
from ruqqus.helpers.markdown import *
from ruqqus.helpers.get import *
from ruqqus.classes import *
from ruqqus.mail import *
from flask import *
from ruqqus.__main__ import app, cache, limiter, db_session
from pusher_push_notifications import PushNotifications

@app.route("/@<username>/reply/<id>", methods=["POST"])
@auth_required
def messagereply(v, username, id):
	message = request.form.get("message", "")
	user = get_user(username)
	with CustomRenderer() as renderer: text_html = renderer.render(mistletoe.Document(message))
	text_html = sanitize(text_html, linkgen=True)
	parent = get_comment(int(id), v=v)
	new_comment = Comment(author_id=v.id,
							parent_submission=None,
							parent_fullname=parent.fullname,
							parent_comment_id=id,
							level=parent.level + 1,
							sentto=user.username
							)
	g.db.add(new_comment)
	g.db.flush()
	new_aux = CommentAux(id=new_comment.id, body=message, body_html=text_html)
	g.db.add(new_aux)
	notif = Notification(comment_id=new_comment.id, user_id=user.id)
	g.db.add(notif)
	g.db.commit()
	return redirect('/notifications?all=true')

@app.route("/songs/<id>", methods=["GET"])
def songs(id):
	try: id = int(id)
	except: return '', 400
	user = g.db.query(User).filter_by(id=id).first()
	return send_from_directory('/songs/', f'{user.song}.mp3')

@app.route("/subscribe/<post_id>", methods=["POST"])
@auth_required
def subscribe(v, post_id):
	new_sub = Subscription(user_id=v.id, submission_id=post_id)
	g.db.add(new_sub)
	g.db.commit()
	return "", 204
	
@app.route("/unsubscribe/<post_id>", methods=["POST"])
@auth_required
def unsubscribe(v, post_id):
	sub=g.db.query(Subscription).filter_by(user_id=v.id, submission_id=post_id).first()
	g.db.delete(sub)
	return "", 204

@app.route("/leaderboard", methods=["GET"])
@auth_desired
def leaderboard(v):
	if v and v.is_banned and not v.unban_utc: return render_template("seized.html")
	users1, users2 = leaderboard()
	return render_template("leaderboard.html", v=v, users1=users1, users2=users2)

@cache.memoize(timeout=86400)
def leaderboard():
	users = g.db.query(User).options(lazyload('*'))
	users1= sorted(users, key=lambda x: x.dramacoins, reverse=True)[:100]
	users2 = sorted(users1, key=lambda x: x.follower_count, reverse=True)[:10]
	return users1[:25], users2

@app.route("/@<username>/message", methods=["POST"])
@auth_required
def message2(v, username):
	user = get_user(username, v=v)
	if user.is_blocking: return jsonify({"error": "You're blocking this user."}), 403
	if user.is_blocked: return jsonify({"error": "This user is blocking you."}), 403
	message = request.form.get("message", "")
	send_pm(v.id, user, message)
	return redirect('/notifications?sent=true')

@app.route("/2faqr/<secret>", methods=["GET"])
@auth_required
def mfa_qr(secret, v):
	x = pyotp.TOTP(secret)
	qr = qrcode.QRCode(
		error_correction=qrcode.constants.ERROR_CORRECT_L
	)
	qr.add_data(x.provisioning_uri(v.username, issuer_name="Drama"))
	img = qr.make_image(fill_color="#FF66AC", back_color="white")

	mem = io.BytesIO()

	img.save(mem, format="PNG")
	mem.seek(0, 0)
	return send_file(mem, mimetype="image/png", as_attachment=False)


@app.route("/api/is_available/<name>", methods=["GET"])
@app.route("/api/v1/is_available/<name>", methods=["GET"])
@auth_desired
@api("read")
def api_is_available(name, v):

	name=name.strip()

	if len(name)<3 or len(name)>25:
		return jsonify({name:False})
		
	name=name.replace('_','\_')

	x= g.db.query(User).options(
		lazyload('*')
		).filter(
		or_(
			User.username.ilike(name),
			User.original_username.ilike(name)
			)
		).first()

	if x:
		return jsonify({name: False})
	else:
		return jsonify({name: True})


@app.route("/uid/<uid>", methods=["GET"])
def user_uid(uid):

	user = get_account(uid)

	return redirect(user.permalink)

@app.route("/id/<uid>", methods=["GET"])
def user_uid2(uid):

	user = get_account(int(uid))
	return redirect(user.permalink)

# Allow Id of user to be queryied, and then redirect the bot to the
# actual user api endpoint.
# So they get the data and then there will be no need to reinvent
# the wheel.
@app.route("/api/v1/uid/<uid>", methods=["GET"])
@auth_desired
@api("read")
def user_by_uid(uid, v=None):
	user=get_account(uid)
	
	return redirect(f'/api/v1/user/{user.username}/info')
		
@app.route("/u/<username>", methods=["GET"])
def redditor_moment_redirect(username):
	return redirect(f"/@{username}")

@app.route("/@<username>/followers", methods=["GET"])
@auth_required
def followers(username, v):
	if v and v.is_banned and not v.unban_utc: return render_template("seized.html")

	u = get_user(username, v=v)
	users = [x.user for x in u.followers]
	return render_template("followers.html", v=v, u=u, users=users)

@app.route("/@<username>", methods=["GET"])
@app.route("/api/v1/user/<username>/listing", methods=["GET"])
@auth_desired
@api("read")
def u_username(username, v=None):
	if v and v.is_banned and not v.unban_utc: return render_template("seized.html")

	# username is unique so at most this returns one result. Otherwise 404

	# case insensitive search

	u = get_user(username, v=v)

	# check for wrong cases

	if username != u.username:
		return redirect(request.path.replace(username, u.username))

	if u.reserved:
		return {'html': lambda: render_template("userpage_reserved.html",
												u=u,
												v=v),
				'api': lambda: {"error": f"That username is reserved for: {u.reserved}"}
				}

	if u.is_deleted and (not v or v.admin_level < 3):
		return {'html': lambda: render_template("userpage_deleted.html",
												u=u,
												v=v),
				'api': lambda: {"error": "That user deactivated their account."}
				}

	if u.is_private and (not v or (v.id != u.id and v.admin_level < 3)):
		return {'html': lambda: render_template("userpage_private.html",
												u=u,
												v=v),
				'api': lambda: {"error": "That userpage is private"}
				}

	if u.is_blocking and (not v or v.admin_level < 3):
		return {'html': lambda: render_template("userpage_blocking.html",
												u=u,
												v=v),
				'api': lambda: {"error": f"You are blocking @{u.username}."}
				}

	if u.is_blocked and (not v or v.admin_level < 3):
		return {'html': lambda: render_template("userpage_blocked.html",
												u=u,
												v=v),
				'api': lambda: {"error": "This person is blocking you."}
				}

	sort = request.args.get("sort", "new")
	t = request.args.get("t", "all")
	page = int(request.args.get("page", "1"))
	page = max(page, 1)

	ids = u.userpagelisting(v=v, page=page, sort=sort, t=t)

	# we got 26 items just to see if a next page exists
	next_exists = (len(ids) == 26)
	ids = ids[0:25]

   # If page 1, check for sticky
	if page == 1:
		sticky = []
		sticky = g.db.query(Submission).filter_by(is_pinned=True, author_id=u.id).all()
		if sticky:
			for p in sticky:
				ids = [p.id] + ids

	listing = get_posts(ids, v=v, sort="new")

	if u.unban_utc:
		unban = datetime.fromtimestamp(u.unban_utc).strftime('%c')
		return {'html': lambda: render_template("userpage.html",
												unban=unban,
												u=u,
												v=v,
												listing=listing,
												page=page,
												sort=sort,
												t=t,
												next_exists=next_exists,
												is_following=(v and u.has_follower(v))),
				'api': lambda: jsonify({"data": [x.json for x in listing]})
				}

	return {'html': lambda: render_template("userpage.html",
										u=u,
										v=v,
										listing=listing,
										page=page,
										sort=sort,
										t=t,
										next_exists=next_exists,
										is_following=(v and u.has_follower(v))),
		'api': lambda: jsonify({"data": [x.json for x in listing]})
		}


@app.route("/@<username>/comments", methods=["GET"])
@app.route("/api/v1/user/<username>/comments", methods=["GET"])
@auth_desired
@api("read")
def u_username_comments(username, v=None):
	if v and v.is_banned and not v.unban_utc: return render_template("seized.html")

	# username is unique so at most this returns one result. Otherwise 404

	# case insensitive search

	user = get_user(username, v=v)

	# check for wrong cases

	if username != user.username: return redirect(f'{user.url}/comments')

	u = user

	if u.reserved:
		return {'html': lambda: render_template("userpage_reserved.html",
												u=u,
												v=v),
				'api': lambda: {"error": f"That username is reserved for: {u.reserved}"}
				}

	if u.is_private and (not v or (v.id != u.id and v.admin_level < 3)):
		return {'html': lambda: render_template("userpage_private.html",
												u=u,
												v=v),
				'api': lambda: {"error": "That userpage is private"}
				}

	if u.is_blocking and (not v or v.admin_level < 3):
		return {'html': lambda: render_template("userpage_blocking.html",
												u=u,
												v=v),
				'api': lambda: {"error": f"You are blocking @{u.username}."}
				}

	if u.is_blocked and (not v or v.admin_level < 3):
		return {'html': lambda: render_template("userpage_blocked.html",
												u=u,
												v=v),
				'api': lambda: {"error": "This person is blocking you."}
				}

	page = int(request.args.get("page", "1"))
	sort=request.args.get("sort","new")
	t=request.args.get("t","all")

	ids = user.commentlisting(
		v=v, 
		page=page,
		sort=sort,
		t=t,
		)

	# we got 26 items just to see if a next page exists
	next_exists = (len(ids) == 26)
	ids = ids[0:25]

	listing = get_comments(ids, v=v)

	is_following = (v and user.has_follower(v))

	board = get_board(1)
	return {"html": lambda: render_template("userpage_comments.html",
											u=user,
											v=v,
											listing=listing,
											page=page,
											sort=sort,
											t=t,
											next_exists=next_exists,
											is_following=is_following,
											standalone=True),
			"api": lambda: jsonify({"data": [c.json for c in listing]})
			}

@app.route("/api/v1/user/<username>/info", methods=["GET"])
@auth_desired
@api("read")
def u_username_info(username, v=None):

	user=get_user(username, v=v)

	if user.is_blocking:
		return jsonify({"error": "You're blocking this user."}), 401
	elif user.is_blocked:
		return jsonify({"error": "This user is blocking you."}), 403

	return jsonify(user.json)


@app.route("/api/follow/<username>", methods=["POST"])
@auth_required
def follow_user(username, v):

	target = get_user(username)

	if target.id==v.id:
		return jsonify({"error": "You can't follow yourself!"}), 400

	# check for existing follow
	if g.db.query(Follow).filter_by(user_id=v.id, target_id=target.id).first():
		abort(409)

	new_follow = Follow(user_id=v.id,
						target_id=target.id)

	g.db.add(new_follow)
	g.db.flush()
	target.stored_subscriber_count=target.follower_count
	g.db.add(target)
	g.db.commit()

	existing = g.db.query(Notification).filter_by(followsender=v.id, user_id=target.id).first()
	if not existing: send_follow_notif(v.id, target.id, f"@{v.username} has followed you!")
	return "", 204


@app.route("/api/unfollow/<username>", methods=["POST"])
@auth_required
def unfollow_user(username, v):

	target = get_user(username)

	# check for existing follow
	follow = g.db.query(Follow).filter_by(
		user_id=v.id, target_id=target.id).first()

	if not follow:
		abort(409)

	g.db.delete(follow)

	existing = g.db.query(Notification).filter_by(followsender=v.id, user_id=target.id).first()
	if not existing: send_unfollow_notif(v.id, target.id, f"@{v.username} has unfollowed you!")
	return "", 204


@app.route("/@<username>/pic/profile")
@limiter.exempt
def user_profile(username):
	x = get_user(username)
	return redirect(x.profile_url)

@app.route("/uid/<uid>/pic/profile")
@limiter.exempt
def user_profile_uid(uid):
	x=get_account(uid)
	return redirect(x.profile_url)


@app.route("/@<username>/saved/posts", methods=["GET"])
@app.route("/api/v1/saved/posts", methods=["GET"])
@auth_required
@api("read")
def saved_posts(v, username):

	page=int(request.args.get("page",1))

	ids=v.saved_idlist(page=page)

	next_exists=len(ids)==26

	ids=ids[0:25]

	listing = get_posts(ids, v=v, sort="new")

	return {'html': lambda: render_template("userpage.html",
											u=v,
											v=v,
											listing=listing,
											page=page,
											next_exists=next_exists,
											),
			'api': lambda: jsonify({"data": [x.json for x in listing]})
			}


@app.route("/@<username>/saved/comments", methods=["GET"])
@app.route("/api/v1/saved/comments", methods=["GET"])
@auth_required
@api("read")
def saved_comments(v, username):

	page=int(request.args.get("page",1))

	ids=v.saved_comment_idlist(page=page)

	next_exists=len(ids)==26

	ids=ids[0:25]

	listing = get_comments(ids, v=v, sort="new")


	return {'html': lambda: render_template("userpage_comments.html",
											u=v,
											v=v,
											listing=listing,
											page=page,
											next_exists=next_exists,
											standalone=True),
			'api': lambda: jsonify({"data": [x.json for x in listing]})
			}