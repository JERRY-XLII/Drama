from __future__ import unicode_literals
from ruqqus.helpers.alerts import *
from ruqqus.helpers.sanitize import *
from ruqqus.helpers.filters import filter_comment_html
from ruqqus.helpers.markdown import *
from ruqqus.helpers.discord import remove_user, set_nick
from ruqqus.mail import *
from .front import frontlist
from ruqqus.__main__ import app, cache
import youtube_dl

valid_username_regex = re.compile("^[a-zA-Z0-9_\-]{3,25}$")
valid_title_regex = re.compile("^((?!<).){3,100}$")
valid_password_regex = re.compile("^.{8,100}$")

youtubekey = environ.get("youtubekey").strip()

@app.route("/settings/profile", methods=["POST"])
@auth_required
@validate_formkey
def settings_profile_post(v):
	updated = False

	if request.values.get("slurreplacer", v.slurreplacer) != v.slurreplacer:
		updated = True
		v.slurreplacer = request.values.get("slurreplacer", None) == 'true'

	if request.values.get("hidevotedon", v.hidevotedon) != v.hidevotedon:
		updated = True
		v.hidevotedon = request.values.get("hidevotedon", None) == 'true'

	if request.values.get("newtab", v.newtab) != v.newtab:
		updated = True
		v.newtab = request.values.get("newtab", None) == 'true'

	if request.values.get("newtabexternal", v.newtabexternal) != v.newtabexternal:
		updated = True
		v.newtabexternal = request.values.get("newtabexternal", None) == 'true'

	if request.values.get("oldreddit", v.oldreddit) != v.oldreddit:
		updated = True
		v.oldreddit = request.values.get("oldreddit", None) == 'true'

	if request.values.get("over18", v.over_18) != v.over_18:
		updated = True
		v.over_18 = request.values.get("over18", None) == 'true'

	if request.values.get("hide_offensive",
						  v.hide_offensive) != v.hide_offensive:
		updated = True
		v.hide_offensive = request.values.get("hide_offensive", None) == 'true'
		
	if request.values.get("hide_bot",
						  v.hide_bot) != v.hide_bot:
		updated = True
		v.hide_bot = request.values.get("hide_bot", None) == 'true'

	if request.values.get("filter_nsfw", v.filter_nsfw) != v.filter_nsfw:
		updated = True
		v.filter_nsfw = not request.values.get("filter_nsfw", None) == 'true'

	if request.values.get("private", v.is_private) != v.is_private:
		updated = True
		v.is_private = request.values.get("private", None) == 'true'

	if request.values.get("nofollow", v.is_nofollow) != v.is_nofollow:
		updated = True
		v.is_nofollow = request.values.get("nofollow", None) == 'true'

	if request.values.get("bio") is not None:
		bio = request.values.get("bio")[0:1500]

		if bio == v.bio:
			return render_template("settings_profile.html",
								   v=v,
								   error="You didn't change anything")

		for i in re.finditer('^(https:\/\/.*\.(png|jpg|jpeg|gif))', bio, re.MULTILINE): bio = bio.replace(i.group(1), f'![]({i.group(1)})')
		with CustomRenderer() as renderer:
			bio_html = renderer.render(mistletoe.Document(bio))
		bio_html = sanitize(bio_html, linkgen=True)

		# Run safety filter
		bans = filter_comment_html(bio_html)

		if bans:
			ban = bans[0]
			reason = f"Remove the {ban.domain} link from your bio and try again."
			if ban.reason:
				reason += f" {ban.reason_text}"
				
			#auto ban for digitally malicious content
			if any([x.reason==4 for x in bans]):
				v.ban(days=30, reason="Digitally malicious content is not allowed.")
			return jsonify({"error": reason}), 401

		v.bio = bio
		v.bio_html=bio_html
		g.db.add(v)
		return render_template("settings_profile.html",
							   v=v,
							   msg="Your bio has been updated.")

	if request.values.get("filters") is not None:

		filters=request.values.get("filters")[0:1000].strip()

		if filters==v.custom_filter_list:
			return render_template("settings_profile.html",
								   v=v,
								   error="You didn't change anything")

		v.custom_filter_list=filters
		g.db.add(v)
		return render_template("settings_profile.html",
							   v=v,
							   msg="Your custom filters have been updated.")



	x = request.values.get("title_id", None)
	if x:
		x = int(x)
		if x == 0:
			v.title_id = None
			updated = True
		elif x > 0:
			title = get_title(x)
			if bool(eval(title.qualification_expr)):
				v.title_id = title.id
				updated = True
			else:
				return jsonify({"error": f"You don't meet the requirements for title `{title.text}`."}), 403
		else:
			abort(400)

	defaultsortingcomments = request.values.get("defaultsortingcomments")
	if defaultsortingcomments:
		if defaultsortingcomments in ["new", "old", "controversial", "top", "bottom", "random"]:
			v.defaultsortingcomments = defaultsortingcomments
			updated = True
		else:
			abort(400)

	defaultsorting = request.values.get("defaultsorting")
	if defaultsorting:
		if defaultsorting in ["hot", "new", "old", "comments", "controversial", "top", "bottom", "random"]:
			v.defaultsorting = defaultsorting
			updated = True
		else:
			abort(400)

	defaulttime = request.values.get("defaulttime")
	if defaulttime:
		if defaulttime in ["hour", "day", "week", "month", "year", "all"]:
			v.defaulttime = defaulttime
			updated = True
		else:
			abort(400)

	theme = request.values.get("theme")
	if theme:
		v.theme = theme
		if theme == "coffee": v.themecolor = "38a169"
		elif theme == "tron": v.themecolor = "80ffff"
		g.db.add(v)
		return "", 204

	if updated:
		g.db.add(v)

		return jsonify({"message": "Your settings have been updated."})

	else:
		return jsonify({"error": "You didn't change anything."}), 400

