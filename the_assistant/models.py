from the_assistant import db, login_manager
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(40), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    characters = db.relationship('Character', backref='author', lazy=True)
    monsters = db.relationship('Monster', backref='author', lazy=True)
    npcs = db.relationship('Npc', backref='author', lazy=True)
    shops = db.relationship('Shop', backref='author', lazy=True)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}'"

class Character(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    character_name = db.Column(db.String(40), nullable=False)
    total_hp = db.Column(db.Integer, nullable=False)
    current_hp = db.Column(db.Integer, nullable=False)
    armor_class = db.Column(db.Integer, nullable=False)
    strength = db.Column(db.Integer, nullable=False)
    dexterity = db.Column(db.Integer, nullable=False)
    constitution = db.Column(db.Integer, nullable=False)
    intelligence = db.Column(db.Integer, nullable=False)
    wisdom = db.Column(db.Integer, nullable=False)
    charisma = db.Column(db.Integer, nullable=False)
    char_bio = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"Character('{self.character_name}', '{self.total_hp}')"

class Monster(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    monster_name = db.Column(db.String(50), nullable=False)
    total_hp = db.Column(db.Integer, nullable=False)
    current_hp = db.Column(db.Integer, nullable=False)
    monster_description = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"Monsters('{self.monster_name}', '{self.total_hp}'"

class Npc(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    npc_name = db.Column(db.String(50), nullable=False)
    job = db.Column(db.String(50), nullable=False)
    npc_desctription = db.Column(db.String(1000), nullable=False)
    total_hp = db.Column(db.Integer, nullable=False)
    current_hp = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"Npc('{self.npc_name}', '{self.job}', '{self.total_hp}')"

class Shop(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    shop_name = db.Column(db.String(40), nullable=False)
    shop_owner = db.Column(db.String(40), nullable=False)
    inventory = db.Column(db.String(1225), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"Shop('{self.shop_name}', '{self.shop_owner}')"