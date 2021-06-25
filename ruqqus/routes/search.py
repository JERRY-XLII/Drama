from ruqqus.classes import *
from ruqqus.helpers.wrappers import *
from urllib.parse import quote
import re

from sqlalchemy import *

from flask import *
from ruqqus.classes.domains import reasons as REASONS
from ruqqus.__main__ import app, cache
import random



query_regex=re.compile("(\w+):(\S+)")
valid_params=[
	'author',
	'domain',
	'guild',
	'url'
]

def searchparse(text):

	#takes test in filter:term format and returns data

	criteria = {x[0]:x[1] for x in query_regex.findall(text)}

	for x in criteria:
		if x in valid_params:
			text = text.replace(f"{x}:{criteria[x]}", "")

	text=text.lstrip().rstrip()

	if text:
		criteria['q']=text

	return criteria



@cache.memoize(300)
def searchlisting(criteria, v=None, page=1, t="None", sort="top", b=None):

	posts = g.db.query(Submission).options(
				lazyload('*')
			).join(
				Submission.submission_aux,
			).join(
				Submission.author
			).join(
				Submission.board
			)
	
	if 'q' in criteria:
		words=criteria['q'].split()
		words=[SubmissionAux.title.ilike('%'+x+'%') for x in words]
		words=tuple(words)
		posts=posts.filter(*words)
		
	if 'author' in criteria:
		posts=posts.filter(
				Submission.author_id==get_user(criteria['author']).id,
				User.is_private==False,
				User.is_deleted==False
			)

	if b:
		posts=posts.filter(Submission.board_id==b.id)
	elif 'guild' in criteria:
		board=get_guild(criteria["guild"])
		posts=posts.filter(
				Submission.board_id==board.id,
			)

	if 'url' in criteria:
		url=criteria['url']
		url=url.replace('%','\%')
		url=url.replace('_','\_')
		posts=posts.filter(
			SubmissionAux.url.ilike("%"+criteria['url']+"%")
			)

	if 'domain' in criteria:
		domain=criteria['domain']
		posts=posts.filter(
			or_(
				SubmissionAux.url.ilike("https://"+domain+'/%'),
				SubmissionAux.url.ilike("https://"+domain+'/%'),
				SubmissionAux.url.ilike("https://"+domain),
				SubmissionAux.url.ilike("https://"+domain),
				SubmissionAux.url.ilike("https://www."+domain+'/%'),
				SubmissionAux.url.ilike("https://www."+domain+'/%'),
				SubmissionAux.url.ilike("https://www."+domain),
				SubmissionAux.url.ilike("https://www."+domain)
				)
			)

	if not(v and v.admin_level >= 3):
		posts = posts.filter(
			Submission.deleted_utc == 0,
			Submission.is_banned == False,
			)

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
			Submission.author_id.notin_(blocked),
			Board.is_banned==False,
		)
	else:
		posts = posts.filter(
			Submission.post_public == True,
			Board.is_banned==False,
			)

	if t:
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
		posts = posts.filter(Submission.created_utc >= cutoff)

	posts=posts.options(
		contains_eager(Submission.submission_aux),
		contains_eager(Submission.author),
		contains_eager(Submission.board)
		)

	if sort == "hot":
		posts = posts.order_by(Submission.score_hot.desc()).all()
	elif sort == "new":
		posts = posts.order_by(Submission.created_utc.desc()).all()
	elif sort == "old":
		posts = posts.order_by(Submission.created_utc.asc()).all()
	elif sort == "controversial":
		posts = posts.order_by(Submission.score_disputed.desc()).all()
	elif sort == "top":
		posts = posts.order_by(Submission.score_top.desc()).all()
	elif sort == "bottom":
		posts = posts.order_by(Submission.score_top.asc()).all()
	elif sort == "comments":
		posts = posts.order_by(Submission.comment_count.desc()).all()
	elif sort == "random":
		posts = posts.all()
		posts = random.sample(posts, k=len(posts))
	else:
		abort(400)

	total = len(posts)

	slice = 25 * (page - 1)
	posts = posts[slice:26]

	return total, [x.id for x in posts]


