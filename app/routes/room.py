from uuid import uuid4
import random

from flask import Blueprint, render_template, redirect, url_for, request

from app.db import Room, Session

room_blueprint = Blueprint("rooms", __name__)


@room_blueprint.get("/")
def index():
    with Session() as session:
        rooms = session.query(Room).filter_by(is_reserved=False).all()
        random.shuffle(rooms)
        return render_template("index.html", rooms=rooms)


@room_blueprint.route("/add_room/", methods=["GET", "POST"])
def add_room():
    with Session() as session:
        if request.method == "POST":
            number = request.form.get("number")
            price = request.form.get("price")
            floor = request.form.get("floor")
            img_url = None
            img_name_orig = None
            img_name = None

            photo = request.files.get("photo")
            if photo and photo.filename:
                img_name_orig = photo.filename
                img_name = uuid4().hex + "." + img_name_orig.split(".")[-1]
                img_url = f"/static/img/{img_name}"
                photo.save("app" + img_url)

            room = Room(
                number=number,
                floor=floor,
                price=price,
                img_name=img_name,
                img_name_orig=img_name_orig,
                img_url=img_url
            )
            session.add(room)
            session.commit()
            return redirect(url_for("rooms.manage_rooms"))

        return render_template("add_room.html")


@room_blueprint.get("/manage_rooms/")
def manage_rooms():
    with Session() as session:
        rooms = session.query(Room).all()
        return render_template("manage_rooms.html", rooms=rooms)


@room_blueprint.get("/delete/<int:id>/")
def delete_room(id):
    with Session() as session:
        room = session.query(Room).filter_by(id=id).first()
        session.delete(room)
        session.commit()
        return redirect(url_for("rooms.manage_rooms"))


@room_blueprint.route("/edit_room/<int:id>/", methods=["GET", "POST"])
def edit_room(id):
    with Session() as session:
        room = session.query(Room).filter_by(id=id).first()

        if request.method == "POST":
            room.number = request.form.get("number")
            room.floor = request.form.get("floor")
            room.price = request.form.get("price")
            room.is_reserved = True if request.form.get("is_reserved") else False

            photo = request.files.get("photo")
            if photo and photo.filename:
                room.img_name_orig = photo.filename
                room.img_name = uuid4().hex + "." + photo.filename.split(".")[-1]
                room.img_url = "/static/img/" + room.img_name
                photo.save("/app" + room.img_url)

            session.commit()
            return redirect(url_for("rooms.manage_rooms"))

        return render_template("edit_room.html", room=room)


@room_blueprint.get("/reserve/<int:id>/")
def reserve(id):
    with Session() as session:
        room = session.query(Room).filter_by(id=id).first()
        room.is_reserved = True
        session.commit()
        return render_template("reserved.html", room=room)