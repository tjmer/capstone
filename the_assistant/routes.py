from flask import render_template, url_for, flash, redirect, request, abort
from wtforms.validators import Email
from the_assistant import app, db, bcrypt
from the_assistant.models import User, Character, Monster, Shop
from the_assistant.forms import RegistrationForm, LoginForm, UpdateAccountForm, CreateCharacter, CreateMonster, CreateShop
from flask_login import login_user, current_user, logout_user, login_required
import requests
import json
import secrets
import os

@app.route('/')
def landing():
    return render_template('welcome.html',title='Welcome')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('landing'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created!  You are now able to log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('landing'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('landing'))
        else:
            flash('Login failed, please check username and password', 'danger')

    return render_template('login.html', title='Login', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('landing'))

@app.route('/battle')
@login_required
def battle():
    characters = Character.query.all()
    monsters = Monster.query.all()
    return render_template('battle.html', title='Battle', characters=characters, monsters=monsters)

def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)
    form_picture.save(picture_path)
    return picture_fn

@app.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Account', image_file=image_file, form=form)

@app.route('/battle/createplayer', methods=['GET', 'POST'])
@login_required
def createplayer():
    form = CreateCharacter()
    if form.validate_on_submit():
        character = Character(character_name=form.character_name.data, total_hp=form.total_health.data, current_hp=form.current_health.data, armor_class=form.ac.data,
                              strength=form.strength.data, dexterity=form.dexterity.data, constitution=form.constition.data, intelligence=form.intelligence.data,
                              wisdom=form.wisdom.data, charisma=form.charisma.data, char_bio=form.bio.data, author=current_user)
        db.session.add(character)
        db.session.commit()
        flash("Created character!", 'success')
        return redirect(url_for('battle'))
    return render_template('makeplayer.html', title='Create Player', form=form, legend='Create Character')

@app.route('/battle/<int:character_id>')
@login_required
def character(character_id):
    character = Character.query.get_or_404(character_id)
    return render_template('character.html', title=character.character_name, character= character)

@app.route('/battle/<int:character_id>/update', methods=['GET', 'POST'])
@login_required
def update_character(character_id):
    character = Character.query.get_or_404(character_id)
    if character.author != current_user:
        abort(403)
    form = CreateCharacter()
    if form.validate_on_submit():
        character.character_name = form.character_name.data
        character.character_total_hp = form.total_health.data
        character.current_hp = form.current_health.data
        character.armor_class = form.ac.data
        character.strength = form.strength.data
        character.dexterity = form.dexterity.data
        character.constitution = form.constition.data
        character.intelligence = form.intelligence.data
        character.wisdom = form.wisdom.data
        character.charisma = form.charisma.data
        character.char_bio = form.bio.data
        db.session.commit()
        flash('Character updated!', 'success')
        return redirect(url_for('character', character_id=character.id))
    elif request.method == 'GET':
        form.character_name.data = character.character_name
        form.total_health.data = character.total_hp
        form.current_health.data = character.current_hp
        form.ac.data = character.armor_class
        form.strength.data = character.strength
        form.dexterity.data = character.dexterity
        form.constition.data = character.constitution
        form.intelligence.data = character.intelligence
        form.wisdom.data = character.wisdom
        form.charisma.data = character.charisma
        form.bio.data = character.char_bio
    return render_template('makeplayer.html', title='Update Player', form=form, legend='Update Character')

@app.route('/battle/<int:character_id>/delete', methods=['POST'])
@login_required
def delete_character(character_id):
    character = Character.query.get_or_404(character_id)
    if character.author != current_user:
        abort(403)
    db.session.delete(character)
    db.session.commit()
    flash('Character deleted!', 'success')
    return redirect(url_for('battle'))

@app.route('/battle/createmonster', methods=['GET', 'POST'])
@login_required
def createmonster():
    form = CreateMonster()
    if form.validate_on_submit():
        monster = Monster(monster_name=form.monster_name.data, total_hp=form.total_hp.data, current_hp=form.current_hp.data,
                          armor_class=form.armor_class.data, monster_description=form.monster_desc.data, author=current_user)
        db.session.add(monster)
        db.session.commit()
        flash("Created monster!", 'success')
        return redirect(url_for('battle'))
    return render_template('makemonster.html', title='Create Monster', form=form, legend= 'Create Monster')