@app.route("/changelogsub", methods=["POST"])
@auth_required
@validate_formkey
def changelogsub(v):
	v.changelogsub = not v.changelogsub
	g.db.add(v)
	cache.delete_memoized(frontlist)
	return "", 204

@app.route("/settings/namecolor", methods=["POST"])
@auth_required
@validate_formkey
def namecolor(v):
	color = str(request.form.get("color", "")).strip()
	if color not in ['ff66ac','805ad5','62ca56','38a169','80ffff','2a96f3','eb4963','ff0000','f39731','30409f','3e98a7','e4432d','7b9ae4','ec72de','7f8fa6', 'f8db58']: abort(400)
	v.namecolor = color
	g.db.add(v)
	return redirect("/settings/profile")
	
@app.route("/settings/themecolor", methods=["POST"])
@auth_required
@validate_formkey
def themecolor(v):
	themecolor = str(request.form.get("themecolor", "")).strip()
	if themecolor not in ['ff66ac','805ad5','62ca56','38a169','80ffff','2a96f3','eb4963','ff0000','f39731','30409f','3e98a7','e4432d','7b9ae4','ec72de','7f8fa6', 'f8db58']: abort(400)
	v.themecolor = themecolor
	g.db.add(v)
	return redirect("/settings/profile")

@app.route("/settings/titlecolor", methods=["POST"])
@auth_required
@validate_formkey
def titlecolor(v):
	titlecolor = str(request.form.get("titlecolor", "")).strip()
	if titlecolor not in ['ff66ac','805ad5','62ca56','38a169','80ffff','2a96f3','eb4963','ff0000','f39731','30409f','3e98a7','e4432d','7b9ae4','ec72de','7f8fa6', 'f8db58']: abort(400)
	v.titlecolor = titlecolor
	g.db.add(v)
	return redirect("/settings/profile")

