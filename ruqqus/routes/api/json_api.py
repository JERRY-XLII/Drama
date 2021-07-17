from ruqqus.helpers.wrappers import *


@app.route("/api/v1/guild/<boardname>", methods=["GET"])
@auth_desired
@api("read")
def guild_info(v, boardname):
	guild = get_guild(boardname)

	return jsonify(guild.json)


@app.route("/api/v1/user/<username>", methods=["GET"])
@auth_desired
@api("read")
def user_info(v, username):

	user = get_user(username, v=v)
	return jsonify(user.json)
