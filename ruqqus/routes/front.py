import time
from flask import *
from sqlalchemy import *
from sqlalchemy.orm import lazyload
import random

from ruqqus.helpers.wrappers import *
from ruqqus.helpers.get import *

from ruqqus.__main__ import app, cache
from ruqqus.classes.submission import Submission
from ruqqus.classes.categories import CATEGORIES

@app.route("/post/", methods=["GET"])
def slash_post():
	return redirect("/")

@app.route("/notifications", methods=["GET"])
@auth_required
def notifications(v):

	if v and v.is_banned and not v.unban_utc: return render_template("seized.html")

	page = int(request.args.get('page', 1))
	all_ = request.args.get('all', False)
	sent = request.args.get('sent', False)
	if sent:
		comments = g.db.query(Comment).filter_by(author=v).filter(Comment.parent_submission==None).order_by(Comment.created_utc.desc()).all()
		next_exists = (len(comments) == 26)
		comments = comments[0:25]
	else:
		cids = v.notification_commentlisting(page=page, all_=all_)
		next_exists = (len(cids) == 26)
		cids = cids[0:25]
		comments = get_comments(cids, v=v, sort_type="new", load_parent=True)

	listing = []
	for c in comments:
		c._is_blocked = False
		c._is_blocking = False
		c.replies = []
		if c.author_id == 1046:
			c._is_system = True
			listing.append(c)
		elif c.level > 1 and c.parent_comment and c.parent_comment.author_id == v.id:
			c._is_comment_reply = True
			parent = c.parent_comment

			if parent in listing:
				parent.replies = parent.replies + [c]
			else:
				parent.replies = [c]
				listing.append(parent)

		elif c.level == 1 and c.post and c.post.author_id == v.id:
			c._is_post_reply = True
			listing.append(c)
		else:
			c._is_username_mention = True
			listing.append(c)

	board = get_board(1)
	nsfw = (v and v.over_18) or session_over18(board)
	nsfl = (v and v.show_nsfl) or session_isnsfl(board)
	return render_template("notifications.html",
						   v=v,
						   nsfw = nsfw,
						   nsfl = nsfl,
						   notifications=listing,
						   next_exists=next_exists,
						   page=page,
						   standalone=True,
						   render_replies=True,
						   is_notification_page=True)

@cache.memoize(timeout=1500)
def frontlist(v=None, sort="hot", page=1,t="all", ids_only=True, filter_words='', **kwargs):

	# cutoff=int(time.time())-(60*60*24*30)

	posts = g.db.query(Submission).options(lazyload('*')).filter_by(is_banned=False,stickied=False,private=False,).filter(Submission.deleted_utc == 0)

		
	if v and v.admin_level == 0:
		blocking = g.db.query(
			UserBlock.target_id).filter_by(
			user_id=v.id).subquery()
		blocked = g.db.query(
			UserBlock.user_id).filter_by(
			target_id=v.id).subquery()
		posts = posts.filter(
			Submission.author_id.notin_(blocking),
			Submission.author_id.notin_(blocked)
		)

	if v and filter_words:
		posts=posts.join(Submission.submission_aux)
		for word in filter_words:
			#print(word)
			posts=posts.filter(not_(SubmissionAux.title.ilike(f'%{word}%')))

	if t != 'all': 
		cutoff = 0
		now = int(time.time())
		if t == 'day':
			cutoff = now - 86400
		elif t == 'week':
			cutoff = now - 604800
		elif t == 'month':
			cutoff = now - 2592000
		elif t == 'year':
			cutoff = now - 31536000
		posts = posts.filter(Submission.created_utc >= cutoff)

	gt = kwargs.get("gt")
	lt = kwargs.get("lt")

	if gt:
		posts = posts.filter(Submission.created_utc > gt)

	if lt:
		posts = posts.filter(Submission.created_utc < lt)

	if sort == "hot":
		posts = sorted(posts.all(), key=lambda x: x.hotscore, reverse=True)
	elif sort == "new":
		posts = posts.order_by(Submission.created_utc.desc()).all()
	elif sort == "old":
		posts = posts.order_by(Submission.created_utc.asc()).all()
	elif sort == "controversial":
		posts = sorted(posts.all(), key=lambda x: x.score_disputed, reverse=True)
	elif sort == "top":
		posts = posts.order_by(Submission.score.desc()).all()
	elif sort == "bottom":
		posts = posts.order_by(Submission.score.asc()).all()
	elif sort == "comments":
		posts = posts.order_by(Submission.comment_count.desc()).all()
	elif sort == "random":
		posts = posts.all()
		posts = random.sample(posts, k=len(posts))
	else:
		abort(400)

	firstrange = 25 * (page - 1)
	secondrange = firstrange+26
	posts = posts[firstrange:secondrange]
	
	words = ['r-pe', 'k-d', 'm-lest', 's-x', 'captainmeta4', 'dissident001', 'p-do', 'ladine', 'egypt']

	if not v or v.admin_level == 0:
		for post in posts:
			if (not (v and post.author_id == v.id)) and post.author and post.author.admin_level == 0:
				for word in words:
					if word in post.title.lower():
						posts.remove(post)
						break

	if ids_only:
		posts = [x.id for x in posts]
		return posts
	return posts