@app.route('/battle/monster/<int:monster_id>')
@login_required
def monster(monster_id):
    monster = Monster.query.get_or_404(monster_id)
    return render_template('monster.html', title=monster.monster_name, monster= monster)

@app.route('/battle/monster/<int:monster_id>/update', methods=['GET', 'POST'])
@login_required
def update_monster(monster_id):
    monster = Monster.query.get_or_404(monster_id)
    if monster.author != current_user:
        abort(403)
    form = CreateMonster()
    if form.validate_on_submit():
        monster.monster_name = form.monster_name.data
        monster.total_hp = form.total_hp.data
        monster.current_hp = form.current_hp.data
        monster.armor_class = form.armor_class.data
        monster.monster_description = form.monster_desc.data
        db.session.commit()
        flash('Updated Monster!', 'success')
        return redirect(url_for('monster', monster_id=monster.id))
    elif request.method == 'GET':
        form.monster_name.data = monster.monster_name
        form.total_hp.data = monster.total_hp
        form.current_hp.data = monster.current_hp
        form.armor_class.data = monster.armor_class
        form.monster_desc.data = monster.monster_description
    return render_template('makemonster.html', title='Update Monster', form=form, legend= 'Update Monster')

@app.route('/battle/monster/<int:monster_id>/delete', methods=['POST'])
@login_required
def delete_monster(monster_id):
    monster = Monster.query.get_or_404(monster_id)
    if monster.author != current_user:
        abort(403)
    db.session.delete(monster)
    db.session.commit()
    flash('Monster has been deleted!', 'success')
    return redirect(url_for('battle'))

