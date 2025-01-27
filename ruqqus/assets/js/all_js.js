// Using mouse

document.body.addEventListener('mousedown', function() {
	document.body.classList.add('using-mouse');
});

document.body.addEventListener('keydown', function(event) {
	if (event.keyCode === 9) {
		document.body.classList.remove('using-mouse');
	}
});

// 2FA toggle modal

$('#2faModal').on('hidden.bs.modal', function () {

	var box = document.getElementById("2faToggle");
	
	box.checked = !box.checked;

});

//email change

// Show confirm password field when user clicks email box

$('#new_email').on('input', function () {

	var id = document.getElementById("email-password");
	var id2 = document.getElementById("email-password-label");
	var id3 = document.getElementById("emailpasswordRequired");

	id.classList.remove("d-none");
	id2.classList.remove("d-none");
	id3.classList.remove("d-none");

});

//GIFS

	// Identify which comment form to insert GIF into

	var commentFormID;

	function commentForm(form) {
		commentFormID = form;
	};


	// Insert EMOJI markdown into comment box function

	function getEmoji(searchTerm, form) {

		var emoji = ' :'+searchTerm+': '
			
		var commentBox = document.getElementById(form);

		var old	= commentBox.value;

		commentBox.value = old + emoji;

	}

	function loadEmojis(form) {

		const emojis = [
		{
			type:'platy',
			emojis: ['platyblush','platybruh','platycaveman','platycheer','platydown','platyeyes','platyheart','platylol','platymicdrop','platynooo','platysalute','platyseethe','platythumbsup','platywave']
		},
		{
			type:'marsey',
			emojis: ['marseysipping', 'marseyjamming','marseyangel','marseyblowkiss','marseycry','marseydead','marseyexcited','marseygift','marseyinabox','marseylaugh','marseylove','marseymad','marseyparty','marseyrain','marseyreading','marseyready','marseysad','marseyscarf','marseyshook','marseysleep','marseythumbsup','marseywave', 'marsey69', 'marseycomrade', 'marseyira', 'marseyisis', 'marseymerchant', 'marseynut', 'marseyreich', 'marseyglam', 'marseycowboy', 'marseypat', 'marseypanties', 'marseybingus', 'marseydepressed', 'marseygift']
		},
		{
			type:'tay',
			emojis: ['tayaaa','tayadmire','taycat','taycelebrate','taychefkiss','taychristmas','tayclap','taycold','taycrown','tayflex','tayflirt','taygrimacing','tayhappy','tayheart','tayhmm','tayhuh','tayhyperdab','tayjammin','taylaugh','taymindblown','tayno','taynod','taypeace','taypray','tayrun','tayscrunch','tayshake','tayshrug','taysilly','tayslide','taysmart','taystop','taytantrum','taytea','taythink','tayvibin','taywhat','taywine','taywine2','taywink','tayyes']
		},
		{
			type:'classic',
			emojis: ['2thumbsup','aliendj','ambulance','angry','angrywhip','argue','aroused','ashamed','badass','banana','band','banghead','batman','bigeyes','bite','blind','blowkiss','blush','bong','bounce','bow','breakheart','bs','cartwheel','cat','celebrate','chainsaw','cheers','clap','cold','confused','crazyeyes','cry','cthulhu','cute','D','daydream','ddr','deadpool','devilsmile','diddle','die','distress','disturbing','dizzy','domo','doughboy','drink','drool','dudeweedlmao','edward','electro','elephant','embarrassed','emo','emo2','evil','evilclown','evilgrin','facepalm','fap','flamethrower','flipbird','flirt','frown','gasp','glomp','go','gooby','grr','gtfo','guitar','haha','handshake','happydance','headbang','heart','heartbeat','hearts','highfive','hmm','hmph','holdhands','horny','hug','hugging','hugs','hump','humpbed','hysterical','ily','inlove','jason','jawdrop','jedi','jester','kaboom','kick','kiss','kitty','laughchair','lick','link','lol','lolbeat','loving','makeout','medal','megaman','megamanguitar','meow','metime','mooning','mummy','na','nauseous','nervous','ninja','nod','nono','omg','onfire','ooo','orly','p','paddle','panda','pandabutt','paranoid','party','pat','peek','pikachu','pimp','plzdie','poke','popcorn','pout','probe','puke','punch','quote','raccoon','roar','rofl','roflmao','rolleyes','sad','sadeyes','sadhug','samurai','sarcasm','scoot','scream','shmoopy','shrug','skull','slap','slapfight','sleepy','smackfish','smackhead','smh','smile','smoke','sonic','spank','sparta','sperm','spiderman','stab','star','stare','stfu','suicide','surprisehug','suspicious','sweat','swordfight','taco','talk2hand','tantrum','teehee','thinking','threesome','throw','throwaway','tickle','typing','uhuh','vampbat','viking','violin','vulgar','wah','wat','whip','whipping','wink','witch','wizard','woah','woo','work','worship','wow','XD','yay','zzz']
		},
		{
			type:'rage',
			emojis: ['bitchplease','cerealguypart2','challengeaccepted','contentiouscereal','cryingatcuteness','derp','derpcornsyrup','derpcrying','derpcute','derpdumb','derpeuphoria','derpinahd','derpinapokerface','derpinasnickering','derpprocessing','derprealization','derpsnickering','derptalking','derpthinking','derpthumbsup','derpunimpressed','derpwhy','donotwant','epicfacefeatures','fancywithwine','fffffffuuuuuuuuuuuu','flipthetable','foreveralone','foreveralonehappy','hewillnever','idontknow','interuptedreading','iseewhatyoudidthere','killherkillher','ledesire','leexcited','legenius','lelolidk','lemiddlefinger','lemindblown','leokay','lepanicrunning','lepokerface','lepokerface2','lerageface','leseriousface','likeaboss','lolface','longwhiskers','manymiddlefingers','megusta','motherfucker','motherofgod','mysides','ohgodwhy','pervertedspiderman','picard','ragestrangle','rukiddingme','tfwyougettrolled','trollolol','truestorybro','xallthey','yuno']
		},
		{
			type:'wojak',
			emojis: ['abusivewife','ancap','bardfinn','bloomer','boomer','boomermonster','brainletbush','brainletcaved','brainletchair','brainletchest','brainletmaga','brainletpit','chad','chadarab','chadasian','chadblack','chadjesus','chadjew','chadjihadi','chadlatino','chadlibleft','chadnordic','chadsikh','chadusa','coomer','doomer','doomerfront','doomergirl','ethot','fatbrain','fatpriest','femboy','gogetter','grug','monke','nazijak','npc','npcfront','npcmaga','psychojak','ragejak','ragemask','ramonajak','soyjackwow','soyjak','soyjakfront','soyjakhipster','soyjakmaga','soyjakyell','tomboy','zoomer','zoomersoy']
		},
		{
			type:'flags',
			emojis: ['animesexual','blacknation','blm','blueline','dreamgender','fatpride','incelpride','israel','landlordlove','scalperpride','superstraight','trans','translord','transracial','usa']
		}
		]

		for (i=0; i < emojis.length; i++) {

			let container = document.getElementById(`EMOJIS_${emojis[i].type}`)
			let str = ''
			let arr = emojis[i].emojis

			for (j=0; j < arr.length; j++) { 
				str += `<button class="btn m-1 px-0" onclick="getEmoji(\'${arr[j]}\', \'${form}\')" style="width:40px; overflow: hidden; border: none;" data-toggle="tooltip" title=":${arr[j]}:" delay:="0"><img width=30 src="/assets/images/emojis/${arr[j]}.gif" alt="${arr[j]}-emoji"/></button>`;
			}

			container.innerHTML = str
		}
	}


	function getGif(searchTerm) {

		if (searchTerm !== undefined) {
			document.getElementById('gifSearch').value = searchTerm;
		}
		else {
			document.getElementById('gifSearch').value = null;
		}

			// load more gifs div
			var loadGIFs = document.getElementById('gifs-load-more');

			// error message div
			var noGIFs = document.getElementById('no-gifs-found');

			// categories div
			var cats = document.getElementById('GIFcats');

			// container div
			var container = document.getElementById('GIFs');

			// modal body div
			var modalBody = document.getElementById('gif-modal-body')

			// UI buttons
			var backBtn = document.getElementById('gifs-back-btn');
			var cancelBtn = document.getElementById('gifs-cancel-btn');

			container.innerHTML = '';

			if (searchTerm == undefined) {
				container.innerHTML = '<div class="card" onclick="getGif(\'agree\');" style="overflow: hidden;"> <div class="gif-cat-overlay"> <div style="position: relative;top: 50%;transform: translateY(-50%);color: #ffffff;font-weight: bold;">Agree</div> </div> <img class="img-fluid" src="https://media.giphy.com/media/wGhYz3FHaRJgk/200w_d.gif"> </div> <div class="card" onclick="getGif(\'laugh\');" style="overflow: hidden;"> <div class="gif-cat-overlay"> <div style="position: relative;top: 50%;transform: translateY(-50%);color: #ffffff;font-weight: bold;">Laugh</div> </div> <img class="img-fluid" src="https://media.giphy.com/media/O5NyCibf93upy/200w_d.gif"> </div> <div class="card" onclick="getGif(\'confused\');" style="overflow: hidden;"> <div class="gif-cat-overlay"> <div style="position: relative;top: 50%;transform: translateY(-50%);color: #ffffff;font-weight: bold;">Confused</div> </div> <img class="img-fluid" src="https://media.giphy.com/media/3o7btPCcdNniyf0ArS/200w_d.gif"> </div> <div class="card" onclick="getGif(\'sad\');" style="overflow: hidden;"> <div class="gif-cat-overlay"> <div style="position: relative;top: 50%;transform: translateY(-50%);color: #ffffff;font-weight: bold;">Sad</div> </div> <img class="img-fluid" src="https://media.giphy.com/media/ISOckXUybVfQ4/200w_d.gif"> </div> <div class="card" onclick="getGif(\'happy\');" style="overflow: hidden;"> <div class="gif-cat-overlay"> <div style="position: relative;top: 50%;transform: translateY(-50%);color: #ffffff;font-weight: bold;">Happy</div> </div> <img class="img-fluid" src="https://media.giphy.com/media/XR9Dp54ZC4dji/200w_d.gif"> </div> <div class="card" onclick="getGif(\'awesome\');" style="overflow: hidden;"> <div class="gif-cat-overlay"> <div style="position: relative;top: 50%;transform: translateY(-50%);color: #ffffff;font-weight: bold;">Awesome</div> </div> <img class="img-fluid" src="https://media.giphy.com/media/3ohzdIuqJoo8QdKlnW/200w_d.gif"> </div> <div class="card" onclick="getGif(\'yes\');" style="overflow: hidden;"> <div class="gif-cat-overlay"> <div style="position: relative;top: 50%;transform: translateY(-50%);color: #ffffff;font-weight: bold;">Yes</div> </div> <img class="img-fluid" src="https://media.giphy.com/media/J336VCs1JC42zGRhjH/200w_d.gif"> </div> <div class="card" onclick="getGif(\'no\');" style="overflow: hidden;"> <div class="gif-cat-overlay"> <div style="position: relative;top: 50%;transform: translateY(-50%);color: #ffffff;font-weight: bold;">No</div> </div> <img class="img-fluid" src="https://media.giphy.com/media/1zSz5MVw4zKg0/200w_d.gif"> </div> <div class="card" onclick="getGif(\'love\');" style="overflow: hidden;"> <div class="gif-cat-overlay"> <div style="position: relative;top: 50%;transform: translateY(-50%);color: #ffffff;font-weight: bold;">Love</div> </div> <img class="img-fluid" src="https://media.giphy.com/media/4N1wOi78ZGzSB6H7vK/200w_d.gif"> </div> <div class="card" onclick="getGif(\'please\');" style="overflow: hidden;"> <div class="gif-cat-overlay"> <div style="position: relative;top: 50%;transform: translateY(-50%);color: #ffffff;font-weight: bold;">Please</div> </div> <img class="img-fluid" src="https://media.giphy.com/media/qUIm5wu6LAAog/200w_d.gif"> </div> <div class="card" onclick="getGif(\'scared\');" style="overflow: hidden;"> <div class="gif-cat-overlay"> <div style="position: relative;top: 50%;transform: translateY(-50%);color: #ffffff;font-weight: bold;">Scared</div> </div> <img class="img-fluid" src="https://media.giphy.com/media/bEVKYB487Lqxy/200w_d.gif"> </div> <div class="card" onclick="getGif(\'angry\');" style="overflow: hidden;"> <div class="gif-cat-overlay"> <div style="position: relative;top: 50%;transform: translateY(-50%);color: #ffffff;font-weight: bold;">Angry</div> </div> <img class="img-fluid" src="https://media.giphy.com/media/12Pb87uq0Vwq2c/200w_d.gif"> </div> <div class="card" onclick="getGif(\'awkward\');" style="overflow: hidden;"> <div class="gif-cat-overlay"> <div style="position: relative;top: 50%;transform: translateY(-50%);color: #ffffff;font-weight: bold;">Awkward</div> </div> <img class="img-fluid" src="https://media.giphy.com/media/unFLKoAV3TkXe/200w_d.gif"> </div> <div class="card" onclick="getGif(\'cringe\');" style="overflow: hidden;"> <div class="gif-cat-overlay"> <div style="position: relative;top: 50%;transform: translateY(-50%);color: #ffffff;font-weight: bold;">Cringe</div> </div> <img class="img-fluid" src="https://media.giphy.com/media/1jDvQyhGd3L2g/200w_d.gif"> </div> <div class="card" onclick="getGif(\'omg\');" style="overflow: hidden;"> <div class="gif-cat-overlay"> <div style="position: relative;top: 50%;transform: translateY(-50%);color: #ffffff;font-weight: bold;">OMG</div> </div> <img class="img-fluid" src="https://media.giphy.com/media/3o72F8t9TDi2xVnxOE/200w_d.gif"> </div> <div class="card" onclick="getGif(\'why\');" style="overflow: hidden;"> <div class="gif-cat-overlay"> <div style="position: relative;top: 50%;transform: translateY(-50%);color: #ffffff;font-weight: bold;">Why</div> </div> <img class="img-fluid" src="https://media.giphy.com/media/1M9fmo1WAFVK0/200w_d.gif"> </div> <div class="card" onclick="getGif(\'gross\');" style="overflow: hidden;"> <div class="gif-cat-overlay"> <div style="position: relative;top: 50%;transform: translateY(-50%);color: #ffffff;font-weight: bold;">Gross</div> </div> <img class="img-fluid" src="https://media.giphy.com/media/pVAMI8QYM42n6/200w_d.gif"> </div> <div class="card" onclick="getGif(\'meh\');" style="overflow: hidden;"> <div class="gif-cat-overlay"> <div style="position: relative;top: 50%;transform: translateY(-50%);color: #ffffff;font-weight: bold;">Meh</div> </div> <img class="img-fluid" src="https://media.giphy.com/media/xT77XTpyEzJ4OJO06c/200w_d.gif"> </div>'
				backBtn.innerHTML = null;
				cancelBtn.innerHTML = null;
				noGIFs.innerHTML = null;
				loadGIFs.innerHTML = null;
			} else {
				backBtn.innerHTML = '<button class="btn btn-link pl-0 pr-3" id="gifs-back-btn" onclick="getGif();"><i class="fas fa-long-arrow-left text-muted"></i></button>';

				cancelBtn.innerHTML = '<button class="btn btn-link pl-3 pr-0" id="gifs-cancel-btn" onclick="getGif();"><i class="fas fa-times text-muted"></i></button>';

				let gifs = [];
				let apiKey = tenor_api_key();
				let lmt = 25;
				let url = "https://g.tenor.com/v1/search/?q=" + searchTerm + "&key=" + apiKey + "&limit=" + lmt;
				fetch(url)
				.then(response => {
					return response.json();
				})
				.then(json => {
					let results = json.results.map(function(obj) {
						return {
							id: obj.id,
							preview: obj.media[0].tinygif.url,
							url: obj.media[0].gif.url,
							source: obj.url,
							bgColor: obj.bg_color
						}
					});
					
					gifs = results

					// loop for fetching mutliple GIFs and creating the card divs
					if (gifs.length) {
						for (var i = 0; i < gifs.length; i++) {
							container.innerHTML += ('<div class="card bg-white" style="overflow: hidden" data-dismiss="modal" aria-label="Close" onclick="insertGIF(\'' + gifs[i].url + '\',\'' + commentFormID + '\')"><div class="gif-cat-overlay"></div><img class="img-fluid" src="' + gifs[i].preview + '"></div>');
							noGIFs.innerHTML = null;
							loadGIFs.innerHTML = '<div class="text-center py-3"><div class="mb-3"><i class="fad fa-grin-beam-sweat text-gray-500" style="font-size: 3.5rem;"></i></div><p class="font-weight-bold text-gray-500 mb-0">Thou&#39;ve reached the end of the list!</p></div>';
						}
					} else {
						noGIFs.innerHTML = '<div class="text-center py-3 mt-3"><div class="mb-3"><i class="fad fa-frown text-gray-500" style="font-size: 3.5rem;"></i></div><p class="font-weight-bold text-gray-500 mb-0">Aw shucks. No GIFs found...</p></div>';
						container.innerHTML = null;
						loadGIFs.innerHTML = null;
					}
				})
				.catch(err => alert(err));
			};
		}
	// Insert GIF markdown into comment box function

	function insertGIF(url,form) {

		var gif = "![](" + url +")";

		var commentBox = document.getElementById(form);

		var old	= commentBox.value;

		commentBox.value = old + gif;

	}

	// When GIF keyboard is hidden, hide all GIFs

	$('#gifModal').on('hidden.bs.modal', function (e) {

		document.getElementById('gifSearch').value = null;

		// load more gifs div

		var loadGIFs = document.getElementById('gifs-load-more');

		// no GIFs div

		var noGIFs = document.getElementById('no-gifs-found');

		// container div

		var container = document.getElementById('GIFs');

		// UI buttons

		var backBtn = document.getElementById('gifs-back-btn');

		var cancelBtn = document.getElementById('gifs-cancel-btn');

		// Remove inner HTML from container var

		container.innerHTML = '<div class="card" onclick="getGif(\'agree\');" style="overflow: hidden;"> <div class="gif-cat-overlay"> <div style="position: relative;top: 50%;transform: translateY(-50%);color: #cfcfcf;font-weight: bold;">Agree</div> </div> <img class="img-fluid" src="https://media.giphy.com/media/wGhYz3FHaRJgk/200w_d.gif"> </div> <div class="card" onclick="getGif(\'laugh\');" style="overflow: hidden;"> <div class="gif-cat-overlay"> <div style="position: relative;top: 50%;transform: translateY(-50%);color: #cfcfcf;font-weight: bold;">Laugh</div> </div> <img class="img-fluid" src="https://media.giphy.com/media/O5NyCibf93upy/200w_d.gif"> </div> <div class="card" onclick="getGif(\'confused\');" style="overflow: hidden;"> <div class="gif-cat-overlay"> <div style="position: relative;top: 50%;transform: translateY(-50%);color: #cfcfcf;font-weight: bold;">Confused</div> </div> <img class="img-fluid" src="https://media.giphy.com/media/3o7btPCcdNniyf0ArS/200w_d.gif"> </div> <div class="card" onclick="getGif(\'sad\');" style="overflow: hidden;"> <div class="gif-cat-overlay"> <div style="position: relative;top: 50%;transform: translateY(-50%);color: #cfcfcf;font-weight: bold;">Sad</div> </div> <img class="img-fluid" src="https://media.giphy.com/media/ISOckXUybVfQ4/200w_d.gif"> </div> <div class="card" onclick="getGif(\'happy\');" style="overflow: hidden;"> <div class="gif-cat-overlay"> <div style="position: relative;top: 50%;transform: translateY(-50%);color: #cfcfcf;font-weight: bold;">Happy</div> </div> <img class="img-fluid" src="https://media.giphy.com/media/XR9Dp54ZC4dji/200w_d.gif"> </div> <div class="card" onclick="getGif(\'awesome\');" style="overflow: hidden;"> <div class="gif-cat-overlay"> <div style="position: relative;top: 50%;transform: translateY(-50%);color: #cfcfcf;font-weight: bold;">Awesome</div> </div> <img class="img-fluid" src="https://media.giphy.com/media/3ohzdIuqJoo8QdKlnW/200w_d.gif"> </div> <div class="card" onclick="getGif(\'yes\');" style="overflow: hidden;"> <div class="gif-cat-overlay"> <div style="position: relative;top: 50%;transform: translateY(-50%);color: #cfcfcf;font-weight: bold;">Yes</div> </div> <img class="img-fluid" src="https://media.giphy.com/media/J336VCs1JC42zGRhjH/200w_d.gif"> </div> <div class="card" onclick="getGif(\'no\');" style="overflow: hidden;"> <div class="gif-cat-overlay"> <div style="position: relative;top: 50%;transform: translateY(-50%);color: #cfcfcf;font-weight: bold;">No</div> </div> <img class="img-fluid" src="https://media.giphy.com/media/1zSz5MVw4zKg0/200w_d.gif"> </div> <div class="card" onclick="getGif(\'love\');" style="overflow: hidden;"> <div class="gif-cat-overlay"> <div style="position: relative;top: 50%;transform: translateY(-50%);color: #cfcfcf;font-weight: bold;">Love</div> </div> <img class="img-fluid" src="https://media.giphy.com/media/4N1wOi78ZGzSB6H7vK/200w_d.gif"> </div> <div class="card" onclick="getGif(\'please\');" style="overflow: hidden;"> <div class="gif-cat-overlay"> <div style="position: relative;top: 50%;transform: translateY(-50%);color: #cfcfcf;font-weight: bold;">Please</div> </div> <img class="img-fluid" src="https://media.giphy.com/media/qUIm5wu6LAAog/200w_d.gif"> </div> <div class="card" onclick="getGif(\'scared\');" style="overflow: hidden;"> <div class="gif-cat-overlay"> <div style="position: relative;top: 50%;transform: translateY(-50%);color: #cfcfcf;font-weight: bold;">Scared</div> </div> <img class="img-fluid" src="https://media.giphy.com/media/bEVKYB487Lqxy/200w_d.gif"> </div> <div class="card" onclick="getGif(\'angry\');" style="overflow: hidden;"> <div class="gif-cat-overlay"> <div style="position: relative;top: 50%;transform: translateY(-50%);color: #cfcfcf;font-weight: bold;">Angry</div> </div> <img class="img-fluid" src="https://media.giphy.com/media/12Pb87uq0Vwq2c/200w_d.gif"> </div> <div class="card" onclick="getGif(\'awkward\');" style="overflow: hidden;"> <div class="gif-cat-overlay"> <div style="position: relative;top: 50%;transform: translateY(-50%);color: #cfcfcf;font-weight: bold;">Awkward</div> </div> <img class="img-fluid" src="https://media.giphy.com/media/unFLKoAV3TkXe/200w_d.gif"> </div> <div class="card" onclick="getGif(\'cringe\');" style="overflow: hidden;"> <div class="gif-cat-overlay"> <div style="position: relative;top: 50%;transform: translateY(-50%);color: #cfcfcf;font-weight: bold;">Cringe</div> </div> <img class="img-fluid" src="https://media.giphy.com/media/1jDvQyhGd3L2g/200w_d.gif"> </div> <div class="card" onclick="getGif(\'omg\');" style="overflow: hidden;"> <div class="gif-cat-overlay"> <div style="position: relative;top: 50%;transform: translateY(-50%);color: #cfcfcf;font-weight: bold;">OMG</div> </div> <img class="img-fluid" src="https://media.giphy.com/media/3o72F8t9TDi2xVnxOE/200w_d.gif"> </div> <div class="card" onclick="getGif(\'why\');" style="overflow: hidden;"> <div class="gif-cat-overlay"> <div style="position: relative;top: 50%;transform: translateY(-50%);color: #cfcfcf;font-weight: bold;">Why</div> </div> <img class="img-fluid" src="https://media.giphy.com/media/1M9fmo1WAFVK0/200w_d.gif"> </div> <div class="card" onclick="getGif(\'gross\');" style="overflow: hidden;"> <div class="gif-cat-overlay"> <div style="position: relative;top: 50%;transform: translateY(-50%);color: #cfcfcf;font-weight: bold;">Gross</div> </div> <img class="img-fluid" src="https://media.giphy.com/media/pVAMI8QYM42n6/200w_d.gif"> </div> <div class="card" onclick="getGif(\'meh\');" style="overflow: hidden;"> <div class="gif-cat-overlay"> <div style="position: relative;top: 50%;transform: translateY(-50%);color: #cfcfcf;font-weight: bold;">Meh</div> </div> <img class="img-fluid" src="https://media.giphy.com/media/xT77XTpyEzJ4OJO06c/200w_d.gif"> </div>'

		// Hide UI buttons

		backBtn.innerHTML = null;

		cancelBtn.innerHTML = null;

		// Remove inner HTML from no gifs div

		noGIFs.innerHTML = null;

		// Hide no more gifs div

		loadGIFs.innerHTML = null;

	});

