from ensurepip import bootstrap

from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Boolean
import random
from flask_bootstrap import Bootstrap5


app = Flask(__name__)
Bootstrap5(app)
# CREATE DB
class Base(DeclarativeBase):
    pass
# Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
db = SQLAlchemy(model_class=Base)
db.init_app(app)


# Cafe TABLE Configuration
class Cafe(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    map_url: Mapped[str] = mapped_column(String(500), nullable=False)
    img_url: Mapped[str] = mapped_column(String(500), nullable=False)
    location: Mapped[str] = mapped_column(String(250), nullable=False)
    seats: Mapped[str] = mapped_column(String(250), nullable=False)
    has_toilet: Mapped[bool] = mapped_column(Boolean, nullable=False)
    has_wifi: Mapped[bool] = mapped_column(Boolean, nullable=False)
    has_sockets: Mapped[bool] = mapped_column(Boolean, nullable=False)
    can_take_calls: Mapped[bool] = mapped_column(Boolean, nullable=False)
    coffee_price: Mapped[str] = mapped_column(String(250), nullable=True)

    def to_dict(self):
        dictionary = {}
        for column in self.__table__.columns:
            dictionary[column.name] = getattr(self, column.name)
        return dictionary


with app.app_context():
    db.create_all()

#Home page where all cafes are displayed
@app.route("/")
def home():
    result = db.session.execute(db.select(Cafe).order_by(Cafe.name))
    all_cafes = result.scalars().all()
    print(all_cafes)
    return render_template("index.html", cafes=all_cafes)


# Details page for a single cafe
@app.route("/<int:cafe_id>")
def cafe_detail(cafe_id):
    cafe = db.session.execute(db.select(Cafe).where(Cafe.id == cafe_id)).scalar()
    return render_template("cafe.html", cafe=cafe)



@app.route("/random")
def get_random_cafe():
    with app.app_context():
        result = db.session.execute(db.select(Cafe))
        all_cafes = result.scalars().all()
        random_cafe = random.choice(all_cafes)
        return jsonify(cafe=random_cafe.to_dict())


@app.route("/search")
def search_location():
    location = request.args.get("loc")
    result = db.session.execute(db.select(Cafe).where(Cafe.location == location))
    cafes_at_location = result.scalars().all()
    if cafes_at_location:
        return render_template("locations.html", cafes=cafes_at_location)
    else:
        return jsonify(
            error={"Not Found": "Sorry, we don't have a cafe at that location"}
        ), 404


# HTTP POST - Create Record
@app.route("/add", methods=["GET", "POST"])
def add_cafe():
    new_cafe = Cafe(
        name = request.form.get("name"),
        map_url = request.form.get("map_url"),
        img_url = request.form.get("img_url"),
        location = request.form.get("location"),
        seats = request.form.get("seats"),
        has_toilet=request.form.get("has_toilet") == 'True',  # Convert to Boolean
        has_wifi=request.form.get("has_wifi") == 'True',  # Convert to Boolean
        has_sockets=request.form.get("has_sockets") == 'True',  # Convert to Boolean
        can_take_calls=request.form.get("can_take_calls") == 'True',  # Convert to Boolean
        coffee_price = request.form.get("coffee_price")
    )
    db.session.add(new_cafe)
    db.session.commit()
    return jsonify(response ={"success": "Successfully added new cafe."})

# HTTP PUT/PATCH - Update Record
@app.route("/update-price/<cafe_id>", methods=["PATCH"])
def update_price(cafe_id):
    new_price = request.args.get("new_price")
    cafe_to_update = db.get_or_404(Cafe, cafe_id)
    if cafe_to_update:
        cafe_to_update.coffee_price = new_price
        db.session.commit()
        return jsonify(response = {"Success" : "Successfully updated price."})
    else:
        return jsonify(error = {"Not Found": "Sorry a cafe with that id was not found."})


# HTTP DELETE - Delete Record
@app.route("/report-closed/<cafe_id>", methods=["DELETE"])
def report_closed(cafe_id):
    api_key = request.args.get("api-key")
    cafe_to_delete = db.session.execute(db.select(Cafe).where(Cafe.id == cafe_id)).scalar()

    if cafe_to_delete:
        if api_key == "TopSecretAPIKey":
            db.session.delete(cafe_to_delete)
            db.session.commit()
            return jsonify(response = {"Success" : "Successfully removed cafe."})
        else:
            return jsonify(error={"Forbidden": "The api key is incorrect."}), 403

    else:
        return jsonify(error = {"Not Found": "Sorry a cafe with that id was not found."}), 404


if __name__ == '__main__':
    app.run(debug=True)
