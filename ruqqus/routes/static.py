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
	if v and v.is_banned and not v.unban_utc: return render_template("seized.html")

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

@app.route("/settings", methods=["GET"])
@auth_required
def settings(v):
	if v and v.is_banned and not v.unban_utc: return render_template("seized.html")

	return redirect("/settings/profile")


@app.route("/settings/profile", methods=["GET"])
@auth_required
def settings_profile(v):
	if v and v.is_banned and not v.unban_utc: return render_template("seized.html")

	return render_template("settings_profile.html",
						   v=v)


@app.route("/titles", methods=["GET"])
@auth_desired
def titles(v):
	if v and v.is_banned and not v.unban_utc: return render_template("seized.html")

	titles = [x for x in g.db.query(Title).order_by(text("id asc")).all()]
	return render_template("/titles.html",
						   v=v,
						   titles=titles)

@app.route("/badges", methods=["GET"])
@auth_desired
def badges(v):
	if v and v.is_banned and not v.unban_utc: return render_template("seized.html")

	badges = [
		x for x in g.db.query(BadgeDef).order_by(
			text("rank asc, id asc")).all()]
	return render_template("badges.html",
						   v=v,
						   badges=badges)

@app.route("/blocks", methods=["GET"])
@auth_desired
def blocks(v):
	if v and v.is_banned and not v.unban_utc: return render_template("seized.html")

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
	if v and v.is_banned and not v.unban_utc: return render_template("seized.html")

	users = [x for x in g.db.query(User).filter(User.is_banned != 0).all()]
	return render_template("banned.html", v=v, users=users)

@app.route("/formatting", methods=["GET"])
@auth_desired
def formatting(v):
	if v and v.is_banned and not v.unban_utc: return render_template("seized.html")

	return render_template("formatting.html", v=v)
	
@app.route("/.well-known/brave-rewards-verification.txt", methods=["GET"])
def brave():
	with open(".well-known/brave-rewards-verification.txt", "r") as f: return Response(f.read(), mimetype='text/plain')

@app.route("/badmins", methods=["GET"])
@auth_desired
def help_admins(v):
	if v and v.is_banned and not v.unban_utc: return render_template("seized.html")

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
	if v and v.is_banned and not v.unban_utc: return render_template("seized.html")

	return render_template("settings_security.html",
						   v=v,
						   mfa_secret=pyotp.random_base32() if not v.mfa_secret else None,
						   error=request.args.get("error") or None,
						   msg=request.args.get("msg") or None
						   )

@app.route("/imagehosts", methods=["GET"])
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
