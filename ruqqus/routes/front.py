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

	posts = g.db.query(
		Submission
		).options(
			lazyload('*')
		).filter_by(
			is_banned=False,
			stickied=False,
			private=False,
		).filter(Submission.deleted_utc == 0)

	if (v and v.hide_offensive) or not v:
		posts = posts.filter_by(is_offensive=False)
		
	if v and v.hide_bot:
		posts = posts.filter_by(is_bot=False)

	if v and v.admin_level >= 4:
		board_blocks = g.db.query(
			BoardBlock.board_id).filter_by(
			user_id=v.id).subquery()

		posts = posts.filter(Submission.board_id.notin_(board_blocks))
	elif v:
		m = g.db.query(ModRelationship.board_id).filter_by(
			user_id=v.id, invite_rescinded=False).subquery()
		c = g.db.query(
			ContributorRelationship.board_id).filter_by(
			user_id=v.id).subquery()

		posts = posts.filter(
			or_(
				Submission.author_id == v.id,
				Submission.post_public == True,
				Submission.board_id.in_(m),
				Submission.board_id.in_(c)
			)
		)

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

		board_blocks = g.db.query(
			BoardBlock.board_id).filter_by(
			user_id=v.id).subquery()

		posts = posts.filter(Submission.board_id.notin_(board_blocks))
	else:
		posts = posts.filter_by(post_public=True)

	# board opt out of all
	if v:
		posts = posts.join(Submission.board).filter(
			or_(
				Board.all_opt_out == False,
				Submission.board_id.in_(
					g.db.query(
						Subscription.board_id).filter_by(
						user_id=v.id,
						is_active=True).subquery()
				)
			)
		)
	else:

		posts = posts.join(
			Submission.board).filter_by(
			all_opt_out=False)

	
	posts=posts.options(contains_eager(Submission.board))


	#custom filter
	#print(filter_words)
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
		posts = posts.order_by(Submission.score_best.desc())
	elif sort == "new":
		posts = posts.order_by(Submission.created_utc.desc())
	elif sort == "old":
		posts = posts.order_by(Submission.created_utc.asc())
	elif sort == "controversial":
		posts = posts.order_by(Submission.score_disputed.desc())
	elif sort == "top":
		posts = posts.order_by(Submission.score_top.desc())
	elif sort == "bottom":
		posts = posts.order_by(Submission.score_top.asc())
	elif sort == "comments":
		posts = posts.order_by(Submission.comment_count.desc())
	else:
		abort(400)

	if ids_only:
		posts = [x.id for x in posts.offset(25 * (page - 1)).limit(26).all()]
		return posts
	else:
		return [x for x in posts.offset(25 * (page - 1)).limit(25).all()]

def default_cat_cookie():

	output=[]
	for cat in CATEGORIES:
		for subcat in cat.subcats:
			if subcat.visible:
				output.append(subcat.id)

	output += [0]
	return output

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
					hide_offensive=(v and v.hide_offensive) or not v,
					hide_bot=(v and v.hide_bot),
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
											time_filter=t,
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

	x = g.db.query(Submission).filter(Submission.deleted_utc == 0, Submission.is_banned == False, Submission.score_top > 20)

	total = x.count()
	n = random.randint(0, total - 1)

	post = x.order_by(Submission.id.asc()).offset(n).limit(1).first()
	return redirect(post.permalink)

@cache.memoize(600)
def comment_idlist(page=1, v=None, nsfw=False, **kwargs):

	posts = g.db.query(Submission).options(
		lazyload('*')).join(Submission.board)

	if not nsfw:
		posts = posts.filter_by(over_18=False)

	if v and not v.show_nsfl:
		posts = posts.filter_by(is_nsfl=False)

	if v and v.admin_level >= 4:
		pass
	elif v:
		m = g.db.query(ModRelationship.board_id).filter_by(
			user_id=v.id, invite_rescinded=False).subquery()
		c = g.db.query(
			ContributorRelationship.board_id).filter_by(
			user_id=v.id).subquery()

		posts = posts.filter(
			or_(
				Submission.author_id == v.id,
				Submission.post_public == True,
				Submission.board_id.in_(m),
				Submission.board_id.in_(c),
				Board.is_private == False
			)
		)
	else:
		posts = posts.filter(or_(Submission.post_public ==
								 True, Board.is_private == False))

	posts = posts.subquery()

	comments = g.db.query(Comment).options(lazyload('*'))

	if v and v.hide_offensive:
		comments = comments.filter_by(is_offensive=False)
		
	if v and v.hide_bot:
		comments = comments.filter_by(is_bot=False)

	if v and v.admin_level <= 3:
		# blocks
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

	comments = comments.order_by(Comment.created_utc.desc()).offset(
		25 * (page - 1)).limit(26).all()

	return [x.id for x in comments]


@app.route("/comments", methods=["GET"])
@app.route("/api/v1/front/comments", methods=["GET"])
@auth_desired
@api("read")
def all_comments(v):
	if v and v.is_banned and not v.unban_utc: return render_template("seized.html")

	page = int(request.args.get("page", 1))

	idlist = comment_idlist(v=v,
							page=page,
							hide_offensive=v and v.hide_offensive,
							hide_bot=v and v.hide_bot)

	comments = get_comments(idlist, v=v)

	next_exists = len(idlist) == 26

	idlist = idlist[0:25]

	board = get_board(1)
	return {"html": lambda: render_template("home_comments.html",
											v=v,
											page=page,
											comments=comments,
											standalone=True,
											next_exists=next_exists),
			"api": lambda: jsonify({"data": [x.json for x in comments]})}