import boto3
import requests
from os import environ, remove
import piexif
import time
from urllib.parse import urlparse
from PIL import Image as IImage
import imagehash
from sqlalchemy import func
from os import remove
import base64
import io
from ruqqus.classes.images import *
from ruqqus.__main__ import db_session
from .base36 import hex2bin

BUCKET = "i.ruqqus.ga"
CF_KEY = environ.get("CLOUDFLARE_KEY").strip()
CF_ZONE = environ.get("CLOUDFLARE_ZONE").strip()
imgurkey = environ.get("imgurkey").strip()


# setup AWS connection
S3 = boto3.client("s3",
				aws_access_key_id=environ.get(
					"AWS_ACCESS_KEY_ID").strip(),
				aws_secret_access_key=environ.get(
					"AWS_SECRET_ACCESS_KEY").strip()
				)

def check_phash(db, name):

	return db.query(BadPic).filter(
		func.levenshtein(
			BadPic.phash,
			hex2bin(str(imagehash.phash(IImage.open(name))))
			) < 10
		).first()


def upload_from_url(name, url):

	print('upload from url')

	x = requests.get(url)

	print('got content')

	tempname = name.replace("/", "_")

	with open(tempname, "wb") as file:
		for chunk in x.iter_content(1024):
			file.write(chunk)

	if tempname.split('.')[-1] in ['jpg', 'jpeg']:
		piexif.remove(tempname)

	S3.upload_file(tempname,
				Bucket=BUCKET,
				Key=name,
				ExtraArgs={'ACL': 'public-read',
							"ContentType": "image/png",
							"StorageClass": "INTELLIGENT_TIERING"
							}
				)

	remove(tempname)