// comment collapse

// Toggle comment collapse

function collapse_comment(comment_id) {

	var comment = "comment-" + comment_id;

	document.getElementById(comment).classList.toggle("collapsed");

};

//Commenting form

// Expand comment box on focus, hide otherwise

$('.comment-box').focus(function (event) {
	event.preventDefault();

	$(this).parent().parent().addClass("collapsed");

});

// Comment edit form

toggleEdit=function(id){
	comment=document.getElementById("comment-text-"+id);
	form=document.getElementById("comment-edit-"+id);
	box=document.getElementById('edit-box-comment-'+id);
	actions = document.getElementById('comment-' + id +'-actions');

	comment.classList.toggle("d-none");
	form.classList.toggle("d-none");
	actions.classList.toggle("d-none");
	autoExpand(box);
};

// Post edit form

togglePostEdit=function(id){

	body=document.getElementById("post-body");
	title=document.getElementById("post-title");
	form=document.getElementById("edit-post-body-"+id);
	box=document.getElementById("post-edit-box-"+id);
	box2=document.getElementById("post-edit-box2-"+id);

	body.classList.toggle("d-none");
	title.classList.toggle("d-none");
	form.classList.toggle("d-none");
	autoExpand(box);
	autoExpand(box2);
};

//comment modding
function removeComment(post_id) {
	url="/api/ban_comment/"+post_id

	callback=function(){
		document.getElementById("comment-"+post_id+"-only").classList.add("banned");

		button=document.getElementById("moderate-"+post_id);
		button.onclick=function(){approveComment(post_id)};
		button.innerHTML='<i class="fas fa-clipboard-check"></i>Approve'
	}
	post(url, callback, "Comment has been removed.")
};

