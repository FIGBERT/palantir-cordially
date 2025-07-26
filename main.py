from dataclasses import dataclass
from datetime import datetime

import humanize
from fasthtml import Redirect, ft, serve
from fasthtml import fastapp as fa

import palantir as pltr
import templating as tmpl

app, _ = fa.fast_app()


@dataclass
class EventForm:
    name: str
    location: str
    food: str
    dress_code: str
    when: str
    end: str


@app.get
def index():
    return ft.Title("Cordially"), ft.Hgroup(
        ft.H1("Welcome to Cordially."),
        ft.P("This is not how you use the app."),
        cls="container",
        style="text-align: center;",
    )


@app.get
def admin():
    user = pltr.get_user()

    body = ft.Div(ft.P("No events"))
    events = pltr.events()

    if len(events) > 0:
        elements = []
        for e in events:
            timing = humanize.naturaldate(
                e.when if e.when else datetime.today()
            ).capitalize()
            l = pltr.letter_by_event(e.id)

            elements.append(
                ft.Details(
                    ft.Summary(e.name),
                    ft.Div(
                        ft.P("Dear <RECIPIENT>,"),
                        ft.P(
                            f"You are cordially invited to {e.name} on {timing} at {e.location}."
                        ),
                        ft.P(l.content, style="white-space: pre;"),
                        ft.A(
                            "Event Details",
                            hx_get=event_editor.to(id=e.id),
                            hx_target="body",
                        ),
                        " • ",
                        ft.A(
                            "Edit Letter",
                            hx_get=letter_editor.to(id=l.id),
                            hx_target="body",
                        ),
                        " • ",
                        ft.A(
                            "Manage Invites",
                            hx_get=event_recipients.to(event=e.id, letter=l.id),
                            hx_target="body",
                        ),
                        " • ",
                        ft.A(
                            "View RSVPs",
                            hx_get=event_rsvps.to(id=e.id),
                            hx_target="body",
                        ),
                    ),
                    name="event",
                )
            )
            elements.append(ft.Hr())
        if len(elements) > 1:
            elements.pop()
        body = ft.Div(*elements)

    return ft.Titled(
        f"Welcome, {user}.",
        body,
        ft.Button(
            "New Event",
            hx_get=event_creator.to(),
            hx_target="body",
            style="margin-inline-end: 1rem;",
        ),
        ft.Button("Recipients", hx_get=recipients.to(), hx_target="body"),
    )


@app.get("/event/create")
def event_creator():
    return tmpl.event(count=len(pltr.events()) + 1)


@app.post("/event/create")
def create_event(data: EventForm):
    end = datetime.fromisoformat(data.end) if data.end != "" else datetime.min
    pltr.create_event(
        data.name,
        data.location,
        datetime.fromisoformat(data.when),
        end,
        data.food,
        data.dress_code,
    )

    event = pltr.event_by_name(data.name).id
    if event is not None:
        pltr.create_letter(event)
        letter = pltr.letter_by_event(event).id
        return Redirect(f"/letter?id={letter}")

    return Redirect("/admin")


@app.get("/event/edit")
def event_editor(id: str):
    event = pltr.event_by_id(id)
    if event is None:
        return tmpl.generic_err()
    return tmpl.event(evt=event)


@app.post("/event/edit")
def edit_event(data: EventForm, id: str):
    end = datetime.fromisoformat(data.end) if data.end != "" else datetime.min
    pltr.edit_event(
        id,
        data.name,
        data.location,
        datetime.fromisoformat(data.when),
        end,
        data.food,
        data.dress_code,
    )
    return Redirect("/admin")


@app.delete
def delete_event(id: str):
    letter = pltr.letter_by_event(id).id
    if letter is not None:
        pltr.delete_letter(letter)
        pltr.delete_event(id)

    return Redirect("/admin")


@app.get("/event/recipients")
def event_recipients(event: str, letter: str):
    body = ft.Div(ft.P("No recipients"))
    recipients = pltr.recipients()
    if len(recipients) > 0:
        elements = []
        for person in recipients:
            is_member = pltr.member_of_event(person, letter)

            buttons = []
            if is_member:
                buttons.append(tmpl.remove_recipient_button(letter, person.id))
                buttons.append(tmpl.recipient_show_link_button(letter, person.id))
            else:
                buttons.append(tmpl.add_recipient_button(letter, person.id))

            elements.append(
                ft.Li(f"{person.honorific} {person.name} ", ft.Div(*buttons))
            )
        body = ft.Div(ft.Ul(*elements))

    e = pltr.event_by_id(event)
    return ft.Titled(
        f"{e.name if e else 'Event'}",
        body,
        ft.Button("Back", cls="secondary outline", hx_get=admin.to(), hx_target="body"),
    )


@app.post("/event/recipients")
def add_recipient_to_event(id: str, person: str):
    pltr.create_recipient_letter_link(person, id)
    return ft.Div(
        tmpl.remove_recipient_button(id, person),
        tmpl.recipient_show_link_button(id, person),
    )