@app.route("/", methods=["GET"])
@app.route("/api/v1/listing", methods=["GET"])
@auth_desired
@api("read")
def front_all(v):
	if v and v.is_banned and not v.unban_utc: return render_template("seized.html")

	page = int(request.args.get("page") or 1)

	# prevent invalid paging
	page = max(page, 1)

	if v:
		defaultsorting = v.defaultsorting
		defaulttime = v.defaulttime
	else:
		defaultsorting = "hot"
		defaulttime = "all"

	sort=request.args.get("sort", defaultsorting)
	t=request.args.get('t', defaulttime)

	#handle group cookie
	groups = request.args.get("groups")
	if groups:
		session['groupids']=[int(x) for x in groups.split(',')]
		session.modified=True

	ids = frontlist(sort=sort,
					page=page,
					t=t,
					v=v,
					gt=int(request.args.get("utc_greater_than", 0)),
					lt=int(request.args.get("utc_less_than", 0)),
					filter_words=v.filter_words if v else [],
					)

	# check existence of next page
	next_exists = (len(ids) == 26)
	ids = ids[0:25]

   # If page 1, check for sticky
	if page == 1:
		sticky = []
		sticky = g.db.query(Submission).filter_by(stickied=True).all()
		if sticky:
			for p in sticky:
				ids = [p.id] + ids
	# check if ids exist
	posts = get_posts(ids, sort=sort, v=v)
	
	posts2 = []
	if v and v.hidevotedon:
		for post in posts:
			if post.voted == 0:
				posts2.append(post)
		posts = posts2
		
	return {'html': lambda: render_template("home.html",
											v=v,
											listing=posts,
											next_exists=next_exists,
											sort=sort,
											t=t,
											page=page,
											CATEGORIES=CATEGORIES
											),
			'api': lambda: jsonify({"data": [x.json for x in posts],
									"next_exists": next_exists
									}
								   )
			}

@app.route("/random", methods=["GET"])
@auth_desired
def random_post(v):
	if v and v.is_banned and not v.unban_utc: return render_template("seized.html")

	x = g.db.query(Submission).filter(Submission.deleted_utc == 0, Submission.is_banned == False, Submission.score > 20)

	total = x.count()
	n = random.randint(0, total - 1)

	post = x.order_by(Submission.id.asc()).offset(n).limit(1).first()
	return redirect(post.permalink)

@cache.memoize(600)
def comment_idlist(page=1, v=None, nsfw=False, sort="new", t="all", **kwargs):

	posts = g.db.query(Submission).options(lazyload('*'))

	posts = posts.subquery()

	comments = g.db.query(Comment).options(lazyload('*'))

	if v and v.admin_level <= 3:
		blocking = g.db.query(
			UserBlock.target_id).filter_by(
			user_id=v.id).subquery()
		blocked = g.db.query(
			UserBlock.user_id).filter_by(
			target_id=v.id).subquery()

		comments = comments.filter(
			Comment.author_id.notin_(blocking),
			Comment.author_id.notin_(blocked)
		)

	if not v or not v.admin_level >= 3:
		comments = comments.filter_by(is_banned=False).filter(Comment.deleted_utc == 0)

	comments = comments.join(posts, Comment.parent_submission == posts.c.id)

	now = int(time.time())
	if t == 'day':
		cutoff = now - 86400
	elif t == 'week':
		cutoff = now - 604800
	elif t == 'month':
		cutoff = now - 2592000
	elif t == 'year':
		cutoff = now - 31536000
	else:
		cutoff = 0
	comments = comments.filter(Comment.created_utc >= cutoff)

	if sort == "new":
		comments = comments.order_by(Comment.created_utc.desc()).all()
	elif sort == "old":
		comments = comments.order_by(Comment.created_utc.asc()).all()
	elif sort == "controversial":
		comments = sorted(comments.all(), key=lambda x: x.score_disputed, reverse=True)
	elif sort == "top":
		comments = comments.order_by(Comment.score.desc()).all()
	elif sort == "bottom":
		comments = comments.order_by(Comment.score.asc()).all()

	firstrange = 25 * (page - 1)
	secondrange = firstrange+26
	return [x.id for x in comments[firstrange:secondrange]]


@app.route("/comments", methods=["GET"])
@app.route("/api/v1/front/comments", methods=["GET"])
@auth_desired
@api("read")
def all_comments(v):
	if v and v.is_banned and not v.unban_utc: return render_template("seized.html")

	page = int(request.args.get("page", 1))

	sort=request.args.get("sort", "new")
	t=request.args.get("t", "all")

	idlist = comment_idlist(v=v,
							page=page,
							sort=sort,
							t=t,
							)

	comments = get_comments(idlist, v=v)

	next_exists = len(idlist) == 26

	idlist = idlist[0:25]

	board = get_board(1)
	return {"html": lambda: render_template("home_comments.html",
											v=v,
											sort=sort,
											t=t,
											page=page,
											comments=comments,
											standalone=True,
											next_exists=next_exists),
			"api": lambda: jsonify({"data": [x.json for x in comments]})}