function approveComment(post_id) {
	url="/api/unban_comment/"+post_id

	callback=function(){
		document.getElementById("comment-"+post_id+"-only").classList.remove("banned");

		button=document.getElementById("moderate-"+post_id);
		button.onclick=function(){removeComment(post_id)};
		button.innerHTML='<i class="fas fa-trash-alt"></i>Remove'
	}

	post(url, callback, "Comment has been approved.")
}

admin_comment=function(cid){


	var xhr = new XMLHttpRequest();
	xhr.open("post", "/api/distinguish_comment/"+cid);

	var form = new FormData();

	form.append('formkey', formkey());

	xhr.withCredentials=true;
	xhr.onload=function(){
		if (xhr.status==200) {
			comment=document.getElementById('comment-'+cid+'-only');
			comment.innerHTML=JSON.parse(xhr.response)["html"];
		}
		else {
			var commentError = document.getElementById("comment-error-text");
			$('#toast-comment-success').toast('dispose');
			$('#toast-comment-error').toast('dispose');
			$('#toast-comment-error').toast('show');
			commentError.textContent = JSON.parse(xhr.response)["error"];
		}
	}
	xhr.send(form)
}

//Autoexpand textedit comments

function autoExpand (field) {

	//get current scroll position
	xpos=window.scrollX;
	ypos=window.scrollY;

	// Reset field height
	field.style.height = 'inherit';

	// Get the computed styles for the element
	var computed = window.getComputedStyle(field);

	// Calculate the height
	var height = parseInt(computed.getPropertyValue('border-top-width'), 10)
	+ parseInt(computed.getPropertyValue('padding-top'), 10)
	+ field.scrollHeight
	+ parseInt(computed.getPropertyValue('padding-bottom'), 10)
	+ parseInt(computed.getPropertyValue('border-bottom-width'), 10)
	+ 32;

	field.style.height = height + 'px';

	//keep window position from changing
	window.scrollTo(xpos,ypos);

};