@app.route("/settings/security", methods=["POST"])
@auth_required
@validate_formkey
def settings_security_post(v):
	if request.form.get("new_password"):
		if request.form.get(
				"new_password") != request.form.get("cnf_password"):
			return redirect("/settings/security?error=" +
							escape("Passwords do not match."))

		if not re.match(valid_password_regex, request.form.get("new_password")):
			#print(f"signup fail - {username } - invalid password")
			return redirect("/settings/security?error=" + 
							escape("Password must be between 8 and 100 characters."))

		if not v.verifyPass(request.form.get("old_password")):
			return render_template(
				"settings_security.html", v=v, error="Incorrect password")

		v.passhash = v.hash_password(request.form.get("new_password"))

		g.db.add(v)

		return redirect("/settings/security?msg=" +
						escape("Your password has been changed."))

	if request.form.get("new_email"):

		if not v.verifyPass(request.form.get('password')):
			return redirect("/settings/security?error=" +
							escape("Invalid password."))

		new_email = request.form.get("new_email","").strip()
		#counteract gmail username+2 and extra period tricks - convert submitted email to actual inbox
		if new_email.endswith("@gmail.com"):
			gmail_username=new_email.split('@')[0]
			gmail_username=gmail_username.split("+")[0]
			gmail_username=gmail_username.replace('.','')
			new_email=f"{gmail_username}@gmail.com"
		if new_email == v.email:
			return redirect("/settings/security?error=" +
							escape("That email is already yours!"))

		# check to see if email is in use
		existing = g.db.query(User).filter(User.id != v.id,
										   func.lower(User.email) == new_email.lower()).first()
		if existing:
			return redirect("/settings/security?error=" +
							escape("That email address is already in use."))

		url = f"https://{app.config['SERVER_NAME']}/activate"

		now = int(time.time())

		token = generate_hash(f"{new_email}+{v.id}+{now}")
		params = f"?email={quote(new_email)}&id={v.id}&time={now}&token={token}"

		link = url + params

		send_mail(to_address=new_email,
				  subject="Verify your email address.",
				  html=render_template("email/email_change.html",
									   action_url=link,
									   v=v)
				  )

		return redirect("/settings/security?msg=" + escape(
			"Check your email and click the verification link to complete the email change."))

	if request.form.get("2fa_token", ""):

		if not v.verifyPass(request.form.get('password')):
			return redirect("/settings/security?error=" +
							escape("Invalid password or token."))

		secret = request.form.get("2fa_secret")
		x = pyotp.TOTP(secret)
		if not x.verify(request.form.get("2fa_token"), valid_window=1):
			return redirect("/settings/security?error=" +
							escape("Invalid password or token."))

		v.mfa_secret = secret
		g.db.add(v)

		return redirect("/settings/security?msg=" +
						escape("Two-factor authentication enabled."))

	if request.form.get("2fa_remove", ""):

		if not v.verifyPass(request.form.get('password')):
			return redirect("/settings/security?error=" +
							escape("Invalid password or token."))

		token = request.form.get("2fa_remove")

		if not v.validate_2fa(token):
			return redirect("/settings/security?error=" +
							escape("Invalid password or token."))

		v.mfa_secret = None
		g.db.add(v)

		return redirect("/settings/security?msg=" +
						escape("Two-factor authentication disabled."))

@app.route("/settings/log_out_all_others", methods=["POST"])
@auth_required
@validate_formkey
def settings_log_out_others(v):

	submitted_password = request.form.get("password", "")

	if not v.verifyPass(submitted_password):
		return render_template("settings_security.html",
							   v=v, error="Incorrect Password"), 401

	# increment account's nonce
	v.login_nonce += 1

	# update cookie accordingly
	session["login_nonce"] = v.login_nonce

	g.db.add(v)

	return render_template("settings_security.html", v=v,
						   msg="All other devices have been logged out")


@app.route("/settings/images/profile", methods=["POST"])
@auth_required
@validate_formkey
def settings_images_profile(v):
	if v.can_upload_avatar:

		if request.content_length > 1024 * 1024:
			g.db.rollback()
			abort(413)

		v.set_profile(request.files["profile"])
		return render_template("settings_profile.html",
							   v=v, msg="Profile picture successfully updated.")

	return render_template("settings_profile.html", v=v,
						   msg="Avatars require 300 reputation.")


@app.route("/settings/images/banner", methods=["POST"])
@auth_required
@validate_formkey
def settings_images_banner(v):
	if v.can_upload_banner:
		if request.content_length > 16 * 1024 * 1024:
			g.db.rollback()
			abort(413)

		v.set_banner(request.files["banner"])

		return render_template("settings_profile.html",
							   v=v, msg="Banner successfully updated.")

	return render_template("settings_profile.html", v=v,
						   msg="Banners require 500 reputation.")


@app.route("/settings/delete/profile", methods=["POST"])
@auth_required
@validate_formkey
def settings_delete_profile(v):

	v.del_profile()

	return render_template("settings_profile.html", v=v,
						   msg="Profile picture successfully removed.")

@app.route("/settings/delete/banner", methods=["POST"])
@auth_required
@validate_formkey
def settings_delete_banner(v):

	v.del_banner()

	return render_template("settings_profile.html", v=v,
						   msg="Banner successfully removed.")


@app.route("/settings/toggle_collapse", methods=["POST"])
@auth_required
@validate_formkey
def settings_toggle_collapse(v):

	session["sidebar_collapsed"] = not session.get("sidebar_collapsed", False)

	return "", 204


@app.route("/settings/read_announcement", methods=["POST"])
@auth_required
@validate_formkey
def update_announcement(v):

	v.read_announcement_utc = int(time.time())
	g.db.add(v)

	return "", 204


