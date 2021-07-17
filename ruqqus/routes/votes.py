from ruqqus.helpers.wrappers import *
from ruqqus.helpers.get import *
from ruqqus.classes import *
from flask import *
from ruqqus.__main__ import app


@app.route("/api/v1/vote/post/<post_id>/<x>", methods=["POST"])
@app.route("/api/vote/post/<post_id>/<x>", methods=["POST"])
@is_not_banned
@no_negative_balance("toast")
@api("vote")
@validate_formkey
def api_vote_post(post_id, x, v):

	if x not in ["-1", "0", "1"]:
		abort(400)

	# disallow bots
	if request.headers.get("X-User-Type","") == "Bot":
		abort(403)

	x = int(x)

	if x==-1:
		count=g.db.query(Vote).filter(
			Vote.user_id.in_(
				tuple(
					[v.id]+[x.id for x in v.alts]
					)
				),
			Vote.created_utc > (int(time.time())-3600), 
			Vote.vote_type==-1
			).count()
		if count >=15 and v.admin_level==0:
			return jsonify({"error": "You're doing that too much. Try again later."}), 403

	post = get_post(post_id)

	if post.is_banned:
		return jsonify({"error":"That post has been removed."}), 403
	elif post.deleted_utc > 0:
		return jsonify({"error":"That post has been deleted."}), 403
	elif post.is_archived:
		return jsonify({"error":"That post is archived and can no longer be voted on."}), 403

	# check for existing vote
	existing = g.db.query(Vote).filter_by(
		user_id=v.id, submission_id=post.id).first()
	if existing:
		existing.change_to(x)
		g.db.add(existing)

	else:
		vote = Vote(user_id=v.id,
					vote_type=x,
					submission_id=base36decode(post_id),
					creation_ip=request.remote_addr,
					app_id=v.client.application.id if v.client else None
					)

		g.db.add(vote)

	try:
		g.db.flush()
	except:
		return jsonify({"error":"Vote already exists."}), 422
		
	posts = []
	posts.append(post)

	post.upvotes = post.ups
	post.downvotes = post.downs
	g.db.add(post)
	return "", 204

@app.route("/api/v1/vote/comment/<comment_id>/<x>", methods=["POST"])
@app.route("/api/vote/comment/<comment_id>/<x>", methods=["POST"])
@is_not_banned
@no_negative_balance("toast")
@api("vote")
@validate_formkey
def api_vote_comment(comment_id, x, v):

	if x not in ["-1", "0", "1"]:
		abort(400)

	# disallow bots
	if request.headers.get("X-User-Type","") == "Bot":
		abort(403)

	x = int(x)

	comment = get_comment(comment_id)

	# check for existing vote
	existing = g.db.query(CommentVote).filter_by(
		user_id=v.id, comment_id=comment.id).first()
	if existing:
		existing.change_to(x)
		g.db.add(existing)
	else:

		vote = CommentVote(user_id=v.id,
						   vote_type=x,
						   comment_id=base36decode(comment_id),
						   creation_ip=request.remote_addr,
						   app_id=v.client.application.id if v.client else None
						   )

		g.db.add(vote)
	try:
		g.db.flush()
	except:
		return jsonify({"error":"Vote already exists."}), 422

	comment.upvotes = comment.ups
	comment.downvotes = comment.downs
	g.db.add(comment)
	return make_response(""), 204