document.addEventListener('input', function (event) {
	if (event.target.tagName.toLowerCase() !== 'textarea') return;
	autoExpand(event.target);
}, false);

// Delete Post

function delete_postModal(id) {

	// Passed data for modal

	document.getElementById("deletePostButton-mobile").addEventListener("click", delete_post);

	document.getElementById("deletePostButton").addEventListener("click", delete_post);

	function delete_post(){	

		this.innerHTML='<span class="spinner-border spinner-border-sm mr-2" role="status" aria-hidden="true"></span>Deleting post';	
		this.disabled = true; 
		post('/delete_post/' + id,
			callback = function() {

				location.reload();
			}
			)
	}

};

// Delete Comment

function delete_commentModal(id) {

	// Passed data for modal

	document.getElementById("deleteCommentButton").onclick = function() {	

		this.innerHTML='<span class="spinner-border spinner-border-sm mr-2" role="status" aria-hidden="true"></span>Deleting comment';	
		this.disabled = true; 
		post('/delete/comment/' + id,
			callback = function() {

				location.reload();
			}
			)
	}

};

//Email verification text

function emailVerifyText() {

	document.getElementById("email-verify-text").innerHTML = "Verification email sent! Please check your inbox.";

}

//flagging
// Flag Comment

report_commentModal = function(id, author) {

	document.getElementById("comment-author").textContent = author;

	//offtopic.disabled=true;

	document.getElementById("reportCommentButton").onclick = function() {

		this.innerHTML='<span class="spinner-border spinner-border-sm mr-2" role="status" aria-hidden="true"></span>Reporting comment';
		this.disabled = true;
		post('/api/flag/comment/' + id,
			callback = function() {

				document.getElementById("reportCommentFormBefore").classList.add('d-none');
				document.getElementById("reportCommentFormAfter").classList.remove('d-none');
			}
			)
	}

};

