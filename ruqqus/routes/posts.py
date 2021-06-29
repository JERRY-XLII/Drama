from urllib.parse import urlparse, ParseResult, urlunparse, urlencode
import mistletoe
from sqlalchemy import func
from sqlalchemy.orm import aliased
from bs4 import BeautifulSoup
import urllib.parse
import secrets
import threading
import requests
import re
import bleach
import time
import gevent

from ruqqus.helpers.wrappers import *
from ruqqus.helpers.base36 import *
from ruqqus.helpers.sanitize import *
from ruqqus.helpers.filters import *
from ruqqus.helpers.embed import *
from ruqqus.helpers.markdown import *
from ruqqus.helpers.get import *
from ruqqus.helpers.thumbs import *
from ruqqus.helpers.session import *
from ruqqus.helpers.aws import *
from ruqqus.helpers.alerts import send_notification
from ruqqus.helpers.discord import send_message
from ruqqus.classes import *
from .front import frontlist
from flask import *
from ruqqus.__main__ import app, limiter, cache, db_session

BAN_REASONS = ['',
			   "URL shorteners are not permitted.",
			   "Pornographic material is not permitted.",  # defunct
			   "Copyright infringement is not permitted."
			   ]

BUCKET = "i.rdrama.net"

with open("snappy.txt", "r") as f:
	snappyquotes = f.read().split("{[para]}")

@app.route("/api/publish/<pid>", methods=["POST"])
@is_not_banned
@validate_formkey
def publish(pid, v):
	post = get_post(pid)
	if not post.author_id == v.id: abort(403)
	post.private = False
	g.db.add(post)
	cache.delete_memoized(frontlist)
	g.db.commit()
	return "", 204

@app.route("/submit", methods=["GET"])
@auth_required
@no_negative_balance("html")
def submit_get(v):
	if v and v.is_banned and not v.unban_utc: return render_template("seized.html")

	board = request.args.get("guild", "general")
	b = get_guild(board, graceful=True)
	if not b:

		b = get_guild("general")


	return render_template("submit.html",
						   v=v,
						   b=b
						   )

@app.route("/post_short/", methods=["GET"])
@app.route("/post_short/<base36id>", methods=["GET"])
@app.route("/post_short/<base36id>/", methods=["GET"])
def incoming_post_shortlink(base36id=None):

	if not base36id:
		return redirect('/')

	if base36id == "robots.txt":
		return redirect('/robots.txt')

	try:
		x=base36decode(base36id)
	except:
		abort(400)

	post = get_post(base36id)
	return redirect(post.permalink)

@app.route("/post/<pid>", methods=["GET"])
@app.route("/post/<pid>/", methods=["GET"])
@app.route("/post/<pid>/<anything>", methods=["GET"])
@app.route("/api/v1/post/<pid>", methods=["GET"])
@app.route("/test/post/<pid>", methods=["GET"])
@auth_desired
@api("read")
def post_base36id(pid, anything=None, v=None):
	try: pid = int(pid)
	except Exception as e: pass
		
	post = get_post_with_comments(pid, v=v, sort=request.args.get("sort", "top"))
	
	post.views += 1

	board = post.board

	if board.is_banned and not (v and v.admin_level > 3):
		return render_template("board_banned.html",
							   v=v,
							   b=board,
							   p=True)

	if post.over_18 and not (v and v.over_18) and not session_over18(board):
		t = int(time.time())
		return {"html":lambda:render_template("errors/nsfw.html",
							   v=v,
							   t=t,
							   lo_formkey=make_logged_out_formkey(t),
							   board=post.board

							   ),
				"api":lambda:(jsonify({"error":"Must be 18+ to view"}), 451)
				}
	
	post.tree_comments()

	return {
		"html":lambda:post.rendered_page(v=v),
		"api":lambda:jsonify(post.json)
		}