@app.route('/reference', methods=['GET', 'POST'])
@login_required
def reference():
    melee = ["greatsword", "longsword", "shortsword", "scimitar", "rapier", "dagger", "sickle",
            "handaxe","battleaxe", "greataxe", "light-hammer", "warhammer", "club", "greatclub",
            "flail", "glaive", "halberd", "spear", "lance", "pike", "war-pick", "trident", "javelin", "maul",
            "morningstar", "mace", "quarterstaff"]
    
    ranged = ["longbow", "shortbow", "crossbow-hand", "crossbow-light", "crossbow-heavy", "sling", "blowgun", "dart"]

    monsters = ["assassin", 'bandit', 'bandit-captain', 'black-bear', 'boar', 'bugbear', 'centaur', 'commoner', 'cult-fanatic',
                'cultist', 'dire-wolf', 'dryad', 'ghast', 'ghost', 'giant-rat', 'gnoll', 'goblin', 'gorgon', 'griffon', 
                'guard', 'hawk', 'hobgoblin', 'hydra', 'knight', 'kobold', 'lich', 'lion', 'lizard', 'lizardfolk', 'mage',
                'medusa', 'mimic', 'minotaur', 'noble', 'ogre', 'orc', 'priest', 'rat', 'raven', 'riding-horse', 'roc',
                ]
    shops = Shop.query.all()
    wname = ''
    wcat = ''
    wdice = ''
    wdtype = ''
    wcost = ''
    wcostunit = ''

    rname = ''
    rcat = ''
    rdice = ''
    rdtype = ''
    rcost = ''
    rcostunit = ''

    mname = ''
    msize = ''
    mtype = ''
    mspeed = ''
    mac = ''
    mhp = ''
    mdice = ''
    mstr = ''
    mdex = ''
    mconst = ''
    mint = ''
    mwis = ''
    mchar = ''
    mchallenge = ''

    if request.method == 'POST':
        meleew = request.form.get('melee', None)
        rangew = request.form.get('ranged', None)
        monsterw = request.form.get('monster', None)

        if meleew != None:
            req = requests.get(f'https://www.dnd5eapi.co/api/equipment/{meleew}')
            data = json.loads(req.content)
            wname = data['name']
            wcat = data['weapon_category']
            wdice = data['damage']['damage_dice']
            wdtype = data['damage']['damage_type']['name']
            wcost = data['cost']['quantity']
            wcostunit = data['cost']['unit']
            return render_template('references.html', title='References', shops=shops, range=ranged, melee=melee, monsters=monsters, wname=wname, wcat=wcat, wdice=wdice, wdtype= wdtype, wcost=wcost,
                                   wcostunit=wcostunit, rcostunit=rcostunit, rname=rname, rcat=rcat, rdice=rdice, rdtype=rdtype, rcost=rcost, mname=mname,
                                   msize=msize, mtype=mtype, mspeed=mspeed, mac=mac, mhp=mhp, mdice=mdice, mstr=mstr, mdex=mdex, mconst=mconst, mint=mint,
                                   mwis=mwis, mchar=mchar, mchallenge=mchallenge)

        elif rangew != None:
            req = requests.get(f'https://www.dnd5eapi.co/api/equipment/{rangew}')
            data = json.loads(req.content)
            rname = data['name']
            rcat = data['weapon_category']
            rdice = data['damage']['damage_dice']
            rdtype = data['damage']['damage_type']['name']
            rcost = data['cost']['quantity']
            rcostunit = data['cost']['unit']
            return render_template('references.html', title='References', shops=shops, range=ranged, melee=melee, monsters=monsters, wname=wname, wcat=wcat, wdice=wdice, wdtype= wdtype, wcost=wcost,
                                   rname=rname, rcat=rcat, rdice=rdice, rdtype=rdtype, rcost=rcost, mname=mname,
                                   wcostunit=wcostunit, rcostunit=rcostunit, msize=msize, mtype=mtype, mspeed=mspeed, mac=mac, mhp=mhp, mdice=mdice, mstr=mstr, mdex=mdex, mconst=mconst, mint=mint,
                                   mwis=mwis, mchar=mchar, mchallenge=mchallenge)

        elif monsterw != None:
            req = requests.get(f'https://www.dnd5eapi.co/api/monsters/{monsterw}')
            data = json.loads(req.content)
            mname = data['name']
            msize = data['size']
            mtype = data['type']
            mspeed = data['speed']['walk']
            mac = data['armor_class']
            mhp = data['hit_points']
            mdice = data['hit_dice']
            mstr = data['strength']
            mdex = data['dexterity']
            mconst = data['constitution']
            mint = data['intelligence']
            mwis = data['wisdom']
            mchar = data['charisma']
            mchallenge = data['challenge_rating']
            return render_template('references.html', title='References', shops=shops, range=ranged, melee=melee, monsters=monsters, wname=wname, wcat=wcat, wdice=wdice, wdtype= wdtype, wcost=wcost,
                                   rname=rname, rcat=rcat, rdice=rdice, rdtype=rdtype, rcost=rcost, mname=mname,
                                   msize=msize, mtype=mtype, mspeed=mspeed, mac=mac, mhp=mhp, mdice=mdice, mstr=mstr, mdex=mdex, mconst=mconst, mint=mint,
                                   mwis=mwis, mchar=mchar, mchallenge=mchallenge)

    return render_template('references.html', title='References', shops=shops, range=ranged, melee=melee, monsters=monsters, wname=wname, wcat=wcat, wdice=wdice, wdtype= wdtype, wcost=wcost,
                           rname=rname, rcat=rcat, rdice=rdice, rdtype=rdtype, rcost=rcost, mname=mname,
                           wcostunit=wcostunit, rcostunit=rcostunit, msize=msize, mtype=mtype, mspeed=mspeed, mac=mac, mhp=mhp, mdice=mdice, mstr=mstr, mdex=mdex, mconst=mconst, mint=mint,
                           mwis=mwis, mchar=mchar, mchallenge=mchallenge)

@app.route('/createshop', methods=['GET', 'POST'])
@login_required
def createshop():
    form= CreateShop()
    if form.validate_on_submit():
        shop = Shop(shop_name=form.shop_name.data, shop_owner=form.shop_owner.data, inventory=form.inventory.data, author=current_user)
        db.session.add(shop)
        db.session.commit()
        flash('Shop made!', 'success')
        return redirect(url_for('reference'))
    return render_template('createshop.html', title='Create Shop', legend="Create Shop", form=form)

@app.route('/references/<int:shop_id>')
@login_required
def shop(shop_id):
    shop = Shop.query.get_or_404(shop_id)
    return render_template('shop.html', title=shop.shop_name, shop= shop)