$('#reportCommentModal').on('hidden.bs.modal', function () {

	var button = document.getElementById("reportCommentButton");

	var beforeModal = document.getElementById("reportCommentFormBefore");
	var afterModal = document.getElementById("reportCommentFormAfter");

	button.innerHTML='Report comment';
	button.disabled= false;
	afterModal.classList.add('d-none');

	if ( beforeModal.classList.contains('d-none') ) {
		beforeModal.classList.remove('d-none');
	}

});


// Flag Submission

report_postModal = function(id, author, board) {

	document.getElementById("post-author").textContent = author;

	selectbox=document.getElementById('report-type-dropdown');
	selectbox.value='reason_not_selected';

	submitbutton=document.getElementById("reportPostButton");
	submitbutton.disabled=true;

	submitbutton.onclick = function() {

		this.innerHTML='<span class="spinner-border spinner-border-sm mr-2" role="status" aria-hidden="true"></span>Reporting post';
		this.disabled = true;

		var xhr = new XMLHttpRequest();
		xhr.open("POST", '/api/flag/post/'+id, true);
		var form = new FormData()
		form.append("formkey", formkey());

		dropdown=document.getElementById("report-type-dropdown");
		form.append("report_type", dropdown.options[dropdown.selectedIndex].value);

		xhr.withCredentials=true;

		xhr.onload=function() {
			document.getElementById("reportPostFormBefore").classList.add('d-none');
			document.getElementById("reportPostFormAfter").classList.remove('d-none');
		};

		xhr.onerror=function(){alert(errortext)};
		xhr.send(form);

	}
};

$('#reportPostModal').on('hidden.bs.modal', function () {

	var button = document.getElementById("reportPostButton");

	var beforeModal = document.getElementById("reportPostFormBefore");
	var afterModal = document.getElementById("reportPostFormAfter");

	button.innerHTML='Report post';
	button.disabled= false;

	afterModal.classList.add('d-none');

	if ( beforeModal.classList.contains('d-none') ) {
		beforeModal.classList.remove('d-none');
	}

});

//enlarge thumbs
// Enlarge submissionlisting thumbnail

enlarge_thumb = function(post_id) {

	document.getElementById(post_id).classList.toggle("enlarged");

};

//iOS webapp stuff

(function(document,navigator,standalone) {
						// prevents links from apps from oppening in mobile safari
						// this javascript must be the first script in your <head>
						if ((standalone in navigator) && navigator[standalone]) {
							var curnode, location=document.location, stop=/^(a|html)$/i;
							document.addEventListener('click', function(e) {
								curnode=e.target;
								while (!(stop).test(curnode.nodeName)) {
									curnode=curnode.parentNode;
								}
										// Condidions to do this only on links to your own app
										// if you want all links, use if('href' in curnode) instead.
										if('href' in curnode && ( curnode.href.indexOf('http') || ~curnode.href.indexOf(location.host) ) ) {
											e.preventDefault();
											location.href = curnode.href;
										}
									},false);
						}
					})(document,window.navigator,'standalone');

//POST

function post(url, callback, errortext) {
	var xhr = new XMLHttpRequest();
	xhr.open("POST", url, true);
	var form = new FormData()
	form.append("formkey", formkey());
	xhr.withCredentials=true;
	xhr.onerror=function() { alert(errortext); };
	xhr.onload = function() {
		if (xhr.status >= 200 && xhr.status < 300) {
			callback();
		} else {
			xhr.onerror();
		}
	};
	xhr.send(form);
};

function post_toast(url, callback) {
	var xhr = new XMLHttpRequest();
	xhr.open("POST", url, true);
	var form = new FormData()
	form.append("formkey", formkey());
	xhr.withCredentials=true;

	xhr.onload = function() {
		if (xhr.status==204) {}
			else if (xhr.status >= 200 && xhr.status < 300) {
				$('#toast-post-success').toast('dispose');
				$('#toast-post-success').toast('show');
				document.getElementById('toast-post-success-text').innerText = JSON.parse(xhr.response)["message"];
				callback(xhr)
				return true

			} else if (xhr.status >= 300 && xhr.status < 400) {
				window.location.href = JSON.parse(xhr.response)["redirect"]
			} else {
				data=JSON.parse(xhr.response);
				
				$('#toast-post-error').toast('dispose');
				$('#toast-post-error').toast('show');
				document.getElementById('toast-post-error-text').innerText = data["error"];
				return false
				
			}
		};

		xhr.send(form);

	}

//Element deleter

function deleteElement(eid) {
	x=document.getElementById(eid)
	x.parentElement.removeChild(x)

}


//Signup js
// Display username and password requirements on input

$('#password-register').on('input', function () {

	var charCount = document.getElementById("password-register").value;
	var id = document.getElementById("passwordHelpRegister");
	var successID = document.getElementById("passwordHelpSuccess");

	if (charCount.length >= 8) {
		id.classList.add("d-none");
		successID.classList.remove("d-none");
	}
	else {
		id.classList.remove("d-none");
		successID.classList.add("d-none");
	};

});

// Check username length, special chars

$('#username-register').on('input', function () {

	var charCount = document.getElementById("username-register").value;
	var id = document.getElementById("usernameHelpRegister");
	var successID = document.getElementById("usernameHelpSuccess");

	var ruqqusAPI = '/api/is_available/' + charCount;

	if (charCount.length >= 3) {

		$.getJSON(ruqqusAPI, function(result) {
			$.each(result, function(i, field) {
				if (field == false) {
					id.innerHTML = '<span class="form-text font-weight-bold text-danger mt-1">Username already taken :(';
				}
			});
		});

	}

	if (!/[^a-zA-Z0-9_\-$]/.test(charCount)) {
		// Change alert text
		id.innerHTML = '<span class="form-text font-weight-bold text-success mt-1">Username is a-okay!';

		if (charCount.length < 3) {
			id.innerHTML = '<span class="form-text font-weight-bold text-muted mt-1">Username must be at least 3 characters long.';
		}
		else if (charCount.length > 25) {
			id.innerHTML = '<span class="form-text font-weight-bold text-danger mt-1">Username must be 25 characters or less.';
		}
	}
	else {
		id.innerHTML = '<span class="form-text font-weight-bold text-danger mt-1">No special characters or spaces allowed.</span>';
	};

});

// Search Icon
// Change navbar search icon when form is in focus, active states

$(".form-control").focus(function () {
	$(this).prev('.input-group-append').removeClass().addClass('input-group-append-focus');
	$(this).next('.input-group-append').removeClass().addClass('input-group-append-focus');
});

