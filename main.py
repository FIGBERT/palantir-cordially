import os
from dataclasses import dataclass
from datetime import datetime
from cordially_sdk import UserTokenAuth, FoundryClient
from cordially_sdk.ontology.objects import Event
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
        H1(f"Welcome to Cordially."),
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
        body = Div(
            *[
                Article(
                    e.name,
                    Footer(
                        e.location,
                        Br(),
                        humanize.naturaldate(
                            e.when if e.when is not None else datetime.today()
                        ).capitalize(),
                    ),
                    hx_get=f"/event/edit?id={e.id}",
                    hx_target="body",
                    style="width: 15rem;",
                )
                for e in events
            ],
            style="display: flex; justify-content: space-between; flex-wrap: wrap;",
        )

    return Titled(
        f"Welcome, {user}.",
        body,
        Button("New Event", hx_get="/event/create", hx_target="body"),
    )


@rt("/event")
def delete(id: str):
    _ = client.ontology.actions.delete_event(event=id)
    return Redirect("/admin")


@rt("/event/edit")
def get(id: str):
    event = client.ontology.objects.Event.get(id=id)
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
                style="background-color: #d93526; border-color: #d93526; margin-inline-end: 1rem;",
                hx_delete="/event",
                hx_confirm="Are you sure you want to delete the event?",
            ),
            Button("Back", cls="secondary outline", hx_get="/admin", hx_target="body"),
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
    return Redirect("/admin")


serve()