@cache.memoize(300)
def searchcommentlisting(criteria, v=None, page=1, t="None", sort="top"):

	comments = g.db.query(Comment).options(lazyload('*')).filter(Comment.parent_submission != None).join(Comment.comment_aux)

	if 'q' in criteria:
		words=criteria['q'].split()
		words=[CommentAux.body.ilike('%'+x+'%') for x in words]
		words=tuple(words)
		comments=comments.filter(*words)

	if not(v and v.admin_level >= 3):
		comments = comments.filter(
			Comment.deleted_utc == 0,
			Comment.is_banned == False)

	if t:
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

	comments=comments.options(contains_eager(Comment.comment_aux),)

	if sort == "hot":
		comments = comments.order_by(Comment.score_hot.desc())
	elif sort == "new":
		comments = comments.order_by(Comment.created_utc.desc())
	elif sort == "old":
		comments = comments.order_by(Comment.created_utc.asc())
	elif sort == "controversial":
		comments = comments.order_by(Comment.score_disputed.desc())
	elif sort == "top":
		comments = comments.order_by(Comment.score_top.desc())
	elif sort == "bottom":
		comments = comments.order_by(Comment.score_top.asc())

	total = comments.count()
	comments = [x for x in comments.offset(25 * (page - 1)).limit(26).all()]

	return total, [x.id for x in comments]

@app.route("/search/posts", methods=["GET"])
@app.route("/api/v1/search", methods=["GET"])
@app.route("/api/vue/search")
@auth_desired
@api("read")
def searchposts(v, search_type="posts"):
	if v and v.is_banned and not v.unban_utc: return render_template("seized.html")

	query = request.args.get("q", '').lstrip().rstrip()

	page = max(1, int(request.args.get("page", 1)))

	sort = request.args.get("sort", "top").lower()
	t = request.args.get('t', 'all').lower()



	# posts search

	criteria=searchparse(query)
	total, ids = searchlisting(criteria, v=v, page=page, t=t, sort=sort)

	next_exists = (len(ids) == 26)
	ids = ids[0:25]

	posts = get_posts(ids, v=v)

	if v and v.admin_level>3 and "domain" in criteria:
		domain=criteria['domain']
		domain_obj=get_domain(domain)
	else:
		domain=None
		domain_obj=None

	return {"html":lambda:render_template("search.html",
						   v=v,
						   query=query,
						   total=total,
						   page=page,
						   listing=posts,
						   sort=sort,
						   time_filter=t,
						   next_exists=next_exists,
						   domain=domain,
						   domain_obj=domain_obj,
						   reasons=REASONS
						   ),
			"api":lambda:jsonify({"data":[x.json for x in posts]})
			}

@app.route("/search/comments", methods=["GET"])
@app.route("/api/v1/search/comments", methods=["GET"])
@app.route("/api/vue/search/comments")
@auth_desired
@api("read")
def searchcomments(v):
	if v and v.is_banned and not v.unban_utc: return render_template("seized.html")

	query = request.args.get("q", '').lstrip().rstrip()

	page = max(1, int(request.args.get("page", 1)))

	sort = request.args.get("sort", "top").lower()
	t = request.args.get('t', 'all').lower()

	criteria=searchparse(query)
	total, ids = searchcommentlisting(criteria, v=v, page=page, t=t, sort=sort)

	next_exists = (len(ids) == 26)
	ids = ids[0:25]

	comments = get_comments(ids, v=v)

	return {"html":lambda:render_template("search_comments.html",
						   v=v,
						   query=query,
						   total=total,
						   page=page,
						   comments=comments,
						   sort=sort,
						   time_filter=t,
						   next_exists=next_exists,
						   ),
			"api":lambda:jsonify({"data":[x.json for x in comments]})
			}
			
@app.route("/search/users", methods=["GET"])
@app.route("/api/v1/search/users", methods=["GET"])
@app.route("/api/vue/search/users")
@auth_desired
@api("read")
def searchusers(v, search_type="posts"):
	if v and v.is_banned and not v.unban_utc: return render_template("seized.html")

	query = request.args.get("q", '').lstrip().rstrip()

	page = max(1, int(request.args.get("page", 1)))
	sort = request.args.get("sort", "top").lower()
	t = request.args.get('t', 'all').lower()
	term=query.lstrip('@')
	term=term.replace('\\','')
	term=term.replace('_','\_')
	
	now=int(time.time())
	users=g.db.query(User).filter(User.username.ilike(f'%{term}%'))
	
	users=users.order_by(User.username.ilike(term).desc(), User.stored_subscriber_count.desc())
	
	total=users.count()
	
	users=[x for x in users.offset(25 * (page-1)).limit(26)]
	next_exists=(len(users)==26)
	users=users[0:25]
	
	
	
	return {"html":lambda:render_template("search_users.html",
				   v=v,
				   query=query,
				   total=total,
				   page=page,
				   users=users,
				   sort=sort,
				   time_filter=t,
				   next_exists=next_exists
				  ),
			"api":lambda:jsonify({"data":[x.json for x in users]})
			}