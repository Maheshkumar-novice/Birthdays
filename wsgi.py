import datetime
from typing import Annotated

from dotenv import load_dotenv
from flask import Flask, Response, redirect, render_template, request, url_for
from sqlalchemy import String, create_engine, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column
from sqlalchemy.sql import expression
from turbo_flask import Turbo

load_dotenv()
engine = create_engine("sqlite:///main.db", echo=True)

class Base(DeclarativeBase):
    pass


class Birthday(Base):
    __tablename__ = "birthdays"

    _timestamp = Annotated[
        datetime.datetime,
        mapped_column(nullable=True),
    ]

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(500))
    date: Mapped[_timestamp]
    is_deleted: Mapped[bool] = mapped_column(
        default=False,
        server_default=expression.false(),
    )


app = Flask(__name__)
turbo = Turbo(app)


@app.route("/", methods=["GET"])
def home() -> str:
    return render_template(
        "home.html",
    )


@app.route("/birthdays", methods=["GET"])
def links() -> str:
    with Session(engine) as session:
        return render_template(
            "birthdays.html",
            birthdays=session.scalars(
                select(Birthday).where(Birthday.is_deleted == False),  # noqa: E712
            ),
        )


@app.route("/", methods=["POST"])
def create() -> Response:
    name = request.form["name"]
    date = request.form["date"]
    date = datetime.datetime.strptime(date, "%Y-%m-%d").astimezone()

    with Session(engine) as session:
        birthday = Birthday(name=name, date=date)
        session.add(birthday)
        session.commit()

        if turbo.can_stream():
            content = render_template("birthday.html", birthday=birthday)

            if turbo.can_push():
                turbo.push(
                    turbo.append(content, target="birthdays"),
                )

            return turbo.stream(
                turbo.append(content, target="birthdays"),
            )

        return redirect(url_for("home")), 303


@app.route("/delete/<int:id>", methods=["DELETE"])
def delete(id: int) -> Response:
    with Session(engine) as session:
        birthday = session.get(Birthday, id)
        birthday.is_deleted = True
        session.commit()

        if turbo.can_stream():
            if turbo.can_push():
                turbo.push(turbo.remove(id))
            return turbo.stream(turbo.remove(id))

    return redirect(url_for("home")), 303
