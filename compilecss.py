for theme in ['dark', 'light', 'coffee', 'tron']:
	text = open(f"D:/#D/ruqqus/assets/style/{theme}_ff66ac.css", encoding='utf-8').read()
	for color in ['805ad5','62ca56','38a169','80ffff','2a96f3','62ca56','eb4963','ff0000','f39731','30409f','3e98a7','e4432d','7b9ae4','ec72de','7f8fa6', 'f8db58']:
		newtext = text.replace("ff66ac", color).replace("ff4097", color)
		open(f"D:/#D/ruqqus/assets/style/{theme}_{color}.css", encoding='utf-8', mode='w').write(newtext)