from dataclasses import dataclass
from datetime import datetime
from fasthtml.common import *
import humanize
import palantir as pltr

DELETE_STYLE = "background-color: #d93526; border-color: #d93526;"

app, rt = fast_app()


@dataclass
class EventForm:
    name: str
    location: str
    food: str
    dress_code: str
    when: str
    end: str


@rt("/")
def get():
    return Title("Cordially"), Hgroup(
        H1("Welcome to Cordially."),
        P("This is not how you use the app."),
        cls="container",
        style="text-align: center;",
    )


@rt("/admin")
def get():
    user = pltr.get_user()

    body = Div(P("No events"))
    events = pltr.events()

    if len(events) > 0:
        elements = []
        for e in events:
            timing = humanize.naturaldate(
                e.when if e.when is not None else datetime.today()
            ).capitalize()
            l = pltr.letter_by_event(e.id)

            elements.append(
                Details(
                    Summary(e.name),
                    Div(
                        P("Dear <RECIPIENT>,"),
                        P(
                            f"You are cordially invited to {e.name} on {timing} at {e.location}."
                        ),
                        P(l.content, style="white-space: pre;"),
                        A(
                            "Event Details",
                            hx_get=f"/event/edit?id={e.id}",
                            hx_target="body",
                        ),
                        " • ",
                        A(
                            "Edit Letter",
                            hx_get=f"/letter?id={l.id}",
                            hx_target="body",
                        ),
                        " • ",
                        A(
                            "Manage Invites",
                            hx_get=f"/event/recipients?event={e.id}&letter={l.id}",
                            hx_target="body",
                        ),
                        " • ",
                        A(
                            "View RSVPs",
                            hx_get=f"/event/rsvps?id={e.id}",
                            hx_target="body",
                        ),
                    ),
                    name="event",
                )
            )
            elements.append(Hr())
        if len(elements) > 1:
            elements.pop()
        body = Div(*elements)

    return Titled(
        f"Welcome, {user}.",
        body,
        Button(
            "New Event",
            hx_get="/event/create",
            hx_target="body",
            style="margin-inline-end: 1rem;",
        ),
        Button("Recipients", hx_get="/recipients", hx_target="body"),
    )


@rt("/event")
def delete(id: str):
    letter = pltr.letter_by_event(id).id
    if letter is not None:
        pltr.delete_letter(letter)
        pltr.delete_event(id)

    return Redirect("/admin")


@rt("/event/edit")
def get(id: str):
    event = pltr.event_by_id(id)
    if event is None:
        return Titled(
            "Error", P("Could not find this event"), A(Button("Back", href="/admin"))
        )

    return Titled(
        "Edit Event",
        Form(
            Input(type="hidden", name="id", value=id),
            Label(
                "Name",
                Input(
                    type="text",
                    id="name",
                    name="name",
                    required=True,
                    value=event.name,
                ),
                fr="name",
            ),
            Label(
                "Location",
                Input(
                    type="text",
                    id="location",
                    name="location",
                    placeholder="Chateau Bleu",
                    required=True,
                    value=event.location,
                ),
                fr="location",
            ),
            Div(
                Label(
                    "Start",
                    Input(
                        type="datetime-local",
                        id="when",
                        name="when",
                        required=True,
                        value=event.when.strftime("%Y-%m-%dT%H:%M:%S"),
                    ),
                    fr="when",
                ),
                Label(
                    "End",
                    Input(
                        type="datetime-local",
                        id="end",
                        name="end",
                        value=event.end.strftime("%Y-%m-%dT%H:%M:%S"),
                    ),
                    fr="end",
                ),
                cls="grid",
            ),
            Div(
                Label(
                    "Food",
                    Input(
                        type="text",
                        id="food",
                        name="food",
                        placeholder="Homemade feast",
                        value=event.food,
                    ),
                    fr="food",
                ),
                Label(
                    "Dress Code",
                    Input(
                        type="text",
                        id="dress_code",
                        name="dress_code",
                        placeholder="Black tie",
                        value=event.dress_code,
                    ),
                    fr="dress_code",
                ),
                cls="grid",
            ),
            Button("Save", style="margin-inline-end: 1rem;", hx_post="/event/edit"),
            Button(
                "Delete",
                style=DELETE_STYLE,
                hx_delete="/event",
                hx_confirm="Are you sure you want to delete the event?",
            ),
        ),
    )