@app.route("/edit_post/<pid>", methods=["POST"])
@is_not_banned
@no_negative_balance("html")
@validate_formkey
def edit_post(pid, v):

	p = get_post(pid)

	if not p.author_id == v.id:
		abort(403)

	if p.is_banned:
		abort(403)

	if p.board.has_ban(v):
		abort(403)

	body = request.form.get("body", "")
	#body=preprocess(body)
	with CustomRenderer() as renderer:
		body_md = renderer.render(mistletoe.Document(body))
	body_html = sanitize(body_md, linkgen=True)

	# Run safety filter
	bans = filter_comment_html(body_html)
	if bans:
		ban = bans[0]
		reason = f"Remove the {ban.domain} link from your post and try again."
		if ban.reason:
			reason += f" {ban.reason_text}"
			
		#auto ban for digitally malicious content
		if any([x.reason==4 for x in bans]):
			v.ban(days=30, reason="Digitally malicious content is not allowed.")
			abort(403)
			
		return {"error": reason}, 403

	# check spam
	soup = BeautifulSoup(body_html, features="html.parser")
	links = [x['href'] for x in soup.find_all('a') if x.get('href')]

	for link in links:
		parse_link = urlparse(link)
		check_url = ParseResult(scheme="https",
								netloc=parse_link.netloc,
								path=parse_link.path,
								params=parse_link.params,
								query=parse_link.query,
								fragment='')
		check_url = urlunparse(check_url)

		badlink = g.db.query(BadLink).filter(
			literal(check_url).contains(
				BadLink.link)).first()
		if badlink:
			if badlink.autoban:
				text = "Your Drama account has been suspended for 1 day for the following reason:\n\n> Too much spam!"
				send_notification(v, text)
				v.ban(days=1, reason="spam")

				return redirect('/notifications')
			else:

				return {"error": f"The link `{badlink.link}` is not allowed. Reason: {badlink.reason}"}


	p.body = body
	p.body_html = body_html
	if request.form.get("title"): p.title = request.form.get("title")
	if int(time.time()) - p.created_utc > 60 * 3: p.edited_utc = int(time.time())
	g.db.add(p)
	
	notify_users = set()
	
	soup = BeautifulSoup(body_html, features="html.parser")
	for mention in soup.find_all("a", href=re.compile("^/@(\w+)")):
		username = mention["href"].split("@")[1]
		user = g.db.query(User).filter_by(username=username).first()
		if user and not v.any_block_exists(user) and user.id != v.id: notify_users.add(user)
		
	for x in notify_users: send_notification(x, f"@{v.username} has mentioned you: https://rdrama.net{p.permalink}")

	return redirect(p.permalink)

