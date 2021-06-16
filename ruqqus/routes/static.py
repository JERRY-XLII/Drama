import time
import jinja2
import pyotp
import pprint
from flask import *

from ruqqus.helpers.wrappers import *
import ruqqus.classes
from ruqqus.classes import *
from ruqqus.mail import *
from ruqqus.__main__ import app, limiter
from ruqqus.helpers.get import get_account
from ruqqus.helpers.alerts import *

# take care of misc pages that never really change (much)

@app.route("/oauthhelp", methods=["GET"])
@auth_desired
def oauthhelp(v):
	return render_template("oauthhelp.html", v=v)

@app.route("/contact", methods=["GET"])
@auth_desired
def contact(v):
	return render_template("contact.html", v=v)

@app.route("/contact", methods=["POST"])
@auth_desired
def submit_contact(v):

	message = f'This message has been sent automatically to all admins via https://rdrama.net/contact, user email is "{v.email}"\n\nMessage:\n\n' + request.form.get("message", "")

	admins = g.db.query(User).filter(User.admin_level > 0).all()

	for x in admins: send_pm(v.id, x, message)

	return render_template("contact.html", v=v, msg="Your message has been sent.")

@app.route('/assets/<path:path>')
@limiter.exempt
def static_service(path):
	resp = make_response(send_from_directory('./assets', path))
	resp.headers.add("Cache-Control", "public")

	if request.path.endswith('.css'):
		resp.headers.add("Content-Type", "text/css")
	return resp


@app.route("/robots.txt", methods=["GET"])
def robots_txt():
	return send_file("./assets/robots.txt")


@app.route("/slurs.txt", methods=["GET"])
def slurs():
	resp = make_response('\n'.join([x.keyword for x in g.db.query(
		BadWord).order_by(BadWord.keyword.asc()).all()]))
	resp.headers.add("Content-Type", "text/plain")
	return resp


@app.route("/settings", methods=["GET"])
@auth_required
def settings(v):
	return redirect("/settings/profile")


@app.route("/settings/profile", methods=["GET"])
@auth_required
def settings_profile(v):
	return render_template("settings_profile.html",
						   v=v)


@app.route("/titles", methods=["GET"])
@auth_desired
def titles(v):
	titles = [x for x in g.db.query(Title).order_by(text("id asc")).all()]
	return render_template("/titles.html",
						   v=v,
						   titles=titles)

@app.route("/badges", methods=["GET"])
@auth_desired
def badges(v):
	badges = [
		x for x in g.db.query(BadgeDef).order_by(
			text("rank asc, id asc")).all()]
	return render_template("badges.html",
						   v=v,
						   badges=badges)

@app.route("/leaderboard", methods=["GET"])
@auth_desired
def leaderboard(v):
	li = leaderboard2()
	return render_template("leaderboard.html", v=v, users1=li[0], users2=li[1], users3=li[2], users4=li[3])

@cache.memoize(600)
def leaderboard2():
	users = g.db.query(User).options(lazyload('*'))
	users1 = [x for x in users.order_by(User.stored_karma.desc()).all()][:50]
	users2 = [x for x in users.order_by(User.follower_count.desc()).all()][:10]
	users3 = sorted(list(users1), key=lambda x: x.post_count, reverse=True)[:10]
	users4 = sorted(list(users1), key=lambda x: x.comment_count, reverse=True)[:10]
	users1 = users1[:25]
	return [users1, users2, users3, users4]

@app.route("/blocks", methods=["GET"])
@auth_desired
def blocks(v):
	blocks=g.db.query(UserBlock).all()
	users = []
	targets = []
	for x in blocks:
		users.append(get_account2(x.user_id))
		targets.append(get_account2(x.target_id))

	return render_template("blocks.html", v=v, users=users, targets=targets)

@app.route("/banned", methods=["GET"])
@auth_desired
def banned(v):
	users = [x for x in g.db.query(User).filter(User.is_banned != 0).all()]
	return render_template("banned.html", v=v, users=users)

@app.route("/formatting", methods=["GET"])
@auth_desired
def formatting(v):
	return render_template("formatting.html", v=v)
	
@app.route("/.well-known/brave-rewards-verification.txt", methods=["GET"])
def brave():
	with open(".well-known/brave-rewards-verification.txt", "r") as f: return Response(f.read(), mimetype='text/plain')

@app.route("/badmins", methods=["GET"])
@auth_desired
def help_admins(v):

	admins = g.db.query(User).filter(
		User.admin_level > 1,
		User.id > 1).order_by(
		User.id.asc()).all()
	admins = [x for x in admins]

	exadmins = g.db.query(User).filter_by(
		admin_level=1).order_by(
		User.id.asc()).all()
	exadmins = [x for x in exadmins]

	return render_template("admins.html",
						   v=v,
						   admins=admins,
						   exadmins=exadmins
						   )


@app.route("/settings/security", methods=["GET"])
@auth_required
def settings_security(v):
	return render_template("settings_security.html",
						   v=v,
						   mfa_secret=pyotp.random_base32() if not v.mfa_secret else None,
						   error=request.args.get("error") or None,
						   msg=request.args.get("msg") or None
						   )

@app.route("/settings/premium", methods=["GET"])
@auth_required
def settings_premium(v):
	return render_template("settings_premium.html",
						   v=v,
						   error=request.args.get("error") or None,
						   msg=request.args.get("msg") or None
						   )

@app.route("/about/<path:path>")
def about_path(path):
	return redirect(f"/{path}")

@app.route("/info/image_hosts", methods=["GET"])
def info_image_hosts():

	sites = g.db.query(Domain).filter_by(
		show_thumbnail=True).order_by(
		Domain.domain.asc()).all()

	sites = [x.domain for x in sites]

	text = "\n".join(sites)

	resp = make_response(text)
	resp.mimetype = "text/plain"
	return resp

@app.route("/dismiss_mobile_tip", methods=["POST"])
def dismiss_mobile_tip():

	session["tooltip_last_dismissed"]=int(time.time())
	session.modified=True

	return "", 204
