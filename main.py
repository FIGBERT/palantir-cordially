import os
from dataclasses import dataclass
from datetime import datetime
from cordially_sdk import UserTokenAuth, FoundryClient
from cordially_sdk.ontology.objects import Event, Letter
from fasthtml.common import *
import humanize

auth = UserTokenAuth(token=os.environ["FOUNDRY_TOKEN"])
client = FoundryClient(auth=auth, hostname="https://figbert.usw-18.palantirfoundry.com")
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
    user = client.foundry_sdk.admin.User.get_current().given_name

    body = Div(P("No events"))
    events = list(
        client.ontology.objects.Event.order_by(Event.object_type.when.asc()).iterate()
    )

    if len(events) > 0:
        elements = []
        for e in events:
            timing = humanize.naturaldate(
                e.when if e.when is not None else datetime.today()
            ).capitalize()
            l = list(
                client.ontology.objects.Letter.where(
                    Letter.object_type.event_id == e.id
                ).iterate()
            )[0]

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
    letter = list(
        client.ontology.objects.Letter.where(
            Letter.object_type.event_id == id
        ).iterate()
    )[0].id
    if letter is not None:
        _ = client.ontology.actions.delete_letter(letter=letter)
        _ = client.ontology.actions.delete_event(event=id)

    return Redirect("/admin")


@rt("/event/edit")
def get(id: str):
    event = client.ontology.objects.Event.get(id)
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
                style="background-color: #d93526; border-color: #d93526;",
                hx_delete="/event",
                hx_confirm="Are you sure you want to delete the event?",
            ),
        ),
    )


@rt("/event/edit")
def post(data: EventForm, id: str):
    end = datetime.fromisoformat(data.end) if data.end != "" else datetime.min

    _ = client.ontology.actions.edit_event(
        event=id,
        name=data.name,
        location=data.location,
        accepting_invites=True,
        when=datetime.fromisoformat(data.when),
        end=end,
        food=data.food,
        dress_code=data.dress_code,
    )
    return Redirect("/admin")


@rt("/event/create")
def get():
    count = len(list(client.ontology.objects.Event.iterate())) + 1
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
    _ = client.ontology.actions.create_event(
        name=data.name,
        location=data.location,
        accepting_invites=True,
        when=datetime.fromisoformat(data.when),
        end=end,
        food=data.food,
        dress_code=data.dress_code,
    )

    event = list(
        client.ontology.objects.Event.where(
            Event.object_type.name == data.name
        ).iterate()
    )[0].id
    if event is not None:
        _ = client.ontology.actions.create_letter(event_id=event, content="")
        letter = list(
            client.ontology.objects.Letter.where(
                Letter.object_type.event_id == event
            ).iterate()
        )[0].id
        return Redirect(f"/letter?id={letter}")

    return Redirect("/admin")


@rt("/letter")
def get(id: str):
    letter = client.ontology.objects.Letter.get(id)
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
    _ = client.ontology.actions.edit_letter(letter=id, content=content)
    return Redirect("/admin")


@rt("/recipients")
def get():
    body = Div(P("No recipients"))
    recipients = list(client.ontology.objects.Recipient.iterate())
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
    _ = client.ontology.actions.create_recipient(name=name, honorific=hnr)
    return Redirect("/recipients")


@rt("/recipient/edit")
def get(id: str):
    recipient = client.ontology.objects.Recipient.get(id)
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
                style="background-color: #d93526; border-color: #d93526;",
                hx_delete="/recipient",
                hx_confirm="Are you sure you want to delete the recipient?",
            ),
        ),
    )


@rt("/recipient/edit")
def post(id: str, name: str, hnr: str):
    _ = client.ontology.actions.edit_recipient(recipient=id, name=name, honorific=hnr)
    return Redirect("/recipients")


@rt("/recipient")
def delete(id: str):
    _ = client.ontology.actions.delete_recipient(recipient=id)
    return Redirect("/recipients")


serve()