@app.route("/settings/blocks", methods=["GET"])
@auth_required
def settings_blockedpage(v):
	if v and v.is_banned and not v.unban_utc: return render_template("seized.html")

	#users=[x.target for x in v.blocked]

	return render_template("settings_blocks.html",
						   v=v)

@app.route("/settings/css", methods=["GET"])
@auth_required
def settings_css_get(v):
	if v and v.is_banned and not v.unban_utc: return render_template("seized.html")

	return render_template("settings_css.html", v=v)

@app.route("/settings/css", methods=["POST"])
@auth_required
def settings_css(v):
	css = request.form.get("css").replace('\\', '')[0:50000]

	if not v.agendaposter:
		v.css = css
	else:
		v.css = 'body *::before, body *::after { content: "Trans rights are human rights!"; }'
	g.db.add(v)
	return render_template("settings_css.html", v=v)

@app.route("/settings/profilecss", methods=["GET"])
@auth_required
def settings_profilecss_get(v):
	if v and v.is_banned and not v.unban_utc: return render_template("seized.html")
	if v.dramacoins < 1000: return "You must have +1000 dramacoins to set profile css."
	return render_template("settings_profilecss.html", v=v)

@app.route("/settings/profilecss", methods=["POST"])
@auth_required
def settings_profilecss(v):
	if v.dramacoins < 1000: return "You must have +1000 dramacoins to set profile css."
	profilecss = request.form.get("profilecss").replace('\\', '')[0:50000]
	v.profilecss = profilecss
	g.db.add(v)
	return render_template("settings_profilecss.html", v=v)

@app.route("/settings/block", methods=["POST"])
@auth_required
@validate_formkey
def settings_block_user(v):

	user = get_user(request.values.get("username"), graceful=True)

	if not user:
		return jsonify({"error": "That user doesn't exist."}), 404

	if user.id == v.id:
		return jsonify({"error": "You can't block yourself."}), 409

	if v.has_block(user):
		return jsonify({"error": f"You have already blocked @{user.username}."}), 409

	if user.id == 1046:
		return jsonify({"error": "You can't block @Drama."}), 409

	new_block = UserBlock(user_id=v.id,
						  target_id=user.id,
						  created_utc=int(time.time())
						  )
	g.db.add(new_block)

	cache.delete_memoized(frontlist)

	existing = g.db.query(Notification).filter_by(blocksender=v.id, user_id=user.id).first()
	if not existing: send_block_notif(v.id, user.id, f"@{v.username} has blocked you!")

	if request.args.get("notoast"): return "", 204
	return jsonify({"message": f"@{user.username} blocked."})


@app.route("/settings/unblock", methods=["POST"])
@auth_required
@validate_formkey
def settings_unblock_user(v):

	user = get_user(request.values.get("username"))

	x = v.has_block(user)
	
	if not x: abort(409)

	g.db.delete(x)

	cache.delete_memoized(frontlist)

	existing = g.db.query(Notification).filter_by(unblocksender=v.id, user_id=user.id).first()
	if not existing: send_unblock_notif(v.id, user.id, f"@{v.username} has unblocked you!")

	if request.args.get("notoast"): return "", 204
	return jsonify({"message": f"@{user.username} unblocked."})


@app.route("/settings/apps", methods=["GET"])
@auth_required
def settings_apps(v):
	if v and v.is_banned and not v.unban_utc: return render_template("seized.html")

	return render_template("settings_apps.html", v=v)


@app.route("/settings/remove_discord", methods=["POST"])
@auth_required
@validate_formkey
def settings_remove_discord(v):

	if v.admin_level>1:
		return render_template("settings_filters.html", v=v, error="Admins can't disconnect Discord.")

	remove_user(v)

	v.discord_id=None
	g.db.add(v)
	g.db.commit()

	return redirect("/settings/profile")

@app.route("/settings/content", methods=["GET"])
@auth_required
def settings_content_get(v):
	if v and v.is_banned and not v.unban_utc: return render_template("seized.html")

	return render_template("settings_filters.html", v=v)

@app.route("/settings/name_change", methods=["POST"])
@auth_required
@validate_formkey
def settings_name_change(v):

	new_name=request.form.get("name").strip()

	#make sure name is different
	if new_name==v.username:
		return render_template("settings_profile.html",
						   v=v,
						   error="You didn't change anything")

	#verify acceptability
	if not re.match(valid_username_regex, new_name):
		return render_template("settings_profile.html",
						   v=v,
						   error=f"This isn't a valid username.")

	#verify availability
	name=new_name.replace('_','\_')

	x= g.db.query(User).options(
		lazyload('*')
		).filter(
		or_(
			User.username.ilike(name),
			User.original_username.ilike(name)
			)
		).first()

	if x and x.id != v.id:
		return render_template("settings_profile.html",
						   v=v,
						   error=f"Username `{new_name}` is already in use.")

	v=g.db.query(User).with_for_update().options(lazyload('*')).filter_by(id=v.id).first()

	v.username=new_name
	v.name_changed_utc=int(time.time())

	set_nick(v, new_name)

	g.db.add(v)
	g.db.commit()

	return redirect("/settings/profile")

