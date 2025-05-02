from flask import Flask, jsonify, render_template, request, url_for, redirect
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Boolean
from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, SubmitField, URLField
from wtforms.validators import DataRequired, URL
from flask_bootstrap import Bootstrap5

app = Flask(__name__)
app.config['SECRET_KEY'] = 'sdfa098324'
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

# Flask WTForm for adding a new cafe
class CafeForm(FlaskForm):
    name = StringField('Cafe Name', validators=[DataRequired()])
    map_url = URLField('Map URL', validators=[DataRequired(), URL()])
    img_url = URLField('Image URL', validators=[DataRequired(), URL()])
    location = StringField('Location', validators=[DataRequired()])
    seats = StringField('Seats', validators=[DataRequired()])
    has_toilet = BooleanField('Has Toilet')
    has_wifi = BooleanField('Has Wifi')
    has_sockets = BooleanField('Has Sockets')
    can_take_calls = BooleanField('Can Take Calls')
    coffee_price = StringField('Coffee Price')
    submit = SubmitField('Add Cafe')

#Home page where all cafes are displayed
@app.route("/")
def home():
    result = db.session.execute(db.select(Cafe).order_by(Cafe.name))
    all_cafes = result.scalars().all()
    return render_template("index.html", cafes=all_cafes)


# Details page for a single cafe
@app.route("/<int:cafe_id>")
def cafe_detail(cafe_id):
    cafe = db.session.execute(db.select(Cafe).where(Cafe.id == cafe_id)).scalar()
    return render_template("cafe.html", cafe=cafe)

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

# Adding a new cafe
@app.route("/add", methods=["GET", "POST"])
def add_cafe():
    form = CafeForm()
    if form.validate_on_submit():
        new_cafe = Cafe(
            name=form.name.data,
            location=form.location.data,
            img_url=form.img_url.data,
            map_url=form.map_url.data,
            seats=form.seats.data,
            has_toilet=form.has_toilet.data,
            has_wifi=form.has_wifi.data,
            has_sockets=form.has_sockets.data,
            can_take_calls=form.can_take_calls.data,
            coffee_price=form.coffee_price.data,
        )
        db.session.add(new_cafe)
        db.session.commit()
        return redirect(url_for('home'))
    return render_template("add_cafe.html", form=form)

# Update an existing cafe
@app.route("/update-cafe/<cafe_id>", methods=["GET", "POST"])
def update_cafe(cafe_id):
    cafe_to_update = db.get_or_404(Cafe, cafe_id)
    form = CafeForm(obj=cafe_to_update)
    if form.validate_on_submit():
        form.populate_obj(cafe_to_update)
        db.session.commit()
        return redirect(url_for('cafe_detail', cafe_id=cafe_id))
    return render_template("update_cafe.html", form=form, cafe=cafe_to_update)


#Delete cafe from database
@app.route("/report-closed/<cafe_id>", methods=["POST"])
def report_closed(cafe_id):
    cafe_to_delete = db.get_or_404(Cafe, cafe_id)
    db.session.delete(cafe_to_delete)
    db.session.commit()
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