@app.route('/reference/shop/<int:shop_id>/update', methods=['GET', 'POST'])
@login_required
def update_shop(shop_id):
    shop = Shop.query.get_or_404(shop_id)
    if shop.author != current_user:
        abort(403)
    form= CreateShop()
    if form.validate_on_submit():
        shop.shop_name = form.shop_name.data
        shop.shop_owner = form.shop_owner.data
        shop.inventory = form.inventory.data
        db.session.commit()
        flash('Shop updated!', 'success')
        return redirect(url_for('shop', shop_id=shop.id))
    elif request.method == 'GET':
        form.shop_name.data = shop.shop_name
        form.shop_owner.data = shop.shop_owner
        form.inventory.data = shop.inventory
    return render_template('createshop.html', title='Update Shop', form=form, legend= 'Update shop')

@app.route('/reference/shop/<int:shop_id>/delete', methods=['POST'])
@login_required
def delete_shop(shop_id):
    shop = Shop.query.get_or_404(shop_id)
    if shop.author != current_user:
        abort(403)
    db.session.delete(shop)
    db.session.commit()
    flash('Shop has been deleted!', 'success')
    return redirect(url_for('reference'))

@app.route('/spells', methods=['GET', 'POST'])
@login_required
def spells():
    spellcant = ['acid-splash', 'chill-touch', 'dancing-lights', 'druidcraft', 'eldritch-blast', 'fire-bolt',
                 'guidance', 'light', 'mage-hand', 'mending', 'message', 'minor-illusion', 'poison-spray', 'prestidigitation',
                 'produce-flame', 'ray-of-frost', 'resistance', 'sacred-flame', 'shillelagh', 'shocking-grasp',
                 'thaumaturgy', 'true-strike', 'vicious-mockery']
    
    spell1 = ['alarm', 'animal-friendship', 'bane', 'bless', 'burning-hands', 'charm-person', 'color-spray',
              'command', 'comprehend-languages', 'create-or-destroy-water', 'cure-wounds', 'detect-evil-and-good',
              'detect-magic', 'detect-poison-and-disease', 'disguise-self', 'divine-favor', 'entangle', 'expeditious-retreat',
              'faerie-fire', 'false-life', 'feather-fall', 'find-familiar', 'floating-disk', 'fog-cloud', 'goodberry',
              'grease', 'guiding-bold', 'healing-word', 'hellish-rebuke', 'heroism', 'hideous-laughter', "hunters-mark",
              'identify', 'illusory-script', 'inflict-wounds', 'jump', 'longstider', 'mage-armor', 'magic-missile', 'protection-from-evil-and-good',
              'purify-food-and-drink', 'sanctuary', 'shield', 'shield-of-faith', 'silent-image', 'sleep', 'speak-with-animals',
              'thunderwave', 'unseen-servant']
    
    spell2 = ['acid-arrow', 'aid', 'alter-self', 'animal-messenger', 'arcane-lock', 'arcanists-magic-aura', 'augury', 'barkskin',
              'blindness-deafness', 'blur', 'branding-smite', 'calm-emotions', 'continual-flame', 'darkness', 'darkvision', 'detect-thoughts',
              'enhance-ability', 'enlarge-reduce', 'enthrall', 'find-steed', 'find-traps', 'flame-blade', 'flaming-sphere', 'gentle-repose',
              'gust-of-wind', 'heat-metal', 'hold-person', 'invisibility', 'knock', 'lesser-restoration', 'levitate', 'locate-animals-or-plants',
              'locate-object', 'magic-mouth', 'magic-weapon', 'mirror-image', 'misty-step', 'moonbeam', 'pass-without-trace',
              'prayer-of-healing', 'protection-from-poison', 'ray-of-enfeeblement', 'rope-trick', 'scorching-ray', 'see-invisiblity',
              'shatter', 'silence', 'spider-climb', 'spike-growth', 'spiritual-weapon', 'suggestion', 'warding-bond',
              'web', 'zone-of-truth']
    
    spell3 = ['animate-dead', 'beacon-of-hope', 'bestow-curse', 'blink', 'call-lightning', 'clairvoyance', 'conjure-animals', 'counterspell',
              'create-food-and-water', 'daylight', 'dispel-magic', 'fear', 'fireball', 'fly', 'gaseous-form', 'glyph-of-warding', 'haste',
              'hypnotic-pattern', 'lightning-bolt', 'magic-circle', 'major-image', 'mass-healing-word', 'meld-into-stone', 'nondetection',
              'phantom-steed', 'plant-growth', 'protection-from-energy', 'remove-curse', 'revivify', 'sending', 'sleet-storm', 'slow',
              'speak-with-dead', 'spirit-guardians', 'stinking-cloud', 'tiny-hut', 'tongues', 'vampiric-touch', 'water-breathing',
              'water-walk', 'wind-wall']

    spell4 = ['arcane-eye', 'banishment', 'black-tentacles', 'blight', 'compulsion', 'confusion', 'conjure-minor-elementals', 'conjure-woodland-beings',
              'control-water', 'death-ward', 'dimension-door', 'divination', 'dominate-beast', 'fabricate', 'faithful-hound', 'fire-shield',
              'freedom-of-movement', 'giant-insect', 'greater-invisibility', 'guardian-of-faith', 'hallucinatory-terrain', 'ice-storm',
              'locate-creature', 'phantasmal-killer', 'polymorph', 'private-sanctum', 'resilient-sphere', 'secret-chest', 'stone-shape',
              'stoneskin', 'wall-of-fire']
    
    spell5 = ['animate-objects', 'antilife-shell', 'arcane-hand', 'awaken', 'cloudkill', 'commune', 'commune-with-nature', 'cone-of-cold',
              'conjure-elemental', 'contact-other-plane', 'contagion', 'creation', 'dispel-evil-and-good', 'dominate-person', 'dream',
              'flame-strike', 'geas', 'greater-restoration', 'hallow', 'hold-monster', 'insect-plague', 'legend-lore', 'mass-cure-wounds',
              'mislead', 'modify-memory', 'passwall', 'planar-binding', 'raise-dead', 'reincarnate', 'scrying', 'seeming', 'telekinesis',
              'telepathic-bond', 'teleportation-circle', 'tree-stride', 'wall-of-force', 'wall-of-stone']

    spell6 = ['blade-barrier', 'chain-lightning', 'circle-of-death', 'conjure-fey', 'contingency', 'create-undead', 'disintegrate', 'eyebite',
              'find-the-path', 'flesh-to-stone', 'forbiddance', 'freezing-sphere', 'globe-of-Invulnerability', 'guards-and-wards', 'harm', 'heal',
              'heroes-feast', 'instant-summons', 'irresistible-dance', 'magic-jar', 'mass-suggestion', 'move-earth', 'planar-ally', 'programmed-illusion',
              'sunbeam', 'transport-via-plants', 'true-seeing', 'wall-of-ice', 'wall-of-thorns', 'wind-walk', 'word-of-recall']
    
    spell7 = ['arcane-sword', 'conjure-celestial', 'delayed-blast-fireball', 'divine-word', 'etherealness', 'finger-of-death',
              'fire-storm', 'forcecage', 'magnificent-mansion', 'mirge-arcane', 'plane-shift', 'prismatic-spray', 'project-image', 'regenerate',
              'resurrection', 'reverse-gravity', 'sequester', 'simulacrum', 'symbol', 'teleport']

    spell8 = ['animal-shapes', 'antimagic-field', 'antipathy-sympathy', 'clone', 'control-weather', 'demiplane', 'dominate-monster', 'earthquake',
              'feeblemind', 'glibness', 'holy-aura', 'incendiary-cloud', 'maze', 'mind-blank', 'power-word-stun', 'sunburst']

    spell9 = ['astral-projection', 'foresight', 'gate', 'imprisonment', 'mass-heal', 'meteor-swarm', 'power-word-kill', 'prismatic-wall', 'shapechange',
              'storm-of-vengeance', 'time-stop', 'true-polymorph', 'true-resurrection', 'weird', 'wish']

    sname = ''
    sdesc = ''
    shigher_level = ''
    srange = ''
    scomponents = ''
    smaterial = ''
    sritual = ''
    sduration = ''
    sconcentration = ''
    scasting_time = ''
    slevel = ''
    sattack_type = ''
    sdamage_type = ''
    sdal_1 = ''
    sdal_2 = ''
    sdal_3 = ''
    sdal_4 = ''
    sdal_5 = ''
    sdal_6 = ''
    sdal_7 = ''
    sdal_8 = ''
    sdal_9 = ''
    sschool = ''

    if request.method == 'POST':
        spell0 = request.form.get('cantrip-spell', None)
        lvl1spell = request.form.get('lvl1-spell', None)
        lvl2spell = request.form.get('lvl2-spell', None)
        lvl3spell = request.form.get('lvl3-spell', None)
        lvl4spell = request.form.get('lvl4-spell', None)
        lvl5spell = request.form.get('lvl5-spell', None)
        lvl6spell = request.form.get('lvl6-spell', None)
        lvl7spell = request.form.get('lvl7-spell', None)
        lvl8spell = request.form.get('lvl8-spell', None)
        lvl9spell = request.form.get('lvl9-spell', None)

        if (spell0 != None or lvl1spell != None or lvl2spell != None or lvl3spell != None or lvl4spell != None or lvl5spell != None or 
            lvl6spell != None or lvl7spell != None or lvl8spell != None or lvl9spell != None):
            req = requests.get(f'https://www.dnd5eapi.co/api/spells/{spell0 or lvl1spell or lvl2spell or lvl3spell or lvl4spell or lvl5spell or lvl6spell or lvl7spell or lvl8spell or lvl9spell}')
            data = json.loads(req.content)

            sname = data['name']
            sdesc = data['desc']
            try:
                shigher_level = data['higher_level']
            except:
                shigher_level = ''
            srange = data['range']
            scomponents = data['components']
            try:
                smaterial = data['material']
            except:
                smaterial = ''
            sritual = data['ritual']
            sduration = data['duration']
            sconcentration = data['concentration']
            scasting_time = data['casting_time']
            slevel = data['level']
            try:
                sattack_type = data['attack_type']
            except:
                sattack_type = ''
            try:
                sdamage_type = data['damage']['damage_type']['name']
            except:
                sdamage_type = ''
            try:
                sdal_1 = data['damage']['damage_at_slot_level']['1']
            except:
                sdal_1 = ''
            try:
                sdal_2 = data['damage']['damage_at_slot_level']['2']
            except:
                sdal_2 = ''
            try:
                sdal_3 = data['damage']['damage_at_slot_level']['3']
            except:
                sdal_3 = ''
            try:
                sdal_4 = data['damage']['damage_at_slot_level']['4']
            except:
                sdal_4 = ''
            try:
                sdal_5 = data['damage']['damage_at_slot_level']['5']
            except:
                sdal_5 = ''
            try:
                sdal_6 = data['damage']['damage_at_slot_level']['6']
            except:
                sdal_6 = ''
            try:
                sdal_7 = data['damage']['damage_at_slot_level']['7']
            except:
                sdal_7 = ''
            try:
                sdal_8 = data['damage']['damage_at_slot_level']['8']
            except:
                sdal_8 = ''
            try:
                sdal_9 = data['damage']['damage_at_slot_level']['9']
            except:
                sdal_9 = ''
            sschool = data['school']['name']
            return render_template('spells.html', title='Spells', spellcant=spellcant, spell1=spell1, spell2=spell2,
                           spell3=spell3, spell4=spell4, spell5=spell5, spell6=spell6, spell7=spell7, spell8=spell8, spell9=spell9,
                           sname=sname, sdesc=sdesc, shigher_level=shigher_level, srange=srange, scomponents=scomponents,
                           smaterial=smaterial, sritual=sritual, sduration=sduration, sconcentration=sconcentration,
                           scasting_time=scasting_time, slevel=slevel, sattack_type=sattack_type, sdamage_type=sdamage_type,
                           sdal_1=sdal_1, sdal_2=sdal_2, sdal_3=sdal_3, sdal_4=sdal_4, sdal_5=sdal_5, sdal_6=sdal_6,
                           sdal_7=sdal_7, sdal_8=sdal_8, sdal_9=sdal_9, sschool=sschool)

    return render_template('spells.html', title='Spells', spellcant=spellcant, spell1=spell1, spell2=spell2,
                           spell3=spell3, spell4=spell4, spell5=spell5, spell6=spell6, spell7=spell7, spell8=spell8, spell9=spell9,
                           sname=sname, sdesc=sdesc, shigher_level=shigher_level, srange=srange, scomponents=scomponents,
                           smaterial=smaterial, sritual=sritual, sduration=sduration, sconcentration=sconcentration,
                           scasting_time=scasting_time, slevel=slevel, sattack_type=sattack_type, sdamage_type=sdamage_type,
                           sdal_1=sdal_1, sdal_2=sdal_2, sdal_3=sdal_3, sdal_4=sdal_4, sdal_5=sdal_5, sdal_6=sdal_6,
                           sdal_7=sdal_7, sdal_8=sdal_8, sdal_9=sdal_9, sschool=sschool)