def crop_and_resize(img, resize):

	i = img

	# get constraining dimension
	org_ratio = i.width / i.height
	new_ratio = resize[0] / resize[1]

	if new_ratio > org_ratio:
		crop_height = int(i.width / new_ratio)
		box = (0, (i.height // 2) - (crop_height // 2),
			i.width, (i.height // 2) + (crop_height // 2))
	else:
		crop_width = int(new_ratio * i.height)
		box = ((i.width // 2) - (crop_width // 2), 0,
			(i.width // 2) + (crop_width // 2), i.height)

	return i.resize(resize, box=box)


def upload_file(name, file, resize=None):

	if resize:
		tempname = name.replace("/", "_")

		file.save(tempname)

		if tempname.split('.')[-1] in ['jpg', 'jpeg']:
			piexif.remove(tempname)

		i = IImage.open(tempname)
		i = crop_and_resize(i, resize)
		img = io.BytesIO()
		i.save(img, format='PNG')
		req = requests.post('https://api.imgur.com/3/upload.json', headers = {"Authorization": f"Client-ID {imgurkey}"}, data = {'image': base64.b64encode(img.getvalue())})
		try: resp = req.json()['data']
		except Exception as e:
			print(e)
			print(req)
			print(req.text)
			return
		remove(tempname)
	else:
		req = requests.post('https://api.imgur.com/3/upload.json', headers = {"Authorization": f"Client-ID {imgurkey}"}, data = {'image': base64.b64encode(file.read())})
		try: resp = req.json()['data']
		except Exception as e:
			print(e)
			print(req)
			print(req.text)
			return
	try: url = resp['link'].replace(".png", "_d.png").replace(".jpg", "_d.jpg").replace(".jpeg", "_d.jpeg") + "?maxwidth=9999"
	except Exception as e:
		print(e)
		print(req)
		print(req.text)
		return
	
	new_image = Image(
		text=url,
		deletehash=resp["deletehash"],
		)
		
	g.db.add(new_image)
	g.db.flush()

	return(url)

	
def upload_from_file(name, filename, resize=None):

	tempname = name.replace("/", "_")

	if filename.split('.')[-1] in ['jpg', 'jpeg']:
		piexif.remove(tempname)

	i = IImage.open(tempname)
	i = crop_and_resize(i, resize)
	img = io.BytesIO()
	i.save(img, format='PNG')
	try: 
		req = requests.post('https://api.imgur.com/3/upload.json', headers = {"Authorization": f"Client-ID {imgurkey}"}, data = {'image': base64.b64encode(img.getvalue())})
		resp = req.json()['data']
		remove(filename)
		url = resp['link'].replace(".png", "_d.png").replace(".jpg", "_d.jpg").replace(".jpeg", "_d.jpeg") + "?maxwidth=9999"
	except Exception as e:
		print(e)
		print(req)
		print(req.text)
		return
	
	new_image = Image(
		text=url,
		deletehash=resp["deletehash"],
		)
		
	g.db.add(new_image)
	g.db.flush()

	return(url)

def delete_file(name):
	
	image = g.db.query(Image).filter(Image.text == name).first()
	if image:
		requests.delete(f'https://api.imgur.com/3/image/{image.deletehash}', headers = {"Authorization": f"Client-ID {imgurkey}"})
		headers = {"Authorization": f"Bearer {CF_KEY}", "Content-Type": "application/json"}
		data = {'files': [name]}
		url = f"https://api.cloudflare.com/client/v4/zones/{CF_ZONE}/purge_cache"
		requests.post(url, headers=headers, json=data)


def check_csam(post):

	# Relies on Cloudflare's photodna implementation
	# 451 returned by CF = positive match

	# ignore non-link posts
	if not post.url:
		return

	parsed_url = urlparse(post.url)

	if parsed_url.netloc != BUCKET:
		return

	headers = {"User-Agent": "Drama webserver"}
	for i in range(10):
		x = requests.get(post.url, headers=headers)

		if x.status_code in [200, 451]:
			break
		else:
			time.sleep(20)

	db=db_session()

	if x.status_code == 451:

		# ban user and alts
		post.author.ban_reason="Sexualizing Minors"
		post.author.is_banned=1
		db.add(v)
		for alt in post.author.alts_threaded(db):
			alt.ban_reason="Sexualizing Minors"
			alt.is_banned=1
			db.add(alt)

		# remove content
		post.is_banned = True
		db.add(post)

		db.commit()

		# nuke aws
		delete_file(parsed_url.path.lstrip('/'))
		db.close()
		return

	#check phash
	tempname = f"test_post_{post.base36id}"

	with open(tempname, "wb") as file:
		for chunk in x.iter_content(1024):
			file.write(chunk)

	h=check_phash(db, tempname)
	if h:

		now=int(time.time())
		unban=now+60*60*24*h.ban_time if h.ban_time else 0
		# ban user and alts
		post.author.ban_reason=h.ban_reason
		post.author.is_banned=1
		post.author.unban_utc = unban
		db.add(v)
		for alt in post.author.alts_threaded(db):
			alt.ban_reason=h.ban_reason
			alt.is_banned=1
			alt.unban_utc = unban
			db.add(alt)

		# remove content
		post.is_banned = True
		db.add(post)

		db.commit()

		# nuke aws
		delete_file(parsed_url.path.lstrip('/'))

	remove(tempname)
	db.close()




def check_csam_url(url, v, delete_content_function):

	parsed_url = urlparse(url)

	if parsed_url.netloc != BUCKET:
		return

	headers = {"User-Agent": "Drama webserver"}
	for i in range(10):
		x = requests.get(url, headers=headers)

		if x.status_code in [200, 451]:
			break
		else:
			time.sleep(20)

	db=db_session()

	if x.status_code == 451:
		v.ban_reason="Sexualizing Minors"
		v.is_banned=1
		db.add(v)
		for alt in v.alts_threaded(db):
			alt.ban_reason="Sexualizing Minors"
			alt.is_banned=1
			db.add(alt)

		delete_content_function()

		db.commit()
		db.close()
		delete_file(parsed_url.path.lstrip('/'))
		return

	tempname=f"test_from_url_{parsed_url.path}"
	tempname=tempname.replace('/','_')

	with open(tempname, "wb") as file:
		for chunk in x.iter_content(1024):
			file.write(chunk)

	h=check_phash(db, tempname)
	if h:

		now=int(time.time())
		unban=now+60*60*24*h.ban_time if h.ban_time else 0
		# ban user and alts
		v.ban_reason=h.ban_reason
		v.is_banned=1
		v.unban_utc = unban
		db.add(v)
		for alt in v.alts_threaded(db):
			alt.ban_reason=h.ban_reason
			alt.is_banned=1
			alt.unban_utc = unban
			db.add(alt)

		delete_content_function()

		db.commit()

		# nuke aws
		delete_file(parsed_url.path.lstrip('/'))

	remove(tempname)
	db.close()