@app.route("/settings/song_change", methods=["POST"])
@auth_required
@validate_formkey
def settings_song_change(v):
	song=request.form.get("song").strip()

	if song == "" and v.song and os.path.isfile(f"/songs/{v.song}.mp3") and g.db.query(User).filter_by(song=v.song).count() == 1:
		os.remove(f"/songs/{v.song}.mp3")
		v.song=None
		g.db.add(v)
		return redirect("/settings/profile")

	song = song.replace("https://music.youtube.com", "https://youtube.com")
	if song.startswith(("https://www.youtube.com/watch?v=", "https://youtube.com/watch?v=", "https://m.youtube.com/watch?v=")):
		id = song.split("v=")[1]
	elif song.startswith("https://youtu.be/"):
		id = song.split("https://youtu.be/")[1]
	else:
		return render_template("settings_profile.html",
					v=v,
					error=f"Not a youtube link.")

	if "?" in id: id = id.split("?")[0]
	if "&" in id: id = id.split("&")[0]

	if os.path.isfile(f'/songs/{id}.mp3'): 
		v.song=id
		g.db.add(v)
		g.db.commit()
		return redirect("/settings/profile")
		
	
	req = requests.get(f"https://www.googleapis.com/youtube/v3/videos?id={id}&key={youtubekey}&part=contentDetails").json()
	try: duration = req['items'][0]['contentDetails']['duration']
	except:
		print(req)
		abort(400)
	if "H" in duration:
		return render_template("settings_profile.html",
					v=v,
					error=f"Duration of the video must not exceed 10 minutes.")

	if "M" in duration:
		duration = int(duration.split("PT")[1].split("M")[0])
		if duration > 10: 
			return render_template("settings_profile.html",
						v=v,
						error=f"Duration of the video must not exceed 10 minutes.")


	if v.song and os.path.isfile(f"/songs/{v.song}.mp3") and g.db.query(User).filter_by(song=v.song).count() == 1:
		os.remove(f"/songs/{v.song}.mp3")

	ydl_opts = {
		'outtmpl': '/songs/%(title)s.%(ext)s',
		'format': 'bestaudio/best',
		'postprocessors': [{
			'key': 'FFmpegExtractAudio',
			'preferredcodec': 'mp3',
			'preferredquality': '192',
		}],
	}

	with youtube_dl.YoutubeDL(ydl_opts) as ydl:
		try: ydl.download([f"https://youtube.com/watch?v={id}"])
		except Exception as e:
			print(e)
			return render_template("settings_profile.html",
						   v=v,
						   error=f"Age-restricted videos aren't allowed.")

	files = os.listdir("/songs/")
	paths = [os.path.join("/songs/", basename) for basename in files]
	songfile = max(paths, key=os.path.getctime)
	os.rename(songfile, f"/songs/{id}.mp3")

	v.song=id
	g.db.add(v)

	return redirect("/settings/profile")

@app.route("/settings/title_change", methods=["POST"])
@auth_required
@validate_formkey
def settings_title_change(v):

	if v.flairchanged: abort(403)
	
	new_name=request.form.get("title").strip()

	#verify acceptability
	if not re.match(valid_title_regex, new_name):
		return render_template("settings_profile.html",
						   v=v,
						   error=f"This isn't a valid flair.")

	#make sure name is different
	if new_name==v.customtitle:
		return render_template("settings_profile.html",
						   v=v,
						   error="You didn't change anything")

	v.customtitleplain = new_name
	new_name = new_name.replace('_','\_')
	new_name = sanitize(new_name, linkgen=True, flair=True)

	v = g.db.query(User).with_for_update().options(lazyload('*')).filter_by(id=v.id).first()
	v.customtitle = new_name

	g.db.add(v)
	g.db.commit()

	return redirect("/settings/profile")

@app.route("/settings/badges", methods=["POST"])
@auth_required
@validate_formkey
def settings_badge_recheck(v):

	v.refresh_selfset_badges()

	return jsonify({"message":"Badges Refreshed"})