@app.route("/submit/title", methods=['GET'])
@limiter.limit("6/minute")
@is_not_banned
@no_negative_balance("html")
#@tos_agreed
#@validate_formkey
def get_post_title(v):

	url = request.args.get("url", None)
	if not url:
		return abort(400)

	#mimic chrome browser agent
	headers = {"User-Agent": f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.72 Safari/537.36"}
	try:
		x = requests.get(url, headers=headers)
	except BaseException:
		return jsonify({"error": "Could not reach page"}), 400


	if not x.status_code == 200:
		return jsonify({"error": f"Page returned {x.status_code}"}), x.status_code


	try:
		soup = BeautifulSoup(x.content, 'html.parser')

		data = {"url": url,
				"title": soup.find('title').string
				}

		return jsonify(data)
	except BaseException:
		return jsonify({"error": f"Could not find a title"}), 400

def thumbs(new_post):
	pid = new_post.base36id
	post = get_post(pid, graceful=True, session=g.db)
	if not post:
		# account for possible follower lag
		time.sleep(60)
		post = get_post(pid, session=g.db)

	fetch_url=post.url

	#get the content

	#mimic chrome browser agent
	headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.72 Safari/537.36"}

	try:
		x=requests.get(fetch_url, headers=headers)
	except:
		return False, "Unable to connect to source"

	if x.status_code != 200:
		return False, f"Source returned status {x.status_code}."

	#if content is image, stick with that. Otherwise, parse html.

	if x.headers.get("Content-Type","").startswith("text/html"):
		#parse html, find image, load image
		soup=BeautifulSoup(x.content, 'html.parser')
		#parse html

		#first, set metadata
		try:
			meta_title=soup.find('title')
			if meta_title:
				post.submission_aux.meta_title=str(meta_title.string)[0:500]

			meta_desc = soup.find('meta', attrs={"name":"description"})
			if meta_desc:
				post.submission_aux.meta_description=meta_desc['content'][0:1000]

			if meta_title or meta_desc:
				g.db.add(post.submission_aux)
				g.db.commit()

		except Exception as e:
			pass

		#create list of urls to check
		thumb_candidate_urls=[]

		#iterate through desired meta tags
		meta_tags = [
			"ruqqus:thumbnail",
			"twitter:image",
			"og:image",
			"thumbnail"
			]

		for tag_name in meta_tags:
			


			tag = soup.find(
				'meta', 
				attrs={
					"name": tag_name, 
					"content": True
					}
				)
			if not tag:
				tag = soup.find(
					'meta',
					attrs={
						'property': tag_name,
						'content': True
						}
					)
			if tag:
				thumb_candidate_urls.append(expand_url(post.url, tag['content']))

		#parse html doc for <img> elements
		for tag in soup.find_all("img", attrs={'src':True}):
			thumb_candidate_urls.append(expand_url(post.url, tag['src']))


		#now we have a list of candidate urls to try
		for url in thumb_candidate_urls:

			try:
				image_req=requests.get(url, headers=headers)
			except:
				continue

			if image_req.status_code >= 400:
				continue

			if not image_req.headers.get("Content-Type","").startswith("image/"):
				continue

			if image_req.headers.get("Content-Type","").startswith("image/svg"):
				continue

			image = PILimage.open(BytesIO(image_req.content))
			if image.width < 30 or image.height < 30:
				continue

			break

		else:
			#getting here means we are out of candidate urls (or there never were any)
			return False, "No usable images"




	elif x.headers.get("Content-Type","").startswith("image/"):
		#image is originally loaded fetch_url
		image_req=x
		image = PILimage.open(BytesIO(x.content))

	else:

		print(f'Unknown content type {x.headers.get("Content-Type")}')
		return False, f'Unknown content type {x.headers.get("Content-Type")} for submitted content'

	name = f"posts/{post.base36id}/thumb.png"
	tempname = name.replace("/", "_")

	with open(tempname, "wb") as file:
		for chunk in image_req.iter_content(1024):
			file.write(chunk)

	post.thumburl = aws.upload_from_file(name, tempname, resize=(375, 227))
	if post.thumburl: post.has_thumb = True
	g.db.add(post)
	g.db.commit()

	try: remove(tempname)
	except FileNotFoundError: pass

def archiveorg(url):
	try: requests.get(f'https://web.archive.org/save/{url}', headers={'User-Agent': 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'}, timeout=100)
	except Exception as e: print(e)

@app.route("/submit", methods=['POST'])
@app.route("/api/v1/submit", methods=["POST"])
@app.route("/api/vue/submit", methods=["POST"])
@limiter.limit("6/minute")
@is_not_banned
@no_negative_balance('html')
@tos_agreed
@validate_formkey
@api("create")
def submit_post(v):

	title = request.form.get("title", "").lstrip().rstrip()

	title = title.lstrip().rstrip()
	title = title.replace("\n", "")
	title = title.replace("\r", "")
	title = title.replace("\t", "")

	url = request.form.get("url", "")

	board = get_guild(request.form.get('board', 'general'), graceful=True)
	if not board:
		board = get_guild('general')

	if not title:
		return {"html": lambda: (render_template("submit.html",
												 v=v,
												 error="Please enter a better title.",
												 title=title,
												 url=url,
												 body=request.form.get(
													 "body", ""),
												 b=board
												 ), 400),
				"api": lambda: ({"error": "Please enter a better title"}, 400)
				}

	# if len(title)<10:
	#	 return render_template("submit.html",
	#							v=v,
	#							error="Please enter a better title.",
	#							title=title,
	#							url=url,
	#							body=request.form.get("body",""),
	#							b=board
	#							)


	elif len(title) > 500:
		return {"html": lambda: (render_template("submit.html",
												 v=v,
												 error="500 character limit for titles.",
												 title=title[0:500],
												 url=url,
												 body=request.form.get(
													 "body", ""),
												 b=board
												 ), 400),
				"api": lambda: ({"error": "500 character limit for titles"}, 400)
				}

	parsed_url = urlparse(url)
	if not (parsed_url.scheme and parsed_url.netloc) and not request.form.get(
			"body") and not request.files.get("file", None):
		return {"html": lambda: (render_template("submit.html",
												 v=v,
												 error="Please enter a url or some text.",
												 title=title,
												 url=url,
												 body=request.form.get(
													 "body", ""),
												 b=board
												 ), 400),
				"api": lambda: ({"error": "`url` or `body` parameter required."}, 400)
				}
	# sanitize title
	title = bleach.clean(title, tags=[])

	# Force https for submitted urls

	if request.form.get("url"):
		new_url = ParseResult(scheme="https",
							  netloc=parsed_url.netloc,
							  path=parsed_url.path,
							  params=parsed_url.params,
							  query=parsed_url.query,
							  fragment=parsed_url.fragment)
		url = urlunparse(new_url)
	else:
		url = ""

	if "i.imgur.com" in url: url = url.replace(".png", "_d.png").replace(".jpg", "_d.jpg").replace(".jpeg", "_d.jpeg") + "?maxwidth=8888"
	
	body = request.form.get("body", "")
	# check for duplicate
	dup = g.db.query(Submission).join(Submission.submission_aux).filter(

		Submission.author_id == v.id,
		Submission.deleted_utc == 0,
		Submission.board_id == board.id,
		SubmissionAux.title == title,
		SubmissionAux.url == url,
		SubmissionAux.body == body
	).first()

	if dup:
		return redirect(dup.permalink)


	# check for domain specific rules

	parsed_url = urlparse(url)

	domain = parsed_url.netloc

	# check ban status
	domain_obj = get_domain(domain)
	if domain_obj:
		if not domain_obj.can_submit:
		  
			if domain_obj.reason==4:
				v.ban(days=30, reason="Digitally malicious content")
			elif domain_obj.reason==7:
				v.ban(reason="Sexualizing minors")

			return {"html": lambda: (render_template("submit.html",
													 v=v,
													 error=BAN_REASONS[domain_obj.reason],
													 title=title,
													 url=url,
													 body=request.form.get(
														 "body", ""),
													 b=board
													 ), 400),
					"api": lambda: ({"error": BAN_REASONS[domain_obj.reason]}, 400)
					}

		# check for embeds
		if domain_obj.embed_function:
			try:
				embed = eval(domain_obj.embed_function)(url)
			except BaseException:
				embed = None
		else:
			embed = None
	else:

		embed = None

	# board
	board_name = request.form.get("board", "general")
	board_name = board_name.lstrip("+")
	board_name = board_name.rstrip()

	board = get_guild(board_name, graceful=True)

	if not board:

		return {"html": lambda: (render_template("submit.html",
												 v=v,
												 error=f"Please enter a Guild to submit to.",
												 title=title,
												 url=url, body=request.form.get(
													 "body", ""),
												 b=None
												 ), 403),
				"api": lambda: (jsonify({"error": f"403 Forbidden - +{board.name} has been banned."}))
				}

	if board.is_banned:

		return {"html": lambda: (render_template("submit.html",
												 v=v,
												 error=f"+{board.name} has been banned.",
												 title=title,
												 url=url, body=request.form.get(
													 "body", ""),
												 b=None
												 ), 403),
				"api": lambda: (jsonify({"error": f"403 Forbidden - +{board.name} has been banned."}))
				}

	if board.has_ban(v):
		return {"html": lambda: (render_template("submit.html",
												 v=v,
												 error=f"You are exiled from +{board.name}.",
												 title=title,
												 url=url, body=request.form.get(
													 "body", ""),
												 b=None
												 ), 403),
				"api": lambda: (jsonify({"error": f"403 Not Authorized - You are exiled from +{board.name}"}), 403)
				}

	if (board.restricted_posting or board.is_private) and not (
			board.can_submit(v)):
		return {"html": lambda: (render_template("submit.html",
												 v=v,
												 error=f"You are not an approved contributor for +{board.name}.",
												 title=title,
												 url=url,
												 body=request.form.get(
													 "body", ""),
												 b=None
												 ), 403),
				"api": lambda: (jsonify({"error": f"403 Not Authorized - You are not an approved contributor for +{board.name}"}), 403)
				}

	# similarity check
	now = int(time.time())
	cutoff = now - 60 * 60 * 24


	similar_posts = g.db.query(Submission).options(
		lazyload('*')
		).join(
			Submission.submission_aux
		).filter(
			#or_(
			#	and_(
					Submission.author_id == v.id,
					SubmissionAux.title.op('<->')(title) < app.config["SPAM_SIMILARITY_THRESHOLD"],
					Submission.created_utc > cutoff
			#	),
			#	and_(
			#		SubmissionAux.title.op('<->')(title) < app.config["SPAM_SIMILARITY_THRESHOLD"]/2,
			#		Submission.created_utc > cutoff
			#	)
			#)
	).all()

	if url:
		similar_urls = g.db.query(Submission).options(
			lazyload('*')
		).join(
			Submission.submission_aux
		).filter(
			#or_(
			#	and_(
					Submission.author_id == v.id,
					SubmissionAux.url.op('<->')(url) < app.config["SPAM_URL_SIMILARITY_THRESHOLD"],
					Submission.created_utc > cutoff
			#	),
			#	and_(
			#		SubmissionAux.url.op('<->')(url) < app.config["SPAM_URL_SIMILARITY_THRESHOLD"]/2,
			#		Submission.created_utc > cutoff
			#	)
			#)
		).all()
	else:
		similar_urls = []

	threshold = app.config["SPAM_SIMILAR_COUNT_THRESHOLD"]
	if v.age >= (60 * 60 * 24 * 7):
		threshold *= 3
	elif v.age >= (60 * 60 * 24):
		threshold *= 2

	if max(len(similar_urls), len(similar_posts)) >= threshold:

		text = "Your Drama account has been suspended for 1 day for the following reason:\n\n> Too much spam!"
		send_notification(v, text)

		v.ban(reason="Spamming.",
			  days=1)

		for alt in v.alts:
			if not alt.is_suspended:
				alt.ban(reason="Spamming.")

		for post in similar_posts + similar_urls:
			post.is_banned = True
			post.is_pinned = False
			post.ban_reason = "Automatic spam removal. This happened because the post's creator submitted too much similar content too quickly."
			g.db.add(post)
			ma=ModAction(
					user_id=2317,
					target_submission_id=post.id,
					kind="ban_post",
					board_id=post.board_id,
					note="spam"
					)
			g.db.add(ma)
		g.db.commit()
		return redirect("/notifications")

	# catch too-long body
	if len(str(body)) > 10000:

		return {"html": lambda: (render_template("submit.html",
												 v=v,
												 error="10000 character limit for text body.",
												 title=title,
												 url=url,
												 body=request.form.get(
													 "body", ""),
												 b=board
												 ), 400),
				"api": lambda: ({"error": "10000 character limit for text body."}, 400)
				}

	if len(url) > 2048:

		return {"html": lambda: (render_template("submit.html",
												 v=v,
												 error="2048 character limit for URLs.",
												 title=title,
												 url=url,
												 body=request.form.get(
													 "body", ""),
												 b=board
												 ), 400),
				"api": lambda: ({"error": "2048 character limit for URLs."}, 400)
				}

	# render text

	#body=preprocess(body)

	with CustomRenderer() as renderer:
		body_md = renderer.render(mistletoe.Document(body))
	body_html = sanitize(body_md, linkgen=True)

	# Run safety filter
	bans = filter_comment_html(body_html)
	if bans:
		ban = bans[0]
		reason = f"Remove the {ban.domain} link from your post and try again."
		if ban.reason:
			reason += f" {ban.reason_text}"
			
		#auto ban for digitally malicious content
		if any([x.reason==4 for x in bans]):
			v.ban(days=30, reason="Digitally malicious content is not allowed.")
			abort(403)
			
		return {"html": lambda: (render_template("submit.html",
												 v=v,
												 error=reason,
												 title=title,
												 url=url,
												 body=request.form.get(
													 "body", ""),
												 b=board
												 ), 403),
				"api": lambda: ({"error": reason}, 403)
				}

	# check spam
	soup = BeautifulSoup(body_html, features="html.parser")
	links = [x['href'] for x in soup.find_all('a') if x.get('href')]

	if url:
		links = [url] + links

	for link in links:
		parse_link = urlparse(link)
		check_url = ParseResult(scheme="https",
								netloc=parse_link.netloc,
								path=parse_link.path,
								params=parse_link.params,
								query=parse_link.query,
								fragment='')
		check_url = urlunparse(check_url)

		badlink = g.db.query(BadLink).filter(
			literal(check_url).contains(
				BadLink.link)).first()
		if badlink:
			if badlink.autoban:
				text = "Your Drama account has been suspended for 1 day for the following reason:\n\n> Too much spam!"
				send_notification(v, text)
				v.ban(days=1, reason="spam")

				return redirect('/notifications')
			else:

				return {"html": lambda: (render_template("submit.html",
														 v=v,
														 error=f"The link `{badlink.link}` is not allowed. Reason: {badlink.reason}.",
														 title=title,
														 url=url,
														 body=request.form.get(
															 "body", ""),
														 b=board
														 ), 400),
						"api": lambda: ({"error": f"The link `{badlink.link}` is not allowed. Reason: {badlink.reason}"}, 400)
						}

	# check for embeddable video
	domain = parsed_url.netloc

	if url:
		repost = g.db.query(Submission).join(Submission.submission_aux).filter(
			SubmissionAux.url.ilike(url),
			Submission.board_id == board.id,
			Submission.deleted_utc == 0,
			Submission.is_banned == False
		).order_by(
			Submission.id.asc()
		).first()
	else:
		repost = None

	if repost and request.values.get("no_repost"):
		return redirect(repost.permalink)

	if request.files.get('file') and not v.can_submit_image:
		abort(403)

	# offensive
	is_offensive = False
	for x in g.db.query(BadWord).all():
		if (body and x.check(body)) or x.check(title):
			is_offensive = True
			break

	new_post = Submission(
		private=bool(request.form.get("private","")),
		author_id=v.id,
		domain_ref=domain_obj.id if domain_obj else None,
		board_id=board.id,
		original_board_id=board.id,
		over_18=bool(request.form.get("over_18","")),
		is_nsfl=bool(request.form.get("is_nsfl","")),
		post_public=not board.is_private,
		repost_id=repost.id if repost else None,
		is_offensive=is_offensive,
		app_id=v.client.application.id if v.client else None,
		creation_region=request.headers.get("cf-ipcountry"),
		is_bot = request.headers.get("X-User-Type","").lower()=="bot"
	)

	g.db.add(new_post)
	g.db.flush()
	
	for rd in ["https://reddit.com/", "https://new.reddit.com/", "https://www.reddit.com/"]:
		url = url.replace(rd, "https://old.reddit.com/")
			
	url = url.replace("https://mobile.twitter.com", "https://twitter.com")

	new_post_aux = SubmissionAux(id=new_post.id,
								 url=url,
								 body=body,
								 body_html=body_html,
								 embed_url=embed,
								 title=title
								 )
	g.db.add(new_post_aux)
	g.db.flush()

	vote = Vote(user_id=v.id,
				vote_type=1,
				submission_id=new_post.id
				)
	g.db.add(vote)
	g.db.flush()

	g.db.refresh(new_post)

	# check for uploaded image
	if request.files.get('file'):

		#check file size
		if request.content_length > 16 * 1024 * 1024:
			g.db.rollback()
			abort(413)

		file = request.files['file']
		if not file.content_type.startswith('image/'):
			return {"html": lambda: (render_template("submit.html",
														 v=v,
														 error=f"Image files only.",
														 title=title,
														 body=request.form.get(
															 "body", ""),
														 b=board
														 ), 400),
						"api": lambda: ({"error": f"Image files only"}, 400)
						}

		name = f'post/{new_post.base36id}/{secrets.token_urlsafe(8)}'
		new_post.url = upload_file(name, file)
		new_post.domain_ref = 1  # id of i.ruqqus.ga domain
		g.db.add(new_post)
		g.db.add(new_post.submission_aux)
		g.db.commit()

		#csam detection
		def del_function():
			db=db_session()
			delete_file(name)
			new_post.is_banned=True
			db.add(new_post)
			db.commit()
			ma=ModAction(
				kind="ban_post",
				user_id=2317,
				note="banned image",
				target_submission_id=new_post.id
				)
			db.add(ma)
			db.commit()
			db.close()

			
		csam_thread=threading.Thread(target=check_csam_url, 
									 args=(new_post.url, 
										   v, 
										   del_function
										  )
									)
		csam_thread.start()
	
	g.db.commit()

    # spin off thumbnail generation and csam detection as  new threads
	if (new_post.url or request.files.get('file')) and (v.is_activated or request.headers.get('cf-ipcountry')!="T1"): thumbs(new_post)

	# expire the relevant caches: front page new, board new
	cache.delete_memoized(frontlist)
	cache.delete_memoized(User.userpagelisting)
	g.db.commit()

	notify_users = set()
	
	soup = BeautifulSoup(body_html, features="html.parser")
	for mention in soup.find_all("a", href=re.compile("^/@(\w+)")):
		username = mention["href"].split("@")[1]
		user = g.db.query(User).filter_by(username=username).first()
		if user and not v.any_block_exists(user) and user.id != v.id: notify_users.add(user)
		
	for x in notify_users: send_notification(x, f"@{v.username} has mentioned you: https://rdrama.net{new_post.permalink}")

	new_post.upvotes = new_post.ups
	new_post.downvotes = new_post.downs
	g.db.add(new_post)
	g.db.commit()

	c = Comment(author_id=261,
		distinguish_level=6,
		parent_submission=new_post.id,
		parent_fullname=new_post.fullname,
		level=1,
		over_18=False,
		is_nsfl=False,
		is_offensive=False,
		original_board_id=1,
		is_bot=True,
		app_id=None,
		creation_region=request.headers.get("cf-ipcountry")
		)

	g.db.add(c)
	g.db.flush()

	if v.id == 995: body = "fuck off carp"
	else: body = random.choice(snappyquotes)
	if new_post.url:
		body += f"\n\n---\n\nSnapshots:\n\n* [archive.org](https://web.archive.org/{urllib.parse.quote(new_post.url)})\n* [archive.today](https://archive.today/?url={urllib.parse.quote(new_post.url)}&run=1) (click to archive)"
		gevent.spawn(archiveorg,new_post.url)
	with CustomRenderer(post_id=new_post.id) as renderer: body_md = renderer.render(mistletoe.Document(body))
	body_html = sanitize(body_md, linkgen=True)
	c_aux = CommentAux(
		id=c.id,
		body_html=body_html,
		body=body
	)
	g.db.add(c_aux)
	g.db.flush()
	n = Notification(comment_id=c.id, user_id=v.id)
	g.db.add(n)

	send_message(f"https://rdrama.net{new_post.permalink}")
	return {"html": lambda: redirect(new_post.permalink),
			"api": lambda: jsonify(new_post.json)
			}

# @app.route("/api/nsfw/<pid>/<x>", methods=["POST"])
# @auth_required
# @validate_formkey
# def api_nsfw_pid(pid, x, v):

#	 try:
#		 x=bool(int(x))
#	 except:
#		 abort(400)

#	 post=get_post(pid)

#	 if not v.admin_level >=3 and not post.author_id==v.id and not post.board.has_mod(v):
#		 abort(403)

#	 post.over_18=x
#	 g.db.add(post)
#

#	 return "", 204


@app.route("/delete_post/<pid>", methods=["POST"])
@app.route("/api/v1/delete_post/<pid>", methods=["POST"])
@auth_required
@api("delete")
@validate_formkey
def delete_post_pid(pid, v):

	post = get_post(pid)
	if not post.author_id == v.id:
		abort(403)

	post.deleted_utc = int(time.time())
	post.is_pinned = False
	post.stickied = False

	g.db.add(post)

	# clear cache
	cache.delete_memoized(User.userpagelisting)

	if post.age >= 3600 * 6:
		cache.delete_memoized(frontlist, sort="new")

	# delete i.ruqqus.ga
	if post.domain == "i.ruqqus.ga":

		segments = post.url.split("/")
		pid = segments[4]
		rand = segments[5]
		if pid == post.base36id:
			key = f"post/{pid}/{rand}"
			delete_file(key)
			#post.is_image = False
			g.db.add(post)

	return "", 204

@app.route("/undelete_post/<pid>", methods=["POST"])
@app.route("/api/v1/undelete_post/<pid>", methods=["POST"])
@auth_required
@api("delete")
@validate_formkey
def undelete_post_pid(pid, v):
	post = get_post(pid)
	if not post.author_id == v.id: abort(403)
	post.deleted_utc =0
	g.db.add(post)
	cache.delete_memoized(frontlist)
	return "", 204

@app.route("/embed/post/<pid>", methods=["GET"])
def embed_post_pid(pid):

	post = get_post(pid)

	if post.is_banned or post.board.is_banned:
		abort(410)

	return render_template("embeds/submission.html", p=post)

@app.route("/api/toggle_comment_nsfw/<cid>", methods=["POST"])
@app.route("/api/v1/toggle_comment_nsfw/<cid>", methods=["POST"])
@is_not_banned
@api("update")
@validate_formkey
def toggle_comment_nsfw(cid, v):

	comment = g.db.query(Comment).filter_by(id=base36decode(cid)).first()
	if not comment.author_id == v.id and not v.admin_level >= 3: abort(403)
	comment.over_18 = not comment.over_18
	g.db.add(comment)
	return "", 204
	
@app.route("/api/toggle_post_nsfw/<pid>", methods=["POST"])
@app.route("/api/v1/toggle_post_nsfw/<pid>", methods=["POST"])
@is_not_banned
@api("update")
@validate_formkey
def toggle_post_nsfw(pid, v):

	post = get_post(pid)

	mod=post.board.has_mod(v)

	if not post.author_id == v.id and not v.admin_level >= 3 and not mod:
		abort(403)

	if post.board.over_18 and post.over_18:
		abort(403)

	post.over_18 = not post.over_18
	g.db.add(post)

	if post.author_id!=v.id:
		ma=ModAction(
			kind="set_nsfw" if post.over_18 else "unset_nsfw",
			user_id=v.id,
			target_submission_id=post.id,
			board_id=post.board.id,
			)
		g.db.add(ma)

	return "", 204

@app.route("/save_post/<pid>", methods=["POST"])
@auth_required
@validate_formkey
def save_post(pid, v):

	post=get_post(pid)

	new_save=SaveRelationship(user_id=v.id, submission_id=post.id, type=1)

	g.db.add(new_save)

	try: g.db.flush()
	except: abort(422)

	return "", 204

@app.route("/unsave_post/<pid>", methods=["POST"])
@auth_required
@validate_formkey
def unsave_post(pid, v):

	post=get_post(pid)

	save=g.db.query(SaveRelationship).filter_by(user_id=v.id, submission_id=post.id, type=1).first()

	g.db.delete(save)
	
	return "", 204