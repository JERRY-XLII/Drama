git pull
sass D:/#D/ruqqus/assets/style/dark.scss D:/#D/ruqqus/assets/style/dark_ff66ac.css
sass D:/#D/ruqqus/assets/style/light.scss D:/#D/ruqqus/assets/style/light_ff66ac.css
sass D:/#D/ruqqus/assets/style/coffee.scss D:/#D/ruqqus/assets/style/coffee_ff66ac.css
sass D:/#D/ruqqus/assets/style/tron.scss D:/#D/ruqqus/assets/style/tron_ff66ac.css
python3 ./compilecss.py
git add .
git commit -m "" --allow-empty-message
git push