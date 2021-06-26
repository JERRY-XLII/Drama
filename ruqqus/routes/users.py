from urllib.parse import urlparse
import mistletoe
from sqlalchemy import func
from bs4 import BeautifulSoup
import pyotp
import qrcode
import io
import gevent

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

BAN_REASONS = ['',
			   "URL shorteners are not permitted."
			   ]

@app.route("/leaderboard", methods=["GET"])
@auth_desired
def leaderboard(v):
	if v and v.is_banned and not v.unban_utc: return render_template("seized.html")
	
	users1, users2, users3, users4 = leaderboard()
	return render_template("leaderboard.html", v=v, users1=users1, users2=users2, users3=users3, users4=users4)

@cache.memoize(timeout=1800)
def leaderboard():
	users1 = g.db.query(User).options(lazyload('*')).order_by(User.stored_karma.desc()).limit(100)
	users2 = sorted(list(users1), key=lambda x: x.follower_count, reverse=True)[:10]
	users3 = sorted(list(users1), key=lambda x: x.post_count, reverse=True)[:10]
	users4 = sorted(list(users1), key=lambda x: x.comment_count, reverse=True)[:10]
	return users1.limit(25).all(), users2, users3, users4


@app.route("/@<username>/message", methods=["GET"])
@auth_required
def message1(v, username):
	if v and v.is_banned and not v.unban_utc: return render_template("seized.html")

	user = get_user(username, v=v)
	if user.is_blocking: return jsonify({"error": "You're blocking this user."}), 403
	if user.is_blocked: return jsonify({"error": "This user is blocking you."}), 403
	return render_template("privatemessage.html", v=v, username=username)

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

	name=name.lstrip().rstrip()

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

	user = get_account2(uid)
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

	page = int(request.args.get("page", "1"))
	page = max(page, 1)

	ids = u.userpagelisting(v=v, page=page)

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

	return {'html': lambda: render_template("userpage.html",
											u=u,
											v=v,
											listing=listing,
											page=page,
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

	ids = user.commentlisting(v=v, page=page)

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

	send_notification(target, f"@{v.username} has followed you!")
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

	return "", 204


@app.route("/api/agree_tos", methods=["POST"])
@auth_required
def api_agree_tos(v):

	v.tos_agreed_utc = int(time.time())

	g.db.add(v)

	return redirect("/terms")


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


@app.route("/@<username>/saved", methods=["GET"])
@app.route("/api/v1/saved", methods=["GET"])
@auth_required
@api("read")
def saved_listing(v, username):

	page=int(request.args.get("page",1))

	ids=v.saved_idlist(page=page)

	next_exists=len(ids)==26

	ids=ids[0:25]

	listing = get_posts(ids, v=v, sort="new")

	return {'html': lambda: render_template("userpage_saved.html",
											u=v,
											v=v,
											listing=listing,
											page=page,
											next_exists=next_exists,
											),
			'api': lambda: jsonify({"data": [x.json for x in listing]})
			}

def convert_file(html):

	if not isinstance(html, str):
		return html

	soup=BeautifulSoup(html, 'html.parser')

	for thing in soup.find_all('link', rel="stylesheet"):

		if not thing['href'].startswith('https'):

			if app.config["FORCE_HTTPS"]:
				thing["href"]=f"https://{app.config['SERVER_NAME']}{thing['href']}"
			else: 
				thing["href"]=f"https://{app.config['SERVER_NAME']}{thing['href']}"

	for thing in soup.find_all('a', href=True):

		if thing["href"].startswith('/') and not thing["href"].startswith(("javascript",'//')):
			if app.config["FORCE_HTTPS"]:
				thing["href"]=f"https://{app.config['SERVER_NAME']}{thing['href']}"
			else:
				thing["href"]=f"https://{app.config['SERVER_NAME']}{thing['href']}"

	for thing in soup.find_all('img', src=True):

		if thing["src"].startswith('/') and not thing["src"].startswith('//'):
			if app.config["FORCE_HTTPS"]:
				thing["src"]=f"https://{app.config['SERVER_NAME']}{thing['src']}"
			else:
				thing["src"]=f"https://{app.config['SERVER_NAME']}{thing['src']}"




	return str(soup)


def info_packet(username, method="html"):

	print(f"starting {username}")

	packet={}

	with app.test_request_context("/my_info"):

		db=db_session()
		g.timestamp=int(time.time())
		g.db=db

		user=get_user(username)

		#submissions
		post_ids=db.query(Submission.id).filter_by(author_id=user.id).order_by(Submission.created_utc.desc()).all()
		post_ids=[i[0] for i in post_ids]
		posts=get_posts(post_ids, v=user)
		packet["posts"]={
			'html':lambda:render_template("userpage.html", v=None, u=user, listing=posts, page=1, next_exists=False),
			'json':lambda:[x.self_download_json for x in posts]
		}

		#comments
		comment_ids=db.query(Comment.id).filter_by(author_id=user.id).order_by(Comment.created_utc.desc()).all()
		comment_ids=[x[0] for x in comment_ids]
		comments=get_comments(comment_ids, v=user)
		packet["comments"]={
			'html':lambda:render_template("userpage_comments.html", v=None, u=user, listing=comments, page=1, next_exists=False),
			'json':lambda:[x.self_download_json for x in comments]
		}

		#upvoted posts
		upvote_query=db.query(Vote.submission_id).filter_by(user_id=user.id, vote_type=1).order_by(Vote.id.desc()).all()
		upvote_posts=get_posts([i[0] for i in upvote_query], v=user)
		upvote_posts=[i for i in upvote_posts]
		for post in upvote_posts:
			post.__dict__['voted']=1
		packet['upvoted_posts']={
			'html':lambda:render_template("userpage.html", v=None, listing=posts, page=1, next_exists=False),
			'json':lambda:[x.json_core for x in upvote_posts]
		}

		print('post_downvotes')
		downvote_query=db.query(Vote.submission_id).filter_by(user_id=user.id, vote_type=-1).order_by(Vote.id.desc()).all()
		downvote_posts=get_posts([i[0] for i in downvote_query], v=user)
		packet['downvoted_posts']={
			'html':lambda:render_template("userpage.html", v=None, listing=posts, page=1, next_exists=False),
			'json':lambda:[x.json_core for x in downvote_posts]
		}

		print('comment_upvotes')
		upvote_query=db.query(CommentVote.comment_id).filter_by(user_id=user.id, vote_type=1).order_by(CommentVote.id.desc()).all()
		upvote_comments=get_comments([i[0] for i in upvote_query], v=user)
		packet["upvoted_comments"]={
			'html':lambda:render_template("userpage_comments.html", v=None, listing=upvote_comments, page=1, next_exists=False),
			'json':lambda:[x.json_core for x in upvote_comments]
		}

		print('comment_downvotes')
		downvote_query=db.query(CommentVote.comment_id).filter_by(user_id=user.id, vote_type=-1).order_by(CommentVote.id.desc()).all()
		downvote_comments=get_comments([i[0] for i in downvote_query], v=user)
		packet["downvoted_comments"]={
			'html':lambda:render_template("userpage_comments.html", v=None, listing=downvote_comments, page=1, next_exists=False),
			'json':lambda:[x.json_core for x in downvote_comments]
		}

		print('blocked users')
		blocked_users=db.query(UserBlock.target_id).filter_by(user_id=user.id).order_by(UserBlock.id.desc()).all()
		users=[get_account(base36encode(x[0])) for x in blocked_users]
		packet["blocked_users"]={
			"html":lambda:render_template("admin/new_users.html", users=users, v=None, page=1, next_exists=False),
			"json":lambda:[x.json_core for x in users]
		}




		send_mail(
			user.email,
			"Your Drama Data",
			"Your Drama data is attached.",
			"Your Drama data is attached.",
			files={f"{user.username}_{entry}.{method}": io.StringIO(convert_file(str(packet[entry][method]()))) for entry in packet}
		)


	print("finished")



@app.route("/my_info", methods=["POST"])
@limiter.limit("2/day")
@auth_required
@validate_formkey
def my_info_post(v):

	if not v.is_activated:
		return redirect("/settings/security")

	method=request.values.get("method","html")
	if method not in ['html','json']:
		abort(400)

	gevent.spawn_later(5, info_packet, v.username, method=method)

	return "started"