@rt("/event/edit")
def post(data: EventForm, id: str):
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


@rt("/event/create")
def get():
    count = len(pltr.events()) + 1
    return Titled(
        "New Event",
        Form(
            Label(
                "Name",
                Input(
                    type="text",
                    id="name",
                    name="name",
                    placeholder=f"Event {count}",
                    required=True,
                ),
                fr="name",
            ),
            Label(
                "Location",
                Input(
                    type="text",
                    id="location",
                    name="location",
                    placeholder="Chateau Bleu",
                    required=True,
                ),
                fr="location",
            ),
            Div(
                Label(
                    "Start",
                    Input(type="datetime-local", id="when", name="when", required=True),
                    fr="when",
                ),
                Label(
                    "End",
                    Input(type="datetime-local", id="end", name="end"),
                    fr="end",
                ),
                cls="grid",
            ),
            Div(
                Label(
                    "Food",
                    Input(
                        type="text",
                        id="food",
                        name="food",
                        placeholder="Homemade feast",
                    ),
                    fr="food",
                ),
                Label(
                    "Dress Code",
                    Input(
                        type="text",
                        id="dress_code",
                        name="dress_code",
                        placeholder="Black tie",
                    ),
                    fr="dress_code",
                ),
                cls="grid",
            ),
            Button(
                "Create",
                style="margin-inline-end: 1rem;",
                hx_post="/event/create",
                hx_target="body",
            ),
            Button("Back", cls="secondary outline", hx_get="/admin", hx_target="body"),
        ),
    )


@rt("/event/create")
def post(data: EventForm):
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


@rt("/event/recipients")
def get(event: str, letter: str):
    body = Div(P("No recipients"))
    recipients = pltr.recipients()
    if len(recipients) > 0:
        elements = []
        for person in recipients:
            is_member = pltr.member_of_event(person, letter)

            buttons = []
            if is_member:
                buttons.append(
                    Button(
                        "-",
                        hx_delete=f"/event/recipients?id={letter}&person={person.id}",
                        hx_target="closest div",
                        hx_swap="outerHTML",
                        hx_trigger="click",
                        style=f"{DELETE_STYLE} padding: revert; line-height: unset; margin-inline-end: 1rem;",
                    )
                )
                buttons.append(
                    Span(
                        Button(
                            "Link",
                            hx_get=f"/event/link/show?ltr={letter}&rcp={person.id}",
                            hx_target=f"closest span",
                            hx_swap="outerHTML",
                            hx_trigger="click",
                            style="padding: revert; line-height: unset;",
                            cls="secondary",
                        ),
                    )
                )
            else:
                buttons.append(
                    Button(
                        "+",
                        hx_post=f"/event/recipients?id={letter}&person={person.id}",
                        hx_target="closest div",
                        hx_swap="outerHTML",
                        hx_trigger="click",
                        style="padding: revert; line-height: unset; margin-inline-end: 1rem;",
                    )
                )

            elements.append(Li(f"{person.honorific} {person.name} ", Div(*buttons)))
        body = Div(Ul(*elements))

    e = pltr.event_by_id(event)
    return Titled(
        e.name,
        body,
        Button("Back", cls="secondary outline", hx_get="/admin", hx_target="body"),
    )


@rt("/event/recipients")
def post(id: str, person: str):
    pltr.create_recipient_letter_link(person, id)
    return Div(
        Button(
            "-",
            hx_delete=f"/event/recipients?id={id}&person={person}",
            hx_target="closest div",
            hx_swap="outerHTML",
            hx_trigger="click",
            style=f"{DELETE_STYLE} padding: revert; line-height: unset; margin-inline-end: 1rem;",
        ),
        Span(
            Button(
                "Link",
                hx_get=f"/event/link/show?ltr={id}&rcp={person}",
                hx_target=f"closest span",
                hx_swap="outerHTML",
                hx_trigger="click",
                style="padding: revert; line-height: unset;",
                cls="secondary",
            ),
        ),
    )