@app.delete("/event/recipients")
def remove_recipient_from_event(id: str, person: str):
    pltr.delete_recipient_letter_link(person, id)

    letter = pltr.letter_by_id(id)
    rsvps = pltr.rsvps_between(letter.event_id if letter else None, person)
    if len(rsvps) > 0:
        pltr.delete_rsvp(rsvps[0])

    return ft.Div(tmpl.add_recipient_button(id, person))


@app.get("/event/link/show")
def show_recipient_event_link(ltr: str, rcp: str):
    return tmpl.recipient_link(ltr, rcp)


@app.get("/event/link/hide")
def hide_recipient_event_link(ltr: str, rcp: str):
    return tmpl.recipient_show_link_button(ltr, rcp)


@app.get("/event/rsvps")
def event_rsvps(id: str):
    body = ft.Div(ft.P("No RSVPs"))
    rsvps = pltr.rsvps_for(id)
    if len(rsvps) > 0:
        elements = []
        for rsvp in rsvps:
            person = pltr.recipient(rsvp.recipient_id)
            elements.append(
                ft.Li(
                    f"{person.honorific if person else ''} {person.name if person else ''} "
                )
            )
        body = ft.Div(ft.Ul(*elements))

    e = pltr.event_by_id(id)
    return ft.Titled(
        f"{e.name if e else 'Your'} RSVPs",
        body,
        ft.Button("Back", cls="secondary outline", hx_get=admin.to(), hx_target="body"),
    )


@app.get("/letter")
def letter_editor(id: str):
    letter = pltr.letter_by_id(id)
    if letter is None:
        return tmpl.generic_err()

    return ft.Titled(
        "Compose Letter",
        ft.Form(
            ft.Input(type="hidden", name="id", value=letter.id),
            ft.Textarea(letter.content, name="content"),
            ft.Button("Save", hx_post=edit_letter.to()),
        ),
    )


@app.post("/letter")
def edit_letter(id: str, content: str):
    pltr.edit_letter(id, content)
    return Redirect("/admin")


@app.get("/recipients")
def recipients():
    body = ft.Div(ft.P("No recipients"))
    recipients = pltr.recipients()
    if len(recipients) > 0:
        elements = []
        for person in recipients:
            elements.append(
                ft.Li(
                    f"{person.honorific} {person.name} (",
                    ft.A(
                        "Edit",
                        hx_get=recipient_editor.to(id=person.id),
                        hx_target="body",
                    ),
                    ")",
                )
            )
        body = ft.Div(ft.Ul(*elements))

    return ft.Titled(
        "Recipients",
        body,
        ft.Button(
            "New Recipient",
            hx_get=recipient_creator.to(),
            hx_target="body",
            style="margin-inline-end: 1rem;",
        ),
        ft.Button("Back", cls="secondary outline", hx_get=admin.to(), hx_target="body"),
    )


@app.get("/recipient/create")
def recipient_creator():
    return tmpl.recipient()


@app.post("/recipient/create")
def create_recipient(name: str, hnr: str):
    pltr.create_recipient(name, hnr)
    return Redirect("/recipients")


@app.get("/recipient/edit")
def recipient_editor(id: str):
    recipient = pltr.recipient(id)
    if recipient is None:
        return tmpl.generic_err()
    return tmpl.recipient(recipient)


@app.post("/recipient/edit")
def edit_recipient(id: str, name: str, hnr: str):
    pltr.edit_recipient(id, name, hnr)
    return Redirect("/recipients")


@app.delete("/recipient")
def delete_recipient(id: str):
    pltr.delete_recipient(id)
    return Redirect("/recipients")


@app.post("/rsvp")
def create_rsvp(evt: str, rcp: str):
    pltr.create_rsvp(evt, rcp)
    return tmpl.rsvp_button(evt, rcp, True)


@app.delete("/rsvp")
def delete_rsvp(evt: str, rcp: str):
    rsvp = pltr.rsvps_between(evt, rcp)[0]
    pltr.delete_rsvp(rsvp)
    return tmpl.rsvp_button(evt, rcp)


@app.get("/view/{ltr}/{rcp}")
def bespoke_view(ltr: str, rcp: str):
    letter = pltr.letter_by_id(ltr)
    recipient = pltr.recipient(rcp)
    if letter is None or recipient is None:
        return tmpl.generic_err()

    event = pltr.event_by_id(letter.event_id)
    if event is None:
        return tmpl.generic_err()

    is_member = pltr.member_of_event(recipient, ltr)
    if not is_member:
        return tmpl.permission_err()

    timing = humanize.naturaldate(
        event.when if event.when else datetime.today()
    ).capitalize()

    is_rsvpd = len(pltr.rsvps_between(event.id, recipient.id)) > 0
    return ft.Title(event.name), ft.Main(
        ft.Article(
            ft.P(f"Dear {recipient.honorific} {recipient.name},"),
            ft.P(
                f"You are cordially invited to {event.name} on {timing} at {event.location}."
            ),
            ft.P(letter.content, style="white-space: pre-wrap;"),
            style="max-width: 25rem; margin-inline: auto;",
        ),
        tmpl.rsvp_button(event.id, recipient.id, is_rsvpd),
        cls="container",
    )


serve()