$(".form-control").focusout(function () {
	$(this).prev('.input-group-append-focus').removeClass().addClass('input-group-append');
	$(this).next('.input-group-append-focus').removeClass().addClass('input-group-append');
});

//spinner effect

$(document).ready(function() {
	$('#login').submit(function() {
			// disable button
			$("#login_button").prop("disabled", true);
			// add spinner to button
			$("#login_button").html('<span class="spinner-border spinner-border-sm mr-2" role="status" aria-hidden="true"></span>Signing in');
		});
});

$(document).ready(function() {
	$('#signup').submit(function() {
			// disable button
			$("#register_button").prop("disabled", true);
			// add spinner to button
			$("#register_button").html('<span class="spinner-border spinner-border-sm mr-2" role="status" aria-hidden="true"></span>Registering');
		});
});

$(document).ready(function() {
	$('#submitform').submit(function() {
			// disable button
			$("#create_button").prop("disabled", true);
			// add spinner to button
			$("#create_button").html('<span class="spinner-border spinner-border-sm mr-2" role="status" aria-hidden="true"></span>Creating post');
		});
});

// Voting

var upvote = function(event) {

	var type = event.target.dataset.contentType;
	var id = event.target.dataset.idUp;

	var downvoteButton = document.getElementsByClassName(type + '-' + id + '-down');
	var upvoteButton = document.getElementsByClassName(type + '-' + id + '-up');
	var scoreText = document.getElementsByClassName(type + '-score-' + id);

	for (var j = 0; j < upvoteButton.length && j < downvoteButton.length && j < scoreText.length; j++) {

		var thisUpvoteButton = upvoteButton[j];
		var thisDownvoteButton = downvoteButton[j];
		var thisScoreText = scoreText[j];
		var thisScore = Number(thisScoreText.textContent);

		if (thisUpvoteButton.classList.contains('active')) {
			thisUpvoteButton.classList.remove('active')
			thisScoreText.textContent = thisScore - 1
			voteDirection = "0"
		} else if (thisDownvoteButton.classList.contains('active')) {
			thisUpvoteButton.classList.add('active')
			thisDownvoteButton.classList.remove('active')
			thisScoreText.textContent = thisScore + 2
			voteDirection = "1"
		} else {
			thisUpvoteButton.classList.add('active')
			thisScoreText.textContent = thisScore + 1
			voteDirection = "1"
		}

		if (thisUpvoteButton.classList.contains('active')) {
			thisScoreText.classList.add('score-up')
			thisScoreText.classList.remove('score-down')
			thisScoreText.classList.remove('score')
		} else if (thisDownvoteButton.classList.contains('active')) {
			thisScoreText.classList.add('score-down')
			thisScoreText.classList.remove('score-up')
			thisScoreText.classList.remove('score')
		} else {
			thisScoreText.classList.add('score')
			thisScoreText.classList.remove('score-up')
			thisScoreText.classList.remove('score-down')
		}
	}

	post_toast("/api/vote/" + type + "/" + id + "/" + voteDirection);
	
}

var downvote = function(event) {

	var type = event.target.dataset.contentType;
	var id = event.target.dataset.idDown;

	var downvoteButton = document.getElementsByClassName(type + '-' + id + '-down');
	var upvoteButton = document.getElementsByClassName(type + '-' + id + '-up');
	var scoreText = document.getElementsByClassName(type + '-score-' + id);

	for (var j = 0; j < upvoteButton.length && j < downvoteButton.length && j < scoreText.length; j++) {

		var thisUpvoteButton = upvoteButton[j];
		var thisDownvoteButton = downvoteButton[j];
		var thisScoreText = scoreText[j];
		var thisScore = Number(thisScoreText.textContent);

		if (thisDownvoteButton.classList.contains('active')) {
			thisDownvoteButton.classList.remove('active')
			thisScoreText.textContent = thisScore + 1
			voteDirection = "0"
		} else if (thisUpvoteButton.classList.contains('active')) {
			thisDownvoteButton.classList.add('active')
			thisUpvoteButton.classList.remove('active')
			thisScoreText.textContent = thisScore - 2
			voteDirection = "-1"
		} else {
			thisDownvoteButton.classList.add('active')
			thisScoreText.textContent = thisScore - 1
			voteDirection = "-1"
		}

		if (thisUpvoteButton.classList.contains('active')) {
			thisScoreText.classList.add('score-up')
			thisScoreText.classList.remove('score-down')
			thisScoreText.classList.remove('score')
		} else if (thisDownvoteButton.classList.contains('active')) {
			thisScoreText.classList.add('score-down')
			thisScoreText.classList.remove('score-up')
			thisScoreText.classList.remove('score')
		} else {
			thisScoreText.classList.add('score')
			thisScoreText.classList.remove('score-up')
			thisScoreText.classList.remove('score-down')
		}
	}

	post_toast("/api/vote/" + type + "/" + id + "/" + voteDirection);
	
}


var register_votes = function() {
	var upvoteButtons = document.getElementsByClassName('upvote-button')

	var downvoteButtons = document.getElementsByClassName('downvote-button')

	var voteDirection = 0

	for (var i = 0; i < upvoteButtons.length; i++) {
		upvoteButtons[i].addEventListener('click', upvote, false);
		upvoteButtons[i].addEventListener('keydown', function(event) {
			if (event.keyCode === 13) {
				upvote(event)
			}
		}, false)
	};

	for (var i = 0; i < downvoteButtons.length; i++) {
		downvoteButtons[i].addEventListener('click', downvote, false);
		downvoteButtons[i].addEventListener('keydown', function(event) {
			if (event.keyCode === 13) {
				downvote(event)
			}
		}, false)
	};
}

register_votes()

function vote_comment(comment_id, direction) {
	url="/api/vote/comment/"+ comment_id +"/"+direction;

	callback=function(){
		thing = document.getElementById("comment-"+ comment_id+"-actions");
		uparrow1=document.getElementById("comment-"+ comment_id +"-up");
		downarrow1=document.getElementById("comment-"+ comment_id +"-down");
		scoreup1=document.getElementById("comment-"+ comment_id +"-score-up");
		scorenone1=document.getElementById("comment-"+ comment_id +"-score-none");
		scoredown1=document.getElementById("comment-"+ comment_id +"-score-down");

		if (direction=="1") {
			thing.classList.add("upvoted");
			thing.classList.remove("downvoted");
			uparrow1.onclick=function(){vote_comment(comment_id, 0)};
			downarrow1.onclick=function(){vote_comment(comment_id, -1)};
			scoreup1.classList.remove("d-none");
			scorenone1.classList.add("d-none");
			scoredown1.classList.add("d-none");
		}
		else if (direction=="-1"){
			thing.classList.remove("upvoted");
			thing.classList.add("downvoted");
			uparrow1.onclick=function(){vote_comment(comment_id, 1)};
			downarrow1.onclick=function(){vote_comment(comment_id, 0)};
			scoreup1.classList.add("d-none");
			scorenone1.classList.add("d-none");
			scoredown1.classList.remove("d-none");
		}
		else if (direction=="0"){
			thing.classList.remove("upvoted");
			thing.classList.remove("downvoted");
			uparrow1.onclick=function(){vote_comment(comment_id, 1)};
			downarrow1.onclick=function(){vote_comment(comment_id, -1)};
			scoreup1.classList.add("d-none");
			scorenone1.classList.remove("d-none");
			scoredown1.classList.add("d-none");
		}
	}

	post(url, callback, "Unable to vote at this time. Please try again later.");
}