@rt("/event/recipients")
def delete(id: str, person: str):
    pltr.delete_recipient_letter_link(person, id)

    letter = pltr.letter_by_id(id)
    rsvps = pltr.rsvps_between(letter.event_id, person)
    if len(rsvps) > 0:
        pltr.delete_rsvp(rsvps[0])

    return Div(
        Button(
            "+",
            hx_post=f"/event/recipients?id={id}&person={person}",
            hx_swap="outerHTML",
            hx_trigger="click",
            style="padding: revert; line-height: unset;",
        )
    )


@rt("/event/rsvps")
def get(id: str):
    body = Div(P("No RSVPs"))
    rsvps = pltr.rsvps_for(id)
    if len(rsvps) > 0:
        elements = []
        for rsvp in rsvps:
            person = pltr.recipient(rsvp.recipient_id)
            elements.append(Li(f"{person.honorific} {person.name} "))
        body = Div(Ul(*elements))

    e = pltr.event_by_id(id)
    return Titled(
        f"{e.name} RSVPs",
        body,
        Button("Back", cls="secondary outline", hx_get="/admin", hx_target="body"),
    )


@rt("/event/link/show")
def get(ltr: str, rcp: str):
    return Span(
        Input(type="text", value=f"/view/{ltr}/{rcp}", disabled=True),
        Button(
            "Hide",
            hx_get=f"/event/link/hide?ltr={ltr}&rcp={rcp}",
            hx_target=f"closest span",
            hx_swap="outerHTML",
            hx_trigger="click",
            style="padding: revert; line-height: unset;",
            cls="secondary",
        ),
        role="group",
        style="margin-block-start: 1rem;",
    )


@rt("/event/link/hide")
def get(ltr: str, rcp: str):
    return Span(
        Button(
            "Link",
            hx_get=f"/event/link/show?ltr={ltr}&rcp={rcp}",
            hx_target=f"closest span",
            hx_swap="outerHTML",
            hx_trigger="click",
            style="padding: revert; line-height: unset;",
            cls="secondary",
        ),
    )


@rt("/letter")
def get(id: str):
    letter = pltr.letter_by_id(id)
    if letter is None:
        return Titled(
            "Error", P("Could not find this letter."), A(Button("Back", href="/admin"))
        )

    return Titled(
        "Compose Letter",
        Form(
            Input(type="hidden", name="id", value=letter.id),
            Textarea(letter.content, name="content"),
            Button("Save", hx_post="/letter"),
        ),
    )


@rt("/letter")
def post(id: str, content: str):
    pltr.edit_letter(id, content)
    return Redirect("/admin")


@rt("/recipients")
def get():
    body = Div(P("No recipients"))
    recipients = pltr.recipients()
    if len(recipients) > 0:
        elements = []
        for person in recipients:
            elements.append(
                Li(
                    f"{person.honorific} {person.name} (",
                    A(
                        "Edit",
                        hx_get=f"/recipient/edit?id={person.id}",
                        hx_target="body",
                    ),
                    ")",
                )
            )
        body = Div(Ul(*elements))

    return Titled(
        "Recipients",
        body,
        Button(
            "New Recipient",
            hx_get="/recipient/create",
            hx_target="body",
            style="margin-inline-end: 1rem;",
        ),
        Button("Back", cls="secondary outline", hx_get="/admin", hx_target="body"),
    )


@rt("/recipient/create")
def get():
    return Titled(
        "New Recipient",
        Form(
            Label(
                "Honorific",
                Input(type="text", id="hnr", name="hnr", placeholder="Prof."),
                fr="hnr",
            ),
            Label(
                "Name",
                Input(type="text", id="name", name="name", placeholder="Diamond"),
                fr="name",
            ),
            Button(
                "Create",
                style="margin-inline-end: 1rem;",
                hx_post="/recipient/create",
                hx_target="body",
            ),
            Button(
                "Back", cls="secondary outline", hx_get="/recipients", hx_target="body"
            ),
        ),
    )


