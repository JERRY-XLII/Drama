from ruqqus.helpers.wrappers import *
from ruqqus.helpers.security import *
from ruqqus.helpers.discord import add_role, delete_role
from ruqqus.__main__ import app

SERVER_ID = environ.get("DISCORD_SERVER_ID",'').strip()
CLIENT_ID = environ.get("DISCORD_CLIENT_ID",'').strip()
CLIENT_SECRET = environ.get("DISCORD_CLIENT_SECRET",'').strip()
BOT_TOKEN = environ.get("DISCORD_BOT_TOKEN").strip()
DISCORD_ENDPOINT = "https://discordapp.com/api/v6"


WELCOME_CHANNEL="846509313941700618"

@app.route("/discord", methods=["GET"])
@auth_required
def join_discord(v):
	
	if v.is_banned != 0: return "You're banned"
	if v.admin_level == 0 and v.dramacoins < 150: return "You must earn 150 dramacoins before entering the Discord server. You earn dramacoins by making posts/comments and getting upvoted."
	
	now=int(time.time())

	state=generate_hash(f"{now}+{v.id}+discord")

	state=f"{now}.{state}"

	return redirect(f"https://discord.com/api/oauth2/authorize?client_id={CLIENT_ID}&redirect_uri=https%3A%2F%2F{app.config['SERVER_NAME']}%2Fdiscord_redirect&response_type=code&scope=identify%20guilds.join&state={state}")

@app.route("/discord_redirect", methods=["GET"])
@auth_required
def discord_redirect(v):


	#validate state
	now=int(time.time())
	state=request.args.get('state','').split('.')

	timestamp=state[0]

	state=state[1]

	if int(timestamp) < now-600:
		abort(400)

	if not validate_hash(f"{timestamp}+{v.id}+discord", state):
		abort(400)

	#get discord token
	code = request.args.get("code","")
	if not code:
		abort(400)

	data={
		"client_id":CLIENT_ID,
		'client_secret': CLIENT_SECRET,
		'grant_type': 'authorization_code',
		'code': code,
		'redirect_uri': f"https://{app.config['SERVER_NAME']}/discord_redirect",
		'scope': 'identify guilds.join'
	}
	headers={
		'Content-Type': 'application/x-www-form-urlencoded'
	}
	url="https://discord.com/api/oauth2/token"

	x=requests.post(url, headers=headers, data=data)

	x=x.json()


	try:
		token=x["access_token"]
	except KeyError:
		abort(403)


	#get user ID
	url="https://discord.com/api/users/@me"
	headers={
		'Authorization': f"Bearer {token}"
	}
	x=requests.get(url, headers=headers)

	x=x.json()



	#add user to discord
	headers={
		'Authorization': f"Bot {BOT_TOKEN}",
		'Content-Type': "application/json"
	}

	#remove existing user if applicable
	if v.discord_id and v.discord_id != x['id']:
		url=f"https://discord.com/api/guilds/{SERVER_ID}/members/{v.discord_id}"
		requests.delete(url, headers=headers)

	if g.db.query(User).filter(User.id!=v.id, User.discord_id==x["id"]).first():
		return render_template("message.html", title="Discord account already linked.", error="That Discord account is already in use by another user.", v=v)

	v.discord_id=x["id"]
	g.db.add(v)
	g.db.commit()

	url=f"https://discord.com/api/guilds/{SERVER_ID}/members/{x['id']}"

	name=v.username
	if v.real_id:
		name+= f" | {v.real_id}"

	data={
		"access_token":token,
		"nick":name,
	}

	x=requests.put(url, headers=headers, json=data)

	if x.status_code in [201, 204]:

		if v.admin_level > 0: add_role(v, "admin")
		else: add_role(v, "newuser")
		
		time.sleep(0.1)
		
		add_role(v, "feedback")

		time.sleep(0.1)

		if v.dramacoins > 100: add_role(v, "linked")
		else: add_role(v, "norep")
		
	else:
		return jsonify(x.json())

	#check on if they are already there
	#print(x.status_code)

	if x.status_code==204:

		##if user is already a member, remove old roles and update nick
		delete_role(v, "nick")


		url=f"https://discord.com/api/guilds/{SERVER_ID}/members/{v.discord_id}"
		data={
			"nick": name
		}

		req=requests.patch(url, headers=headers, json=data)

		#print(req.status_code)
		#print(url)

	return redirect(f"https://discord.com/channels/{SERVER_ID}/{WELCOME_CHANNEL}")