//yt embed

function getId(url) {
	var regExp = /^.*(youtu.be\/|v\/|u\/\w\/|embed\/|watch\?v=|\&v=)([^#\&\?]*).*/;
	var match = url.match(regExp);

	if (match && match[2].length == 11) {
		return match[2];
	} else {
		return 'error';
	}
}

var myUrl = $('#embedURL').text();

myId = getId(myUrl);

$('#ytEmbed').html('<iframe width="100%" height="475" src="//www.youtube.com/embed/' + myId + '" frameborder="0" allowfullscreen></iframe>');


// Expand Images on Desktop

function expandDesktopImage(image, link) {

// Link text

var linkText = document.getElementById("desktop-expanded-image-link");
var imgLink = document.getElementById("desktop-expanded-image-wrap-link");

var inlineImage = document.getElementById("desktop-expanded-image");

inlineImage.src = image.replace("100w.gif", "giphy.gif");
linkText.href = image;
imgLink.href=image;

if (image.includes("i.ruqqus.ga")) {
	linkText.textContent = 'Go to website';
}
else {
	linkText.textContent = 'View original';
}
};

// When image modal is closed

$('#expandImageModal').on('hidden.bs.modal', function (e) {

	// remove image src and link

	document.getElementById("desktop-expanded-image").src = '';

	document.getElementById("desktop-expanded-image-link").href = '';

});

// Text Formatting

// Bold Text

makeBold = function (form) {
	var text = document.getElementById(form);
	var startIndex = text.selectionStart,
	endIndex = text.selectionEnd;
	var selectedText = text.value.substring(startIndex, endIndex);

	var format = '**'

	if (selectedText.includes('**')) {
		text.value = selectedText.replace(/\*/g, '');
		
	}
	else if (selectedText.length == 0) {
		text.value = text.value.substring(0, startIndex) + selectedText + text.value.substring(endIndex);
	}
	else {
		text.value = text.value.substring(0, startIndex) + format + selectedText + format + text.value.substring(endIndex);
	}
}

// Italicize Comment Text

makeItalics = function (form) {
	var text = document.getElementById(form);
	var startIndex = text.selectionStart,
	endIndex = text.selectionEnd;
	var selectedText = text.value.substring(startIndex, endIndex);

	var format = '*'

	if (selectedText.includes('*')) {
		text.value = selectedText.replace(/\*/g, '');
		
	}
	else if (selectedText.length == 0) {
		text.value = text.value.substring(0, startIndex) + selectedText + text.value.substring(endIndex);
	}
	else {
		text.value = text.value.substring(0, startIndex) + format + selectedText + format + text.value.substring(endIndex);
	}
}

// Quote Comment Text

makeQuote = function (form) {
	var text = document.getElementById(form);
	var startIndex = text.selectionStart,
	endIndex = text.selectionEnd;
	var selectedText = text.value.substring(startIndex, endIndex);

	var format = '>'

	if (selectedText.includes('>')) {
		text.value = text.value.substring(0, startIndex) + selectedText.replace(/\>/g, '') + text.value.substring(endIndex);
		
	}
	else if (selectedText.length == 0) {
		text.value = text.value.substring(0, startIndex) + selectedText + text.value.substring(endIndex);
	}
	else {
		text.value = text.value.substring(0, startIndex) + format + selectedText + text.value.substring(endIndex);
	}
}

// Character Count

function charLimit(form, text) {

	var input = document.getElementById(form);

	var text = document.getElementById(text);

	var length = input.value.length;

	var maxLength = input.getAttribute("maxlength");

	if (length >= maxLength) {
		text.style.color = "#E53E3E";
	}
	else if (length >= maxLength * .72){
		text.style.color = "#FFC107";
	}
	else {
		text.style.color = "#A0AEC0";
	}

	text.innerText = maxLength - length;

}

// Mobile bottom navigation bar

window.onload = function () {
	var prevScrollpos = window.pageYOffset;
	window.onscroll = function () {
		var currentScrollPos = window.pageYOffset;

		var topBar = document.getElementById("fixed-bar-mobile");

		var bottomBar = document.getElementById("mobile-bottom-navigation-bar");

		var dropdown = document.getElementById("mobileSortDropdown");

		var navbar = document.getElementById("navbar");

		if (bottomBar != null) {
			if (prevScrollpos > currentScrollPos && (window.innerHeight + currentScrollPos) < (document.body.offsetHeight - 65)) {
				bottomBar.style.bottom = "0px";
			} 
			else if (currentScrollPos <= 125 && (window.innerHeight + currentScrollPos) < (document.body.offsetHeight - 65)) {
				bottomBar.style.bottom = "0px";
			}
			else if (prevScrollpos > currentScrollPos && (window.innerHeight + currentScrollPos) >= (document.body.offsetHeight - 65)) {
				bottomBar.style.bottom = "-50px";
			}
			else {
				bottomBar.style.bottom = "-50px";
			}
		}

	// Execute if bottomBar exists

	if (topBar != null && dropdown != null) {
		if (prevScrollpos > currentScrollPos) {
			topBar.style.top = "48px";
			navbar.classList.remove("shadow");
		} 
		else if (currentScrollPos <= 125) {
			topBar.style.top = "48px";
			navbar.classList.remove("shadow");
		}
		else {
			topBar.style.top = "-48px";
			dropdown.classList.remove('show');
			navbar.classList.add("shadow");
		}
	}
	prevScrollpos = currentScrollPos;
}
}

// Tooltips

$(document).ready(function(){
	$('[data-toggle="tooltip"]').tooltip(); 
});

// Paste to create submission

document.addEventListener('paste', function (event) {

	var nothingFocused = document.activeElement === document.body;

	if (nothingFocused) {

		if (document.getElementById('guild-name-reference')) {
			var guild = document.getElementById('guild-name-reference').innerText;
		}

		var clipText = event.clipboardData.getData('Text');

		var url = new RegExp('^(?:[a-z]+:)?//', 'i');

		if (url.test(clipText) && window.location.pathname !== '/submit' && guild == undefined) {
			window.location.href = '/submit?url=' + clipText;
		}
		else if (url.test(clipText) && window.location.pathname !== '/submit' && guild !== undefined) {
			window.location.href = '/submit?url=' + clipText + '&guild=' + guild;
		}
		else if (url.test(clipText) && window.location.pathname == '/submit' && guild == undefined) {

			document.getElementById("post-URL").value = clipText;

			autoSuggestTitle()

		}
	}
});

//	Submit Page Front-end Validation

function checkForRequired() {

// Divs

var title = document.getElementById("post-title");

var url = document.getElementById("post-URL");

var text = document.getElementById("post-text");

var button = document.getElementById("create_button");

var image = document.getElementById("file-upload");

// Toggle reuqired attribute

if (url.value.length > 0 || image.value.length > 0) {
	text.required = false;
	url.required=false;
} else if (text.value.length > 0 || image.value.length > 0) {
	url.required = false;
} else {
	text.required = true;
	url.required = true;
}

// Validity check

var isValidTitle = title.checkValidity();

var isValidURL = url.checkValidity();

var isValidText = text.checkValidity();

// Disable submit button if invalid inputs

if (isValidTitle && (isValidURL || image.value.length>0)) {
	button.disabled = false;
} else if (isValidTitle && isValidText) {
	button.disabled = false;
} else {
	button.disabled = true;
}

}

// Auto-suggest title given URL

function autoSuggestTitle()	{

	var urlField = document.getElementById("post-URL");

	var titleField = document.getElementById("post-title");

	var isValidURL = urlField.checkValidity();

	if (isValidURL && urlField.value.length > 0 && titleField.value === "") {

		var x = new XMLHttpRequest();
		x.withCredentials=true;
		x.onreadystatechange = function() {
			if (x.readyState == 4 && x.status == 200) {

				title=JSON.parse(x.responseText)["title"];
				titleField.value=title;

				checkForRequired()
			}
		}
		x.open('get','/submit/title?url=' + urlField.value);
		x.send(null);

	};

};

// Run AutoSuggestTitle function on load

if (window.location.pathname=='/submit') {
	window.onload = autoSuggestTitle();
}

// Invite user to mod
function invite_mod_to_guild(boardid) {

	var inviteForm = document.getElementById("invite-form");

	var inviteError = document.getElementById("toast-error-message");

	var usernameField = document.getElementById("invite-username");

	var isValidUsername = usernameField.checkValidity();

	username = usernameField.value;

	if (isValidUsername) {

		var xhr = new XMLHttpRequest();
		xhr.open("post", "/mod/invite_mod/"+boardid);
		xhr.withCredentials=true;
		f=new FormData();
		f.append("username", username);
		f.append("formkey", formkey());
		xhr.onload=function(){
			if (xhr.status==204) {
				window.location.reload(true);
			}
			else {
				$('#toast-invite-error').toast('dispose');
				$('#toast-invite-error').toast('show');
				inviteError.textContent = JSON.parse(xhr.response)["error"];
			}
		}
		xhr.send(f)
	}

}

block_user=function() {

	var exileForm = document.getElementById("exile-form");

	var exileError = document.getElementById("toast-error-message");

	var usernameField = document.getElementById("exile-username");

	var isValidUsername = usernameField.checkValidity();

	username = usernameField.value;

	if (isValidUsername) {

		var xhr = new XMLHttpRequest();
		xhr.open("post", "/settings/block");
		xhr.withCredentials=true;
		f=new FormData();
		f.append("username", username);
		f.append("formkey", formkey());
		xhr.onload=function(){
			if (xhr.status<300) {
				window.location.reload(true);
			}
			else {
				$('#toast-exile-error').toast('dispose');
				$('#toast-exile-error').toast('show');
				exileError.textContent = JSON.parse(xhr.response)["error"];
			}
		}
		xhr.send(f)
	}

}

post_comment=function(fullname){


	var form = new FormData();

	form.append('formkey', formkey());
	form.append('parent_fullname', fullname);
	form.append('submission', document.getElementById('reply-form-submission-'+fullname).value);
	form.append('body', document.getElementById('reply-form-body-'+fullname).value);
	form.append('file', document.getElementById('file-upload-reply-'+fullname).files[0]);
	var xhr = new XMLHttpRequest();
	xhr.open("post", "/api/comment");
	xhr.withCredentials=true;
	xhr.onload=function(){
		if (xhr.status==200) {
			commentForm=document.getElementById('comment-form-space-'+fullname);
			commentForm.innerHTML=JSON.parse(xhr.response)["html"];
			$('#toast-comment-success').toast('dispose');
			$('#toast-comment-error').toast('dispose');
			$('#toast-comment-success').toast('show');
		}
		else {
			var commentError = document.getElementById("comment-error-text");
			$('#toast-comment-success').toast('dispose');
			$('#toast-comment-error').toast('dispose');
			$('#toast-comment-error').toast('show');
			commentError.textContent = JSON.parse(xhr.response)["error"];
		}
	}
	xhr.send(form)

	document.getElementById('save-reply-to-'+fullname).classList.add('disabled');

}

herald_comment=function(bid,cid){


	var xhr = new XMLHttpRequest();
	xhr.open("post", "/mod/distinguish_comment/"+bid+'/'+cid);

	var form = new FormData();

	form.append('formkey', formkey());

	xhr.withCredentials=true;
	xhr.onload=function(){
		if (xhr.status==200) {
			comment=document.getElementById('comment-'+cid+'-only');
			comment.innerHTML=JSON.parse(xhr.response)["html"];
		}
		else {
			var commentError = document.getElementById("comment-error-text");
			$('#toast-comment-success').toast('dispose');
			$('#toast-comment-error').toast('dispose');
			$('#toast-comment-error').toast('show');
			commentError.textContent = JSON.parse(xhr.response)["error"];
		}
	}
	xhr.send(form)

}

//part of submit page js

hide_image=function(){
	x=document.getElementById('image-upload-block');
	url=document.getElementById('post-URL').value;
	if (url.length>=1){
		x.classList.add('d-none');
	}
	else {
		x.classList.remove('d-none');
	}
}


comment_edit=function(id){

	var commentError = document.getElementById("comment-error-text");

	var form = new FormData();

	form.append('formkey', formkey());
	form.append('body', document.getElementById('comment-edit-body-'+id).value);
	form.append('file', document.getElementById('file-edit-reply-'+id).files[0]);

	var xhr = new XMLHttpRequest();
	xhr.open("post", "/edit_comment/"+id);
	xhr.withCredentials=true;
	xhr.onload=function(){
		if (xhr.status==200) {
			commentForm=document.getElementById('comment-text-'+id);
			commentForm.innerHTML=JSON.parse(xhr.response)["html"];
			document.getElementById('cancel-edit-'+id).click()
			$('#toast-comment-success').toast('dispose');
			$('#toast-comment-error').toast('dispose');
			$('#toast-comment-success').toast('show');
		}
		else {
			$('#toast-comment-success').toast('dispose');
			$('#toast-comment-error').toast('dispose');
			$('#toast-comment-error').toast('show');
			commentError.textContent = JSON.parse(xhr.response)["error"];
		}
	}
	xhr.send(form)

}


//mobile prompt
if (("standalone" in window.navigator) &&			 // Check if "standalone" property exists
		window.navigator.standalone){							 // Test if using standalone navigator

		// Web page is loaded via app mode (full-screen mode)
		// (window.navigator.standalone is TRUE if user accesses website via App Mode)

} else {
	if (window.innerWidth <= 737){
		try {
			$('#mobile-prompt').tooltip('show')
			$('.tooltip')[0].addEventListener(
				'click', 
				function(event){
					$('#mobile-prompt').tooltip('hide')
					var xhr = new XMLHttpRequest();
					xhr.withCredentials=true;
					xhr.open("POST", '/dismiss_mobile_tip', true);
					xhr.send();
				}
			)
		} catch (error) {
			console.error(error);
		}
	}
}

$('.mention-user').click(function (event) {

	if (event.which != 1) {
		return
	}

	event.preventDefault();

	window.location.href='/@' + $(this).data('original-name');

});

$('.expandable-image').click( function(event) {

	if (event.which != 1) {
		return
	}
	event.preventDefault();

	var url= $(this).data('url');

	expandDesktopImage(url,url);
})

$('.text-expand').click(function(event){
  if (event.which != 1) {
    return
  };
  id=$(this).data('id');


  $('#post-text-'+id).toggleClass('d-none');
  $('.text-expand-icon-'+id).toggleClass('fa-expand-alt');
  $('.text-expand-icon-'+id).toggleClass('fa-compress-alt');

})

if (window.location.pathname.includes('/@')) {
	var userid = document.getElementById("userid").value;
	if (userid != "nosong")
	{
		var audio = new Audio(`/songs/${userid}`);
		audio.loop=true;
		audio.play();
		document.getElementById('userpage').addEventListener('click', () => {
			if (audio.paused) audio.play(); 
		}, {once : true});
	}
}