@rt("/recipient/create")
def post(name: str, hnr: str):
    pltr.create_recipient(name, hnr)
    return Redirect("/recipients")


@rt("/recipient/edit")
def get(id: str):
    recipient = pltr.recipient(id)
    if recipient is None:
        return Titled(
            "Error",
            P("Could not find this recipient"),
            A(Button("Back", href="/recipients")),
        )

    return Titled(
        "New Recipient",
        Form(
            Input(type="hidden", name="id", value=id),
            Label(
                "Honorific",
                Input(
                    type="text",
                    id="hnr",
                    name="hnr",
                    placeholder="Prof.",
                    value=recipient.honorific,
                ),
                fr="hnr",
            ),
            Label(
                "Name",
                Input(
                    type="text",
                    id="name",
                    name="name",
                    placeholder="Diamond",
                    value=recipient.name,
                ),
                fr="name",
            ),
            Button(
                "Save",
                style="margin-inline-end: 1rem;",
                hx_post="/recipient/edit",
                hx_target="body",
            ),
            Button(
                "Delete",
                style=DELETE_STYLE,
                hx_delete="/recipient",
                hx_confirm="Are you sure you want to delete the recipient?",
            ),
        ),
    )


@rt("/recipient/edit")
def post(id: str, name: str, hnr: str):
    pltr.edit_recipient(id, name, hnr)
    return Redirect("/recipients")


@rt("/recipient")
def delete(id: str):
    pltr.delete_recipient(id)
    return Redirect("/recipients")


@rt("/view/{ltr}/{rcp}")
def get(ltr: str, rcp: str):
    letter = pltr.letter_by_id(ltr)
    recipient = pltr.recipient(rcp)
    if letter is None or recipient is None:
        return Titled(
            "Error", P("Not sure what happened."), A(Button("Back", href="/admin"))
        )

    event = pltr.event_by_id(letter.event_id)

    is_member = pltr.member_of_event(recipient, ltr)
    if not is_member:
        return Titled(
            "None shall pass.", P("Are you lost?"), A(Button("Back", href="/admin"))
        )

    timing = humanize.naturaldate(
        event.when if event.when else datetime.today()
    ).capitalize()

    is_rsvpd = len(pltr.rsvps_between(event.id, recipient.id)) > 0
    button = Button(
        "RSVP",
        hx_post=f"/rsvp?evt={event.id}&rcp={recipient.id}",
        hx_swap="outerHTML",
        style="display: block; margin-inline: auto;",
    )
    if is_rsvpd:
        button = Button(
            "Cancel",
            hx_delete=f"/rsvp?evt={event.id}&rcp={recipient.id}",
            hx_swap="outerHTML",
            style=f"{DELETE_STYLE} display: block; margin-inline: auto;",
        )

    return Title(event.name), Main(
        Article(
            P(f"Dear {recipient.honorific} {recipient.name},"),
            P(
                f"You are cordially invited to {event.name} on {timing} at {event.location}."
            ),
            P(letter.content, style="white-space: pre-wrap;"),
            style="max-width: 25rem; margin-inline: auto;",
        ),
        button,
        cls="container",
    )


@rt("/rsvp")
def post(evt: str, rcp: str):
    pltr.create_rsvp(evt, rcp)
    return Button(
        "Cancel",
        hx_delete=f"/rsvp?evt={evt}&rcp={rcp}",
        hx_swap="outerHTML",
        style=f"{DELETE_STYLE} display: block; margin-inline: auto;",
    )


@rt("/rsvp")
def delete(evt: str, rcp: str):
    rsvp = pltr.rsvps_between(evt, rcp)[0]
    pltr.delete_rsvp(rsvp)
    return (
        Button(
            "RSVP",
            hx_post=f"/rsvp?evt={evt}&rcp={rcp}",
            hx_swap="outerHTML",
            style="display: block; margin-inline: auto;",
        ),
    )


serve()
